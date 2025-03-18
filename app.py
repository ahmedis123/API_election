from flask import Flask, request, jsonify
import psycopg2
from psycopg2 import pool, Error
import hashlib
import logging
from datetime import datetime

# تكوين نظام التسجيل
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('election_system.log'),
        logging.StreamHandler()
    ]
)

app = Flask(__name__)

# تكوين Connection Pool
try:
    connection_pool = psycopg2.pool.SimpleConnectionPool(
        minconn=2,
        maxconn=10,
        host="aws-0-eu-central-1.pooler.supabase.com",
        port="6543",
        database="postgres",
        user="postgres.frzhxdxupmnuozfwnjcg",
        password="Ahmedis123@a"
    )
    logging.info("تم تهيئة مجموعة الاتصالات بنجاح")
except Error as e:
    logging.critical("فشل في تهيئة مجموعة الاتصالات: %s", e)
    raise

# وظائف إدارة الاتصالات
def get_connection():
    try:
        return connection_pool.getconn()
    except Error as e:
        logging.warning("فشل في الحصول على اتصال: %s", e)
        return None

def release_connection(connection):
    if connection:
        try:
            connection_pool.putconn(connection)
        except Error as e:
            logging.warning("فشل في إعادة الاتصال: %s", e)

# تشفير كلمة المرور
def hash_password(password):
    try:
        return hashlib.sha256((password + "Elction").encode()).hexdigest()
    except Exception as e:
        logging.error("خطأ في تشفير كلمة المرور: %s", e)
        raise

# إنشاء الجداول
def create_tables():
    conn = get_connection()
    if not conn:
        logging.critical("فشل إنشاء الجداول: لا يوجد اتصال بقاعدة البيانات")
        return

    try:
        with conn.cursor() as cursor:
            # ... (نفس الجداول السابقة)
        logging.info("تم إنشاء الجداول بنجاح")
    except Error as e:
        logging.critical("فشل في إنشاء الجداول: %s", e)
        conn.rollback()
    finally:
        release_connection(conn)

# ---------------------------------------------------
# نقاط نهاية الناخبين
# ---------------------------------------------------
@app.route('/voters', methods=['POST'])
def add_voter():
    # ... (الكود السابق مع التعديلات)

@app.route('/voters/<int:voter_id>', methods=['PUT'])
def update_voter(voter_id):
    if voter_id <= 0:
        logging.warning("معرف ناخب غير صالح: %s", voter_id)
        return jsonify({"error": "معرف غير صالح"}), 400

    conn = get_connection()
    if not conn:
        logging.error("فشل تحديث الناخب: لا يوجد اتصال")
        return jsonify({"error": "خطأ في قاعدة البيانات"}), 500

    try:
        data = request.get_json()
        with conn.cursor() as cursor:
            # ... (تنفيذ الاستعلام مع التسجيل)
            conn.commit()
            return jsonify({"message": "تم التحديث بنجاح"}), 200
    except Error as e:
        logging.error("خطأ في تحديث الناخب: %s", e)
        return jsonify({"error": "فشل في العملية"}), 500
    finally:
        release_connection(conn)

# ---------------------------------------------------
# نقاط نهاية الانتخابات
# ---------------------------------------------------
@app.route('/elections', methods=['POST'])
def add_election():
    conn = get_connection()
    if not conn:
        logging.error("فشل إضافة انتخابات: لا يوجد اتصال")
        return jsonify({"error": "خطأ في قاعدة البيانات"}), 500

    try:
        data = request.get_json()
        with conn.cursor() as cursor:
            cursor.execute(
                """INSERT INTO Elections (...) VALUES (...);""",
                (data['ElectionDate'], data['ElectionType'], data['ElectionStatus'])
            )
            conn.commit()
            return jsonify({"message": "تمت إضافة الانتخابات"}), 201
    except Error as e:
        logging.warning("خطأ في إضافة الانتخابات: %s", e)
        return jsonify({"error": "فشل في العملية"}), 500
    finally:
        release_connection(conn)

# ---------------------------------------------------
# نقاط نهاية التصويت
# ---------------------------------------------------
@app.route('/castVote', methods=['POST'])
def castVote():
    data = request.get_json()
    required_fields = ["voter_id", "election_id", "candidate_id", "date"]
    
    if not all(field in data for field in required_fields):
        logging.warning("بيانات تصويت ناقصة")
        return jsonify({"error": "بيانات مطلوبة مفقودة"}), 400

    conn = get_connection()
    if not conn:
        logging.error("فشل التصويت: لا يوجد اتصال")
        return jsonify({"error": "خطأ في قاعدة البيانات"}), 500

    try:
        with conn.cursor() as cursor:
            # التحقق من حالة الناخب
            cursor.execute(
                "SELECT HasVoted FROM Voters WHERE VoterID = %s",
                (data['voter_id'],)
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
                """INSERT INTO Votes (...) VALUES (...);""",
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
                (data['voter_id'],)
            
            conn.commit()
            return jsonify({"message": "تم تسجيل التصويت بنجاح"}), 200

    except Error as e:
        conn.rollback()
        logging.error("خطأ في التصويت: %s", e)
        return jsonify({"error": "فشل في العملية"}), 500
    finally:
        release_connection(conn)

# ---------------------------------------------------
# نقاط نهاية النتائج
# ---------------------------------------------------
@app.route('/election_results/<int:election_id>', methods=['GET'])
def get_election_results(election_id):
    if election_id <= 0:
        logging.warning("معرف انتخاب غير صالح: %s", election_id)
        return jsonify({"error": "معرف غير صالح"}), 400

    conn = get_connection()
    if not conn:
        logging.error("فشل جلب النتائج: لا يوجد اتصال")
        return jsonify({"error": "خطأ في قاعدة البيانات"}), 500

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """SELECT c.CandidateName, p.PartyName, r.CountVotes
                FROM Results r
                JOIN Candidates c ON r.CandidateID = c.CandidateID
                WHERE r.ElectionID = %s
                ORDER BY r.CountVotes DESC""",
                (election_id,)
            )
            results = [
                {"name": row[0], "party": row[1], "votes": row[2]}
                for row in cursor.fetchall()
            ]
            return jsonify(results), 200
    except Error as e:
        logging.error("خطأ في جلب النتائج: %s", e)
        return jsonify({"error": "فشل في العملية"}), 500
    finally:
        release_connection(conn)

# ---------------------------------------------------
# نقاط نهاية المشرفين
# ---------------------------------------------------
@app.route('/login_admin', methods=['POST'])
def login_admin():
    data = request.get_json()
    if not data or 'Email' not in data or 'password' not in data:
        logging.warning("بيانات دخول مشرف ناقصة")
        return jsonify({"error": "بيانات مطلوبة مفقودة"}), 400

    conn = get_connection()
    if not conn:
        logging.error("فشل تسجيل دخول المشرف: لا يوجد اتصال")
        return jsonify({"error": "خطأ في قاعدة البيانات"}), 500

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """SELECT Privileges FROM Admins 
                WHERE Email = %s AND Password = %s""",
                (data['Email'], hash_password(data['password']))
            result = cursor.fetchone()
            
            if not result:
                logging.warning("محاولة دخول فاشلة للمشرف: %s", data['Email'])
                return jsonify({"error": "بيانات اعتماد خاطئة"}), 401
                
            return jsonify({
                "privileges": result[0]
            }), 200
    except Error as e:
        logging.error("خطأ في تسجيل دخول المشرف: %s", e)
        return jsonify({"error": "فشل في العملية"}), 500
    finally:
        release_connection(conn)

# ---------------------------------------------------
# التشغيل الرئيسي
# ---------------------------------------------------
if __name__ == '__main__':
    try:
        create_tables()
        app.run(host='0.0.0.0', debug=False)
    except Exception as e:
        logging.critical("فشل في بدء التطبيق: %s", e)
        raise
