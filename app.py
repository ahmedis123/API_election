from flask import Flask, request, jsonify
from psycopg2 import pool, Error
import hashlib
import logging

# تهيئة التطبيق
app = Flask(__name__)

# تكوين نظام التسجيل
logging.basicConfig(level=logging.WARNING)  # تسجيل التحذيرات والأخطاء فقط
logger = logging.getLogger(__name__)

# تهيئة بركة الاتصالات
postgreSQL_pool = None

def initialize_pool():
    global postgreSQL_pool
    try:
        postgreSQL_pool = pool.SimpleConnectionPool(
            1,  # أقل عدد من الاتصالات
            20,  # أقصى عدد من الاتصالات
            host="aws-0-eu-central-1.pooler.supabase.com",
            port="6543",
            database="postgres",
            user="postgres.frzhxdxupmnuozfwnjcg",
            password="Ahmedis123@a"
        )
        logger.info("تم تهيئة بركة الاتصالات بنجاح")
    except Error as e:
        logger.error(f"خطأ في تهيئة بركة الاتصالات: {e}")

# وظيفة الحصول على اتصال من البركة
def create_connection():
    try:
        if postgreSQL_pool:
            connection = postgreSQL_pool.getconn()
            logger.info("تم الحصول على اتصال من البركة")
            return connection
        else:
            logger.error("بركة الاتصالات غير مهيأة")
            return None
    except Error as e:
        logger.error(f"خطأ في الحصول على اتصال: {e}")
        return None

# وظيفة تشفير كلمة المرور
def hash_password(password):
    combined = password + "Elction"
    return hashlib.sha256(combined.encode()).hexdigest()

# وظيفة إنشاء الجداول
def create_tables():
    with create_connection() as connection:
        if connection:
            cursor = connection.cursor()
            try:
                # إنشاء جدول الانتخابات
                cursor.execute('''CREATE TABLE IF NOT EXISTS Elections (
                                    ElectionID SERIAL PRIMARY KEY,
                                    ElectionDate TEXT,
                                    ElectionType TEXT,
                                    ElectionStatus TEXT
                                )''')
                logger.info("تم إنشاء جدول الانتخابات")

                # إنشاء جدول الناخبين
                cursor.execute('''CREATE TABLE IF NOT EXISTS Voters (
                                    VoterID SERIAL PRIMARY KEY,
                                    NationalID TEXT UNIQUE,
                                    VoterName TEXT,
                                    State TEXT,
                                    Email TEXT,
                                    HasVoted BOOLEAN,
                                    DateOfBirth DATE,
                                    Gender TEXT,
                                    Password TEXT,
                                    Phone TEXT UNIQUE
                                )''')
                logger.info("تم إنشاء جدول الناخبين")

                # إنشاء جدول المرشحين
                cursor.execute('''CREATE TABLE IF NOT EXISTS Candidates (
                                    CandidateID SERIAL PRIMARY KEY,
                                    NationalID TEXT UNIQUE,
                                    CandidateName TEXT,
                                    PartyName TEXT,
                                    Biography TEXT,
                                    CandidateProgram TEXT,
                                    ElectionID INTEGER,
                                    FOREIGN KEY (ElectionID) REFERENCES Elections (ElectionID) ON DELETE CASCADE
                                )''')
                logger.info("تم إنشاء جدول المرشحين")

                # إنشاء جدول الأصوات
                cursor.execute('''CREATE TABLE IF NOT EXISTS Votes (
                                    VoteID SERIAL PRIMARY KEY,
                                    VoterID INTEGER,
                                    ElectionDate TEXT,
                                    CandidateID INTEGER,
                                    ElectionID INTEGER,
                                    FOREIGN KEY (VoterID) REFERENCES Voters (VoterID),
                                    FOREIGN KEY (CandidateID) REFERENCES Candidates (CandidateID),
                                    FOREIGN KEY (ElectionID) REFERENCES Elections (ElectionID)
                                )''')
                logger.info("تم إنشاء جدول الأصوات")

                # إنشاء جدول النتائج
                cursor.execute('''CREATE TABLE IF NOT EXISTS Results (
                                    ResultID SERIAL PRIMARY KEY,
                                    CountVotes INTEGER,
                                    CandidateID INTEGER,
                                    ResultDate TEXT,
                                    ElectionID INTEGER,
                                    FOREIGN KEY (CandidateID) REFERENCES Candidates (CandidateID),
                                    FOREIGN KEY (ElectionID) REFERENCES Elections (ElectionID)
                                )''')
                logger.info("تم إنشاء جدول النتائج")

                # إنشاء جدول الإداريين
                cursor.execute('''CREATE TABLE IF NOT EXISTS Admins (
                                    AdminID SERIAL PRIMARY KEY,
                                    AdminName TEXT,
                                    Email TEXT UNIQUE,
                                    Password TEXT,
                                    Privileges TEXT
                                )''')
                logger.info("تم إنشاء جدول الإداريين")

                connection.commit()
                logger.info("تم إنشاء جميع الجداول بنجاح")
            except Error as e:
                logger.error(f"خطأ في إنشاء الجداول: {e}")
                connection.rollback()
            finally:
                cursor.close()
        else:
            logger.error("فشل في الاتصال بقاعدة البيانات")

# ------------------- الناخبون -------------------
@app.route('/voters', methods=['POST'])
def add_voter():
    data = request.get_json()
    required_fields = ["NationalID", "VoterName", "State", "Email", "HasVoted", "DateOfBirth", "Gender", "Password", "Phone"]
    
    if not all(field in data for field in required_fields):
        logger.warning("حقول مطلوبة مفقودة في إضافة ناخب")
        return jsonify({"error": "الحقول المطلوبة مفقودة"}), 400

    with create_connection() as conn:
        if not conn:
            return jsonify({"error": "فشل الاتصال بقاعدة البيانات"}), 500
            
        cursor = conn.cursor()
        try:
            cursor.execute('''INSERT INTO Voters (
                NationalID, VoterName, State, Email, 
                HasVoted, DateOfBirth, Gender, Password, Phone
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)''', 
            (
                data['NationalID'], data['VoterName'], data['State'], 
                data['Email'], data['HasVoted'], data['DateOfBirth'],
                data['Gender'], hash_password(data['Password']), data['Phone']
            ))
            conn.commit()
            logger.info(f"تمت إضافة ناخب جديد: {data['NationalID']}")
            return jsonify({"message": "تمت الإضافة بنجاح"}), 201
        except Error as e:
            logger.error(f"خطأ في إضافة ناخب: {e}")
            return jsonify({"error": "فشل في العملية"}), 500

# ------------------- تسجيل الدخول -------------------
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    national_id = data.get('national_id')
    password = data.get('password')

    with create_connection() as conn:
        if not conn:
            return jsonify({"error": "فشل الاتصال بالخادم"}), 500

        cursor = conn.cursor()
        try:
            cursor.execute('''SELECT VoterID, HasVoted FROM Voters 
                           WHERE NationalID = %s AND Password = %s''',
                           (national_id, hash_password(password)))
            result = cursor.fetchone()
            
            if result:
                logger.info(f"تسجيل دخول ناجح للناخب: {national_id}")
                return jsonify({
                    "voter_id": result[0],
                    "has_voted": result[1]
                }), 200
            else:
                logger.warning(f"محاولة تسجيل دخول فاشلة: {national_id}")
                return jsonify({"error": "بيانات غير صحيحة"}), 401
        except Error as e:
            logger.error(f"خطأ في تسجيل الدخول: {e}")
            return jsonify({"error": "خطأ في الخادم"}), 500

# ------------------- الإداريون -------------------
@app.route('/admin', methods=['POST'])
def add_admin():
    data = request.get_json()
    required_fields = ["AdminName", "Email", "Password", "Privileges"]
    
    if not all(field in data for field in required_fields):
        return jsonify({"error": "الحقول المطلوبة مفقودة"}), 400

    with create_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''INSERT INTO Admins 
                            (AdminName, Email, Password, Privileges)
                            VALUES (%s, %s, %s, %s)''',
                            (data['AdminName'], data['Email'], 
                             hash_password(data['Password']), data['Privileges']))
            conn.commit()
            logger.info(f"تمت إضافة مدير جديد: {data['Email']}")
            return jsonify({"message": "تمت الإضافة بنجاح"}), 201
        except Error as e:
            logger.error(f"خطأ في إضافة مدير: {e}")
            return jsonify({"error": "فشل في العملية"}), 500

# ------------------- تشغيل التطبيق -------------------
if __name__ == '__main__':
    initialize_pool()  # تهيئة البركة أولاً
    create_tables()     # إنشاء الجداول
    app.run(host='0.0.0.0', port=5000, debug=False)
