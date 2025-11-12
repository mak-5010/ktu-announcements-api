# Quick Start Guide - KTU Announcements API

Choose your deployment method and get started in minutes!

## 🎯 Which Option Should I Choose?

```
Do you want it FREE?
├─ YES → Oracle Cloud (100% free forever)
│
└─ NO (okay with $3-5/month)
   ├─ Want simplest setup? → Railway or Fly.io
   └─ Want best performance? → Hetzner VPS + Coolify
```

---

## ⚡ Option 1: Oracle Cloud (FREE Forever)

**Time**: ~30 minutes | **Cost**: $0 | **Difficulty**: Medium

### Step 1: Sign Up
```
Visit: https://www.oracle.com/cloud/free/
Sign up (credit card required but NOT charged)
```

### Step 2: Create VM
1. Compute → Instances → Create Instance
2. Choose Ubuntu 22.04
3. Shape: VM.Standard.E2.1.Micro (1GB RAM) - Always Free
4. Download SSH key
5. Create

### Step 3: SSH into VM
```bash
chmod 400 ~/Downloads/ssh-key.key
ssh -i ~/Downloads/ssh-key.key ubuntu@YOUR_VM_IP
```

### Step 4: Install Docker
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker
sudo apt install docker-compose -y
```

### Step 5: Deploy
```bash
git clone https://github.com/mak-5010/ktu-announcements-api.git
cd ktu-announcements-api
docker-compose up -d
```

### Step 6: Open Firewall
**In Oracle Console**:
- Subnet → Security List → Add Ingress Rule
- Source: 0.0.0.0/0, Port: 8080

**On VM**:
```bash
sudo ufw allow 8080
sudo ufw enable
```

### ✅ Done! Access: `http://YOUR_VM_IP:8080`

---

## ⚡ Option 2: Railway (~$3/month)

**Time**: 5 minutes | **Cost**: ~$3/month | **Difficulty**: Easy

### One-Time Setup
```bash
npm install -g @railway/cli
railway login
```

### Deploy
```bash
cd ktu-announcements-api
railway link  # or railway init
railway up
```

### Get URL
Railway provides a public URL automatically. Check dashboard.

### ✅ Done! Access your Railway URL

---

## ⚡ Option 3: Fly.io (~$3-5/month)

**Time**: 5 minutes | **Cost**: ~$3-5/month | **Difficulty**: Easy

### Install CLI
```bash
curl -L https://fly.io/install.sh | sh
```

### Deploy
```bash
cd ktu-announcements-api
fly auth login
fly launch --no-deploy

# Edit fly.toml if needed (already provided)
fly deploy
```

### Get URL
```bash
fly status
# Your URL: https://ktu-announcements-api.fly.dev
```

### ✅ Done! Access your Fly.io URL

---

## ⚡ Option 4: Hetzner + Coolify ($4.50/month)

**Time**: 20 minutes | **Cost**: $4.50/month | **Difficulty**: Medium

### Step 1: Get VPS
```
Visit: https://www.hetzner.com/cloud
Buy: CX11 (2GB RAM, €4.15/month)
Choose: Ubuntu 22.04
```

### Step 2: SSH & Install Coolify
```bash
ssh root@YOUR_VPS_IP

# Install Coolify (one command)
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash
```

### Step 3: Access Coolify
```
Open: http://YOUR_VPS_IP:8000
Create account
```

### Step 4: Deploy
1. Sources → Add GitHub
2. Projects → New Project
3. Connect your repository
4. Deploy

### ✅ Done! Coolify provides URL

---

## 🔗 After Deployment: WordPress Setup

### 1. Install WordPress Plugin
```bash
# Upload wordpress-plugin folder to:
/wp-content/plugins/ktu-announcements/
```

### 2. Activate Plugin
WordPress Admin → Plugins → Activate "KTU Announcements"

### 3. Configure
Settings → KTU Announcements → Enter your API URL:
```
http://YOUR_VM_IP:8080/api/ktu/announcements
```

### 4. Test Connection
Click "Test API Connection" button

### 5. Use Shortcode
Add to any page/post:
```
[ktu_announcements limit="10"]
```

### 6. Use in Elementor
1. Add Shortcode widget
2. Paste: `[ktu_announcements]`
3. Style as needed

---

## 🧪 Test Your API

### Local Test
```bash
cd ktu-announcements-api
python3 ktu_scrape_site.py  # Test scraper
python3 server.py            # Test API
```

### Remote Test
```bash
# Replace with your actual URL
curl http://YOUR_URL/health
curl http://YOUR_URL/api/ktu/status
curl http://YOUR_URL/api/ktu/announcements
```

---

## 📊 Quick Comparison

| Platform | Setup Time | Monthly Cost | Always-On | Difficulty |
|----------|------------|--------------|-----------|------------|
| Oracle Cloud | 30 min | **$0** | ✅ | Medium |
| Railway | 5 min | $3 | ✅ | Easy |
| Fly.io | 5 min | $3-5 | ✅ | Easy |
| Hetzner+Coolify | 20 min | $4.50 | ✅ | Medium |

---

## 🆘 Troubleshooting

### API not accessible?
```bash
# Check if running
docker ps
docker-compose logs

# Check firewall
sudo ufw status
```

### Scraper failing?
```bash
# Check logs
docker-compose logs ktu-api

# Test manually
docker exec -it ktu-announcements-api python3 ktu_scrape_site.py
```

### Out of memory?
- Upgrade to 2GB RAM instance
- On Oracle: Use Arm shape for more free RAM (24GB total)

---

## 📚 Need More Help?

- Full details: [DEPLOYMENT_FREE.md](DEPLOYMENT_FREE.md)
- API docs: [README.md](README.md)
- WordPress plugin: [wordpress-plugin/README.md](wordpress-plugin/README.md)

---

## 🎉 Next Steps After Deployment

1. ✅ Test API endpoints
2. ✅ Install WordPress plugin
3. ✅ Configure API URL in plugin settings
4. ✅ Test connection in WP admin
5. ✅ Add shortcode to a test page
6. ✅ Style with Elementor
7. ✅ Launch! 🚀
