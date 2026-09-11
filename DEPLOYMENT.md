# Deploy the prototype

The package serves its frontend and backend together from port **7860**, and includes a Dockerfile. Use a Docker-capable host. A static-only service cannot run this Python backend or safely hold an OpenRouter key.

## Option 1 — Coolify on a server you control

[Coolify](https://coolify.io/docs/get-started/introduction) is an open-source, self-hostable deployment platform. It manages applications on infrastructure you supply; the software being open source does not make the server free. Use an existing university server or your own suitable VPS.

1. Install or use an existing Coolify instance and connect a server, following its current official setup instructions.
2. Put the **contents of this package** in a Git repository. `Dockerfile`, `requirements.txt`, and `backend_server.py` should be at its root. Preserve the entire `static/` directory and dotfiles; omit `.env`, local virtual environments and personal practice logs.
3. In the target Coolify project/environment select **+ New**, connect the repository, and choose **Dockerfile** as the build pack. Set the repository root as the build context and `Dockerfile` as its location.
4. Set the exposed internal port to **7860**. The image already sets `HOST=0.0.0.0` and `PORT=7860`.
5. Add an HTTPS domain and configure DNS as required by your server. For no-key procedural mode, no model secrets are necessary. For OpenRouter, add runtime environment variables `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, and `APP_ACCESS_TOKEN`. Do not put secrets in build arguments.
6. Deploy and inspect build/application logs. Configure the health endpoint as `/health` on port 7860 if using Coolify’s separate health configuration.
7. Open the HTTPS URL, generate a procedural scenario, then test OpenRouter with the demo token. Check mobile rendering, export and a real headset before an interview.

These settings follow [Coolify’s Dockerfile deployment instructions](https://coolify.io/docs/applications/builds/dockerfile). Keep one application process/replica for the supplied in-memory limit. A larger service needs shared rate limiting and per-user authentication.

## Option 2 — Hugging Face Docker Spaces

Hugging Face is a convenient place to showcase research demos and their source. **Its current documentation says Docker/Gradio Spaces require a paid plan to create.** Static Spaces remain free, but cannot run this backend. CPU Basic has no hourly compute charge under the documented arrangement; that is different from the account plan requirement. Check eligibility before choosing this route. [Spaces overview and current requirements](https://huggingface.co/docs/hub/spaces-overview).

1. Create a Space in your account; choose **Docker** and a blank template. Choose visibility intentionally: a public Space exposes both the app and repository.
2. Upload this package’s contents into the Space repository. Keep this package’s `README.md`; its YAML selects `sdk: docker` and `app_port: 7860`. Include all Python files, `requirements.txt`, `Dockerfile`, `static/`, and third-party licenses. No need to upload the proposal or old source files.
3. Commit the upload. Wait for the Docker build to finish and the app to report Running.
4. Try no-key procedural mode first. Then in **Settings → Variables and secrets**, add `OPENROUTER_API_KEY` and `APP_ACCESS_TOKEN` as **secrets**, and `OPENROUTER_MODEL` as a non-sensitive variable. Restart if necessary.
5. Open the app’s direct HTTPS address, select OpenRouter and enter only the demo access token. The OpenRouter key stays in the container.
6. For WebXR, open the direct app URL in the headset browser rather than relying on an embedded page. Actual headset support remains to be verified on your device.

Docker Spaces accept the custom Dockerfile and runtime environment settings; see [Docker Spaces](https://huggingface.co/docs/hub/spaces-sdks-docker). Hosted `localhost` refers to the container, so an Ollama instance running on your laptop is not reachable there. Prefer OpenRouter for this deployment, or separately provision model inference.

## Test the image yourself

With Docker installed, open a terminal in the package root:

```powershell
docker build -t pcgml-demo .
docker run --rm -p 127.0.0.1:7860:7860 pcgml-demo
```

For live inference, copy `.env.example` to a private `.env`, fill the relevant values in an editor, then use:

```powershell
docker run --rm --env-file .env -p 127.0.0.1:7860:7860 pcgml-demo
```

Open [localhost:7860](http://localhost:7860). This binding is for local use; Coolify or your hosting service handles external HTTPS. On Docker Desktop, a host-running Ollama service generally needs `OLLAMA_BASE_URL=http://host.docker.internal:11434` and an appropriate host listener configuration. Do not expose Ollama publicly just to make this work.

## Deployment checks

| Symptom | Check |
|---|---|
| Page is blank or requests fail | Open the backend URL; do not launch the HTML as a file. |
| Live call returns 401 | Enter the configured `APP_ACCESS_TOKEN` in the page. A provider-key rejection is reported separately. |
| Live call returns 503 | Configure the server model/key and demo token, then restart. |
| Structured-output request rejected | Select an OpenRouter endpoint supporting the supplied schema; see the provider documentation. |
| Insufficient credit or rate limit | Check OpenRouter account/model availability or switch to no-key mode. |
| VR button unavailable | Use HTTPS or localhost on a supported browser/headset. Desktop fullscreen is not immersive VR. |
| Practice history disappeared | It is local browser storage, not server storage; use exports and the same browser/origin. |
| Hosting health fails | Ensure the process binds `0.0.0.0:7860` and the proxy targets that port. |

The Docker image has **not** been built in the authoring environment because Docker was unavailable. Local Python/Waitress and desktop browser behavior were tested. Publishing requires your selected host/account; this package has not been publicly deployed.
