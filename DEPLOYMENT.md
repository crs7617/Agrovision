Deployment guide — frontend and backend

This document explains how to build and deploy the AgroVision frontend and backend. It includes Docker-based local production, and short notes for common hosts (Vercel for frontend, Render/Fly/Heroku for backend).

1) Quick local production with Docker (recommended for smoke tests)

Prerequisites:
- Docker and Docker Compose installed on your machine.
- Ensure the following env files are present and filled:
  - backend/.env (SUPABASE_URL, SUPABASE_KEY, FRONTEND_URL, etc.)
  - frontend/agrovision-app/.env.local (NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY, NEXT_PUBLIC_API_BASE_URL)

How to run:
- From repo root (where docker-compose.yml lives):
  docker compose up --build

This will build both images and serve:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000

Notes:
- The frontend expects NEXT_PUBLIC_API_BASE_URL to point to the backend (e.g. http://backend:8000 or the outward address). The Docker Compose file maps ports and uses env file values.
- For local development you already have a dev environment (next dev & uvicorn) — Docker here is for local "production" verification.

2) Deploying the frontend to Vercel

Why Vercel: Next.js first-class support, automatic builds, presets for Next.

Steps:
- Create a Vercel account and connect your Git repository.
- In Vercel project settings > Environment Variables add the following keys (Production):
  - NEXT_PUBLIC_SUPABASE_URL = https://<your-supabase>.supabase.co
  - NEXT_PUBLIC_SUPABASE_ANON_KEY = <anon-key>
  - NEXT_PUBLIC_API_BASE_URL = https://<your-backend-domain>

- Set the Build Command to: npm run build
- Set the Output Directory: (Next.js default; leave blank; Vercel detects Next automatically)

- Add Redirect URL(s) in Supabase > Authentication > Settings > Redirect URLs to include:
  - https://<your-vercel-domain>/api/auth/callback or the OAuth redirect path you use. For signInWithOAuth you typically add: https://<your-vercel-domain>/auth/callback

- Deploy. Vercel will run the build and publish.

3) Deploying the backend

Options (choose one):
- Render.com: easy for FastAPI + Docker or Python
- Fly.io: global small VMs
- DigitalOcean App Platform
- AWS ECS / ECR (more complex)
- Heroku (deprecated-ish but still works)

General steps using Docker (Render / Fly / DigitalOcean):
- Make sure backend/.env contains production values, especially SUPABASE_KEY (server key) and FRONTEND_URL (production frontend URL).
- Create a Docker image using the provided backend/Dockerfile.
- Push image to a registry (Docker Hub, GitHub Container Registry, or let Render build from your repo).
- Configure the service to run CMD: uvicorn main:app --host 0.0.0.0 --port 8000
- Expose port 8000 and set env vars in the host's web UI.

Important: CORS and Redirects
- In backend/main.py (or your CORS middleware), ensure allow_origins contains your production frontend domain(s) (https://<your-vercel-domain>), not just localhost ports.
- In Supabase settings add your production frontend domain to Redirect URLs for OAuth.

4) Using managed deployments without Docker

Vercel (frontend): as above.
Render (backend): create a new Web Service -> Connect repo -> Start Command: uvicorn main:app --host 0.0.0.0 --port 8000 -> Add env vars in the Render dashboard.

5) HTTPS & domain
- Both frontend and backend must be served over HTTPS for OAuth flows and secure cookies. Vercel and Render provide free TLS certs.
- Point your domain's DNS to the hosting provider and add the domain in the provider dashboard and Supabase redirect settings.

6) CI / GitHub actions (suggestion)
- Frontend: Use Vercel integration or add a GitHub Action to build and test on push.
- Backend: Add a CI job to run tests and build Docker image and push to registry on release.

7) Environment variables checklist
- FRONTEND (public): NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY, NEXT_PUBLIC_API_BASE_URL
- BACKEND (private): SUPABASE_URL, SUPABASE_KEY (service role key), FRONTEND_URL (production domain), any other secrets.

8) OAuth (Google) checklist
- Create OAuth credentials in Google Cloud Console. Set the authorized redirect URI to your production callback URL (e.g. https://<your-vercel-domain>/auth/callback).
- In Supabase Dashboard > Authentication > Providers > Google: paste client ID and client secret.
- Add the same redirect URL to Supabase settings and ensure CORS and backend redirect handling align.

9) Post-deploy tests
- Sign in (email/password) and sign in with Google.
- Verify farms appear and maps load.
- Check backend health endpoint: https://<backend>/health or root index.
- Monitor logs for exceptions.

10) Rollback plan
- Keep a copy of previous env vars and image tags. If a deploy fails, revert to the last working tag or deployment.

If you want, I can:
- Generate a GitHub Actions workflow to build and push the backend Docker image.
- Generate a small Render/Vercel step-by-step list with screenshots (if you provide the account details or allow me to continue interactively).
- Run a local docker-compose up and test the built images here.

Which of the following do you want next?
A) I provide step-by-step commands for deploying to Vercel (frontend) + Render (backend).
B) I generate GitHub Actions workflow(s) for CI/CD (build & push backend image, trigger Vercel).
C) I run docker compose up locally here and verify the built containers (I will need to run docker commands on your machine; confirm permission).
D) Something else — tell me which provider you prefer and I'll tailor the instructions.
