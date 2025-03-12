from fastapi import FastAPI, HTTPException, Depends, status, Response
from pydantic import BaseModel
import psycopg2
from psycopg2 import Error
import hashlib
from typing import List, Optional

app = FastAPI()

# Database connection function
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
          print("Database connection successful")
          return connection
      except Error as e:
          print(f"Error connecting to the database: {e}")
          raise HTTPException(status_code=500, detail="Failed to connect to the database")

# Password hashing function
def hash_password(password: str) -> str:
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

# Pydantic models
class Voter(BaseModel):
    NationalID: str
    VoterName: str
    State: str
    Email: str
    HasVoted: bool
    DateOfBirth: str
    Gender: str
    Password: str
    Phone: str

class Candidate(BaseModel):
    NationalID: str
    CandidateName: str
    PartyName: str
    Biography: str
    CandidateProgram: str
    ElectionID: int

class Election(BaseModel):
    ElectionDate: str
    ElectionType: str
    ElectionStatus: str

class Vote(BaseModel):
    VoterID: int
    ElectionDate: str
    CandidateID: int
    ElectionID: int

class Result(BaseModel):
    CountVotes: int
    CandidateID: int
    ResultDate: str
    ElectionID: int

class Admin(BaseModel):
    AdminName: str
    Email: str
    Password: str
    Privileges: str

# Function to add voters
@app.post("/voters", status_code=status.HTTP_201_CREATED)
def add_voter(voter: Voter):
    hashed_password = hash_password(voter.Password)

    with create_connection() as connection:
        if connection is not None:
            cursor = connection.cursor()
            try:
                query = '''INSERT INTO Voters (NationalID, VoterName, State, Email, HasVoted, DateOfBirth, Gender, Password, Phone)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'''
                cursor.execute(query, (
                    voter.NationalID, voter.VoterName, voter.State, voter.Email,
                    voter.HasVoted, voter.DateOfBirth, voter.Gender, hashed_password, voter.Phone
                ))
                connection.commit()
                return {"message": "Voter added successfully!"}
            except psycopg2.IntegrityError as e:
                raise HTTPException(status_code=400, detail="Duplicate entry or invalid data")
            except Exception as e:
                raise HTTPException(status_code=500, detail="Database operation failed")

# Function to add candidates
@app.post("/candidates", status_code=status.HTTP_201_CREATED)
def add_candidate(candidate: Candidate):
    with create_connection() as connection:
        if connection is None:
            raise HTTPException(status_code=500, detail="Failed to connect to the database")

        cursor = connection.cursor()

        try:
            # Check if NationalID is unique
            cursor.execute("SELECT * FROM Candidates WHERE NationalID = %s", (candidate.NationalID,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Candidate with this NationalID already exists")

            # Check if ElectionID exists
            cursor.execute("SELECT * FROM Elections WHERE ElectionID = %s", (candidate.ElectionID,))
            if not cursor.fetchone():
                raise HTTPException(status_code=400, detail="ElectionID does not exist")

            # Add candidate
            query = '''INSERT INTO Candidates (NationalID, CandidateName, PartyName, Biography, CandidateProgram, ElectionID)
                    VALUES (%s, %s, %s, %s, %s, %s)'''
            cursor.execute(query, (
                candidate.NationalID, candidate.CandidateName, candidate.PartyName,
                candidate.Biography, candidate.CandidateProgram, candidate.ElectionID
            ))
            connection.commit()
            return {"message": "Candidate added successfully!"}
        except psycopg2.IntegrityError as e:
            raise HTTPException(status_code=400, detail="Duplicate entry or invalid data")
        except psycopg2.Error as e:
            raise HTTPException(status_code=500, detail="Database operation failed")
        except Exception as e:
            raise HTTPException(status_code=500, detail="An unexpected error occurred")

# Function to add elections
@app.post("/elections", status_code=status.HTTP_201_CREATED)
def add_election(election: Election):
    with create_connection() as connection:
        if connection is not None:
            cursor = connection.cursor()
            try:
                query = '''INSERT INTO Elections (ElectionDate, ElectionType, ElectionStatus)
                        VALUES (%s, %s, %s)'''
                cursor.execute(query, (election.ElectionDate, election.ElectionType, election.ElectionStatus))
                connection.commit()
                return {"message": "Election added successfully!"}
            except psycopg2.IntegrityError as e:
                raise HTTPException(status_code=400, detail="Duplicate entry or invalid data")
            except Exception as e:
                raise HTTPException(status_code=500, detail="Database operation failed")

# Function to add votes
@app.post("/votes", status_code=status.HTTP_201_CREATED)
def add_vote(vote: Vote):
    with create_connection() as connection:
        if connection is not None:
            cursor = connection.cursor()
            try:
                query = '''INSERT INTO Votes (VoterID, ElectionDate, CandidateID, ElectionID)
                        VALUES (%s, %s, %s, %s)'''
                cursor.execute(query, (vote.VoterID, vote.ElectionDate, vote.CandidateID, vote.ElectionID))
                connection.commit()
                return {"message": "Vote added successfully!"}
            except psycopg2.IntegrityError as e:
                raise HTTPException(status_code=400, detail="Duplicate entry or invalid data")
            except Exception as e:
                raise HTTPException(status_code=500, detail="Database operation failed")

# Function to add results
@app.post("/results", status_code=status.HTTP_201_CREATED)
def add_result(result: Result):
    with create_connection() as connection:
        if connection is not None:
            cursor = connection.cursor()
            try:
                query = '''INSERT INTO Results (CountVotes, CandidateID, ResultDate, ElectionID)
                        VALUES (%s, %s, %s, %s)'''
                cursor.execute(query, (result.CountVotes, result.CandidateID, result.ResultDate, result.ElectionID))
                connection.commit()
                return {"message": "Result added successfully!"}
            except psycopg2.IntegrityError as e:
                raise HTTPException(status_code=400, detail="Duplicate entry or invalid data")
            except Exception as e:
                raise HTTPException(status_code=500, detail="Database operation failed")

# Function to add admins
@app.post("/admin", status_code=status.HTTP_201_CREATED)
def add_admin(admin: Admin):
    hashed_password = hash_password(admin.Password)

    with create_connection() as connection:
        if connection is not None:
            cursor = connection.cursor()
            try:
                query = '''INSERT INTO Admins (AdminName, Email, Password, Privileges)
                        VALUES (%s, %s, %s, %s)'''
                cursor.execute(query, (admin.AdminName, admin.Email, hashed_password, admin.Privileges))
                connection.commit()
                return {"message": "Admin added successfully!"}
            except psycopg2.IntegrityError as e:
                raise HTTPException(status_code=400, detail="Duplicate entry or invalid data")
            except Exception as e:
                raise HTTPException(status_code=500, detail="Database operation failed")

# Function to retrieve voters
@app.get("/voters", response_model=List[Voter])
def get_voters():
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Voters')
        rows = cursor.fetchall()

        if not rows:
            raise HTTPException(status_code=404, detail="No Voter found")

        voters = []
        for row in rows:
            voters.append({
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
        return voters

# Function to retrieve candidates
@app.get("/candidates", response_model=List[Candidate])
def get_candidates():
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Candidates')
        candidates = cursor.fetchall()

        if not candidates:
            raise HTTPException(status_code=404, detail="No candidates found")

        candidate_list = []
        for candidate in candidates:
            candidate_list.append({
                "NationalID": candidate[1],
                "CandidateName": candidate[2],
                "PartyName": candidate[3],
                "Biography": candidate[4],
                "CandidateProgram": candidate[5],
                "ElectionID": candidate[6]
            })
        return candidate_list

# Function to retrieve candidates by election ID
@app.get("/candidates/election/{election_id}", response_model=List[Candidate])
def get_candidates_by_election(election_id: int):
    if election_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid ElectionID. It must be a positive integer.")

    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Candidates WHERE ElectionID = %s', (election_id,))
        candidates = cursor.fetchall()

        if not candidates:
            raise HTTPException(status_code=404, detail="No candidates found for the given ElectionID")

        candidate_list = []
        for candidate in candidates:
            candidate_list.append({
                "NationalID": candidate[1],
                "CandidateName": candidate[2],
                "PartyName": candidate[3],
                "Biography": candidate[4],
                "CandidateProgram": candidate[5],
                "ElectionID": candidate[6]
            })
        return candidate_list

# Function to retrieve elections
@app.get("/elections", response_model=List[Election])
def get_elections():
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Elections')
        rows = cursor.fetchall()

        if not rows:
            raise HTTPException(status_code=404, detail="No election found")

        elections = []
        for row in rows:
            elections.append({
                "ElectionDate": row[1],
                "ElectionType": row[2],
                "ElectionStatus": row[3]
            })
        return elections

# Function to retrieve votes
@app.get("/votes", response_model=List[Vote])
def get_votes():
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Votes')
        rows = cursor.fetchall()

        if not rows:
            raise HTTPException(status_code=404, detail="No vote found")

        votes = []
        for row in rows:
            votes.append({
                "VoterID": row[1],
                "ElectionDate": row[2],
                "CandidateID": row[3],
                "ElectionID": row[4]
            })
        return votes

# Function to retrieve results
@app.get("/results", response_model=List[Result])
def get_results():
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Results')
        rows = cursor.fetchall()

        if not rows:
            raise HTTPException(status_code=404, detail="No result found")

        results = []
        for row in rows:
            results.append({
                "CountVotes": row[1],
                "CandidateID": row[2],
                "ResultDate": row[3],
                "ElectionID": row[4]
            })
        return results

# Function to retrieve admins
@app.get("/admin", response_model=List[Admin])
def get_admin():
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Admins')
        rows = cursor.fetchall()

        if not rows:
            raise HTTPException(status_code=404, detail="No admin found")

        admins = []
        for row in rows:
            admins.append({
                "AdminName": row[1],
                "Email": row[2],
                "Password": row[3],
                "Privileges": row[4]
            })
        return admins

# Function to delete a voter
@app.delete("/voters/{voter_id}")
def delete_voter(voter_id: int):
    if voter_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid voter_id. It must be a positive integer.")

    with create_connection() as conn:
        try:
            cursor = conn.cursor()
            query = '''DELETE FROM Voters WHERE VoterID = %s'''
            cursor.execute(query, (voter_id,))
            conn.commit()

            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Voter not found")

            return {"message": "Voter deleted successfully!"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

# Function to update a voter
@app.put("/voters/{voter_id}")
def update_voter(voter_id: int, voter: Voter):
    if voter_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid VoterID. It must be a positive integer.")

    hashed_password = hash_password(voter.Password)

    with create_connection() as conn:
        try:
            cursor = conn.cursor()
            query = '''
                UPDATE Voters SET NationalID = %s, VoterName = %s, State = %s, Email = %s,
                HasVoted = %s, DateOfBirth = %s, Gender = %s, Password = %s, Phone = %s
                WHERE VoterID = %s
            '''
            cursor.execute(query, (
                voter.NationalID, voter.VoterName, voter.State, voter.Email,
                voter.HasVoted, voter.DateOfBirth, voter.Gender, hashed_password,
                voter.Phone, voter_id
            ))
            conn.commit()

            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Voter not found or no changes made")

            return {"message": "Voter updated successfully!"}
        except psycopg2.IntegrityError:
            raise HTTPException(status_code=400, detail="Duplicate entry or invalid data")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

# Function to update a candidate
@app.put("/candidates/{candidate_id}")
def update_candidate(candidate_id: int, candidate: Candidate):
    if candidate_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid CandidateID. It must be a positive integer.")

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
                candidate.NationalID, candidate.CandidateName, candidate.PartyName, candidate.Biography,
                candidate.CandidateProgram, candidate.ElectionID, candidate_id
            ))
            conn.commit()

            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Candidate not found or no changes made")

            return {"message": "Candidate updated successfully!"}
        except psycopg2.IntegrityError:
            raise HTTPException(status_code=400, detail="Duplicate entry or invalid data")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

# Function to delete a candidate
@app.delete("/candidates/{candidate_id}")
def delete_candidate(candidate_id: int):
    if candidate_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid CandidateID. It must be a positive integer.")

    with create_connection() as conn:
        try:
            cursor = conn.cursor()
            query = "DELETE FROM Candidates WHERE CandidateID = %s"
            cursor.execute(query, (candidate_id,))
            conn.commit()

            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Candidate not found")

            return {"message": "Candidate deleted successfully!"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

# Function to update an election
@app.put("/elections/{election_id}")
def update_election(election_id: int, election: Election):
    if election_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid ElectionID. It must be a positive integer.")

    with create_connection() as conn:
        try:
            cursor = conn.cursor()
            query = '''
                UPDATE Elections
                SET ElectionDate = %s, ElectionType = %s, ElectionStatus = %s
                WHERE ElectionID = %s
            '''
            cursor.execute(query, (
                election.ElectionDate, election.ElectionType, election.ElectionStatus, election_id
            ))
            conn.commit()

            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Election not found or no changes made")

            return {"message": "Election updated successfully!"}
        except psycopg2.IntegrityError:
            raise HTTPException(status_code=400, detail="Duplicate entry or invalid data")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

# Function to delete an election
@app.delete("/elections/{election_id}")
def delete_election(election_id: int):
    if election_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid election_id. It must be a positive integer.")

    with create_connection() as conn:
        try:
            cursor = conn.cursor()
            query = '''DELETE FROM Elections WHERE ElectionID = %s'''
            cursor.execute(query, (election_id,))
            conn.commit()

            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Election not found")

            return {"message": "Election deleted successfully!"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

# Function to update an admin
@app.put("/admin/{admin_id}")
def update_admin(admin_id: int, admin: Admin):
    if admin_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid admin_id. It must be a positive integer.")

    hashed_password = hash_password(admin.Password) if len(admin.Password) < 50 else admin.Password

    with create_connection() as conn:
        try:
            cursor = conn.cursor()
            query = '''
                UPDATE Admins
                SET AdminName = %s, Email = %s, Password = %s, Privileges = %s
                WHERE AdminID = %s
            '''
            cursor.execute(query, (
                admin.AdminName, admin.Email, hashed_password, admin.Privileges, admin_id
            ))
            conn.commit()

            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Admin not found or no changes made")

            return {"message": "Admin updated successfully!"}
        except psycopg2.IntegrityError:
            raise HTTPException(status_code=400, detail="Duplicate entry or invalid data")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

# Function to delete an admin
@app.delete("/admin/{admin_id}")
def delete_admin(admin_id: int):
    if admin_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid admin_id. It must be a positive integer.")

    with create_connection() as conn:
        try:
            cursor = conn.cursor()
            query = '''DELETE FROM Admins WHERE AdminID = %s'''
            cursor.execute(query, (admin_id,))
            conn.commit()

            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Admin not found")

            return {"message": "Admin deleted successfully!"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

# Function to retrieve election results sorted by vote count
@app.get("/election_results/{election_id}")
def get_election_results(election_id: int):
    if election_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid ElectionID. It must be a positive integer.")

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
                raise HTTPException(status_code=404, detail="No results found")

            formatted_results = []
            for row in results:
                formatted_results.append({
                    "CandidateID": row[0],
                    "CandidateName": row[2],
                    "PartyName": row[3],
                    "CountVotes": row[8],
                    "ElectionID": row[6]
                })

            return formatted_results
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

# Function to update a vote
@app.put("/votes/{vote_id}")
def update_vote(vote_id: int, vote: Vote):
    if vote_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid voteID. It must be a positive integer.")

    with create_connection() as conn:
        try:
            cursor = conn.cursor()
            query = '''UPDATE Votes SET ElectionDate = %s, CandidateID = %s, ElectionID = %s
                    WHERE VoteID = %s'''
            cursor.execute(query, (
                vote.ElectionDate, vote.CandidateID, vote.ElectionID, vote_id
            ))

            conn.commit()

            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Vote not found or no changes made")

            return {"message": "Vote updated successfully!"}
        except psycopg2.IntegrityError:
            raise HTTPException(status_code=400, detail="Duplicate entry or invalid data")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

# Function to login
@app.post("/login")
def login(voter: VoterLogin):
    connection = create_connection()
    cursor = connection.cursor()

    try:
        hashed_password = hash_password(voter.password)

        cursor.execute('''
            SELECT VoterID, HasVoted FROM Voters
            WHERE NationalID = %s AND Password = %s
        ''', (voter.national_id, hashed_password))
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

            return {"message": "Login successful!", "voter_id": voter_id, "HasVoted": HasVoted, "election_id": election_id}
        else:
            raise HTTPException(status_code=401, detail="خطاء في الرقم الوطني او كلمة السر")

    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        connection.close()

@app.post("/login_admin")
def login_admin(admin: AdminLogin):
    connection = create_connection()
    cursor = connection.cursor()

    try:
        hashed_password = hash_password(admin.password)

        cursor.execute('''
            SELECT Privileges FROM Admins
            WHERE Email = %s AND Password = %s
        ''', (admin.Email, hashed_password))
        result = cursor.fetchone()

        if result:
            Privileges = result[0]
            return {"message": "Login successful!", "Privileges": Privileges}
        else:
            raise HTTPException(status_code=401, detail="خطاء في البريد الإلكتروني او كلمة السر")

    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        connection.close()

@app.post("/castVote")
def castVote(voter_id: int, election_id: int, candidate_id: int, date: str):
    connection = create_connection()
    cursor = connection.cursor()

    try:
        # 1. Check voter status
        cursor.execute("SELECT HasVoted FROM Voters WHERE VoterID = %s", (voter_id,))
        voter = cursor.fetchone()
        if not voter:
            raise HTTPException(status_code=404, detail="Voter not found")

        if voter[0]:  # If the voter has already voted
            raise HTTPException(status_code=400, detail="Voter has already voted")

        # 2. Insert the vote
        cursor.execute("""
            INSERT INTO Votes (VoterID, ElectionID, CandidateID, ElectionDate)
            VALUES (%s, %s, %s, %s)
        """, (voter_id, election_id, candidate_id, date))

        # 3. Update the vote count in Results
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
                INSERT INTO Results (ElectionID, CandidateID, CountVotes, ResultDate)
                VALUES (%s, %s, 1, %s)
            """, (election_id, candidate_id, date))

        # 4. Update the voter's status
        cursor.execute("""
            UPDATE Voters
            SET HasVoted = TRUE
            WHERE VoterID = %s
        """, (voter_id,))

        connection.commit()
        return {"message": "Vote recorded successfully"}
    except psycopg2.Error as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        connection.close()

# Run the server
if __name__ == '__main__':
    create_tables()  # Create tables when the application starts
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
