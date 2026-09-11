"""Local synthetic engineering benchmark; contains no human outcome measurements."""
import argparse
import csv
import json
import statistics
import time
from pathlib import Path
from backend_server import normalize
from catalog import CATALOG
from engine import VERSION, synthesize, validate, diversity

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--runs',type=int,default=30)
    parser.add_argument('--out',type=Path,default=Path('data'))
    args=parser.parse_args()
    if not 1 <= args.runs <= 1000: parser.error('--runs must be 1–1000')
    args.out.mkdir(parents=True,exist_ok=True)
    profile={k:{'attempts':10,'correct':9} for k in CATALOG}
    profile['caught_in_between']['correct']=1
    rows,summary=[],{}
    for strategy in ['static','procedural','adaptive']:
        specs=[]
        for seed in range(args.runs):
            req=normalize({'prompt':'Practice construction safety','seed':seed,'strategy':strategy,'level':'intermediate','profile':profile})
            start=time.perf_counter();spec=synthesize(req);report=validate(spec)
            elapsed=(time.perf_counter()-start)*1000
            specs.append(spec)
            rows.append({'strategy':strategy,'seed':spec['seed'],'scenario_id':spec['scenario_id'],'passed':report['passed'],'generation_and_validation_ms':round(elapsed,3),'hazards':len(spec['hazards']),'weak_category_present':any(h['type']=='caught_in_between' for h in spec['hazards'])})
        part=rows[-args.runs:]
        # Adjacent pairs avoid quadratic output; denominator is explicit.
        pairs=[diversity(specs[i:i+2])['pairs'][0] for i in range(len(specs)-1)]
        latencies=sorted(r['generation_and_validation_ms'] for r in part)
        summary[strategy]={'runs':args.runs,'passed':sum(r['passed'] for r in part),'unique_scenarios':len({s['scenario_id'] for s in specs}),'median_ms':round(statistics.median(latencies),3),'weak_category_coverage':sum(r['weak_category_present'] for r in part)/args.runs,'adjacent_pair_count':len(pairs),'mean_category_jaccard_distance':round(statistics.mean(p['category_jaccard_distance'] for p in pairs),4) if pairs else None}
    result={'engine_version':VERSION,'kind':'synthetic_local_engineering_benchmark','source':'procedural_only_no_model_calls','summary':summary,'limitations':['Fixed synthetic profile; no trainee data or learning-effect measurements.','Passing rates cover only encoded constraints, not complete OSHA compliance.','Static baseline has 3 modules; other strategies use 4, so latency is not a controlled authoring-efficiency comparison.','Timing depends on hardware and runtime. No model accuracy or latency is measured.']}
    (args.out/'benchmark-summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    with (args.out/'benchmark-runs.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
