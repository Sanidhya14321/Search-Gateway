# Deployment Configuration Guide

## 🚨 CRITICAL: Your Login is Stuck Because of Missing Environment Variables

Your frontend (Vercel) cannot connect to your backend (Render) because:
1. Frontend doesn't know the backend URL
2. Backend blocks requests from your Vercel domain
3. Frontend can't authenticate with Supabase

## ✅ Quick Fix - Set These Environment Variables

### ON VERCEL (Frontend)

Go to: https://vercel.com/teams/your-team/crmind-frontend/settings/environment-variables

Add/Update these three environment variables:

```
NEXT_PUBLIC_API_BASE_URL = https://crmind-api.onrender.com
NEXT_PUBLIC_SUPABASE_URL = <YOUR_SUPABASE_URL>
NEXT_PUBLIC_SUPABASE_ANON_KEY = <YOUR_SUPABASE_ANON_KEY>
NEXT_PUBLIC_SITE_URL = https://search-gateway-tau.vercel.app
```

**How to find Supabase credentials:**
1. Go to your Supabase dashboard: https://app.supabase.io
2. Project Settings → API
3. Copy `Project URL` → this is NEXT_PUBLIC_SUPABASE_URL
4. Copy `anon public` key → this is NEXT_PUBLIC_SUPABASE_ANON_KEY

**After setting ENV VARS:**
- Redeploy Vercel: Settings → Deployments → Redeploy production

### ON RENDER (Backend)

Go to: https://dashboard.render.com/services (find your backend service)

Click on your service → Environment

Add/Update:
```
CORS_ALLOWED_ORIGINS = https://search-gateway-tau.vercel.app
```

**After setting ENV VAR:**
- Render auto-detects .env changes and redeploys

---

## 🧪 Test the Fix

1. Go to: https://search-gateway-tau.vercel.app/login
2. Signup with any email/password
3. You should see clear error messages if something is still wrong
4. After fix, you should see dashboard with "Welcome, [email]"

If still stuck, check browser console (F12) for error messages.

---

## 📋 Full Vercel Environment Variables (Complete List)

These are ALL variables that should be on Vercel:

```env
NEXT_PUBLIC_API_BASE_URL=https://crmind-api.onrender.com
NEXT_PUBLIC_SUPABASE_URL=https://[your-id].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
NEXT_PUBLIC_SITE_URL=https://search-gateway-tau.vercel.app
```

---

## 📋 Full Render Environment Variables (Complete List)

These are ALL variables that should be on Render for backend:

```env
DATABASE_URL=<your-supabase-pooler-url>
DATABASE_URL_DIRECT=<your-supabase-direct-url>
SUPABASE_URL=https://[your-id].supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...
SUPABASE_JWT_SECRET=your-jwt-secret
OPENAI_API_KEY=<if using OpenAI>
GROQ_API_KEY=<if using Groq>
API_KEY=prod-secret-key-here
INTERNAL_SERVICE_API_KEY=internal-secret-here
ENVIRONMENT=production
CORS_ALLOWED_ORIGINS=https://search-gateway-tau.vercel.app
```

---

## ⚠️ Common Issues

### Error: "localhost:8000"
- NEXT_PUBLIC_API_BASE_URL not set on Vercel
- Frontend is trying to call backend on same machine

### Error: "CORS"  
- CORS_ALLOWED_ORIGINS on Render doesn't include your Vercel URL
- Or it's set to localhost:3000 instead of your actual domain

### Error: "Supabase not configured"
- NEXT_PUBLIC_SUPABASE_URL or NEXT_PUBLIC_SUPABASE_ANON_KEY missing on Vercel

### Still stuck on login screen
- Open browser console (F12 → Console tab)
- Look for red error messages
- Screenshot and compare to errors listed above

---

## 🔗 Useful Links

- Vercel Environment Variables: https://vercel.com/docs/projects/environment-variables
- Render Environment Variables: https://render.com/docs/environment-variables
- Supabase Project Settings: https://app.supabase.io (select project → Settings → API)
- Your Vercel Dashboard: https://vercel.com/dashboard
- Your Render Dashboard: https://dashboard.render.com

---

Last Updated: 2026-03-23
