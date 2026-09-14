# Day 7/7 — Deploy the AI Agent to Render

This is Part 7 of the 7-part series. In the series we built a first AI
agent with `gpt-5.4-mini`, Python, tools, validation, memory, and FastAPI.

## Deployment Overview

```text
GitHub repository
		↓
Render Web Service
		↓
Install dependencies
		↓
Start FastAPI with Uvicorn
		↓
Public HTTPS URL
```

The deployed service exposes the FastAPI application. Requests are validated
by the API, passed to the agent, and returned as JSON. The agent can use the
weather and stock tools, which call their configured external APIs.

## 1. Verify the Project Before Pushing

From the project directory, verify that the repository contains the files
used by the application:

```text
app.py
requirements.txt
.gitignore
```

Confirm that `requirements.txt` includes every runtime dependency imported by
the application, including FastAPI, Uvicorn, the OpenAI SDK, and the clients
used by the weather and stock tools.

Run the application locally first:

```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

Then open:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
```

Fix local import, validation, or environment-variable errors before deploying.

## 2. Protect Secrets

Never commit `.env`, API keys, or other secrets to GitHub. Add `.env` to
`.gitignore` and use local environment variables only for local development.

The Render service must define these environment variables:

```text
OPENAI_API_KEY
WEATHER_API_KEY
```

Use the exact names expected by the application. Do not paste key values into
this document, source code, README files, or request examples.

## 3. Push the Application to GitHub

Commit the application code, dependency file, and deployment documentation:

```bash
git add .
git commit -m "Deploy AI agent"
git push origin main
```

Use the branch containing `app.py` and `requirements.txt` when creating the
Render service.

## 4. Create the Render Web Service

1. Sign in to [Render](https://render.com/).
2. Select **New +** and choose **Web Service**.
3. Connect the GitHub repository containing this project.
4. Select the deployment branch.
5. Configure the service as follows:

```text
Runtime: Python
Build Command: pip install -r requirements.txt
Start Command: cd app && uvicorn app:app --host 0.0.0.0 --port $PORT
```

The `0.0.0.0` host makes the application reachable from Render, and `$PORT`
uses the port assigned by Render. Do not hard-code a local development port.

Choose the appropriate region and instance plan, then create the service.

## 5. Add Render Environment Variables

In the service dashboard, open **Environment** and add:

```text
OPENAI_API_KEY=<your OpenAI key>
WEATHER_API_KEY=<your weather API key>
```

Save the variables and trigger a deploy if Render does not deploy
automatically. Keep secrets hidden and rotate any key that was accidentally
exposed.

## 6. Monitor the Build and Deploy

Open the **Logs** tab and confirm that:

1. The repository was cloned successfully.
2. `pip install -r requirements.txt` completed successfully.
3. Uvicorn started without an import error.
4. The service is listening on the Render-provided port.
5. The deploy finished with a live service status.

If the build fails, check the dependency versions, Python compatibility, file
names, and the application import path (`app:app`). If startup fails, check
the Render logs and verify that all required environment variables are set.

## 7. Verify the Public Service

Replace `<render-url>` with the HTTPS URL shown in the Render dashboard.

Health check:

```bash
curl https://<render-url>/health
```

The response should indicate that the service is running. Open the generated
OpenAPI documentation:

```text
https://<render-url>/docs
```

Use Swagger UI to inspect the request schema and send a valid request to the
chat endpoint:

```text
POST https://<render-url>/chat
```

Send the same JSON shape used during local testing. Confirm that the response
is valid JSON, validation errors are handled clearly, and tool-backed weather
or stock requests return the expected result.

## 8. Deployment Troubleshooting

| Symptom | Check |
| --- | --- |
| Build cannot install packages | `requirements.txt`, package names, and Python compatibility |
| `Could not import module "app"` | `app.py` is at the service root and exposes `app` |
| Service is unreachable | Start command uses `0.0.0.0` and `$PORT` |
| Missing API key error | Render environment variable names match the code exactly |
| Tool returns an external API error | Provider key, quota, endpoint, and response handling |
| `/docs` works but `/chat` fails | Request body schema, agent configuration, and runtime logs |

After changes, push to GitHub and use **Manual Deploy → Deploy latest commit**
in Render. Re-run `/health`, `/docs`, and `/chat` after every deployment.

## Final Architecture

```text
User
	↓ HTTPS request
Render Web Service
	↓
FastAPI + validation
	↓
GPT-5.4-mini agent
	↓
Weather / stock tools
	↓
External APIs
	↓
Validated JSON response
```

## Completion Checklist

- [ ] Code is pushed to GitHub.
- [ ] `.env` and secrets are excluded from Git.
- [ ] Render is connected to the correct branch.
- [ ] Build command is `pip install -r requirements.txt`.
- [ ] Start command uses `uvicorn app:app --host 0.0.0.0 --port $PORT`.
- [ ] Both required API keys are configured in Render.
- [ ] Build and startup logs are successful.
- [ ] `/health`, `/docs`, and `/chat` work on the public HTTPS URL.

## What You Built

You built and deployed a first production-style AI agent: GPT-5.4-mini,
Python tools, external APIs, memory, validation, FastAPI, and Render.
