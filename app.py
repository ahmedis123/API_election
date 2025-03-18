from flask import Flask, request, jsonify
import psycopg2
from psycopg2 import Error
import hashlib
import logging

app = Flask(__name__)

# تكوين نظام التسجيل
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('election_system.log'),
        logging.StreamHandler()
    ]
)

# وظيفة الاتصال بقاعدة البيانات
def create_connection():
    connection = None
    try:
        connection = psycopg2.connect(
            host="aws-0-eu-central-1.pooler.supabase.com",
            port="6543",
            database="postgres",
            user="postgres.frzhxdxupmnuozfwnjcg",
            password="Ahmedis123@a"
        )
        logging.info("تم الاتصال بقاعدة البيانات بنجاح")
    except Error as e:
        logging.error("خطأ في الاتصال بقاعدة البيانات: %s", e)
    
    return connection

# تشفير كلمة المرور
def hash_password(password):
    try:
        return hashlib.sha256((password + "Elction").encode()).hexdigest()
    except Exception as e:
        logging.error("خطأ في تشفير كلمة المرور: %s", e)
        raise

# إنشاء الجداول (مع تصحيح المسافات البادئة)
def create_tables():
    with create_connection() as connection:
        if connection is not None:
            cursor = connection.cursor()
            try:
                # إنشاء جدول الانتخابات
                cursor.execute('''CREATE TABLE IF NOT EXISTS Elections (
                                    ElectionID SERIAL PRIMARY KEY,
                                    ElectionDate TEXT,
                                    ElectionType TEXT,
                                    ElectionStatus TEXT
                                )''')
                logging.info("تم إنشاء جدول الانتخابات")

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
                logging.info("تم إنشاء جدول الناخبين")

                # ... (بقية الجداول بنفس النمط)

                connection.commit()
                logging.info("تم إنشاء جميع الجداول بنجاح")
                
            except Error as e:
                logging.critical("خطأ في إنشاء الجداول: %s", e)
                connection.rollback()
            finally:
                cursor.close()
        else:
            logging.error("فشل في إنشاء الجداول بسبب مشكلة في الاتصال")

# ... (بقية النقاط بنفس النمط مع التأكد من المسافات البادئة)

@app.route('/castVote', methods=['POST'])
def castVote():
    data = request.get_json()
    required_fields = ["voter_id", "election_id", "candidate_id", "date"]
    
    if not all(field in data for field in required_fields):
        logging.warning("بيانات تصويت ناقصة")
        return jsonify({"error": "بيانات مطلوبة مفقودة"}), 400

    conn = create_connection()
    if not conn:
        logging.error("فشل التصويت: لا يوجد اتصال")
        return jsonify({"error": "خطأ في قاعدة البيانات"}), 500

    try:
        cursor = conn.cursor()
        
        # التحقق من حالة الناخب
        cursor.execute(
            "SELECT HasVoted FROM Voters WHERE VoterID = %s",
            (data['voter_id'],)  # <-- Fixed: Added closing parenthesis
        )
        voter = cursor.fetchone()
        
        if not voter:
            logging.warning("ناخب غير موجود: %s", data['voter_id'])
            return jsonify({"error": "الناخب غير موجود"}), 404
            
        if voter[0]:
            logging.warning("محاولة تصويت مكررة: %s", data['voter_id'])
            return jsonify({"error": "تم التصويت مسبقًا"}), 400

        # إدخال التصويت
        cursor.execute(
            """INSERT INTO Votes (VoterID, ElectionID, CandidateID, ElectionDate)
            VALUES (%s, %s, %s, %s)""",
            (data['voter_id'], data['election_id'], 
             data['candidate_id'], data['date'])
        )

        # تحديث النتائج
        cursor.execute(
            """UPDATE Results SET CountVotes = CountVotes + 1 
            WHERE ElectionID = %s AND CandidateID = %s""",
            (data['election_id'], data['candidate_id'])
        )

        # تحديث حالة الناخب
        cursor.execute(
            "UPDATE Voters SET HasVoted = TRUE WHERE VoterID = %s",
            (data['voter_id'],)  # <-- Fixed: Added closing parenthesis
        )
        
        conn.commit()
        return jsonify({"message": "تم تسجيل التصويت بنجاح"}), 200

    except Error as e:
        conn.rollback()
        logging.error("خطأ في التصويت: %s", e)
        return jsonify({"error": "فشل في العملية"}), 500
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    create_tables()
    app.run(host='0.0.0.0', port=5000, debug=False)
