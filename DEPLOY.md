# 🚀 DEPLOYMENT STEPS

## STEP 1: Deploy Backend on Render

1. Go to https://render.com/dashboard
2. Click "New +" → "Web Service"
3. Connect GitHub: `crs7617/Agrovision`
4. Settings:
   - Name: `agrovision-backend`
   - Root Directory: `backend`
   - Runtime: `Python 3`
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Free tier

5. Environment Variables (copy from `backend/.env`):
   - SUPABASE_URL
   - SUPABASE_KEY
   - GROQ_API_KEY
   - OPENWEATHER_API_KEY
   - GOOGLE_API_KEY
   - FRONTEND_URL = (leave blank for now)

6. Click "Create Web Service"
7. **COPY THE URL** (example: `https://agrovision-backend-abc.onrender.com`)

---

## STEP 2: Deploy Frontend on Vercel

1. Go to https://vercel.com/new
2. Import: `crs7617/Agrovision`
3. Settings:
   - Project: `agrovision-app`
   - Framework: Next.js
   - Root Directory: `frontend/agrovision-app`

4. Environment Variables (copy from `frontend/agrovision-app/.env.local`):
   - NEXT_PUBLIC_SUPABASE_URL
   - NEXT_PUBLIC_SUPABASE_ANON_KEY
   - NEXT_PUBLIC_API_BASE_URL = (paste Render URL from Step 1)

5. Click "Deploy"
6. **COPY THE URL** (example: `https://agrovision-app.vercel.app`)

---

## STEP 3: Update Backend CORS

1. Go back to Render → Your Service → Environment
2. Update `FRONTEND_URL` with your Vercel URL
3. Save (auto redeploys)

---

## STEP 4: Update Supabase

1. Go to https://supabase.com/dashboard/project/fpagxlomlturzoffctdk/auth/url-configuration
2. Site URL: (paste Vercel URL)
3. Redirect URLs: (paste Vercel URL with `/**`)
4. Save

---

## DONE! Test at your Vercel URL
