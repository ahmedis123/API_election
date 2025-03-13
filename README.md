واجهة برمجة التطبيقات لإدارة الانتخابات

هذه واجهة برمجة تطبيقات تعتمد على Flask لإدارة الانتخابات، والناخبين، والمرشحين، والأصوات، والنتائج، والمديرين. يتيح النظام إنشاء واسترجاع وتحديث وحذف الكيانات المختلفة المتعلقة بعملية الانتخابات. كما يتضمن وظائف لإدلاء الأصوات، وتسجيل الدخول كناخب أو مدير، واسترجاع نتائج الانتخابات.

الميزات

إدارة الناخبين: إضافة وتحديث وحذف واسترجاع معلومات الناخبين.

إدارة المرشحين: إضافة وتحديث وحذف واسترجاع معلومات المرشحين.

إدارة الانتخابات: إضافة وتحديث وحذف واسترجاع تفاصيل الانتخابات.

إدارة الأصوات: إيداع الأصوات وتحديثها واسترجاع معلومات الأصوات.

إدارة النتائج: إضافة واسترجاع وتحديث نتائج الانتخابات.

إدارة المديرين: إضافة وتحديث وحذف واسترجاع معلومات المديرين.

المصادقة: وظيفة تسجيل الدخول للناخبين والمديرين.

إيداع الأصوات: إيداع أصوات آمن مع التحقق من منع التصويت المزدوج.


المتطلبات الأساسية

Python 3.x

Flask

psycopg2 (محول PostgreSQL لـ Python)

قاعدة بيانات PostgreSQL


التثبيت

1. استنساخ المستودع:

git clone https://github.com/yourusername/election-management-system.git
cd election-management-system


2. تثبيت المتطلبات:

pip install -r requirements.txt


3. إعداد قاعدة البيانات:

تأكد من تثبيت وتشغيل PostgreSQL.

قم بإنشاء قاعدة بيانات جديدة وتحديث تفاصيل الاتصال في دالة create_connection في الكود.



4. تشغيل التطبيق:

python app.py



نقاط النهاية لواجهة البرمجة

الناخبين

POST /voters: إضافة ناخب جديد.

GET /voters: استرجاع جميع الناخبين.

PUT /voters/int:voter_id: تحديث تفاصيل الناخب.

DELETE /voters/int:voter_id: حذف ناخب.


المرشحون

POST /candidates: إضافة مرشح جديد.

GET /candidates: استرجاع جميع المرشحين.

GET /candidates/election/int:election_id: استرجاع المرشحين حسب معرف الانتخابات.

PUT /candidates/int:candidate_id: تحديث تفاصيل المرشح.

DELETE /candidates/int:candidate_id: حذف مرشح.


الانتخابات

POST /elections: إضافة انتخابات جديدة.

GET /elections: استرجاع جميع الانتخابات.

PUT /elections/int:election_id: تحديث تفاصيل الانتخابات.

DELETE /elections/int:election_id: حذف انتخابات.


الأصوات

POST /votes: إضافة صوت جديد.

GET /votes: استرجاع جميع الأصوات.

PUT /votes/int:vote_id: تحديث صوت.

POST /castVote: إيداع صوت.


النتائج

POST /results: إضافة نتيجة جديدة.

GET /results: استرجاع جميع النتائج.

GET /election_results/int:election_id: استرجاع نتائج الانتخابات حسب معرف الانتخابات.


المديرون

POST /admin: إضافة مدير جديد.

GET /admin: استرجاع جميع المديرين.

PUT /admin/int:admin_id: تحديث تفاصيل المدير.

DELETE /admin/int:admin_id: حذف مدير.


المصادقة

POST /login: تسجيل الدخول كناخب.

POST /login_admin: تسجيل الدخول كمدير.


الاستخدام

1. تشغيل الخادم:

python app.py


2. استخدم عميل API (مثل Postman أو cURL) للتفاعل مع نقاط النهاية لواجهة البرمجة.



أمثلة على الطلبات

إضافة ناخب

POST /voters

{
    "NationalID": "123456789",
    "VoterName": "John Doe",
    "State": "California",
    "Email": "john.doe@example.com",
    "HasVoted": false,
    "DateOfBirth": "1990-01-01",
    "Gender": "Male",
    "Password": "password123",
    "Phone": "1234567890"
}

إيداع صوت

POST /castVote

{
    "voter_id": 1,
    "election_id": 1,
    "candidate_id": 1,
    "date": "2023-10-01"
}

تسجيل الدخول كناخب

POST /login

{
    "national_id": "123456789",
    "password": "password123"
}

مخطط قاعدة البيانات

يتضمن مخطط قاعدة البيانات الجداول التالية:

Elections: يخزن تفاصيل الانتخابات.

Voters: يخزن معلومات الناخبين.

Candidates: يخزن معلومات المرشحين.

Votes: يخزن سجلات الأصوات.

Results: يخزن نتائج الانتخابات.

Admins: يخزن معلومات المديرين.


اعتبارات الأمان

تجزئة كلمات المرور: يتم تجزئة كلمات المرور باستخدام SHA-256 قبل تخزينها في قاعدة البيانات.

التحقق من المدخلات: تأكد من أن جميع الحقول المطلوبة موجودة وصحيحة قبل معالجة الطلبات.

التعامل مع الأخطاء: يتم تنفيذ التعامل مع الأخطاء وتسجيل الأخطاء لالتقاط وتسجيل الاستثناءات.


المساهمة

المساهمات مرحب بها! يرجى استنساخ المستودع وتقديم طلب سحب مع التعديلات الخاصة بك.

الترخيص

يتم ترخيص هذا المشروع بموجب ترخيص MIT. راجع ملف LICENSE لمزيد من التفاصيل.

الاتصال

لأي أسئلة أو مشاكل، يرجى فتح مشكلة على مستودع GitHub.

