# Free Deployment Options for KTU Announcements API

Since Render's Blueprint feature requires a credit card, here are **completely free alternatives** that you can use to host your API.

## 🚨 Important: Resource Requirements

This API uses Selenium with Chrome, which requires:
- **Minimum RAM**: 1GB (512MB won't work reliably)
- **Minimum CPU**: 0.5 vCPU
- **Storage**: 500MB+

Most "free tier" platforms offer only 512MB RAM, which is **insufficient** for Chrome/Selenium.

---

## ✅ Option 1: Oracle Cloud Free Tier (RECOMMENDED) ⭐

**Why Oracle?**
- Truly always free (not a trial)
- Generous resources: 2 VMs with 1GB RAM each OR 4 Arm VMs with 24GB RAM total
- No time limits
- No auto-charges after trial

### Setup Steps

#### 1. Sign Up
1. Go to [Oracle Cloud Free Tier](https://www.oracle.com/cloud/free/)
2. Sign up (credit card required for verification but NOT charged)
3. Choose your home region (closest to India: Mumbai)

#### 2. Create a VM Instance
1. Go to **Compute → Instances → Create Instance**
2. Choose:
   - **Image**: Ubuntu 22.04
   - **Shape**:
     - AMD: VM.Standard.E2.1.Micro (1GB RAM, 1 vCPU) - Always Free
     - OR Arm: VM.Standard.A1.Flex (up to 24GB RAM, 4 vCPU total) - Always Free
3. Download the SSH key pair
4. Click **Create**

#### 3. Configure Firewall
1. In your instance, click on the **Subnet** link
2. Click on the **Default Security List**
3. **Add Ingress Rule**:
   - Source CIDR: `0.0.0.0/0`
   - Destination Port: `8080`
   - Description: `KTU API`

#### 4. Connect via SSH
```bash
chmod 400 ~/Downloads/ssh-key.key
ssh -i ~/Downloads/ssh-key.key ubuntu@<YOUR_VM_IP>
```

#### 5. Install Docker
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo apt install docker-compose -y
```

#### 6. Deploy Your App
```bash
# Clone your repo
git clone https://github.com/mak-5010/ktu-announcements-api.git
cd ktu-announcements-api

# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f
```

#### 7. Open Firewall on VM
```bash
sudo ufw allow 8080
sudo ufw enable
```

#### 8. Access Your API
```
http://<YOUR_VM_IP>:8080
```

### Optional: Add Domain with Cloudflare (Free)
1. Buy a domain or use a free subdomain service
2. Point your domain to Oracle VM IP
3. Use Cloudflare for free SSL

**Cost**: $0/month forever ✅

---

## ✅ Option 2: Railway.app (Pay-as-you-go)

**Status**: No free tier, but $5 starter credit

### Pricing
- First deploy: Uses ~$2-3/month if running 24/7
- You get $5 credit to start

### Deployment Steps

1. **Sign Up**: [Railway.app](https://railway.app/)
2. **Connect GitHub**: Link your repository
3. **Deploy**:
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli

   # Login
   railway login

   # Link project
   railway link

   # Deploy
   railway up
   ```

4. **Configure**:
   - Add environment variable: `PORT=8080`
   - Railway will auto-detect your Dockerfile

5. **Get URL**: Railway provides a public URL automatically

**Cost**: ~$2-3/month (starts after $5 credit runs out)

---

## ✅ Option 3: Fly.io (Pay-as-you-go)

**Status**: Usage-based, ~$5/month threshold for free

### Deployment Steps

1. **Install Fly CLI**:
```bash
curl -L https://fly.io/install.sh | sh
```

2. **Sign Up & Login**:
```bash
fly auth signup
# OR
fly auth login
```

3. **Initialize App**:
```bash
cd ktu-announcements-api
fly launch --no-deploy
```

4. **Edit fly.toml** (auto-generated):
```toml
app = "ktu-announcements-api"
primary_region = "sin" # Singapore

[build]
  dockerfile = "Dockerfile"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = false
  auto_start_machines = true
  min_machines_running = 1

[[vm]]
  memory = '1gb'
  cpu_kind = 'shared'
  cpus = 1
```

5. **Deploy**:
```bash
fly deploy
```

6. **Get URL**:
```bash
fly status
# Your app will be at: https://ktu-announcements-api.fly.dev
```

**Cost**: ~$3-5/month for 1GB RAM instance

---

## ✅ Option 4: Self-Hosted on Cheap VPS

### Recommended Providers

#### Hetzner Cloud (Germany/Finland)
- **Cost**: €4.15/month (~$4.50)
- **Specs**: 2GB RAM, 1 vCPU, 20GB SSD
- **Website**: [hetzner.com/cloud](https://www.hetzner.com/cloud)

#### Contabo (Germany)
- **Cost**: €3.99/month (~$4.30)
- **Specs**: 4GB RAM, 2 vCPU, 50GB SSD
- **Website**: [contabo.com](https://contabo.com/en/vps/)

#### Hostinger VPS (Global)
- **Cost**: $4.99/month
- **Specs**: 1GB RAM, 1 vCPU, 20GB SSD
- **Website**: [hostinger.com/vps-hosting](https://www.hostinger.com/vps-hosting)

### Deployment with Coolify (Free Tool)

Coolify is like a self-hosted Heroku/Render.

1. **Get a VPS** from providers above
2. **Install Coolify** (one command):
```bash
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash
```

3. **Access Coolify**: `http://<your-vps-ip>:8000`
4. **Connect GitHub** repository
5. **Deploy** with one click

**Total Cost**: $4-5/month

---

## ✅ Option 5: Google Cloud Run (Limited Free)

**Free Tier**:
- 2M requests/month
- 180,000 vCPU-seconds/month
- 360,000 GiB-seconds/month
- 1GB network egress

### Deployment Steps

1. **Install gcloud CLI**:
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init
```

2. **Enable APIs**:
```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

3. **Deploy**:
```bash
cd ktu-announcements-api

gcloud run deploy ktu-announcements-api \
  --source . \
  --platform managed \
  --region asia-south1 \
  --memory 1Gi \
  --timeout 300 \
  --allow-unauthenticated
```

4. **Get URL**: Google will provide a URL like:
```
https://ktu-announcements-api-xxx-uc.a.run.app
```

**Limitations**:
- Cold starts (first request may be slow)
- Instance shuts down when idle
- May exceed free tier if heavily used

**Cost**: Free for ~1000 requests/day, then ~$2-5/month

---

## 📊 Comparison Table

| Platform | Cost | RAM | Always-On | Setup Difficulty | Credit Card Required |
|----------|------|-----|-----------|------------------|---------------------|
| **Oracle Cloud** | FREE | 1-24GB | ✅ Yes | Medium | Yes (not charged) |
| **Railway** | $2-3/mo | 1GB+ | ✅ Yes | Easy | Yes |
| **Fly.io** | $3-5/mo | 1GB+ | ✅ Yes | Easy | Yes |
| **Hetzner VPS + Coolify** | $4.50/mo | 2GB | ✅ Yes | Medium | Yes |
| **Google Cloud Run** | Free/$2-5 | 1GB | ❌ No (on-demand) | Medium | Yes |

---

## 🎯 My Recommendation

### For Absolute Free (Best Value): **Oracle Cloud** ⭐⭐⭐⭐⭐
- Always free, no time limits
- Enough resources (1GB+ RAM)
- Reliable uptime
- One-time setup effort

### For Easiest Setup: **Railway** or **Fly.io** ⭐⭐⭐⭐
- Simple deployment
- Auto SSL/domains
- ~$3-5/month

### For Best Price/Performance: **Hetzner VPS + Coolify** ⭐⭐⭐⭐
- $4.50/month
- 2GB RAM, very fast
- Can host multiple projects

---

## 📝 Updated WordPress Plugin Configuration

After deployment, update your WordPress plugin settings:

1. Go to **Settings → KTU Announcements**
2. Enter your new API URL:
   - Oracle: `http://<VM_IP>:8080/api/ktu/announcements`
   - Railway: `https://your-app.railway.app/api/ktu/announcements`
   - Fly.io: `https://ktu-announcements-api.fly.dev/api/ktu/announcements`
   - Cloud Run: `https://ktu-announcements-api-xxx.run.app/api/ktu/announcements`

3. Test connection using the "Test API Connection" button

---

## 🆘 Need Help?

If you need assistance with any deployment option, let me know which platform you choose!
