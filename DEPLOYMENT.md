# أخبار الدوريات الأوروبية - دليل التثبيت والنشر

## المتطلبات
- Python 3.9+
- Node.js 18+
- MongoDB (أو MongoDB Atlas مجاني)
- سيرفر Linux (Hostinger VPS / أي سيرفر)

---

## 1. رفع الكود على السيرفر

```bash
# على السيرفر
git clone https://github.com/YOUR_USERNAME/european-leagues-news.git
cd european-leagues-news
```

---

## 2. إعداد Backend

```bash
cd backend

# إنشاء بيئة افتراضية
python3 -m venv venv
source venv/bin/activate

# تثبيت المكتبات
pip install -r requirements.txt

# إنشاء ملف .env
cp .env.example .env
# عدّل الملف وضع رابط MongoDB الخاص بك
nano .env
```

### ملف backend/.env يجب أن يحتوي على:
```
MONGO_URL=mongodb://localhost:27017
DB_NAME=football_news
```

### إذا تريد استخدام MongoDB Atlas (مجاني):
1. اذهب إلى https://www.mongodb.com/atlas
2. أنشئ حساب مجاني
3. أنشئ Cluster
4. احصل على Connection String
5. ضعه في MONGO_URL

### تشغيل Backend:
```bash
# تشغيل مباشر
uvicorn server:app --host 0.0.0.0 --port 8001

# أو تشغيل في الخلفية مع systemd (أنظر القسم 4)
```

---

## 3. إعداد Frontend

### تعديل رابط الـ API:
عدّل ملف `frontend/.env`:
```
EXPO_PUBLIC_BACKEND_URL=https://YOUR_DOMAIN.com
```

### بناء APK/AAB:
```bash
cd frontend
yarn install

# تسجيل الدخول في Expo
eas login

# بناء APK (للتثبيت المباشر)
eas build --platform android --profile preview

# بناء AAB (لـ Google Play)
eas build --platform android --profile production

# بناء iOS
eas build --platform ios
```

---

## 4. إعداد Systemd Service (تشغيل Backend تلقائي)

أنشئ ملف: `/etc/systemd/system/football-news.service`

```ini
[Unit]
Description=Football News API
After=network.target mongod.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/home/YOUR_USER/european-leagues-news/backend
Environment=PATH=/home/YOUR_USER/european-leagues-news/backend/venv/bin
ExecStart=/home/YOUR_USER/european-leagues-news/backend/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable football-news
sudo systemctl start football-news
sudo systemctl status football-news
```

---

## 5. إعداد Nginx (Reverse Proxy)

أنشئ ملف: `/etc/nginx/sites-available/football-news`

```nginx
server {
    listen 80;
    server_name YOUR_DOMAIN.com;

    # API Backend
    location /api/ {
        proxy_pass http://127.0.0.1:8001/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 120s;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/football-news /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### SSL (HTTPS) مع Let's Encrypt:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d YOUR_DOMAIN.com
```

---

## 6. تثبيت MongoDB على السيرفر

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y mongodb-org
sudo systemctl start mongod
sudo systemctl enable mongod
```

---

## 7. AdMob Configuration

المعرفات محفوظة في `frontend/app.json`:
- App ID: ca-app-pub-7650114689148142~1322307253
- Banner: ca-app-pub-7650114689148142/5665936435
- Interstitial: ca-app-pub-7650114689148142/8100528086
- Native: ca-app-pub-7650114689148142/9037145747

---

## 8. هيكل المشروع

```
├── backend/
│   ├── server.py           ← FastAPI + YallaKora Scraping
│   ├── .env                ← إعدادات MongoDB
│   ├── .env.example        ← مثال للإعدادات
│   └── requirements.txt    ← مكتبات Python
├── frontend/
│   ├── app/
│   │   ├── index.tsx       ← الصفحة الرئيسية
│   │   ├── news-detail.tsx ← صفحة تفاصيل الخبر
│   │   └── _layout.tsx     ← التنقل
│   ├── app.json            ← إعدادات التطبيق + AdMob
│   ├── eas.json            ← إعدادات البناء
│   ├── package.json        ← مكتبات JavaScript
│   └── assets/images/      ← الشعار والأيقونات
├── DEPLOYMENT.md           ← هذا الملف
└── README.md
```

---

## 9. APIs المتاحة

| Endpoint | الوصف |
|----------|-------|
| GET /api/leagues | قائمة الدوريات |
| GET /api/news/{league_id} | أخبار الدوري |
| GET /api/news-counts | عدد الأخبار لكل دوري |
| GET /api/standings/{league_id} | ترتيب الفرق |
| GET /api/matches/{league_id} | المباريات |
| GET /api/search?q={query} | البحث في الأخبار |
| GET /api/news-detail/{league_id}/{news_id} | تفاصيل الخبر |
| GET /api/all-news | جميع الأخبار |

---

## 10. الدعم

للمساعدة أو الاستفسارات، تواصل مع المطور.
