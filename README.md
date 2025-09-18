# Kawiarnia Tej — Flask Site

Coffee shop website with pages, gallery, session cart (no DB), and server-side email orders.

## Quick Start (Local)

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# set environment (or copy .env.example to your shell)
export SECRET_KEY=dev
export MAIL_USERNAME=yourgmail@gmail.com
export MAIL_PASSWORD=your_gmail_app_password
export MAIL_DEFAULT_SENDER=yourgmail@gmail.com

python app.py
# open http://127.0.0.1:5000
```

> If mail env vars are missing, the app logs the email to console instead of sending (for dev).

## Deploy (Gunicorn + Nginx)

- Create systemd service:
```
[Unit]
Description=Gunicorn instance for Kawiarnia Tej
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/kawiarnia_app
Environment="PATH=/opt/kawiarnia_app/venv/bin"
Environment="SECRET_KEY=prod-secret"
Environment="MAIL_USERNAME=yourgmail@gmail.com"
Environment="MAIL_PASSWORD=your_gmail_app_password"
Environment="MAIL_DEFAULT_SENDER=yourgmail@gmail.com"
ExecStart=/opt/kawiarnia_app/venv/bin/gunicorn --workers 3 --bind unix:kawiarnia.sock -m 007 app:app

[Install]
WantedBy=multi-user.target
```

- Nginx site:
```
server {
  listen 80;
  server_name yourdomain.com www.yourdomain.com;

  location /static/ {
    alias /opt/kawiarnia_app/static/;
  }
  location / {
    include proxy_params;
    proxy_pass http://unix:/opt/kawiarnia_app/kawiarnia.sock;
  }
}
```

Enable HTTPS with certbot:
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## Pages

- `/` — hero + carousel + gallery
- `/menu` — sample menu
- `/keto` — static page with text-on-image
- `/ciasta-i-chleby` — choose **Chleby** or **Ciasta**
- `/chleby`, `/ciasta` — product lists with **Add to cart**
- `/zamowienie` — form; sends email to **kacper.rabeda6@gmail.com**
- `/thank-you` — confirmation
