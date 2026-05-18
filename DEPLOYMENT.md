# Barangay DataHub - Deployment Guide

This guide will help you deploy the Barangay DataHub as a free PWA to Render or Railway.

## Prerequisites

- GitHub account (free)
- Git installed
- A Git repository with your code

## Step 1: Push Code to GitHub

```bash
cd c:\Users\LENOVO\Downloads\Mirimi\major_final\brgy-datahub
git add .
git commit -m "Add PWA and deployment configuration"
git push origin main
```

## Step 2: Choose Your Platform

### Option A: Deploy to Render (Recommended for Free)

#### Setup:
1. Go to https://render.com
2. Sign up with GitHub
3. Click "New +" → "Web Service"
4. Connect your repository
5. Configure:
   - **Name**: brgy-datahub
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn barangay_datahub.wsgi:application`

#### Environment Variables (in Render Dashboard):
```
DEBUG=False
SECRET_KEY=generate-a-random-key-here
ALLOWED_HOSTS=your-app-name.onrender.com
DATABASE_URL=leave empty for SQLite
```

**Cost**: Free tier available (with limitations)

---

### Option B: Deploy to Railway

#### Setup:
1. Go to https://railway.app
2. Sign up with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub"
5. Choose your repository

#### Configuration:
1. Add environment variables:
```
DEBUG=False
SECRET_KEY=generate-a-random-key-here
ALLOWED_HOSTS=your-domain.railway.app
```

2. Railway will auto-detect Python and use Procfile

**Cost**: $5/month credit (usually enough for small projects)

---

### Option C: Deploy to Heroku (Paid, $7+/month)

1. Go to https://heroku.com
2. Create new app
3. Connect GitHub repository
4. Set environment variables
5. Deploy

---

## Step 3: Create a Secret Key

Generate a secure SECRET_KEY:

```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and set it as `SECRET_KEY` environment variable on your hosting platform.

---

## Step 4: Database Setup

### Option A: SQLite (Simple, Free)
- No additional setup needed
- Works with all platforms
- Good for small projects

### Option B: PostgreSQL (Recommended for Production)
- **Render**: Includes free PostgreSQL
- **Railway**: Add PostgreSQL add-on
- Update `DATABASE_URL` environment variable

---

## Step 5: Static Files Setup

Static files (CSS, JS, images) are automatically served by WhiteNoise.

No additional configuration needed!

---

## Step 6: Create Admin User

After deployment, run:

```bash
your-platform-shell
python manage.py createsuperuser
```

Or through your platform's command line interface.

---

## Step 7: Enable HTTPS

All three platforms (Render, Railway, Heroku) provide free HTTPS automatically.

---

## PWA Features Enabled

✅ Offline Support - App works without internet  
✅ Installable - Add to home screen  
✅ Fast Loading - Service Worker caching  
✅ Push Notifications Ready  

---

## Testing PWA Locally

1. Stop dev server (CTRL+BREAK)
2. Run production build:

```bash
python manage.py collectstatic --noinput
python -m gunicorn barangay_datahub.wsgi:application
```

3. Visit http://localhost:8000
4. Check browser dev tools → Application tab for Service Worker

---

## Troubleshooting

### 500 Error on Deployment
- Check logs on your platform
- Verify SECRET_KEY is set
- Ensure migrations ran: `python manage.py migrate`

### Service Worker Not Loading
- Ensure HTTPS is enabled
- Check browser console for errors
- Verify manifest.json path

### Static Files Not Loading
- Ensure `DEBUG=False` is set
- Run `collectstatic` before deployment

---

## Next Steps

1. Push your code with PWA files
2. Choose and deploy to a platform
3. Monitor your app with platform logs
4. Share your public URL!

Need help? Check your platform's documentation or troubleshoot in the browser console.
