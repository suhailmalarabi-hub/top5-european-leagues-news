# أخبار الدوريات الأوروبية - PRD

## نظرة عامة
تطبيق موبايل بالعربية يعرض أخبار كرة القدم من يلا كورة مع جدول الترتيب ونتائج المباريات.

## الميزات
1. أخبار حقيقية من يلا كورة مع صور
2. جدول ترتيب الفرق مع شعارات
3. نتائج المباريات مع القنوات والهدافين والبطاقات
4. بحث في الأخبار
5. صفحة تفاصيل الخبر داخل التطبيق
6. إشعارات الأخبار العاجلة (in-app + Push)
7. أعلام الدول بجانب أسماء الدوريات
8. شارة عدد الأخبار لكل دوري
9. زر Sync لتحديث البيانات
10. قسم إعلانات AdMob
11. واجهة عربية RTL كاملة

## الدوريات المدعومة (tour_ids)
- الإنجليزي: 93
- الإسباني: 101
- الإيطالي: 100
- الألماني: 98
- الفرنسي: 95

## AdMob Config
- App ID: ca-app-pub-7650114689148142~1322307253
- Banner: ca-app-pub-7650114689148142/5665936435
- Interstitial: ca-app-pub-7650114689148142/8100528086
- Native Advanced: ca-app-pub-7650114689148142/9037145747

## APIs
- GET /api/leagues
- GET /api/news/{league_id}
- GET /api/news-counts
- GET /api/standings/{league_id}
- GET /api/matches/{league_id}
- GET /api/match-events/{match_url}
- GET /api/search?q={query}
- GET /api/news-detail/{league_id}/{news_id}
- POST /api/register-push-token
