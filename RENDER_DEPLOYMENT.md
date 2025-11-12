# Deploy to Render - Complete Guide

This guide walks you through deploying the KTU Announcements API to Render's **FREE tier**.

## 🎯 Why Render Free Tier?

✅ **Completely FREE** - No credit card required initially
✅ **Easy Setup** - 5-10 minute deployment
✅ **Docker Support** - Uses your Dockerfile
✅ **Auto-deploy** - Updates when you push to GitHub
✅ **Free SSL** - HTTPS included
✅ **750 hours/month** - Sufficient for most use cases

## ⚠️ Free Tier Limitations

- **512MB RAM** - Tight for Chrome/Selenium (optimized in code)
- **Spins down after 15 min** - First request takes 30-60 seconds (cold start)
- **Shared CPU** - May be slower than paid tiers
- **No persistent storage** - Uses in-memory cache (fine for this use case)

---

## 📋 Prerequisites

1. GitHub account
2. Render account (sign up at [render.com](https://render.com/))
3. Your code pushed to GitHub

---

## 🚀 Step-by-Step Deployment

### Step 1: Push Code to GitHub

If you haven't already:

```bash
cd ktu-announcements-api

# Initialize git
git init
git add .
git commit -m "Initial commit: KTU Announcements API"

# Create repo on GitHub, then:
git branch -M main
git remote add origin https://github.com/mak-5010/ktu-announcements-api.git
git push -u origin main
```

---

### Step 2: Sign Up for Render

1. Go to [render.com](https://render.com/)
2. Click "Get Started" or "Sign Up"
3. Sign up with GitHub (recommended) or email
4. Verify your email

**Note**: Free tier doesn't require credit card initially, but you may need to add one later for identity verification.

---

### Step 3: Create New Web Service

1. **Go to Dashboard**: [https://dashboard.render.com/](https://dashboard.render.com/)

2. **Click "New +"** (top right) → Select **"Web Service"**

3. **Connect Repository**:
   - Click "Connect account" if first time
   - Authorize Render to access your GitHub
   - Find and select your `ktu-announcements-api` repository

4. **Configure Service**:

   | Setting | Value |
   |---------|-------|
   | **Name** | `ktu-announcements-api` (or your choice) |
   | **Region** | Singapore (closest to India) or your preferred region |
   | **Branch** | `main` |
   | **Runtime** | Docker |
   | **Instance Type** | **Free** ⭐ |

5. **Advanced Settings** (click "Advanced"):

   **Health Check Path**: `/health`

   **Environment Variables** (optional):
   - `PORT` = `8080` (Render auto-sets this)
   - `HEADLESS` = `true` (already default)

6. **Auto-Deploy**: Leave enabled (recommended)

---

### Step 4: Deploy

1. Click **"Create Web Service"**

2. **Wait for build** (~5-10 minutes first time):
   - Installing dependencies
   - Installing Chrome
   - Building Docker image
   - Starting service

3. **Monitor logs** in real-time on the dashboard

4. **Check for success**:
   - Look for: `Listening at: http://0.0.0.0:8080`
   - Status should turn green

---

### Step 5: Get Your URL

Once deployed, Render provides a URL:

```
https://ktu-announcements-api.onrender.com
```

Or with your custom name:
```
https://your-chosen-name.onrender.com
```

---

### Step 6: Test Your API

```bash
# Health check
curl https://your-app.onrender.com/health

# Get status
curl https://your-app.onrender.com/api/ktu/status

# Get announcements (may take 30-60s first time due to cold start)
curl https://your-app.onrender.com/api/ktu/announcements
```

**Expected first-time behavior**:
- Cold start: 30-60 seconds
- Scraper runs automatically on first request
- Subsequent requests are instant (cached)

---

## 🎨 Optional: Custom Domain

### Free Custom Domain Options

1. **Use Render's domain**: `your-app.onrender.com` (free)

2. **Add your own domain** (if you have one):
   - Settings → Custom Domains
   - Add your domain (e.g., `api.yourdomain.com`)
   - Update DNS records as shown
   - Free SSL included

3. **Use free subdomain services**:
   - [FreeDNS](https://freedns.afraid.org/)
   - [Duck DNS](https://www.duckdns.org/)

---

## 📊 Monitor Your Service

### View Logs
1. Dashboard → Your Service → Logs
2. Real-time log streaming
3. Filter by severity

### Check Metrics
1. Dashboard → Your Service → Metrics
2. CPU usage
3. Memory usage
4. Request count

### Set Up Alerts (Optional)
1. Settings → Notifications
2. Email alerts for failures
3. Slack integration available

---

## 🔧 Troubleshooting

### Issue 1: Build Fails

**Symptom**: Build stops with errors

**Solutions**:
1. Check Dockerfile syntax
2. Verify all files committed to GitHub
3. Check logs for specific error
4. Common fix: Add `.dockerignore` to exclude unnecessary files

### Issue 2: Out of Memory (OOM)

**Symptom**: Service crashes, logs show "Out of memory"

**Solutions**:

**Option A - Optimize** (try first):
1. Already optimized in code with `--single-process` flag
2. Reduce scraping frequency in `server.py` (increase `CACHE_DURATION`)
3. Limit announcements scraped

**Option B - Upgrade**:
1. Upgrade to Starter plan ($7/month)
2. Get 512MB guaranteed RAM + better CPU

**Option C - Use alternative**:
1. Try Oracle Cloud (1GB RAM free)
2. See [DEPLOYMENT_FREE.md](DEPLOYMENT_FREE.md)

### Issue 3: Cold Starts Too Slow

**Symptom**: First request after inactivity takes 60+ seconds

**This is normal for free tier**. Solutions:

1. **Accept it** - WordPress plugin handles this gracefully with retry
2. **Keep warm** - Set up external ping service:
   - [UptimeRobot](https://uptimerobot.com/) - Free, pings every 5 minutes
   - [Cron-job.org](https://cron-job.org/) - Free scheduled pings
3. **Upgrade** - Paid plans don't spin down

### Issue 4: Service Not Accessible

**Checks**:
```bash
# 1. Check service status in dashboard
# 2. Check if service is running
curl https://your-app.onrender.com/health

# 3. Check logs for errors
# 4. Verify GitHub repo is connected
```

### Issue 5: Scraper Fails

**Check logs for**:
- Chrome installation errors
- Network timeouts
- KTU website changes

**Solutions**:
1. Check if KTU site is accessible: https://ktu.edu.in/Menu/announcements
2. Increase `WAIT_SECONDS` in `ktu_scrape_site.py`
3. Check Render logs for specific errors
4. Test scraper locally first

---

## 🔄 Update Your Deployment

### Automatic Updates (Recommended)

1. Make changes locally
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Update: description of changes"
   git push
   ```
3. Render auto-deploys (if enabled)
4. Wait ~3-5 minutes for rebuild

### Manual Deploy

1. Dashboard → Your Service
2. Click "Manual Deploy" → "Deploy latest commit"

---

## 💰 Cost Management

### Stay on Free Tier

- **750 hours/month** = ~31 days of 24/7 uptime
- Free tier should be sufficient if:
  - Only running one service
  - Not exceeding memory limits
  - Okay with cold starts

### When to Upgrade ($7/month)

Consider upgrading if:
- ❌ Out of memory errors
- ❌ Need faster cold starts
- ❌ Need guaranteed uptime
- ❌ Want persistent storage

---

## 🔌 Configure WordPress Plugin

After successful deployment:

1. **Install WordPress Plugin**:
   ```
   Upload wordpress-plugin/ to /wp-content/plugins/ktu-announcements/
   ```

2. **Activate Plugin**:
   - WordPress Admin → Plugins → Activate

3. **Configure**:
   - Settings → KTU Announcements
   - **API URL**: `https://your-app.onrender.com/api/ktu/announcements`
   - **Cache Duration**: 15 minutes (recommended)
   - Click "Save Changes"

4. **Test Connection**:
   - Click "Test API Connection" button
   - Should show: "Success! Found X announcements"

5. **Use Shortcode**:
   ```
   [ktu_announcements limit="10"]
   ```

6. **Add to Elementor**:
   - Shortcode widget → Paste shortcode → Style as needed

---

## 📈 Performance Tips

### Reduce Cold Starts

1. **Use UptimeRobot** (free):
   - Sign up at [uptimerobot.com](https://uptimerobot.com/)
   - Add monitor: `https://your-app.onrender.com/health`
   - Check every 5 minutes
   - Keeps service warm (prevents spin-down)

2. **Optimize Cache**:
   - Increase `CACHE_DURATION` in `server.py` (default: 3600s = 1 hour)
   - Longer cache = fewer scrapes = less memory usage

### Reduce Memory Usage

Already optimized in code:
- ✅ Single worker process
- ✅ Disabled images in Chrome
- ✅ Memory-optimized Chrome flags
- ✅ Efficient caching

If still having issues:
- Reduce background scraping frequency (change `minutes=30` to `minutes=60` in `server.py`)
- Limit announcement count returned

---

## 🆘 Need Help?

1. **Check Render Status**: [status.render.com](https://status.render.com/)
2. **Render Docs**: [render.com/docs](https://render.com/docs)
3. **Check Logs**: Dashboard → Your Service → Logs
4. **Test Locally**: Run `docker-compose up` to test before deploying
5. **Community**: Render Community Forum

---

## ✅ Post-Deployment Checklist

- [ ] Service deployed successfully
- [ ] Health endpoint responds: `/health`
- [ ] API returns data: `/api/ktu/announcements`
- [ ] WordPress plugin configured
- [ ] Shortcode tested on WordPress page
- [ ] (Optional) Set up UptimeRobot to prevent cold starts
- [ ] (Optional) Add custom domain
- [ ] Bookmark Render dashboard for monitoring

---

## 🎉 You're Done!

Your KTU Announcements API is now live on Render's free tier!

**Your API endpoints**:
- Homepage: `https://your-app.onrender.com/`
- Announcements: `https://your-app.onrender.com/api/ktu/announcements`
- Status: `https://your-app.onrender.com/api/ktu/status`
- Refresh: `https://your-app.onrender.com/api/ktu/refresh`
- Health: `https://your-app.onrender.com/health`

**Next**: Configure your WordPress plugin with the API URL and start displaying announcements! 🚀
