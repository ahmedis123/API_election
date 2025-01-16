from flask import Flask, request, jsonify
import psycopg2
from psycopg2 import sql, Error
import hashlib

app = Flask(__name__)

# دالة للاتصال بقاعدة البيانات
def create_connection():
    connection = None
    try:
        connection = psycopg2.connect(
            dbname='election_sys',
            user='admin',
            password='0n4a8VaVktozo7N8VKrYvOMAaXaFdOq0',
            host='dpg-cu4br6l6l47c73b11lt0-a',
            port='5432'
        )
    except Error as e:
        print(f"Error: {e}")
    return connection

# دالة تشفير كلمة المرور
def hash_password(password):
    # دمج كلمة المرور مع Salt
    combined = password + "Elction"
    # توليد الهاش
    hashed_password = hashlib.sha256(combined.encode()).hexdigest()
    return hashed_password

# دالة لإنشاء الجداول
def create_tables():
    with create_connection() as connection:
        if connection is not None:
            cursor = connection.cursor()

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

            cursor.execute('''CREATE TABLE IF NOT EXISTS Candidate (
                                CandidateID SERIAL PRIMARY KEY,
                                NationalID TEXT UNIQUE,
                                CandidateName TEXT,
                                PartyName TEXT,
                                Biography TEXT,
                                CandidateProgram TEXT,
                                ElectionID INTEGER,
                                FOREIGN KEY (ElectionID) REFERENCES Elections (ElectionID) ON DELETE CASCADE
                            )''')

            cursor.execute('''CREATE TABLE IF NOT EXISTS Elections (
                                ElectionID SERIAL PRIMARY KEY,
                                ElectionDate TEXT,
                                ElectionType TEXT,
                                ElectionStatus TEXT
                            )''')

            cursor.execute('''CREATE TABLE IF NOT EXISTS Votes (
                                VoteID SERIAL PRIMARY KEY,
                                VoterID INTEGER,
                                ElectionDate TEXT,
                                CandidateID INTEGER,
                                ElectionID INTEGER,
                                FOREIGN KEY (VoterID) REFERENCES Voters (VoterID),
                                FOREIGN KEY (CandidateID) REFERENCES Candidate (CandidateID),
                                FOREIGN KEY (ElectionID) REFERENCES Elections (ElectionID)
                            )''')

            cursor.execute('''CREATE TABLE IF NOT EXISTS Result (
                                ResultID SERIAL PRIMARY KEY,
                                CountVotes INTEGER,
                                CandidateID INTEGER,
                                ResultDate TEXT,
                                ElectionID INTEGER,
                                FOREIGN KEY (CandidateID) REFERENCES Candidate (CandidateID),
                                FOREIGN KEY (ElectionID) REFERENCES Elections (ElectionID)
                            )''')

            cursor.execute('''CREATE TABLE IF NOT EXISTS Admins (
                                AdminID SERIAL PRIMARY KEY,
                                AdminName TEXT,
                                Email TEXT UNIQUE,
                                Password TEXT,
                                Privileges TEXT
                            )''')
            connection.commit()
            print("Tables created successfully.")
        else:
            print("Failed to create tables due to database connection error.")

# دالة لإضافة الناخبين مع التحقق من صحة الإدخال
@app.route('/voters', methods=['POST'])
def add_voter():
    data = request.get_json()
    required_fields = ["NationalID", "VoterName", "State", "Email", "HasVoted", "DateOfBirth", "Gender", "Password", "Phone"]

    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    hashed_password = hash_password(data['Password'])

    with create_connection() as connection:
        if connection is not None:
            cursor = connection.cursor()
            try:
                query = '''INSERT INTO Voters (NationalID, VoterName, State, Email, HasVoted, DateOfBirth, Gender, Password, Phone)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'''
                cursor.execute(query, (
                    data['NationalID'], data['VoterName'], data['State'], data['Email'],
                    data['HasVoted'], data['DateOfBirth'], data['Gender'], hashed_password, data['Phone']
                ))
                connection.commit()
                return jsonify({"message": "Voter added successfully!"}), 201
            except psycopg2.IntegrityError as e:
                print(f"Integrity error: {e}")
                return jsonify({"error": "Duplicate entry or invalid data"}), 400
            except Exception as e:
                print(f"Database error: {e}")
                return jsonify({"error": "Database operation failed"}), 500

# دالة لإضافة المرشحين
@app.route('/candidates', methods=['POST'])
def add_candidate():
    data = request.get_json()
    required_fields = ["NationalID", "CandidateName", "PartyName", "Biography", "CandidateProgram", "ElectionID"]

    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    with create_connection() as connection:
        if connection is not None:
            cursor = connection.cursor()
            try:
                query = '''INSERT INTO Candidate (NationalID, CandidateName, PartyName, Biography, CandidateProgram, ElectionID)
                           VALUES (%s, %s, %s, %s, %s, %s)'''
                cursor.execute(query, (
                    data['NationalID'], data['CandidateName'], data['PartyName'],
                    data['Biography'], data['CandidateProgram'], data['ElectionID']
                ))
                connection.commit()
                return jsonify({"message": "Candidate added successfully!"}), 201
            except psycopg2.IntegrityError as e:
                print(f"Integrity error: {e}")
                return jsonify({"error": "Duplicate entry or invalid data"}), 400
            except Exception as e:
                print(f"Database error: {e}")
                return jsonify({"error": "Database operation failed"}), 500

# دالة لإضافة الانتخابات
@app.route('/elections', methods=['POST'])
def add_election():
    data = request.get_json()
    required_fields = ["ElectionDate", "ElectionType", "ElectionStatus"]

    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    with create_connection() as connection:
        if connection is not None:
            cursor = connection.cursor()
            try:
                query = '''INSERT INTO Elections (ElectionDate, ElectionType, ElectionStatus)
                        VALUES (%s, %s, %s)'''
                cursor.execute(query, (data['ElectionDate'], data['ElectionType'], data['ElectionStatus']))
                connection.commit()
                return jsonify({"message": "Election added successfully!"}), 201
            except psycopg2.IntegrityError as e:
                print(f"Integrity error: {e}")
                return jsonify({"error": "Duplicate entry or invalid data"}), 400
            except Exception as e:
                print(f"Database error: {e}")
                return jsonify({"error": "Database operation failed"}), 500

# دالة لإضافة تصويت
@app.route('/votes', methods=['POST'])
def add_vote():
    data = request.get_json()
    required_fields = ["VoterID", "ElectionDate", "CandidateID", "ElectionID"]

    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    with create_connection() as connection:
        if connection is not None:
            cursor = connection.cursor()
            try:
                query = '''INSERT INTO Votes (VoterID, ElectionDate, CandidateID, ElectionID)
                        VALUES (%s, %s, %s, %s)'''
                cursor.execute(query, (data['VoterID'], data['ElectionDate'], data['CandidateID'], data['ElectionID']))
                connection.commit()
                return jsonify({"message": "Vote added successfully!"}), 201
            except psycopg2.IntegrityError as e:
                print(f"Integrity error: {e}")
                return jsonify({"error": "Duplicate entry or invalid data"}), 400
            except Exception as e:
                print(f"Database error: {e}")
                return jsonify({"error": "Database operation failed"}), 500

# دالة لإضافة نتيجة
@app.route('/results', methods=['POST'])
def add_result():
    data = request.get_json()
    required_fields = ["CountVotes", "CandidateID", "ResultDate", "ElectionID"]

    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    with create_connection() as connection:
        if connection is not None:
            cursor = connection.cursor()
            try:
                query = '''INSERT INTO Result (CountVotes, CandidateID, ResultDate, ElectionID)
                        VALUES (%s, %s, %s, %s)'''
                cursor.execute(query, (data['CountVotes'], data['CandidateID'], data['ResultDate'], data['ElectionID']))
                connection.commit()
                return jsonify({"message": "Result added successfully!"}), 201
            except psycopg2.IntegrityError as e:
                print(f"Integrity error: {e}")
                return jsonify({"error": "Duplicate entry or invalid data"}), 400
            except Exception as e:
                print(f"Database error: {e}")
                return jsonify({"error": "Database operation failed"}), 500

# دالة لإضافة مدير النظام
@app.route('/admin', methods=['POST'])
def add_admin():
    data = request.get_json()
    required_fields = ["AdminName", "Email", "Password", "Privileges"]

    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    hashed_password = hash_password(data['Password'])

    with create_connection() as connection:
        if connection is not None:
            cursor = connection.cursor()
            try:
                query = '''INSERT INTO Admins (AdminName, Email, Password, Privileges)
                        VALUES (%s, %s, %s, %s)'''
                cursor.execute(query, (data['AdminName'], data['Email'], hashed_password, data['Privileges']))
                connection.commit()
                return jsonify({"message": "Admin added successfully!"}), 201
            except psycopg2.IntegrityError as e:
                print(f"Integrity error: {e}")
                return jsonify({"error": "Duplicate entry or invalid data"}), 400
            except Exception as e:
                print(f"Database error: {e}")
                return jsonify({"error": "Database operation failed"}), 500

# دالة لاسترجاع الناخبين
@app.route('/voters', methods=['GET'])
def get_voters():
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM "Voters"')
        rows = cursor.fetchall()

        if not rows:
            return jsonify({"error": "No Voter found"}), 404

        voters = []
        for row in rows:
            voters.append({
                "VoterID": row[0],
                "NationalID": row[1],
                "VoterName": row[2],
                "State": row[3],
                "Email": row[4],
                "HasVoted": row[5],
                "DateOfBirth": row[6],
                "Gender": row[7],
                "Password": row[8],
                "Phone": row[9]
            })
        return jsonify(voters), 200

# دالة لاسترجاع المرشحين
@app.route('/candidates', methods=['GET'])
def get_Candidate():
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM "Candidate"')
        candidates = cursor.fetchall()

        if not candidates:
            return jsonify({"error": "No candidates found"}), 404

        candidate_list = []
        for candidate in candidates:
            candidate_list.append({
                "CandidateID": candidate[0],
                "NationalID": candidate[1],
                "CandidateName": candidate[2],
                "PartyName": candidate[3],
                "Biography": candidate[4],
                "CandidateProgram": candidate[5],
                "ElectionID": candidate[6]
            })
        return jsonify(candidate_list), 200

# دالة لاسترجاع المرشحين باستخدام معرف الانتخابات
@app.route('/candidates/election/<int:election_id>', methods=['GET'])
def get_candidates_by_election(election_id):
    if election_id <= 0:
        return jsonify({"error": "Invalid ElectionID. It must be a positive integer."}), 400

    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM "Candidate" WHERE "ElectionID" = %s', (election_id,))
        candidates = cursor.fetchall()

        if not candidates:
            return jsonify({"error": "No candidates found for the given ElectionID"}), 404

        candidate_list = []
        for candidate in candidates:
            candidate_list.append({
                "CandidateID": candidate[0],
                "NationalID": candidate[1],
                "CandidateName": candidate[2],
                "PartyName": candidate[3],
                "Biography": candidate[4],
                "CandidateProgram": candidate[5],
                "ElectionID": candidate[6]
            })
        return jsonify(candidate_list), 200

# دالة لاسترجاع الانتخابات
@app.route('/elections', methods=['GET'])
def get_elections():
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM "Elections"')
        rows = cursor.fetchall()

        if not rows:
            return jsonify({"error": "No election found"}), 404

        elections = []
        for row in rows:
            elections.append({
                "ElectionID": row[0],
                "ElectionDate": row[1],
                "ElectionType": row[2],
                "ElectionStatus": row[3]
            })
        return jsonify(elections), 200

# دالة لاسترجاع التصويت
@app.route('/votes', methods=['GET'])
def get_votes():
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM "Vote"')
        rows = cursor.fetchall()

        if not rows:
            return jsonify({"error": "No vote found"}), 404

        votes = []
        for row in rows:
            votes.append({
                "VoteID": row[0],
                "VoterID": row[1],
                "ElectionDate": row[2],
                "CandidateID": row[3],
                "ElectionID": row[4]
            })
        return jsonify(votes), 200

# دالة لاسترجاع النتائج
@app.route('/results', methods=['GET'])
def get_results():
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM "Result"')
        rows = cursor.fetchall()

        if not rows:
            return jsonify({"error": "No result found"}), 404

        results = []
        for row in rows:
            results.append({
                "ResultID": row[0],
                "CountVotes": row[1],
                "CandidateID": row[2],
                "ResultDate": row[3],
                "ElectionID": row[4]
            })
        return jsonify(results), 200

# دالة لاسترجاع مدير النظام
@app.route('/admin', methods=['GET'])
def get_admin():
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM "Admin"')
        rows = cursor.fetchall()

        if not rows:
            return jsonify({"error": "No admin found"}), 404

        admins = []
        for row in rows:
            admins.append({
                "AdminID": row[0],
                "AdminName": row[1],
                "Email": row[2],
                "Password": row[3],
                "Privileges": row[4]
            })
        return jsonify(admins), 200

# دالة لحذف الناخب
@app.route('/voters/<int:voter_id>', methods=['DELETE'])
def delete_voter(voter_id):
    if voter_id <= 0:
        return jsonify({"error": "Invalid voter_id. It must be a positive integer."}), 400

    with create_connection() as conn:
        try:
            cursor = conn.cursor()
            query = '''DELETE FROM Voters WHERE VoterID = %s'''
            cursor.execute(query, (voter_id,))
            conn.commit()

            if cursor.rowcount == 0:
                return jsonify({"error": "Voter not found"}), 404

            return jsonify({"message": "Voter deleted successfully!"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

# دالة لتحديث الناخب
@app.route('/voters/<int:voter_id>', methods=['PUT'])
def update_voter(voter_id):
    if voter_id <= 0:
        return jsonify({"error": "Invalid VoterID. It must be a positive integer."}), 400

    data = request.get_json()
    updatable_fields = ["NationalID", "VoterName", "State", "Email", "HasVoted", "DateOfBirth", "Gender", "Password", "Phone"]
    missing_fields = [field for field in updatable_fields if field not in data or data[field] == ""]
    if missing_fields:
        return jsonify({"error": f"Missing or empty fields: {', '.join(missing_fields)}"}), 400

    hashed_password = hash_password(data['Password'])

    with create_connection() as conn:
        try:
            cursor = conn.cursor()
            query = '''
                UPDATE Voters SET NationalID = %s, VoterName = %s, State = %s, Email = %s,
                HasVoted = %s, DateOfBirth = %s, Gender = %s, Password = %s, Phone = %s
                WHERE VoterID = %s
            '''
            cursor.execute(query, (
                data['NationalID'], data['VoterName'], data['State'], data['Email'],
                data['HasVoted'], data['DateOfBirth'], data['Gender'], hashed_password,
                data['Phone'], voter_id
            ))
            conn.commit()

            if cursor.rowcount == 0:
                return jsonify({"error": "Voter not found or no changes made"}), 404

            return jsonify({"message": "Voter updated successfully!"}), 200
        except psycopg2.IntegrityError:
            return jsonify({"error": "Duplicate entry or invalid data"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

# دالة لتحديث مرشح
@app.route('/candidates/<int:candidate_id>', methods=['PUT'])
def update_candidate(candidate_id):
    if candidate_id <= 0:
        return jsonify({"error": "Invalid CandidateID. It must be a positive integer."}), 400

    data = request.get_json()
    updatable_fields = ["NationalID", "CandidateName", "PartyName", "Biography", "CandidateProgram", "ElectionID"]
    missing_fields = [field for field in updatable_fields if field not in data or data[field] == ""]
    if missing_fields:
        return jsonify({"error": f"Missing or empty fields: {', '.join(missing_fields)}"}), 400

    with create_connection() as conn:
        try:
            cursor = conn.cursor()
            query = '''
                UPDATE Candidate
                SET NationalID = %s, CandidateName = %s, PartyName = %s, Biography = %s,
                    CandidateProgram = %s, ElectionID = %s
                WHERE CandidateID = %s
            '''
            cursor.execute(query, (
                data["NationalID"], data["CandidateName"], data["PartyName"], data["Biography"],
                data["CandidateProgram"], data["ElectionID"], candidate_id
            ))
            conn.commit()

            if cursor.rowcount == 0:
                return jsonify({"error": "Candidate not found or no changes made"}), 404

            return jsonify({"message": "Candidate updated successfully!"}), 200
        except psycopg2.IntegrityError:
            return jsonify({"error": "Duplicate entry or invalid data"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
# دالة لحذف مرشح
@app.route('/candidates/<int:candidate_id>', methods=['DELETE'])
def delete_candidate(candidate_id):
    if candidate_id <= 0:
        return jsonify({"error": "Invalid CandidateID. It must be a positive integer."}), 400

    with create_connection() as conn:
        try:
            cursor = conn.cursor()
            query = "DELETE FROM Candidate WHERE CandidateID = %s"
            cursor.execute(query, (candidate_id,))
            conn.commit()

            if cursor.rowcount == 0:
                return jsonify({"error": "Candidate not found"}), 404

            return jsonify({"message": "Candidate deleted successfully!"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
# دالة لتحديث الانتخابات
@app.route('/elections/<int:election_id>', methods=['PUT'])
def update_election(election_id):
    if election_id <= 0:
        return jsonify({"error": "Invalid ElectionID. It must be a positive integer."}), 400

    data = request.get_json()
    updatable_fields = ["ElectionDate", "ElectionType", "ElectionStatus"]
    missing_fields = [field for field in updatable_fields if field not in data or data[field] == ""]
    if missing_fields:
        return jsonify({"error": f"Missing or empty fields: {', '.join(missing_fields)}"}), 400

    with create_connection() as conn:
        try:
            cursor = conn.cursor()
            query = '''
                UPDATE Elections
                SET ElectionDate = %s, ElectionType = %s, ElectionStatus = %s
                WHERE ElectionID = %s
            '''
            cursor.execute(query, (
                data['ElectionDate'], data['ElectionType'], data['ElectionStatus'], election_id
            ))
            conn.commit()

            if cursor.rowcount == 0:
                return jsonify({"error": "Election not found or no changes made"}), 404

            return jsonify({"message": "Election updated successfully!"}), 200
        except psycopg2.IntegrityError:
            return jsonify({"error": "Duplicate entry or invalid data"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
# دالة لحذف الانتخابات
@app.route('/elections/<int:election_id>', methods=['DELETE'])
def delete_election(election_id):
    if election_id <= 0:
        return jsonify({"error": "Invalid election_id. It must be a positive integer."}), 400

    with create_connection() as conn:
        try:
            cursor = conn.cursor()
            query = '''DELETE FROM Elections WHERE ElectionID = %s'''
            cursor.execute(query, (election_id,))
            conn.commit()

            if cursor.rowcount == 0:
                return jsonify({"error": "Election not found"}), 404

            return jsonify({"message": "Election deleted successfully!"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
# دالة لتحديث مدير نظام
@app.route('/admin/<int:admin_id>', methods=['PUT'])
def update_admin(admin_id):
    if admin_id <= 0:
        return jsonify({"error": "Invalid admin_id. It must be a positive integer."}), 400

    data = request.get_json()
    updatable_fields = ["AdminName", "Email", "Password", "Privileges"]
    missing_fields = [field for field in updatable_fields if field not in data or data[field] == ""]
    if missing_fields:
        return jsonify({"error": f"Missing or empty fields: {', '.join(missing_fields)}"}), 400

    hashed_password = hash_password(data['Password']) if len(data['Password']) < 50 else data['Password']

    with create_connection() as conn:
        try:
            cursor = conn.cursor()
            query = '''
                UPDATE Admin
                SET AdminName = %s, Email = %s, Password = %s, Privileges = %s
                WHERE AdminID = %s
            '''
            cursor.execute(query, (
                data['AdminName'], data['Email'], hashed_password, data['Privileges'], admin_id
            ))
            conn.commit()

            if cursor.rowcount == 0:
                return jsonify({"error": "Admin not found or no changes made"}), 404

            return jsonify({"message": "Admin updated successfully!"}), 200
        except psycopg2.IntegrityError:
            return jsonify({"error": "Duplicate entry or invalid data"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
# دالة لحذف مدير نظام
@app.route('/admin/<int:admin_id>', methods=['DELETE'])
def delete_admin(admin_id):
    if admin_id <= 0:
        return jsonify({"error": "Invalid admin_id. It must be a positive integer."}), 400

    with create_connection() as conn:
        try:
            cursor = conn.cursor()
            query = '''DELETE FROM Admin WHERE AdminID = %s'''
            cursor.execute(query, (admin_id,))
            conn.commit()

            if cursor.rowcount == 0:
                return jsonify({"error": "Admin not found"}), 404

            return jsonify({"message": "Admin deleted successfully!"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
# دالة لاسترجاع النتائج مرتبة حسب عدد الأصوات
@app.route('/election_results/<int:election_id>', methods=['GET'])
def get_election_results(election_id):
    if election_id <= 0:
        return jsonify({"error": "Invalid ElectionID. It must be a positive integer."}), 400

    # الاستعلام عن النتائج
    with create_connection() as conn:
        try:
            cursor = conn.cursor()

            query = '''
                SELECT *
                FROM Candidate AS c
                INNER JOIN Result AS r ON c.CandidateID = r.CandidateID
                WHERE r.ElectionID = %s
            '''
            cursor.execute(query, (election_id,))

            results = cursor.fetchall()

            if not results:
                return jsonify({"error": "No results found"}), 404

            # تجهيز البيانات للإرجاع
            formatted_results = []
            for row in results:
                formatted_results.append({
                    "CandidateID": row[0],
                    "CandidateName": row[2],
                    "PartyName": row[3],
                    "CountVotes": row[8],
                    "ElectionID": row[6]
                })

            return jsonify(formatted_results), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
# دالة لتحديث التصزيت 
@app.route('/Votes/<int:vote_id>', methods=['PUT'])
def update_vote(vote_id):
    if vote_id <= 0:
        return jsonify({"error": "Invalid voteID. It must be a positive integer."}), 400

    # قراءة البيانات المرسلة في الطلب
    data = request.get_json()

    updatable_fields = ["ElectionDate", "CandidateID", "ElectionID"]

    # التحقق من وجود الحقول المطلوبة في الطلب
    missing_fields = [field for field in updatable_fields if field not in data or data[field] == ""]
    if missing_fields:
        return jsonify({"error": f"Missing or empty fields: {', '.join(missing_fields)}"}), 400

    with create_connection() as conn:
        try:
            cursor = conn.cursor()
            query = '''UPDATE Vote SET ElectionDate = %s, CandidateID = %s, ElectionID = %s
                    WHERE VoterID = %s'''
            cursor.execute(query, (
                data['ElectionDate'], data['CandidateID'], data['ElectionID'], vote_id
            ))

            conn.commit()

            if cursor.rowcount == 0:
                return jsonify({"error": "Vote not found or no changes made"}), 404

            return jsonify({"message": "Vote updated successfully!"}), 200
        except psycopg2.IntegrityError:
            return jsonify({"error": "Duplicate entry or invalid data"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
#   دالة لتسجيل الدخول
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    national_id = data['national_id']
    password = data['password']

    connection = create_connection()
    cursor = connection.cursor()

    try:
        hashed_password = hash_password(password)

        cursor.execute('''
            SELECT VoterID, HasVoted FROM Voters
            WHERE NationalID = %s AND Password = %s
        ''', (national_id, hashed_password))
        result = cursor.fetchone()

        if result:
            cursor.execute("SELECT ElectionID FROM Vote WHERE VoterID = %s", (result[0],))
            vote_result = cursor.fetchall()
            if vote_result:
                election_id = [row[0] for row in vote_result]        
            else:
                election_id = []
            voter_id = result[0]
            HasVoted = result[1]

            return jsonify({"message": "Login successful!", "voter_id": voter_id, "HasVoted": HasVoted, "election_id": election_id}), 200
        else:
            return jsonify({"message": "خطاء في الرقم الوطني او كلمة السر"}), 401

    except psycopg2.Error as e:
        return jsonify({"message": str(e)}), 500

    finally:
        connection.close()
        
#    دالة لتسجيل الدخول مدير النظام
@app.route('/login_admin', methods=['POST'])
def login_admin():
    data = request.get_json()
    Email = data['Email']
    password = data['password']

    connection = create_connection()
    cursor = connection.cursor()

    try:
        hashed_password = hash_password(password)

        cursor.execute('''
            SELECT Privileges FROM Admin
            WHERE Email = %s AND Password = %s
        ''', (Email, hashed_password))
        result = cursor.fetchone()

        if result:
            Privileges = result[0]
            return jsonify({"message": "Login successful!", "Privileges": Privileges}), 200
        else:
            return jsonify({"message": "خطاء في الرقم الوطني او كلمة السر"}), 401

    except psycopg2.Error as e:
        return jsonify({"message": str(e)}), 500

    finally:
        connection.close()

@app.route('/castVote', methods=['POST'])
def castVote():
    data = request.get_json()
    voter_id = data['voter_id']
    election_id = data['election_id']
    candidate_id = data['candidate_id']
    date = data['date']

    connection = create_connection()
    cursor = connection.cursor()

    try:
        # 1. التحقق من حالة الناخب
        cursor.execute("SELECT HasVoted FROM Voters WHERE VoterID = %s", (voter_id,))
        voter = cursor.fetchone()
        if not voter:
            return jsonify({"error": "Voter not found"}), 404

        cursor.execute("""
            INSERT INTO Vote (VoterID, ElectionID, CandidateID, ElectionDate )
            VALUES (%s, %s, %s, %s)
        """, (voter_id, election_id, candidate_id, date))

        cursor.execute("""
            SELECT CountVotes FROM Result
            WHERE ElectionID = %s AND CandidateID = %s
        """, (election_id, candidate_id))
        result = cursor.fetchone()
        if result:
            cursor.execute("""
                UPDATE Result
                SET CountVotes = CountVotes + 1
                WHERE ElectionID = %s AND CandidateID = %s
            """, (election_id, candidate_id))
        else:
            cursor.execute("""
                INSERT INTO Result (ElectionID, CandidateID, CountVotes, ResultDate )
                VALUES (%s, %s, 1, %s)
            """, (election_id, candidate_id, date))

        cursor.execute("""
            UPDATE Voters
            SET HasVoted = 1
            WHERE VoterID = %s
        """, (voter_id,))

        connection.commit()
        return jsonify({"message": "Vote recorded successfully"}), 201

    except psycopg2.Error as e:
        connection.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        connection.close()
        
# تشغيل الخادم
if __name__ == '__main__':
    create_tables()  # إنشاء الجداول عند بدء التطبيق
    app.run(debug=True,host='0.0.0.0')
te_id)
        else:
            cursor.execute("""
                INSERT INTO Result (ElectionID, CandidateID, CountVotes, ResultDate )
                VALUES (%s, %s, 1, %s)
            """, (election_id, candidate_id, date))

        cursor.execute("""
            UPDATE Voters
            SET HasVoted = 1
            WHERE VoterID = %s
        """, (voter_id,))

        connection.commit()
        return jsonify({"message": "Vote recorded successfully"}), 201

    except psycopg2.Error as e:
        connection.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        connection.close()
   
# تشغيل الخادم
if __name__ == '__main__':
    create_tables()  # إنشاء الجداول عند بدء التطبيق
    app.run(debug=True,host='0.0.0.0')
  ')
debug=True,host='0.0.0.0')
