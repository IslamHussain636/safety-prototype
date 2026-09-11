import copy
import json
import unittest
from unittest.mock import patch, Mock
import requests
from backend_server import create_app, normalize, parse_composer, ApiError
from engine import synthesize, validate, diversity, weak_category
from catalog import CATALOG

class EngineTests(unittest.TestCase):
    def req(self, **kw): return normalize({"prompt": "fall and electrical", **kw})

    def test_many_seeded_layouts_pass(self):
        for level in ("apprentice", "intermediate", "experienced"):
            for seed in range(100):
                spec=synthesize(self.req(seed=seed,level=level))
                self.assertTrue(validate(spec)["passed"], (seed,level,validate(spec)))

    def test_same_seed_same_output_and_different_seed_varies(self):
        self.assertEqual(synthesize(self.req()),synthesize(self.req()))
        a,b=synthesize(self.req(seed=1)),synthesize(self.req(seed=2))
        self.assertNotEqual(a["scenario_id"],b["scenario_id"])
        self.assertGreater(diversity([a,b])["pairs"][0]["mean_shared_category_displacement_m"],0)

    def test_static_baseline_is_fixed(self):
        a=synthesize(self.req(strategy="static",seed=1))
        b=synthesize(self.req(strategy="static",seed=500,level="experienced",focus=["ppe_missing"]))
        self.assertEqual(a,b)

    def test_adaptive_and_required_categories_are_preserved(self):
        profile={k:{"attempts":10,"correct":10} for k in CATALOG}
        profile["caught_in_between"]["correct"]=0
        req=self.req(strategy="adaptive",profile=profile,level="apprentice",focus=["ppe_missing"])
        spec=synthesize(req,{"hazard_types":["fall","electrical","struck_by"]})
        self.assertEqual(spec["targeted_weak_category"],"caught_in_between")
        self.assertEqual({h["type"] for h in spec["hazards"]},set(CATALOG))
        self.assertTrue(validate(spec)["passed"])
        self.assertIsNone(weak_category({}))

    def test_invalid_geometry_and_catalog_fail_closed(self):
        base=synthesize(self.req())
        for field,value in [("x",-1),("x",float('nan')),("osha_ref","1926.999"),("source_url","https://evil.example"),("conditions",{}),("description","Injected instructions"),("asset","unknown")]:
            bad=copy.deepcopy(base);bad["hazards"][0][field]=value
            self.assertFalse(validate(bad)["passed"],field)
        bad=copy.deepcopy(base);bad["hazards"][1]["x"]=bad["hazards"][0]["x"];bad["hazards"][1]["y"]=bad["hazards"][0]["y"]
        self.assertFalse(validate(bad)["passed"])
        bad=copy.deepcopy(base);bad["spawn"]={"x":bad["hazards"][0]["x"],"y":bad["hazards"][0]["y"]}
        self.assertFalse(validate(bad)["passed"])
        bad=copy.deepcopy(base);bad["hazards"][0]["approach"]={"x":40,"y":40}
        self.assertFalse(validate(bad)["passed"])

    def test_bad_composer_outputs_rejected(self):
        good='{"hazard_types":["fall","electrical","struck_by"]}'
        self.assertEqual(parse_composer('```json\n'+good+'\n```')["hazard_types"][0],"fall")
        for raw in [good+' junk','{"hazard_types":["fake"]}','{"hazard_types":["fall","fall","fall"]}','{"hazard_types":NaN}', '{"hazard_types":[],"hazard_types":["fall","electrical","struck_by"]}']:
            with self.assertRaises(Exception):parse_composer(raw)

class ApiTests(unittest.TestCase):
    def setUp(self):
        self.app=create_app({"TESTING":True,"OPENROUTER_API_KEY":"private-test-key","OPENROUTER_MODEL":"test/model","APP_ACCESS_TOKEN":"test-access","LIVE_CALLS_PER_HOUR":30})
        self.client=self.app.test_client()

    def live(self):
        return self.client.post('/api/generate',json={"prompt":"fall", "source":"openrouter"},headers={"Authorization":"Bearer test-access"})

    def response(self,content):
        r=Mock(status_code=200);r.json.return_value={"choices":[{"message":{"content":content},"finish_reason":"stop"}],"model":"test/model","usage":{"total_tokens":40}}
        return r

    def test_health_and_ui(self):
        with self.client.get('/') as r:
            self.assertEqual(r.status_code,200)
        self.assertNotIn('private-test-key',self.client.get('/health').text)
        self.assertEqual(self.client.get('/api/catalog').status_code,200)

    def test_demo_and_batch(self):
        for path in ['/generate','/api/generate','/api/batch']:
            r=self.client.post(path,json={"prompt":"fall"})
            self.assertEqual(r.status_code,200,r.text)
        data=self.client.post('/api/batch',json={"prompt":"fall"}).json
        self.assertEqual(len(data['items']),3)
        self.assertEqual(data['diversity']['unique_scenarios'],3)

    def test_request_validation(self):
        for body in [None,[],{}, {"prompt":" "},{"prompt":"x","seed":True},{"prompt":"x","seed":-1},{"prompt":"x","level":"expert"},{"prompt":"x","url":"https://evil.example"},{"prompt":"x","profile":{"fall":{"attempts":1,"correct":2}}}]:
            r=self.client.post('/api/generate',data=json.dumps(body),content_type='application/json')
            self.assertEqual(r.status_code,400,r.text)
        self.assertEqual(self.client.post('/api/generate',data='{bad',content_type='application/json').status_code,400)
        self.assertEqual(self.client.post('/api/generate',data='x').status_code,415)
        self.assertEqual(self.client.post('/api/generate',json={"prompt":"x"*17000}).status_code,413)

    @patch('backend_server.requests.post')
    def test_openrouter_contract(self,post):
        post.return_value=self.response('{"hazard_types":["fall","electrical","struck_by"]}')
        r=self.live();self.assertEqual(r.status_code,200,r.text)
        args=post.call_args.kwargs
        self.assertEqual(args['json']['response_format']['type'],'json_schema')
        self.assertTrue(args['json']['provider']['require_parameters'])
        self.assertNotIn('private-test-key',r.text)
        self.assertTrue(r.json['validation']['passed'])

    @patch('backend_server.requests.post')
    def test_auth_blocks_provider(self,post):
        r=self.client.post('/api/generate',json={"prompt":"fall","source":"openrouter"})
        self.assertEqual(r.status_code,401);post.assert_not_called()

    @patch('backend_server.requests.post')
    def test_bad_provider_response_not_rendered(self,post):
        post.return_value=self.response('{"hazard_types":["unknown"]}')
        r=self.live();self.assertEqual(r.status_code,502);self.assertNotIn('scenario',r.json)
        for malformed in [[],{"choices":["bad"]},{"choices":[{"message":[],"finish_reason":"stop"}]}]:
            post.return_value.json.return_value=malformed
            self.assertEqual(self.live().status_code,502)
        post.side_effect=requests.Timeout('private-test-key')
        r=self.live();self.assertEqual(r.status_code,504);self.assertNotIn('private-test-key',r.text)

    @patch('backend_server.requests.post')
    def test_upstream_http_errors_sanitized(self,post):
        for code in [401,402,429,500]:
            post.return_value=Mock(status_code=code,text='private-test-key')
            r=self.live();self.assertEqual(r.status_code,502);self.assertNotIn('private-test-key',r.text)

    @patch('backend_server.requests.post')
    def test_live_rate_limit_and_static_no_call(self,post):
        self.app.config['LIVE_CALLS_PER_HOUR']=0
        self.assertEqual(self.live().status_code,429);post.assert_not_called()
        r=self.client.post('/api/generate',json={"prompt":"x","strategy":"static","source":"openrouter"})
        self.assertEqual(r.status_code,200);post.assert_not_called()

    @patch('backend_server.requests.post')
    def test_ollama_and_batch_single_composition(self,post):
        post.return_value=Mock(status_code=200)
        post.return_value.json.return_value={"done":True,"message":{"content":'{"hazard_types":["fall","electrical","struck_by"]}'}}
        r=self.client.post('/api/batch',json={"prompt":"x","source":"ollama"},headers={"Authorization":"Bearer test-access"})
        self.assertEqual(r.status_code,200,r.text);self.assertEqual(post.call_count,1)
        self.assertEqual(len(r.json['items']),3)

if __name__=='__main__':unittest.main()
