# أخبار الدوريات الأوروبية - PRD

## نظرة عامة
تطبيق موبايل بالعربية يعرض أخبار كرة القدم من موقع يلا كورة مع جدول الترتيب ونتائج المباريات للدوريات الأوروبية الخمسة الكبرى.

## الميزات
1. **أخبار حقيقية** - جلب مباشر من يلا كورة مع صور
2. **جدول ترتيب الفرق** - 20 فريق مع كل الإحصائيات
3. **نتائج المباريات** - القادمة والمنتهية مع القنوات الناقلة
4. **إشعارات الأخبار العاجلة** - بانر داخل التطبيق + Expo Push Notifications
5. **بحث في الأخبار** - شريط بحث عربي مع نتائج فورية
6. **صفحة تفاصيل الخبر** - عرض كامل مع صورة ومحتوى وزر مشاركة
7. **واجهة عربية RTL** كاملة

## الدوريات المدعومة
- الدوري الإنجليزي (Premier League)
- الدوري الإسباني (La Liga)
- الدوري الإيطالي (Serie A)
- الدوري الألماني (Bundesliga)
- الدوري الفرنسي (Ligue 1)

## APIs
- `GET /api/leagues` - قائمة الدوريات
- `GET /api/news/{league_id}` - أخبار الدوري
- `GET /api/standings/{league_id}` - ترتيب الفرق
- `GET /api/matches/{league_id}` - المباريات
- `GET /api/all-news` - جميع الأخبار
- `GET /api/search?q={query}` - البحث في الأخبار
- `GET /api/news-detail/{league_id}/{news_id}` - تفاصيل الخبر
- `POST /api/register-push-token` - تسجيل Push Token

## التقنيات
- Backend: FastAPI + MongoDB + BeautifulSoup
- Frontend: React Native / Expo Router
- Push: expo-notifications + expo-device
- Data: Web scraping from YallaKora
