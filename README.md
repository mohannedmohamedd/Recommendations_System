---
title: Egyptian Recommendations System
emoji: 🚀
colorFrom: blue
colorTo: green
sdk: docker
app_file: app.py
pinned: false
---

# Egyptian Food Recommendation System

This project provides content-based and collaborative recommendation for Egyptian foods.

Quick local steps

1. Create & activate a python venv (recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

Note: `scikit-surprise` may build from source and requires build tools. On Windows ensure Visual C++ build tools are installed, or use the Docker approach below.

Run locally

```powershell
uvicorn app:app --host 0.0.0.0 --port 7860
# then visit http://localhost:7860/health and /sample_recommend
```

Run quick import test

```powershell
python test_imports.py
```

Docker (optional)

```powershell
docker build -t egyptian-food-rec:latest .
docker run --rm -p 7860:7860 egyptian-food-rec:latest
```

Deploying to Hugging Face Spaces

- Option A (recommended): Create a new Space of type "Gradio" or "Static" or "Python" and push the repository files. Spaces will install `requirements.txt`.
- Option B: Use a custom Docker image (push image to a registry and set Space to use it).

If you use the built-in Python Spaces, `scikit-surprise` may take longer to install; the provided `Dockerfile` includes system dependencies to help build it successfully.

CI / Auto-deploy (optional)

- A GitHub Actions workflow template is included at `.github/workflows/ci_and_deploy.yml` which:
	- installs dependencies and runs `test_imports.py` on push/pull_request
	- can build a Docker image and push to GHCR if you add a `GHCR_TOKEN` secret
	- contains a section placeholder to deploy to Hugging Face Spaces (requires `HF_TOKEN` secret)

How I can help next

- I can create the GitHub repo and push these files for you if you give me a token, or I can provide the exact `git` commands for you to run locally and push. After pushing, I can assist with creating the Space and setting secrets.

If you want, I can build the Docker image here and run the tests, or prepare a `setup` GH Action to automatically build and push the image.
