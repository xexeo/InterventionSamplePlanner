<!-- File version: 2.2; date: 2026-05-17 -->

# Render Deployment Guide

This project now has two user interfaces:

- local desktop interface: Tkinter, started with `python run_app.py`
- web interface: Flask REST API plus static browser client, served by `intervention_sample_planner.web_app`

The calculation engine remains the same Python API in `intervention_sample_planner/calculator.py`. The web interface does not duplicate sample-size formulas.

## Why Flask

Flask is used because it keeps the server small, requires no database, serves local static files directly, and exposes REST endpoints with little Render configuration. The front end is plain HTML/CSS/JavaScript inside `intervention_sample_planner/web_static`, so there is no Node.js build step.

## Local Web Run

Install web dependencies:

```powershell
python -m pip install -r requirements.txt
```

Start the web app:

```powershell
python -m flask --app intervention_sample_planner.web_app run
```

Open:

```text
http://127.0.0.1:5000
```

## REST Endpoints

- `GET /health`
- `GET /api/version`
- `GET /api/default-config`
- `GET /api/explanations?language=en`
- `GET /api/ui-text?language=en`
- `POST /api/calculate`
- `POST /api/report/text`
- `POST /api/report/html`
- `POST /api/report/pdf`

The `POST` endpoints accept a JSON object compatible with `schemas/study_config.schema.json`.

## User Files

The web app does not use a database and does not keep user study files on the server. The browser client can:

- load a local JSON file chosen by the user
- save the current configuration as a downloaded JSON file
- download reports as text, HTML, or PDF

## Render Service Setup

Render can read `render.yaml` as a Blueprint. The service configuration is:

- Runtime: Python
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn intervention_sample_planner.web_app:app`
- Python version: `3.11.9`
- Database: none
- Persistent disk: none

If creating the service manually in the Render dashboard, use the same build and start commands.

## Deploy Only When a Tag Is Pushed

Render normally supports automatic deploys from a linked branch. For this project, the requested release flow is tag-driven:

1. In the Render service settings, disable normal auto-deploy if you do not want every branch push deployed.
2. Copy the service Deploy Hook URL from Render.
3. In GitHub, open the repository settings.
4. Go to `Secrets and variables` > `Actions`.
5. Create a repository secret named `RENDER_DEPLOY_HOOK_URL`.
6. Paste the Render Deploy Hook URL as the value.
7. Keep `.github/workflows/deploy-render-on-tag.yml` in the repository.

When a tag such as `v2.2` is pushed, GitHub Actions:

- checks out the tagged commit
- installs `requirements.txt`
- runs unit tests
- calls the Render Deploy Hook with `ref=<tagged commit SHA>`

Using the `ref` query parameter asks Render to deploy the exact commit associated with the tag, not merely whatever commit happens to be newest on the linked branch.

## Release Checklist

1. Run local tests:

```powershell
python -m unittest discover -s tests
```

2. Test the web app locally:

```powershell
python -m flask --app intervention_sample_planner.web_app run
```

3. Commit the release.

4. Tag the release:

```powershell
git tag -a v2.2 -m "version 2.2"
```

5. Push the branch and the tag:

```powershell
git push
git push origin v2.2
```

The tag push starts the GitHub Action, and the action starts the Render deployment.

## Source References

- [Render Deploy Hooks](https://render.com/docs/deploy-hooks)
- [Render deploy process and commands](https://render.com/docs/deploys/)
- [Render deploy a specific commit with deploy hook `ref`](https://render.com/docs/deploying-a-commit)
- [GitHub Actions workflow syntax for push tags](https://docs.github.com/actions/reference/workflows-and-actions/workflow-syntax#onpushbranchestagsbranches-ignoretags-ignore)
