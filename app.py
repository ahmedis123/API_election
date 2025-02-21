from flask import Flask, request, jsonify
import psycopg2
from psycopg2 import Error
import hashlib

app = Flask(__name__)

# Database connection function
def create_connection():
    connection = None
    try:
        connection = psycopg2.connect(
            host="aws-0-eu-central-1.pooler.supabase.com",
            port="6543",
            database="postgres",
            user="postgres.frzhxdxupmnuozfwnjcg",
            password="Ahmedis123@a"  # Ensure the password is correct
        )
        print("Database connection successful")
    except Error as e:
        print(f"Error connecting to the database: {e}")
    
    return connection

# Password hashing function
def hash_password(password):
    combined = password + "Elction"
    hashed_password = hashlib.sha256(combined.encode()).hexdigest()
    return hashed_password

# Function to create tables
def create_tables():
    with create_connection() as connection:
        if connection is not None:
            cursor = connection.cursor()
            try:
                # Create Elections table first
                cursor.execute('''CREATE TABLE IF NOT EXISTS Elections (
                                    ElectionID SERIAL PRIMARY KEY,
                                    ElectionDate TEXT,
                                    ElectionType TEXT,
                                    ElectionStatus TEXT
                                )''')
                print("Elections table created successfully.")

                # Create Voters table
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
                print("Voters table created successfully.")

                # Create Candidates table
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
                print("Candidates table created successfully.")

                # Create Votes table
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
                print("Votes table created successfully.")

                # Create Results table
                cursor.execute('''CREATE TABLE IF NOT EXISTS Results (
                                    ResultID SERIAL PRIMARY KEY,
                                    CountVotes INTEGER,
                                    CandidateID INTEGER,
                                    ResultDate TEXT,
                                    ElectionID INTEGER,
                                    FOREIGN KEY (CandidateID) REFERENCES Candidates (CandidateID),
                                    FOREIGN KEY (ElectionID) REFERENCES Elections (ElectionID)
                                )''')
                print("Results table created successfully.")

                # Create Admins table
                cursor.execute('''CREATE TABLE IF NOT EXISTS Admins (
                                    AdminID SERIAL PRIMARY KEY,
                                    AdminName TEXT,
                                    Email TEXT UNIQUE,
                                    Password TEXT,
                                    Privileges TEXT
                                )''')
                print("Admins table created successfully.")

                connection.commit()
                print("All tables created successfully.")
            except psycopg2.Error as e:
                print(f"Error creating tables: {e}")
                connection.rollback()
            finally:
                cursor.close()
        else:
            print("Failed to create tables due to database connection error.")

# Function to add voters
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

# Function to add candidates
@app.route('/candidates', methods=['POST'])
def add_candidate():
    data = request.get_json()
    required_fields = ["NationalID", "CandidateName", "PartyName", "Biography", "CandidateProgram", "ElectionID"]

    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    connection = None
    try:
        connection = create_connection()
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500

        cursor = connection.cursor()

        # Check if NationalID is unique
        cursor.execute("SELECT * FROM Candidates WHERE NationalID = %s", (data['NationalID'],))
        if cursor.fetchone():
            return jsonify({"error": "Candidate with this NationalID already exists"}), 400

        # Check if ElectionID exists
        cursor.execute("SELECT * FROM Elections WHERE ElectionID = %s", (data['ElectionID'],))
        if not cursor.fetchone():
            return jsonify({"error": "ElectionID does not exist"}), 400

        # Add candidate
        query = '''INSERT INTO Candidates (NationalID, CandidateName, PartyName, Biography, CandidateProgram, ElectionID)
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
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Database operation failed"}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500
    finally:
        if connection:
            connection.close()

# Function to add elections
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

# Function to add votes
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

# Function to add results
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
                query = '''INSERT INTO Results (CountVotes, CandidateID, ResultDate, ElectionID)
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

# Function to add admins
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

# Function to retrieve voters
@app.route('/voters', methods=['GET'])
def get_voters():
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Voters')
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

# Function to retrieve candidates
@app.route('/candidates', methods=['GET'])
def get_candidates():
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Candidates')
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

# Function to retrieve candidates by election ID
@app.route('/candidates/election/<int:election_id>', methods=['GET'])
def get_candidates_by_election(election_id):
    if election_id <= 0:
        return jsonify({"error": "Invalid ElectionID. It must be a positive integer."}), 400

    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Candidates WHERE ElectionID = %s', (election_id,))
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

# Function to retrieve elections
@app.route('/elections', methods=['GET'])
def get_elections():
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Elections')
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

# Function to retrieve votes
@app.route('/votes', methods=['GET'])
def get_votes():
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Votes')
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

# Function to retrieve results
@app.route('/results', methods=['GET'])
def get_results():
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Results')
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

# Function to retrieve admins
@app.route('/admin', methods=['GET'])
def get_admin():
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Admins')
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

# Function to delete a voter
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

# Function to update a voter
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

# Function to update a candidate
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
                UPDATE Candidates
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

# Function to delete a candidate
@app.route('/candidates/<int:candidate_id>', methods=['DELETE'])
def delete_candidate(candidate_id):
    if candidate_id <= 0:
        return jsonify({"error": "Invalid CandidateID. It must be a positive integer."}), 400

    with create_connection() as conn:
        try:
            cursor = conn.cursor()
            query = "DELETE FROM Candidates WHERE CandidateID = %s"
            cursor.execute(query, (candidate_id,))
            conn.commit()

            if cursor.rowcount == 0:
                return jsonify({"error": "Candidate not found"}), 404

            return jsonify({"message": "Candidate deleted successfully!"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

# Function to update an election
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

# Function to delete an election
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

# Function to update an admin
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
                UPDATE Admins
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

# Function to delete an admin
@app.route('/admin/<int:admin_id>', methods=['DELETE'])
def delete_admin(admin_id):
    if admin_id <= 0:
        return jsonify({"error": "Invalid admin_id. It must be a positive integer."}), 400

    with create_connection() as conn:
        try:
            cursor = conn.cursor()
            query = '''DELETE FROM Admins WHERE AdminID = %s'''
            cursor.execute(query, (admin_id,))
            conn.commit()

            if cursor.rowcount == 0:
                return jsonify({"error": "Admin not found"}), 404

            return jsonify({"message": "Admin deleted successfully!"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

# Function to retrieve election results sorted by vote count
@app.route('/election_results/<int:election_id>', methods=['GET'])
def get_election_results(election_id):
    if election_id <= 0:
        return jsonify({"error": "Invalid ElectionID. It must be a positive integer."}), 400

    with create_connection() as conn:
        try:
            cursor = conn.cursor()

            query = '''
                SELECT *
                FROM Candidates AS c
                INNER JOIN Results AS r ON c.CandidateID = r.CandidateID
                WHERE r.ElectionID = %s
            '''
            cursor.execute(query, (election_id,))

            results = cursor.fetchall()

            if not results:
                return jsonify({"error": "No results found"}), 404

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

# Function to update a vote
@app.route('/votes/<int:vote_id>', methods=['PUT'])
def update_vote(vote_id):
    if vote_id <= 0:
        return jsonify({"error": "Invalid voteID. It must be a positive integer."}), 400

    data = request.get_json()
    updatable_fields = ["ElectionDate", "CandidateID", "ElectionID"]
    missing_fields = [field for field in updatable_fields if field not in data or data[field] == ""]
    if missing_fields:
        return jsonify({"error": f"Missing or empty fields: {', '.join(missing_fields)}"}), 400

    with create_connection() as conn:
        try:
            cursor = conn.cursor()
            query = '''UPDATE Votes SET ElectionDate = %s, CandidateID = %s, ElectionID = %s
                    WHERE VoteID = %s'''
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

# Function to login
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
            cursor.execute("SELECT ElectionID FROM Votes WHERE VoterID = %s", (result[0],))
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

# Function to login as admin
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
            SELECT Privileges FROM Admins
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
        # 1. Check voter status
        cursor.execute("SELECT HasVoted FROM Voters WHERE VoterID = %s", (voter_id,))
        voter = cursor.fetchone()
        if not voter:
            return jsonify({"error": "Voter not found"}), 404

        if voter[0]:  # If the voter has already voted
            return jsonify({"error": "Voter has already voted"}), 400

        cursor.execute("""
            INSERT INTO Votes (VoterID, ElectionID, CandidateID, ElectionDate )
            VALUES (%s, %s, %s, %s)
        """, (voter_id, election_id, candidate_id, date))

        cursor.execute("""
            SELECT CountVotes FROM Results
            WHERE ElectionID = %s AND CandidateID = %s
        """, (election_id, candidate_id))
        result = cursor.fetchone()
        if result:
            cursor.execute("""
                UPDATE Results
                SET CountVotes = CountVotes + 1
                WHERE ElectionID = %s AND CandidateID = %s
            """, (election_id, candidate_id))
        else:
            cursor.execute("""
                INSERT INTO Results (ElectionID, CandidateID, CountVotes, ResultDate )
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

# Run the server
if __name__ == '__main__':
    create_tables()  # Create tables when the application starts
    app.run(debug=False, host='0.0.0.0')
