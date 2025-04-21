from flask import Flask, request, jsonify
import psycopg2
from psycopg2 import Error
import hashlib
from datetime import datetime 

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


# إنشاء تطبيق Flask
app = Flask(__name__)

# تعريف مسار الصفحة الرئيسية '/'
@app.route('/')
def index():
    """
    يقدم كود HTML/CSS/JS المدمج مباشرة كسلسلة نصية.
    """
    # استخدام ثلاث علامات اقتباس لإنشاء سلسلة نصية متعددة الأسطر
    html_content = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>نظام تقارير الانتخابات</title>
  <style>
    :root {
      --primary-color: #0056b3;
      --secondary-color: #6c757d;
      --light-bg: #f8f9fa;
      --white: #ffffff;
    }
    * {
      box-sizing: border-box;
    }
    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      margin: 0;
      padding: 1rem;
      background-color: var(--light-bg);
      direction: rtl;
      color: #343a40;
    }
    .main-header {
      display: none; /* Hidden by default, shown in print */
      text-align: center;
      margin-bottom: 2rem;
    }
    .main-header h2 {
      margin: 0;
      color: var(--primary-color);
    }
    .main-header p {
      margin: 0;
      font-size: 14px;
      color: var(--secondary-color);
    }
    .container {
      background-color: var(--white);
      padding: 1.5rem;
      border-radius: 8px;
      box-shadow: 0 0 10px rgba(0,0,0,0.05);
      margin-bottom: 2rem;
      max-width: 1000px;
      margin-left: auto;
      margin-right: auto;
    }
    h1, h2 {
      color: var(--primary-color);
      font-size: 1.4rem;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 1rem;
      font-size: 0.95rem;
      display: block; /* Use block + overflow for responsiveness */
      overflow-x: auto;
      white-space: nowrap;
    }
    th, td {
      border: 1px solid #dee2e6;
      padding: 0.75rem;
      text-align: right;
      min-width: 100px; /* Minimum width for cells */
    }
    th {
      background-color: var(--primary-color);
      color: var(--white);
    }
     table tbody tr:nth-child(even) {
      background-color: #f2f2f2;
    }
    button {
      margin: 0.5rem 0.25rem;
      padding: 0.6rem 1.2rem;
      font-size: 1rem;
      cursor: pointer;
      border: none;
      border-radius: 4px;
      transition: background-color 0.3s ease;
    }
    .btn-view { background-color: var(--secondary-color); color: var(--white); }
    .btn-view:hover { background-color: #5a6268; }
    .btn-primary { background-color: var(--primary-color); color: var(--white); }
    .btn-primary:hover { background-color: #004494; }

    .form-group {
        margin-bottom: 1rem;
        display: flex; /* Use flexbox for layout */
        align-items: center; /* Align items vertically */
        gap: 1rem; /* Space between items */
        flex-wrap: wrap; /* Allow wrapping on smaller screens */
    }
    .form-group label {
        /* display: inline-block; */
        margin-bottom: 0; /* Reset margin */
        font-weight: bold;
    }
     .form-group input[type="text"],
     .form-group input[type="number"],
    .form-group input[type="date"] {
        padding: 0.5rem;
        border: 1px solid #ced4da;
        border-radius: 4px;
        font-size: 1rem;
        /* margin-left: 0.5rem; */
        width: auto; /* Allow input to size based on content/flex */
        flex-grow: 1; /* Allow input to grow */
        min-width: 150px; /* Minimum width */
    }
     .form-group button {
         margin: 0; /* Reset margin */
         flex-shrink: 0; /* Prevent button from shrinking */
     }


    .tools-only {
      /* display: inline-block; */ /* Control visibility for tools on main page */
    }
     .report-tools { /* New class for buttons in new window */
         margin-top: 2rem;
         text-align: center;
     }
     .report-tools button {
         margin: 0.5rem;
     }
     .btn-back { background-color: #dc3545; color: white; }
     .btn-print { background-color: #28a745; color: white; }
     .btn-email { background-color: #007bff; color: white; }
     .btn-main { background-color: #0056b3; color: white; }

     #errorMessage {
         color: red;
         margin-top: 1rem;
         font-weight: bold;
     }
      #loadingMessage {
          color: var(--primary-color);
          margin-top: 1rem;
          font-weight: bold;
          display: none; /* Hidden by default */
      }


    /* Print Styles */
    @media print {
      .main-header { display: block !important; }
      .tools-only, .report-tools, .form-selection, #election-selector, #errorMessage, #loadingMessage { display: none !important; } /* Hide UI elements */
      .container { box-shadow: none; border: none; padding: 0; margin-bottom: 1rem; } /* Adjust layout for print */
      body {
        background-color: white !important;
        color: black !important;
        font-size: 12pt; /* Adjust font size for print */
        padding: 0.5rem;
      }
      table {
        display: table !important; /* Revert table display for print */
        overflow-x: visible !important;
        white-space: normal !important;
        width: 100%; /* Ensure table takes full width */
        page-break-inside: auto; /* Allow tables to break across pages */
      }
       table thead {
           display: table-header-group; /* Repeat table headers on each page */
       }
       table tr {
           page-break-inside: avoid; /* Avoid breaking rows */
           page-break-after: auto;
       }
      th, td {
        min-width: auto !important; /* Remove minimum width in print */
         padding: 0.5rem;
      }
       h1, h2 {
           color: #000 !important; /* Black color for headings in print */
       }
       ul li {
           margin-bottom: 0.3rem;
       }
    }
    /* Responsive Styles */
    @media (max-width: 768px) {
      body {
        padding: 0.5rem;
      }
      .container {
        padding: 1rem;
      }
       .form-group {
           flex-direction: column; /* Stack form elements vertically */
           align-items: stretch; /* Stretch items to full width */
           gap: 0.5rem; /* Adjust gap */
       }
        .form-group label {
           margin-bottom: 0.2rem; /* Add space below label */
       }
       .form-group input[type="text"],
       .form-group input[type="number"],
       .form-group input[type="date"] {
            min-width: auto; /* Allow shrinking */
            width: 100%; /* Full width */
            flex-grow: 0; /* Prevent growing */
       }
       .form-group button {
           width: 100%; /* Full width button */
           margin: 0.5rem 0 0 0; /* Adjust margin */
       }

      table {
        /* Properties already set for responsiveness */
      }
      table th, table td {
        font-size: 0.85rem;
        padding: 0.5rem;
        /* min-width: 120px; */ /* Adjusted min-width */
      }
      h1, h2 {
        font-size: 1.2rem;
      }
       .report-tools button {
           display: block;
           width: 100%;
           margin: 0.5rem 0;
       }
    }
  </style>
</head>
<body>
<div class="main-header" id="printHeader">
  <h2>نظام تقارير الانتخابات</h2>
  <p>المفوضية القومية للانتخابات - السودان</p>
</div>

<div class="container" id="election-selector">
  <h1>تحديد الانتخابات</h1>
  <div class="form-group">
    <label for="electionIdInput">معرف الانتخابات (Election ID):</label>
    <input type="number" id="electionIdInput" value="1" min="1" placeholder="أدخل معرف الانتخابات">
    <button class="btn-primary" onclick="fetchElectionData()">جلب البيانات</button>
  </div>
  <p id="loadingMessage">جارٍ جلب البيانات...</p>
  <p id="errorMessage"></p>
</div>


<div class="container" id="report-general">
  <h1>تقرير عام عن الانتخابات</h1>
  <ul id="election-details-list">
    <li>الرجاء جلب بيانات الانتخابات أولاً.</li>
    </ul>
  <div class="print-footer"><p>التاريخ: <span class="printDate"></span></p></div>
  <button class="btn-view tools-only" onclick="openReportWindow('report-general')">عرض في صفحة جديدة</button>
</div>

<div class="container" id="report-turnout">
  <h1>تقرير إقبال الناخبين</h1>
  <ul id="turnout-details-list">
     <li>الرجاء جلب بيانات الانتخابات أولاً.</li>
    </ul>
  <div class="print-footer"><p>التاريخ: <span class="printDate"></span></p></div>
  <button class="btn-view tools-only" onclick="openReportWindow('report-turnout')">عرض في صفحة جديدة</button>
</div>

<div class="container" id="report-voter-timeframe">
  <h1>تقرير عدد المصوتين في فترة زمنية محددة</h1>
  <div class="tools-only form-selection">
      <div class="form-group">
          <label for="startDate">من تاريخ:</label>
          <input type="date" id="startDate">
      </div>
      <div class="form-group">
          <label for="endDate">إلى تاريخ:</label>
          <input type="date" id="endDate">
      </div>
      <button class="btn-primary" onclick="generateVoterTimeframeReport()">عرض التقرير</button>
  </div>

  <div id="voterTimeframeResults">
      <h2>النتائج للفترة المحددة</h2>
      <table id="voterTimeframeTable">
          <thead>
              <tr>
                  <th>بداية الفترة</th>
                  <th>نهاية الفترة</th>
                  <th>عدد المصوتين</th>
              </tr>
          </thead>
          <tbody>
               <tr>
                  <td id="displayStartDate"></td>
                  <td id="displayEndDate"></td>
                  <td id="displayVoterCount"></td>
              </tr>
              </tbody>
      </table>
       <p id="noDataMessage" style="display: none; color: #dc3545;">لا توجد بيانات متاحة لهذه الفترة.</p>
  </div>

  <div class="print-footer"><p>التاريخ: <span class="printDate"></span></p></div>
  <button class="btn-view tools-only" onclick="openReportWindow('report-voter-timeframe')">عرض في صفحة جديدة</button>
</div>


<div class="container" id="report-results">
  <h1>نتائج المرشحين</h1>
  <table id="results-table">
    <thead><tr><th>المرشح</th><th>الحزب</th><th>الأصوات</th><th>النسبة</th></tr></thead>
    <tbody>
      </tbody>
  </table>
  <div class="print-footer"><p>التاريخ: <span class="printDate"></span></p></div>
  <button class="btn-view tools-only" onclick="openReportWindow('report-results')">عرض في صفحة جديدة</button>
</div>

<div class="container" id="report-demographics">
  <h1>البيانات الديموغرافية</h1>
  <h2>حسب الجنس</h2>
  <table id="gender-demographics-table">
    <thead><tr><th>الجنس</th><th>العدد</th><th>النسبة</th></tr></thead>
    <tbody>
      </tbody>
  </table>
  <h2>حسب الولاية</h2>
  <table id="state-demographics-table">
    <thead><tr><th>الولاية</th><th>العدد</th><th>النسبة</th></tr></thead>
    <tbody>
      </tbody>
  </table>
  <div class="print-footer"><p>التاريخ: <span class="printDate"></span></p></div>
  <button class="btn-view tools-only" onclick="openReportWindow('report-demographics')">عرض في صفحة جديدة</button>
</div>

<script>
  // Global variable to store fetched election data
  let electionData = null;
  const loadingMessageEl = document.getElementById('loadingMessage');
  const errorMessageEl = document.getElementById('errorMessage');

  document.querySelectorAll('.printDate').forEach(el => {
    el.textContent = new Date().toLocaleDateString('ar-EG');
  });

  // Function to clear existing report data
  function clearAllReports() {
      // Clear lists
      document.getElementById('election-details-list').innerHTML = '<li>الرجاء جلب بيانات الانتخابات أولاً.</li>';
      document.getElementById('turnout-details-list').innerHTML = '<li>الرجاء جلب بيانات الانتخابات أولاً.</li>';

      // Clear tables
      document.querySelector('#results-table tbody').innerHTML = '';
      document.querySelector('#gender-demographics-table tbody').innerHTML = '';
      document.querySelector('#state-demographics-table tbody').innerHTML = '';

      // Clear and hide timeframe report results
      document.getElementById('displayStartDate').textContent = '';
      document.getElementById('displayEndDate').textContent = '';
      document.getElementById('displayVoterCount').textContent = '';
      document.getElementById('voterTimeframeTable').style.display = 'none';
      document.getElementById('noDataMessage').style.display = 'none';
       document.getElementById('startDate').value = ''; // Clear date inputs
       document.getElementById('endDate').value = '';
  }

   // Function to format numbers
  function formatNumber(num) {
      if (num === undefined || num === null) return '';
      return num.toLocaleString('ar-EG');
  }

  // Function to calculate and format percentage
  function formatPercentage(part, total) {
      if (total === 0 || total === undefined || total === null || part === undefined || part === null) return '0%';
      return ((part / total) * 100).toFixed(2) + '%';
  }

  // Functions to render specific report sections
  function renderElectionDetails(election) {
      const ul = document.getElementById('election-details-list');
      ul.innerHTML = `
          <li><strong>معرف الانتخابات:</strong> ${election.ElectionID}</li>
          <li><strong>نوع الانتخابات:</strong> ${election.ElectionType}</li>
          <li><strong>تاريخ الانتخابات:</strong> ${election.ElectionDate}</li>
          <li><strong>الحالة:</strong> ${election.ElectionStatus}</li>
      `;
  }

  function renderTurnout(turnout) {
      const ul = document.getElementById('turnout-details-list');
      ul.innerHTML = `
          <li><strong>عدد الناخبين المسجلين:</strong> ${formatNumber(turnout.TotalRegisteredVoters)}</li>
          <li><strong>عدد المصوتين:</strong> ${formatNumber(turnout.VotersVoted)}</li>
          <li><strong>نسبة الإقبال:</strong> ${formatPercentage(turnout.VotersVoted, turnout.TotalRegisteredVoters)}</li>
      `;
  }

  function renderResults(results, totalVotes) {
      const tbody = document.querySelector('#results-table tbody');
      tbody.innerHTML = ''; // Clear existing rows

      if (!results || results.length === 0) {
          tbody.innerHTML = '<tr><td colspan="4" style="text-align: center;">لا توجد نتائج متاحة.</td></tr>';
          return;
      }

      results.forEach(candidate => {
          const row = tbody.insertRow();
          row.innerHTML = `
              <td>${candidate.CandidateName}</td>
              <td>${candidate.PartyName || 'مستقل'}</td>
              <td>${formatNumber(candidate.VoteCount)}</td>
              <td>${formatPercentage(candidate.VoteCount, totalVotes)}</td>
          `;
      });
  }

  function renderDemographics(demographics, totalVoters) {
      // Gender
      const genderTbody = document.querySelector('#gender-demographics-table tbody');
      genderTbody.innerHTML = ''; // Clear existing rows

      if (!demographics || !demographics.GenderDistribution || Object.keys(demographics.GenderDistribution).length === 0) {
           genderTbody.innerHTML = '<tr><td colspan="3" style="text-align: center;">لا توجد بيانات ديموغرافية (الجنس) متاحة.</td></tr>';
      } else {
           for (const gender in demographics.GenderDistribution) {
               const count = demographics.GenderDistribution[gender];
               const row = genderTbody.insertRow();
               row.innerHTML = `
                   <td>${gender || 'غير محدد'}</td>
                   <td>${formatNumber(count)}</td>
                   <td>${formatPercentage(count, totalVoters)}</td>
               `;
           }
      }


      // State
      const stateTbody = document.querySelector('#state-demographics-table tbody');
      stateTbody.innerHTML = ''; // Clear existing rows

       if (!demographics || !demographics.StateDistribution || Object.keys(demographics.StateDistribution).length === 0) {
           stateTbody.innerHTML = '<tr><td colspan="3" style="text-align: center;">لا توجد بيانات ديموغرافية (الولاية) متاحة.</td></tr>';
       } else {
           for (const state in demographics.StateDistribution) {
               const count = demographics.StateDistribution[state];
               const row = stateTbody.insertRow();
               row.innerHTML = `
                   <td>${state || 'غير محدد'}</td>
                   <td>${formatNumber(count)}</td>
                   <td>${formatPercentage(count, totalVoters)}</td>
               `;
           }
       }
  }

  // Main function to fetch data
  async function fetchElectionData() {
      const electionId = document.getElementById('electionIdInput').value;
      errorMessageEl.style.display = 'none'; // Hide previous errors
      loadingMessageEl.style.display = 'none'; // Hide loading initially

      if (!electionId || parseInt(electionId) <= 0) {
          errorMessageEl.textContent = "الرجاء إدخال معرف انتخابات صحيح.";
          errorMessageEl.style.display = 'block';
          clearAllReports(); // Clear old data if input is invalid
          return;
      }

      loadingMessageEl.style.display = 'block'; // Show loading message
      clearAllReports(); // Clear reports while loading

      try {
          const response = await fetch(`https://election-sd.onrender.com/election_reports/${electionId}`);

          if (!response.ok) {
              const errorJson = await response.json();
              const errorMsg = errorJson.error || `حدث خطأ غير معروف (Status: ${response.status})`;
              errorMessageEl.textContent = `خطأ في جلب البيانات: ${errorMsg}`;
              errorMessageEl.style.display = 'block';
              electionData = null; // Clear old data on error
              // Reports are already cleared by clearAllReports()
              return;
          }

          electionData = await response.json();
          console.log("Data fetched successfully:", electionData);

          // Calculate total votes for percentage calculation in results
          const totalVotes = electionData.Turnout ? electionData.Turnout.VotersVoted : 0;
           const totalRegisteredVoters = electionData.Turnout ? electionData.Turnout.TotalRegisteredVoters : 0;

          // Render the data into the respective sections
          if (electionData.Election) renderElectionDetails(electionData.Election);
          if (electionData.Turnout) renderTurnout(electionData.Turnout);
          if (electionData.Results) renderResults(electionData.Results, totalVotes);
          if (electionData.Demographics) renderDemographics(electionData.Demographics, totalRegisteredVoters);

          // Note: VoteTimeData from API includes last day/week/month counts,
          // but the HTML report asks for a custom timeframe.
          // We store electionData.Votes (the raw list) for the timeframe report function.

          // Reset timeframe report display after new data is loaded
          resetTimeframeReportDisplay();


      } catch (error) {
          console.error("Fetch error:", error);
          errorMessageEl.textContent = "فشل في الاتصال بالخادم أو معالجة البيانات.";
          errorMessageEl.style.display = 'block';
          electionData = null; // Clear old data on error
          // Reports are already cleared by clearAllReports()
      } finally {
           loadingMessageEl.style.display = 'none'; // Hide loading message
      }
  }

  // Function to generate the timeframe report using fetched data
  function generateVoterTimeframeReport() {
      if (!electionData || !electionData.Votes) {
          alert("الرجاء جلب بيانات الانتخابات أولاً.");
          return;
      }

      const startDateInput = document.getElementById('startDate').value;
      const endDateInput = document.getElementById('endDate').value;

      const displayStartDateEl = document.getElementById('displayStartDate');
      const displayEndDateEl = document.getElementById('displayEndDate');
      const displayVoterCountEl = document.getElementById('displayVoterCount');
      const noDataMessageEl = document.getElementById('noDataMessage');
      const resultsTable = document.getElementById('voterTimeframeTable');

       // Hide previous results/messages
      resultsTable.style.display = 'none';
      noDataMessageEl.style.display = 'none';
       displayVoterCountEl.textContent = '';


      if (!startDateInput || !endDateInput) {
          alert("الرجاء تحديد تاريخ بداية ونهاية الفترة.");
          return;
      }

      const startDate = new Date(startDateInput + 'T00:00:00'); // Include time to ensure correct date interpretation
      const endDate = new Date(endDateInput + 'T23:59:59.999'); // Include time to include the whole end day


      if (startDate > endDate) {
          alert("تاريخ البداية يجب أن يكون قبل أو يساوي تاريخ النهاية.");
          return;
      }

      // Filter votes based on date
      const votesInTimeframe = electionData.Votes.filter(vote => {
          // Assuming vote.ElectionDate is 'YYYY-MM-DD' string
          const voteDate = new Date(vote.ElectionDate + 'T00:00:00'); // Parse vote date

          return voteDate >= startDate && voteDate <= endDate;
      });

      const voterCount = votesInTimeframe.length;

      displayStartDateEl.textContent = startDateInput; // Display selected input dates
      displayEndDateEl.textContent = endDateInput;

      if (voterCount > 0) {
          displayVoterCountEl.textContent = formatNumber(voterCount);
          resultsTable.style.display = 'table'; // Show table
          noDataMessageEl.style.display = 'none'; // Hide no data message
      } else {
          displayVoterCountEl.textContent = ''; // Clear count
          resultsTable.style.display = 'none'; // Hide table
          noDataMessageEl.style.display = 'block'; // Show no data message
      }

       // Log filtered votes for debugging if needed
      // console.log("Votes in timeframe:", votesInTimeframe);
  }

  // Function to reset the display of the timeframe report section
  function resetTimeframeReportDisplay() {
       document.getElementById('startDate').value = '';
       document.getElementById('endDate').value = '';
       document.getElementById('displayStartDate').textContent = '';
       document.getElementById('displayEndDate').textContent = '';
       document.getElementById('displayVoterCount').textContent = '';
       document.getElementById('voterTimeframeTable').style.display = 'none';
       document.getElementById('noDataMessage').style.display = 'none';
  }


  function openReportWindow(reportId) {
    const content = document.getElementById(reportId).cloneNode(true);

    // Specific handling for timeframe report when opening in new window
    if (reportId === 'report-voter-timeframe') {
       // Remove the form inputs and button
       const formSection = content.querySelector('.form-selection');
       if(formSection) formSection.remove();

        // Ensure the results section is visible if it has content
        const resultsDiv = content.querySelector('#voterTimeframeResults');
        if(resultsDiv) {
            resultsDiv.style.display = 'block'; // Make results visible
            // Check if the table is hidden (meaning no data was found for the selected period)
            const timeframeTable = resultsDiv.querySelector('#voterTimeframeTable');
             const noDataMessage = resultsDiv.querySelector('#noDataMessage');
             if (timeframeTable && timeframeTable.style.display === 'none') {
                 // If table is hidden on main page, show the "no data" message in the new window
                 if (noDataMessage) noDataMessage.style.display = 'block';
             } else {
                 // If table was visible (had data), ensure no data message is hidden
                 if (noDataMessage) noDataMessage.style.display = 'none';
             }
        }
    } else {
        // For other reports, just ensure tools-only buttons are removed
         content.querySelectorAll('.tools-only').forEach(el => el.remove());
    }

     // Ensure the print date is correctly set in the cloned content
     content.querySelectorAll('.printDate').forEach(el => {
         el.textContent = new Date().toLocaleDateString('ar-EG');
     });


    const header = document.getElementById('printHeader').innerHTML;
    const win = window.open('', '_blank', 'width=1000,height=800');
    win.document.write(`
      <html lang="ar" dir="rtl">
      <head>
        <meta charset="UTF-8">
        <title>عرض التقرير</title>
        <style>
          body { font-family: 'Segoe UI', Tahoma; padding: 2rem; direction: rtl; background: white; color: #343a40; line-height: 1.6; }
          .main-header { text-align: center; margin-bottom: 2rem; border-bottom: 2px solid #0056b3; padding-bottom: 1rem; }
          .main-header h2 { color: #0056b3; margin: 0; }
          .main-header p { font-size: 14px; color: #6c757d; margin: 0; }
          h1, h2 { color: #0056b3; font-size: 1.3rem; margin-top: 1.5rem; margin-bottom: 0.8rem;}
           h2 { font-size: 1.2rem; }
          ul { list-style: none; padding: 0; margin-bottom: 1.5rem;}
          ul li { margin-bottom: 0.5rem; }
          table { width: 100%; border-collapse: collapse; margin-top: 1rem; margin-bottom: 1.5rem; font-size: 0.95rem;}
          th, td { border: 1px solid #dee2e6; padding: 0.75rem; text-align: right; }
          th { background-color: #0056b3; color: white; }
           table tbody tr:nth-child(even) { background-color: #f2f2f2; }

          .print-footer { margin-top: 3rem; padding-top: 1rem; border-top: 1px dashed #999; font-size: 14px; color: #333; }
          .report-tools { /* Buttons in new window */
              margin-top: 2rem;
              text-align: center;
          }
          .report-tools button {
              margin: 0.5rem; padding: 0.5rem 1rem; font-size: 1rem; border: none; border-radius: 4px; cursor: pointer;
          }
          .btn-back { background-color: #dc3545; color: white; }
          .btn-print { background-color: #28a745; color: white; }
          .btn-email { background-color: #007bff; color: white; }
          .btn-main { background-color: #0056b3; color: white; }

          #noDataMessage { color: #dc3545; font-weight: bold; margin-top: 1rem; }

          @media print  {
             .report-tools { display: none !important; } /* Hide tools in print view */
             body { padding: 0.5rem; font-size: 12pt; }
             table { display: table !important; width: 100%; }
             th, td { padding: 0.5rem; }
             .container { box-shadow: none; border: none; padding: 0; margin-bottom: 1rem; }
              .main-header { display: block !important; }
               table thead { display: table-header-group; }
               table tr { page-break-inside: avoid; page-break-after: auto; }
          }
           @media (max-width: 768px) {
               body { padding: 0.5rem; }
               table { font-size: 0.85rem; }
               th, td { padding: 0.5rem; }
               .report-tools button { display: block; width: 100%; margin: 0.5rem 0; }
           }

        </style></head>
  <body>
    <div class="main-header">${header}</div>
    <div class="report-content">${content.innerHTML}</div> <div class="report-tools">
      <button class="btn-main" onclick="window.close();">إغلاق النافذة</button>
      <button class="btn-print" onclick="window.print()">طباعة</button>
      <button type="button" class="btn-email" onclick="sendByEmailWindow('${reportId}')">إرسال عبر الإيميل</button>
    </div>
    <script>
      // Ensure print dates are set in the new window
      window.addEventListener('load', () => {
          document.querySelectorAll('.printDate').forEach(el => {
              el.textContent = new Date().toLocaleDateString('ar-EG');
          });

          // In the new window, ensure table display is correct after load
           const timeframeTable = document.getElementById('voterTimeframeTable');
           if (timeframeTable) {
               // If the table had content when cloned, ensure it's 'table'
               if (timeframeTable.querySelector('tbody').children.length > 0 && timeframeTable.querySelector('tbody').children[0].cells.length > 1) {
                    timeframeTable.style.display = 'table';
                     const noDataMessage = document.getElementById('noDataMessage');
                     if(noDataMessage) noDataMessage.style.display = 'none';
               } else {
                    // If the table was empty or hidden when cloned, show the no data message if present
                     timeframeTable.style.display = 'none';
                     const noDataMessage = document.getElementById('noDataMessage');
                     if(noDataMessage) noDataMessage.style.display = 'block';
               }
           }

      });


      function sendByEmailWindow(reportId) {
        // This is a basic implementation, might not work well with complex HTML
        const reportElement = document.getElementById(reportId);
        let reportContent = 'تقرير الانتخابات\\n\\n';

        // Try to extract text content reasonably
        if (reportElement) {
             // Simple text extraction - loses formatting
             // reportContent += reportElement.innerText;

             // More structured extraction based on report ID
             if (reportId === 'report-general') {
                 reportContent += 'تقرير عام عن الانتخابات\\n\\n';
                 const listItems = reportElement.querySelectorAll('ul li');
                 listItems.forEach(item => {
                     reportContent += item.textContent.trim() + '\\n';
                 });

             } else if (reportId === 'report-turnout') {
                  reportContent += 'تقرير إقبال الناخبين\\n\\n';
                 const listItems = reportElement.querySelectorAll('ul li');
                 listItems.forEach(item => {
                     reportContent += item.textContent.trim() + '\\n';
                 });

             } else if (reportId === 'report-results') {
                  reportContent += 'نتائج المرشحين\\n\\n';
                  const rows = reportElement.querySelectorAll('table tbody tr');
                  if (rows.length > 0 && rows[0].cells.length > 1) { // Check if there's actual data
                      reportContent += 'المرشح | الحزب | الأصوات | النسبة\\n';
                      reportContent += '------|-------|--------|-------\\n';
                      rows.forEach(row => {
                          const cells = row.querySelectorAll('td');
                          if (cells.length === 4) {
                              reportContent += \`\${cells[0].textContent.trim()} | \${cells[1].textContent.trim()} | \${cells[2].textContent.trim()} | \${cells[3].textContent.trim()}\\n\`;
                          } else {
                             reportContent += row.textContent.trim() + '\\n'; // Handle 'no data' row
                          }
                      });
                  } else {
                      reportContent += 'لا توجد نتائج متاحة.\\n';
                  }


             } else if (reportId === 'report-demographics') {
                  reportContent += 'البيانات الديموغرافية\\n\\n';
                  reportContent += 'حسب الجنس:\\n';
                  const genderRows = reportElement.querySelectorAll('#gender-demographics-table tbody tr');
                   if (genderRows.length > 0 && genderRows[0].cells.length > 1) {
                       reportContent += 'الجنس | العدد | النسبة\\n';
                       reportContent += '------|-------|-------|\\n';
                       genderRows.forEach(row => {
                           const cells = row.querySelectorAll('td');
                           if (cells.length === 3) {
                              reportContent += \`\${cells[0].textContent.trim()} | \${cells[1].textContent.trim()} | \${cells[2].textContent.trim()}\\n\`;
                           } else {
                               reportContent += row.textContent.trim() + '\\n'; // Handle 'no data' row
                           }
                       });
                   } else {
                        reportContent += 'لا توجد بيانات (الجنس).\\n';
                   }


                  reportContent += '\\nحسب الولاية:\\n';
                   const stateRows = reportElement.querySelectorAll('#state-demographics-table tbody tr');
                   if (stateRows.length > 0 && stateRows[0].cells.length > 1) {
                       reportContent += 'الولاية | العدد | النسبة\\n';
                       reportContent += '--------|-------|-------|\\n';
                       stateRows.forEach(row => {
                           const cells = row.querySelectorAll('td');
                            if (cells.length === 3) {
                              reportContent += \`\${cells[0].textContent.trim()} | \${cells[1].textContent.trim()} | \${cells[2].textContent.trim()}\\n\`;
                           } else {
                               reportContent += row.textContent.trim() + '\\n'; // Handle 'no data' row
                           }
                       });
                    } else {
                         reportContent += 'لا توجد بيانات (الولاية).\\n';
                    }


             } else if (reportId === 'report-voter-timeframe') {
                 reportContent += 'تقرير عدد المصوتين في فترة زمنية محددة:\\n\\n';
                 const startDate = document.getElementById('displayStartDate')?.innerText || 'غير محدد';
                 const endDate = document.getElementById('displayEndDate')?.innerText || 'غير محدد';
                 const voterCount = document.getElementById('displayVoterCount')?.innerText || '';
                 const noData = document.getElementById('noDataMessage')?.innerText || '';

                 reportContent += \`من تاريخ: \${startDate}\\nإلى تاريخ: \${endDate}\\n\\n\`;

                 if (voterCount) {
                     reportContent += \`عدد المصوتين: \${voterCount}\\n\`;
                 } else if (noData && noData !== 'لا توجد بيانات متاحة لهذه الفترة.') { // Avoid duplicating default message
                      reportContent += \`\${noData}\\n\`;
                 } else if (noData === 'لا توجد بيانات متاحة لهذه الفترة.') {
                     reportContent += 'لا توجد بيانات متاحة لهذه الفترة.\\n';
                 } else {
                      reportContent += 'الرجاء تحديد فترة وعرض التقرير أولاً.\\n';
                 }

             } else {
                  // Fallback for any other case - just get the text content
                  reportContent += reportElement.innerText;
             }
        }


        // Encode the content for mailto link
        const body = encodeURIComponent(reportContent);
        // Use window.location.href to open the default email client
        window.location.href = 'mailto:?subject=' + encodeURIComponent('تقرير الانتخابات (' + (document.querySelector('#report-general li:first-child')?.textContent || 'غير محدد') + ')') + '&body=' + body;
      }
    <\/script>
  </body>
  </html>
`);
win.document.close();

}

  // Initial state: Clear reports on page load
  window.addEventListener('load', () => {
       clearAllReports();
  });


</script>

</body>
</html>

"""
    # إرجاع السلسلة النصية. Flask سيعرف أنها HTML.
    return html_content



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
        cursor.execute('SELECT * FROM Candidates ORDER BY CandidateName ASC')
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
        cursor.execute('SELECT * FROM Candidates WHERE ElectionID = %s ORDER BY CandidateName ASC', (election_id,))
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
        return jsonify({"error": "معرّف الانتخابات غير صالح"}), 400

    conn = create_connection()
    if not conn:
        return jsonify({"error": "تعذر الاتصال بالخادم"}), 500

    try:
        with conn.cursor() as cursor:
            # 1. التحقق من وجود الانتخابات
            cursor.execute("SELECT ElectionID FROM Elections WHERE ElectionID = %s", (election_id,))
            if not cursor.fetchone():
                return jsonify({"error": "الانتخابات غير موجودة"}), 404

            # 2. جلب النتائج مع التحقق من ارتباط المرشح بالانتخابات
            query = """
                SELECT 
                    c.CandidateID,
                    c.CandidateName,
                    c.PartyName,
                    r.CountVotes,
                    r.ElectionID
                FROM Results r
                INNER JOIN Candidates c 
                    ON r.CandidateID = c.CandidateID 
                    AND c.ElectionID = %s  -- <-- الشرط الجديد
                WHERE r.ElectionID = %s
                ORDER BY r.CountVotes DESC
            """
            cursor.execute(query, (election_id, election_id))
            results = cursor.fetchall()

            if not results:
                return jsonify({"message": "لا توجد نتائج متاحة لهذه الانتخابات"}), 200

            # تحويل النتائج إلى تنسيق JSON
            formatted_results = [
                {
                    "CandidateID": row[0],
                    "CandidateName": row[1],
                    "PartyName": row[2],
                    "CountVotes": row[3],
                    "ElectionID": row[4]
                }
                for row in results
            ]

            return jsonify(formatted_results), 200

    except psycopg2.DatabaseError as e:
        app.logger.error(f"خطأ قاعدة البيانات: {str(e)}")
        return jsonify({"error": "خطأ في معالجة البيانات"}), 500
    except Exception as e:
        app.logger.error(f"خطأ غير متوقع: {str(e)}")
        return jsonify({"error": "خطأ داخلي"}), 500
    finally:
        if conn:
            conn.close()
            
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
            return jsonify({"error": "لقد صوت الناخب بالفعل"}), 400

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
        return jsonify({"message": "تم تسجيل تصويتك بنجاح."}), 200

    except psycopg2.Error as e:
        connection.rollback()
        print(f"Database error: {e}")  # Log the error
        return jsonify({"error": str(e)}), 500

    finally:
        connection.close()
        
@app.route('/election_reports/<int:election_id>', methods=['GET'])
def get_election_reports(election_id):
    """
    Retrieve all data needed for election reports including:
    - Election details
    - Voter turnout statistics
    - Election results
    - Candidates list
    - Voter demographics
    - Vote counts by time period
    """
    if election_id <= 0:
        return jsonify({"error": "Invalid ElectionID"}), 400

    conn = create_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        with conn.cursor() as cursor:
            # 1. Get election details
            cursor.execute("SELECT * FROM Elections WHERE ElectionID = %s", (election_id,))
            election = cursor.fetchone()
            if not election:
                return jsonify({"error": "Election not found"}), 404

            election_data = {
                "ElectionID": election[0],
                "ElectionDate": election[1],
                "ElectionType": election[2],
                "ElectionStatus": election[3]
            }

            # 2. Get voter turnout statistics
            # Total registered voters
            cursor.execute("SELECT COUNT(*) FROM Voters")
            total_voters = cursor.fetchone()[0]

            # Voters who voted in this election
            cursor.execute("""
                SELECT COUNT(DISTINCT VoterID) 
                FROM Votes 
                WHERE ElectionID = %s
            """, (election_id,))
            voters_voted = cursor.fetchone()[0]

            turnout_percentage = 0
            if total_voters > 0:
                turnout_percentage = round((voters_voted / total_voters) * 100, 2)

            turnout_data = {
                "TotalRegisteredVoters": total_voters,
                "VotersVoted": voters_voted,
                "TurnoutPercentage": turnout_percentage
            }

            # 3. Get election results
            cursor.execute("""
                SELECT c.CandidateID, c.CandidateName, c.PartyName, 
                       COALESCE(r.CountVotes, 0) as VoteCount
                FROM Candidates c
                LEFT JOIN Results r ON c.CandidateID = r.CandidateID AND r.ElectionID = %s
                WHERE c.ElectionID = %s
                ORDER BY VoteCount DESC
            """, (election_id, election_id))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    "CandidateID": row[0],
                    "CandidateName": row[1],
                    "PartyName": row[2],
                    "VoteCount": row[3]
                })

            # 4. Get candidates list
            cursor.execute("""
                SELECT CandidateID, CandidateName, PartyName, NationalID
                FROM Candidates
                WHERE ElectionID = %s
                ORDER BY CandidateName
            """, (election_id,))
            
            candidates = []
            for row in cursor.fetchall():
                candidates.append({
                    "CandidateID": row[0],
                    "CandidateName": row[1],
                    "PartyName": row[2],
                    "NationalID": row[3]
                })

            # 5. Get voter demographics
            # Gender distribution
            cursor.execute("""
                SELECT Gender, COUNT(*) as Count
                FROM Voters
                GROUP BY Gender
            """)
            
            gender_distribution = {}
            for row in cursor.fetchall():
                gender_distribution[row[0]] = row[1]

            # State distribution
            cursor.execute("""
                SELECT State, COUNT(*) as Count
                FROM Voters
                GROUP BY State
            """)
            
            state_distribution = {}
            for row in cursor.fetchall():
                state_distribution[row[0]] = row[1]

            demographics = {
                "GenderDistribution": gender_distribution,
                "StateDistribution": state_distribution
            }

            # 6. Get vote counts by time period
            # Votes in last day, week, month
            cursor.execute("""
                SELECT 
                    COUNT(CASE WHEN TO_DATE(ElectionDate, 'YYYY-MM-DD') >= CURRENT_DATE - INTERVAL '1 day' THEN 1 END) as last_day,
                    COUNT(CASE WHEN TO_DATE(ElectionDate, 'YYYY-MM-DD') >= CURRENT_DATE - INTERVAL '7 days' THEN 1 END) as last_week,
                    COUNT(CASE WHEN TO_DATE(ElectionDate, 'YYYY-MM-DD') >= CURRENT_DATE - INTERVAL '30 days' THEN 1 END) as last_month,
                    COUNT(*) as total
                FROM Votes
                WHERE ElectionID = %s
            """, (election_id,))
            
            time_counts = cursor.fetchone()
            vote_time_data = {
                "LastDay": time_counts[0],
                "LastWeek": time_counts[1],
                "LastMonth": time_counts[2],
                "Total": time_counts[3]
            }

            # Prepare final response
            response = {
                "Election": election_data,
                "Turnout": turnout_data,
                "Results": results,
                "Candidates": candidates,
                "Demographics": demographics,
                "VoteTimeData": vote_time_data,
                "Votes": []  # Will be populated below
            }

            # 7. Get all votes with timestamps for time-based analysis
            cursor.execute("""
                SELECT v.VoteID, v.VoterID, v.ElectionDate, v.CandidateID, c.CandidateName
                FROM Votes v
                JOIN Candidates c ON v.CandidateID = c.CandidateID
                WHERE v.ElectionID = %s
                ORDER BY TO_DATE(v.ElectionDate, 'YYYY-MM-DD')
            """, (election_id,))
            
            for row in cursor.fetchall():
                response["Votes"].append({
                    "VoteID": row[0],
                    "VoterID": row[1],
                    "ElectionDate": row[2],
                    "CandidateID": row[3],
                    "CandidateName": row[4]
                })

            return jsonify(response), 200

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Database operation failed"}), 500
    finally:
        if conn:
            conn.close()
            
# Run the server
if __name__ == '__main__':
    create_tables()  # Create tables when the application starts
    app.run(debug=False, host='0.0.0.0')
