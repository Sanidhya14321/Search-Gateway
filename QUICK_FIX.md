# 🚀 5-Minute Fix for Stuck Login

**Your login is stuck because the frontend can't talk to the backend.** Here's the exact fix:

---

## Step 1: Get Your Supabase Keys (1 minute)

1. Go to: https://app.supabase.io
2. Open your project
3. Click **Settings** → **API** (on the left sidebar)
4. Copy these two values:
   - **Project URL** → save as `SUPABASE_URL`
   - **anon public** (under "API Keys") → save as `SUPABASE_ANON_KEY`

---

## Step 2: Configure Vercel (2 minutes)

1. Go to: https://vercel.com/dashboard
2. Find your frontend project (should be named something like `crmind-frontend` or `search-gateway`)
3. Click on the project
4. Go to **Settings** → **Environment Variables**
5. Add these 4 variables (paste your Supabase keys from Step 1):

```
NEXT_PUBLIC_API_BASE_URL = https://crmind-api.onrender.com
NEXT_PUBLIC_SUPABASE_URL = <paste your Supabase URL here>
NEXT_PUBLIC_SUPABASE_ANON_KEY = <paste your Supabase anon key here>
NEXT_PUBLIC_SITE_URL = https://search-gateway-tau.vercel.app
```

6. Click **Save** for each one
7. Scroll to **Deployments** → Click your latest deployment → **Redeploy**
8. Wait for deployment to finish (should take ~1 minute)

---

## Step 3: Configure Render (1 minute)

1. Go to: https://dashboard.render.com
2. Find your backend service (should be `crmind-api` or similar)
3. Click on it
4. Go to **Environment** tab
5. Add/Update this variable:

```
CORS_ALLOWED_ORIGINS = https://search-gateway-tau.vercel.app
```

6. Click **Save**
7. Render automatically redeploys

---

## Step 4: Test It (1 minute)

1. Go to: https://search-gateway-tau.vercel.app/login
2. Try to **Sign Up** with a test email
3. You should either:
   - ✅ Successfully create an account and see dashboard
   - ❌ See a **clear error message** (if so, copy it and let me know)

If still stuck:
- Open browser console: **F12** → **Console** tab
- Look for red error messages
- Copy the error and send it to me

---

## 🎯 Key Points

- **NEXT_PUBLIC_API_BASE_URL** tells frontend where backend is
- **NEXT_PUBLIC_SUPABASE_*** tells frontend how to authenticate
- **CORS_ALLOWED_ORIGINS** tells backend which domains can call it
- **Without these, login will always be stuck**

---

## ✅ Verification Checklist

After you've set everything, verify:

- [ ] Vercel has 4 environment variables set
- [ ] Render has CORS_ALLOWED_ORIGINS set
- [ ] Both services have redeployed
- [ ] You can see dashboard after signup (even with 0 searches)
- [ ] No red errors in browser console

---

**Time to fix: 5 minutes**  
**Need help? Open browser console (F12) and share the error message**
