# Hostinger VPS Production Deployment Guide for Nexomate

This guide provides the complete, copy-paste instructions to deploy Nexomate on a **Hostinger VPS** (Ubuntu 22.04 or 24.04).

---

## Prerequisites
- **Hostinger VPS** (Ubuntu 22.04 or 24.04, Recommended: KVM 2 or KVM 4 with 8 GB RAM to run `llama3.1` locally).
- Your domain DNS pointed to your VPS IP:
  - `A` record for `app.getnexomate.com` (or `@` for `getnexomate.com`) pointing to `<YOUR_VPS_IP>`.

---

## ⚡ Fast-Track: 1-Click Automated Setup

If you want the entire deployment done automatically (packages, Python venv, Ollama, Llama 3.1, systemd service, and Nginx reverse proxy):

1. **Upload the codebase to your VPS from your local machine:**
   ```powershell
   scp -r nexomate root@<YOUR_VPS_IP>:/var/www/nexomate
   ```

2. **SSH into your Hostinger VPS and run the deploy script:**
   ```bash
   ssh root@<YOUR_VPS_IP>
   cd /var/www/nexomate
   chmod +x deploy_hostinger.sh
   bash deploy_hostinger.sh
   ```
   *The script will prompt for your domain name, configure Nginx, start the background service, and output your live URL.*

---

## Manual Step-by-Step Deployment

If you prefer to configure each component manually, follow the steps below:

### Step 1: Connect to Your Hostinger VPS
Open PowerShell on your computer and connect via SSH:
```bash
ssh root@<YOUR_VPS_IP>
```

---

## Step 2: System Packages Installation
Update the system and install required system utilities:
```bash
apt update && apt upgrade -y
apt install -y python3 python3-pip python3-venv git nginx certbot python3-certbot-nginx
```

---

## Step 3: Install & Start Ollama (Local AI Engine)
```bash
curl -fsSL https://ollama.com/install.sh | sh

# Download the Llama 3.1 model (4.9 GB)
ollama pull llama3.1
```

---

## Step 4: Upload Nexomate Project Codebase
From your **local Windows machine** (open a local PowerShell in `c:\Users\Farhan\Desktop`):
```powershell
scp -r nexomate root@<YOUR_VPS_IP>:/var/www/nexomate
```

Alternatively, if using Git:
```bash
cd /var/www
git clone <YOUR_PRIVATE_REPO_URL> nexomate
```

---

## Step 5: Set Up Python Virtual Environment
Inside your VPS terminal:
```bash
cd /var/www/nexomate

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip & install requirements
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Step 6: Verify Production Environment
Check that your `/var/www/nexomate/.env` contains your verified Hostinger credentials:
```env
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1

SMTP_HOST=smtp.hostinger.com
SMTP_PORT=465
SMTP_USER=connect@getnexomate.com
SMTP_PASSWORD=Dl3sdf@3223

IMAP_HOST=imap.hostinger.com
IMAP_PORT=993
IMAP_USER=connect@getnexomate.com
IMAP_PASSWORD=Dl3sdf@3223
```

Run the production verification script:
```bash
python live_init.py
```
*(All services should return green).*

---

## Step 7: Configure Background Service (systemd)
Keep Nexomate running 24/7 and automatically restart on server reboots:

Create the service file:
```bash
nano /etc/systemd/system/nexomate.service
```

Paste the following:
```ini
[Unit]
Description=Nexomate Streamlit Production Application
After=network.target

[Service]
User=root
WorkingDirectory=/var/www/nexomate
ExecStart=/var/www/nexomate/venv/bin/streamlit run app.py --server.port=8501 --server.address=127.0.0.1 --server.headless=true
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
systemctl daemon-reload
systemctl enable nexomate
systemctl start nexomate

# Check status
systemctl status nexomate
```

---

## Step 8: Configure Nginx & Free SSL Certificate
Create an Nginx configuration file:
```bash
nano /etc/nginx/sites-available/nexomate
```

Paste the following (replace `app.getnexomate.com` with your actual domain):
```nginx
server {
    listen 80;
    server_name app.getnexomate.com;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

Enable the site and reload Nginx:
```bash
ln -s /etc/nginx/sites-available/nexomate /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

Install free Let's Encrypt SSL certificate:
```bash
certbot --nginx -d app.getnexomate.com
```

---

## Helpful Server Management Commands
- Check application logs:
  ```bash
  journalctl -u nexomate -f
  ```
- Restart application:
  ```bash
  systemctl restart nexomate
  ```
- Check Ollama models:
  ```bash
  ollama list
  ```
