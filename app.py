import os
import sqlite3
import json
from datetime import datetime
from functools import wraps
from flask import Flask, render_template_string, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.urandom(24)
DATABASE = 'projects.db'
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY, 
        name TEXT, 
        email TEXT UNIQUE, 
        password TEXT,
        account_type TEXT
)''')

    c.execute('''CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY, 
        user_id INTEGER, 
        project_name TEXT,
        data TEXT, 
        created_at TEXT
)''')

    c.execute('''CREATE TABLE IF NOT EXISTS vendor_details (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,

    -- Basic Vendor Information
    vendor_company_name TEXT,
    contact_person TEXT,
    phone TEXT,
    email TEXT,
    office_address TEXT,
    city_state TEXT,

    -- Business Registration
    gst_number TEXT,
    pan_number TEXT,
    company_reg_no TEXT,
    trade_license TEXT,

    -- Banking Details
    bank_name TEXT,
    account_number TEXT,
    ifsc_code TEXT,
    cancelled_cheque_doc TEXT,

    -- Work Category
    services TEXT,

    -- Experience
    years_experience TEXT,
    projects_completed TEXT,
    major_clients TEXT,

    -- Compliance
    epf_registration TEXT,
    esic_registration TEXT,
    labour_license TEXT,

    -- Pricing
    material_price_list TEXT,
    labour_rates TEXT,
    estimated_project_cost TEXT,

    -- Vendor Capacity
number_of_workers TEXT,
machinery_list TEXT,
monthly_supply_capacity TEXT,

-- Service Area
service_area TEXT,

-- Document Uploads
gst_certificate TEXT,
pan_card_doc TEXT,
labour_license_doc TEXT,
completion_certificate_doc TEXT,
created_at TEXT
)''')
    c.execute('''CREATE TABLE IF NOT EXISTS quotation_requests (
        id INTEGER PRIMARY KEY,
        builder_id INTEGER,
        vendor_id INTEGER,
        project_id INTEGER,

        material TEXT,
        quantity TEXT,

        status TEXT,

        created_at TEXT
   )''')

    conn.commit()
    conn.close()

init_db()

# --- AUTH DECORATOR ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- STYLES ---
BASE_STYLE = """
<style>
    /* Global Body */
    body { 
        font-family: "Times New Roman", Times, serif; 
        background: linear-gradient(135deg, #cce7ff, #d4ffd4, #ffe6f0, #fff9cc, #ffe0b3); 
        color: #2c2c2c; 
        margin: 0; 
    }

    /* Navbar */
    .navbar { 
        background-color: rgba(255,255,255,0.85); 
        color: #2c2c2c; 
        padding: 1rem 2rem; 
        display: flex; 
        justify-content: space-between; 
        align-items: center; 
        border-bottom: 1px solid #ddd;
    }
    .navbar a, .navbar button { 
        color: #2c2c2c; 
        text-decoration: none; 
        margin-left: 15px; 
        background: #ffcc99; 
        border: none; 
        padding: 8px 15px; 
        cursor: pointer; 
        border-radius: 4px; 
        font-family: "Times New Roman"; 
        font-size: 14px; 
        transition: 0.3s;
    }
    .navbar a:hover, .navbar button:hover { 
        background: #ffc266; 
    }

    /* Container */
    .container { 
    max-width: 1100px;
    margin: 30px auto;
    background: rgba(255, 255, 255, 0.9); 
    padding: 40px; 
    border-radius: 12px; 
    box-shadow: 0 10px 30px rgba(0,0,0,0.1); 
}

.report-container{
    max-width:1100px;
    width: calc(100% - 220px);
    margin:30px auto;
    margin-right:350px;
    background: rgba(255,255,255,0.9);
    padding:40px;
    border-radius:12px;
    box-shadow:0 10px 30px rgba(0,0,0,0.1);
}

    /* Buttons */
    .btn-main { 
        background-color: #99d6ff; 
        color: #2c2c2c; 
        padding: 12px 25px; 
        border: none; 
        border-radius: 5px; 
        cursor: pointer; 
        font-size: 16px; 
        width: 100%; 
        transition: 0.3s; 
    }
    .btn-main:hover { 
        background-color: #80cfff; 
    }

.edit-btn{
    display:inline-block;
    margin-top:20px;
    padding:12px 25px;
    background: linear-gradient(135deg, #17a2b8, #138496);
    color:white;
    font-size:15px;
    font-weight:600;
    border-radius:8px;
    text-decoration:none;
    transition:0.3s ease;
    box-shadow:0 4px 12px rgba(0,0,0,0.2);
}

.edit-btn:hover{
    transform: translateY(-2px);
    box-shadow:0 6px 18px rgba(0,0,0,0.3);
    background: linear-gradient(135deg, #138496, #11707f);
}

    /* Form inputs */
    input, select, textarea { 
        width: 100%; 
        padding: 12px; 
        margin: 10px 0; 
        border: 1px solid #ccc; 
        border-radius: 6px; 
        box-sizing: border-box; 
        font-family: "Times New Roman"; 
        font-size: 15px; 
        background: #fffbe6; 
        color: #2c2c2c;
    }

    /* Tables */
    table { 
        width: 100%; 
        border-collapse: collapse; 
        margin-top: 20px; 
        margin-bottom: 30px; 
        background: #ffffffcc; 
    }
    table, th, td { border: 1.5px solid rgba(0,0,0,0.25); }
    th, td { padding: 14px; text-align: left; }
    th { background-color: #ffefd5; color: #2c2c2c; font-weight: bold; }

    /* Overview Boxes */
    .overview-box { 
        background: #fdfdfdcc; 
        padding: 20px; 
        border-left: 5px solid #99d6ff; 
        border-radius: 4px; 
        margin: 20px 0; 
        line-height: 1.6; 
    }

    /* Chart Flex */
    .chart-flex { display: flex; gap: 20px; align-items: flex-start; margin-bottom: 30px; }
    .chart-box { flex: 1; border: 1.5px solid rgba(0,0,0,0.25);  padding: 20px; border-radius: 8px; background: #ffffffcc; }

    /* Alerts */
    .alert { 
        padding: 15px; 
        margin-bottom: 20px; 
        border: 1px solid transparent; 
        border-radius: 4px; 
        color: #721c24; 
        background-color: #f8d7da; 
    }

    /* Diagram Styles */
    .diagram-wrapper { 
        display: flex; 
        justify-content: space-between; 
        padding: 40px 10px; 
        min-height: 500px; 
        position: relative; 
        border: 1px solid #eee; 
        background: #ffffffcc; 
        border-radius: 12px;
    }
    .diag-side { width: 22%; font-size: 15px; }
    .diag-side h4 { color: #3399ff; border-bottom: 2px solid #3399ff; display: inline-block; padding-bottom: 3px; margin-bottom: 20px; }
    .diag-side div { margin-bottom: 12px; }
    .diag-center { width: 45%; display: flex; flex-direction: column; align-items: center; border-left: 2px solid #2c2c2c; border-right: 2px solid #2c2c2c; }
    .level-head { color: #3399ff; font-weight: bold; margin-bottom: 15px; text-transform: uppercase; font-size: 18px; }
    .floor-item { width: 260px; height: 32px; border: 1px solid #7f8c8d; background: #e6f7ff; margin-bottom: 3px; display: flex; align-items: center; justify-content: center; font-size: 13px; color: #2c2c2c; }
    .ground-sep { width: 100%; border-top: 4px solid #2c2c2c; margin: 15px 0; position: relative; }
    .ground-text { position: absolute; right: -130px; top: -12px; font-weight: bold; width: 150px; text-align: left; background: #ffffffcc; padding: 0 5px; color: #2c2c2c; }
    .basement-item { width: 260px; height: 32px; border: 1px dashed #ff9933; background: #fff0e6; margin-bottom: 3px; display: flex; align-items: center; justify-content: center; font-size: 13px; color: #cc6600; }
    .found-text { color: #cc6600; font-weight: bold; margin-top: 15px; text-transform: uppercase; }

.pdf-page{
    page-break-after: always;
    padding: 20px 0;
}

/* ============================= */
/* PERFECT PDF PAGE ALIGNMENT   */
/* ============================= */

@media print {

    @page {
        size: A4;
        margin: 25mm 20mm 25mm 20mm;  /* Top Right Bottom Left */
    }

    body {
        margin: 0 !important;
        padding: 0 !important;
        background: white !important;
    }

    #reportContent {
        width: 100% !important;
        max-width: 100% !important;
        margin: 0 auto !important;
        padding: 0 !important;
    }

    .container, .chart-box {
        page-break-inside: avoid;
    }

    .quote-glass-card{
        display:none !important;
    }

}

/* ============================= */
/* FLOATING MATERIAL QUOTE CARD  */
/* ============================= */

.quote-glass-card{
    position: fixed;
    top: 115px;
    right: 25px;
    width: 250px;
    padding: 22px;
    border-radius: 16px;
    background: rgba(255,255,255,0.25);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    border: 1px solid rgba(255,255,255,0.4);
    box-shadow: 0 8px 32px rgba(0,0,0,0.15);
    text-align: center;
    z-index: 999;
}

.quote-glass-card h4{
    margin-top:0;
    font-size:17px;
    color:#2c2c2c;
}

.quote-btn{
    margin-top:12px;
    padding:10px 15px;
    width:100%;
    border:none;
    border-radius:8px;
    background:#28a745;
    color:white;
    font-size:14px;
    cursor:pointer;
    transition:0.3s;
}

.quote-btn:hover{
    background:#218838;
}

/* Hide card in PDF / Print */
@media print{
    .quote-glass-card{
        display:none !important;
    }
}

</style>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
"""
# --- LOGIN & REGISTER PAGES UNCHANGED ---
LOGIN_PAGE = """
<style>
body{
    margin:0;
    font-family: 'Segoe UI', sans-serif;
    background: url('https://images.unsplash.com/photo-1503387762-592deb58ef4e') no-repeat center center/cover;
    height:100vh;
    overflow:hidden;
}

/* Top Navbar */
.top-bar {
    position: absolute;
    top: 0;
    left: 0;           /* ensure left edge */
    width: 100%;
    display: flex;
    justify-content: space-between; /* keeps About left, others right */
    align-items: center;            /* vertical centering */
    padding: 15px 40px;            /* adjust as needed */
    box-sizing: border-box;
    background-color: rgba(44, 62, 80, 0.9); /* your chosen color */
    border-bottom: 1px solid rgba(255,255,255,0.3);
    z-index: 1000;                  /* above everything */
}

/* About button on left */
.top-bar .about-btn {
    color: white;
    font-weight: 500;
    font-size: 16px;
    cursor: pointer;
}

/* Right side links */
.top-bar .right-links a {
    color: white;
    text-decoration: none;
    margin-left: 25px;
    font-weight: 500;
    font-size: 16px;
}

/* About Panel */
.about-panel{
    position:absolute;
    top:70px;
    left:40px;
    width:400px;
    max-height:70vh;
    overflow-y:auto;
    padding:20px;
    border-radius:15px;
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(15px);
    -webkit-backdrop-filter: blur(15px);
    border:1px solid rgba(255,255,255,0.3);
    box-shadow:0 8px 32px rgba(0,0,0,0.3);
    color:white;
    display:none;
}

.about-panel h3{
    margin-top:0;
    color:#ffc107;
}

/* Center Text */
.hero{
    text-align:center;
    color:white;
    margin-top:80px;
}

.hero h1{
    font-size:42px;
    margin-bottom:10px;
}

.hero p{
    width:60%;
    margin:auto;
    font-size:18px;
    opacity:0.9;
}

/* Glass Card */
.glass-card{
    position:absolute;
    right:8%;
    top:50%;
    transform:translateY(-50%);
    width:380px;
    padding:40px;
    border-radius:20px;
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(15px);
    -webkit-backdrop-filter: blur(15px);
    border:1px solid rgba(255,255,255,0.3);
    box-shadow:0 8px 32px rgba(0,0,0,0.3);
    color:white;
}

.glass-card h2{
    text-align:center;
    margin-bottom:25px;
}

input{
    width:100%;
    padding:12px;
    margin:12px 0;
    border-radius:8px;
    border:none;
    outline:none;
}

button{
    width:100%;
    padding:12px;
    border:none;
    border-radius:8px;
    background:#17a2b8;
    color:white;
    font-size:16px;
    cursor:pointer;
    transition:0.3s;
}

button:hover{
    background:#138496;
}

.alert{
    background:#ff6b6b;
    padding:10px;
    border-radius:6px;
    margin-bottom:15px;
    text-align:center;
}
</style>

<div class="top-bar">
    <span class="about-btn" onclick="toggleAbout()">About Us</span>
    <div class="right-links">
        <a href="/login">Login</a>
        <a href="/register">Register</a>
    </div>
</div>
<div class="about-panel" id="aboutPanel">
    <h3>🏗️ Smart Planning</h3>
    <p>The Pre-Project Analyser is designed to help builders, contractors, and project planners make informed decisions before construction begins. It examines every critical aspect of a project—including feasibility, resource allocation, and cost estimation—to ensure planning is efficient and accurate.</p>

    <h3>📊 Data-Driven Insights</h3>
    <p>Gain a clear understanding of potential challenges with interactive dashboards, visual reports, and predictive analytics. Evaluate timelines, estimate expenses, and simulate scenarios to make confident project choices.</p>

    <h3>⚡ Risk Reduction</h3>
    <p>Reduce uncertainties, avoid budget overruns, and minimize delays by identifying project risks in advance. The tool empowers users to anticipate problems and plan mitigation strategies before breaking ground.</p>

    <h3>💡 Empowering Builders & Developers</h3>
    <p>Whether you are an experienced contractor or a first-time developer, the Pre-Project Analyser simplifies complex planning processes. It guides you toward smarter, stronger, and safer construction projects.</p>

    <h3>🌟 Efficiency & Success</h3>
    <p>By streamlining pre-construction analysis, the tool saves time, improves resource utilization, and strengthens decision-making—helping every project start on a solid foundation and achieve success.</p>

    <h3>🔍 Comprehensive Analysis</h3>
    <p>From small residential projects to large commercial developments, the Pre-Project Analyser provides thorough insights to support strategic planning, ensuring sustainable, cost-effective, and high-quality results.</p>
</div>

<div class="hero">
    <h1>Smart Planning. Strong Foundations.</h1>
    <p>
    To become a trusted digital solution for pre-construction planning by delivering reliable insights, 
    feasibility analysis, and strategic project forecasting.
    </p>
</div>

<div class="glass-card">
    <h2>Welcome Back</h2>

    {% with messages = get_flashed_messages() %}
      {% if messages %}
        {% for message in messages %}
           <div class="alert">{{ message }}</div>
        {% endfor %}
      {% endif %}
    {% endwith %}

    <form method="POST">
        <input type="email" name="email" placeholder="Enter your email" required>
        <input type="password" name="password" placeholder="Enter your password" required>
        <button type="submit">Login</button>
    </form>

    <p style="text-align:center;margin-top:15px;">
        Don't have an account? <a href="/register" style="color:#fff;"><b>Register</b></a>
    </p>
</div>

<script>
function toggleAbout(){
    var panel = document.getElementById('aboutPanel');
    if(panel.style.display === 'block') panel.style.display = 'none';
    else panel.style.display = 'block';
}
</script>
"""

REGISTER_PAGE = """
<style>
body{
    margin:0;
    font-family: 'Segoe UI', sans-serif;
    background: url('https://images.unsplash.com/photo-1503387762-592deb58ef4e') no-repeat center center/cover;
    height:100vh;
    overflow:hidden;
}

.top-bar {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 40px;
    box-sizing: border-box;
    background-color: rgba(44, 62, 80, 0.9);
    border-bottom: 1px solid rgba(255,255,255,0.3);
    z-index: 1000;
}

.top-bar .about-btn {
    color: white;
    font-weight: 500;
    font-size: 16px;
    cursor: pointer;
}

.top-bar .right-links a {
    color: white;
    text-decoration: none;
    margin-left: 25px;
    font-weight: 500;
    font-size: 16px;
}

.top-bar a{
    color:white;
    text-decoration:none;
    margin-left:25px;
    font-weight:500;
    font-size:16px;
}

.hero{
    text-align:center;
    color:white;
    margin-top:80px;
}

.hero h1{
    font-size:42px;
    margin-bottom:10px;
}

.hero p{
    width:60%;
    margin:auto;
    font-size:18px;
    opacity:0.9;
}

.glass-card{
    position:absolute;
    right:8%;
    top:50%;
    transform:translateY(-50%);
    width:380px;
    padding:40px;
    border-radius:20px;
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(15px);
    -webkit-backdrop-filter: blur(15px);
    border:1px solid rgba(255,255,255,0.3);
    box-shadow:0 8px 32px rgba(0,0,0,0.3);
    color:white;
}

.glass-card h2{
    text-align:center;
    margin-bottom:25px;
}

input{
    width:100%;
    padding:12px;
    margin:12px 0;
    border-radius:8px;
    border:none;
    outline:none;
}

button{
    width:100%;
    padding:12px;
    border:none;
    border-radius:8px;
    background:#17a2b8;
    color:white;
    font-size:16px;
    cursor:pointer;
    transition:0.3s;
}

button:hover{
    background:#138496;
}

.alert{
    background:#ff6b6b;
    padding:10px;
    border-radius:6px;
    margin-bottom:15px;
    text-align:center;
}
.account-type{
    margin-bottom:15px;
}

.account-buttons{
    display:flex;
    gap:15px;
}

.type-btn{
    flex:1;
    text-align:center;
    padding:12px;
    border-radius:8px;
    background:rgba(255,255,255,0.2);
    cursor:pointer;
    font-weight:500;
}

.type-btn input{
    display:none;
}

.type-btn:hover{
    background:rgba(255,255,255,0.35);
}

/* Selected button color */
.type-btn span{
    display:block;
    padding:12px;
    border-radius:8px;
    transition:0.3s;
}

/* Selected button color only */
.type-btn input:checked + span{
    background:#17a2b8;
    color:white;
}


</style>

<div class="top-bar">
    <span class="about-btn">About Us</span>
    <div class="right-links">
        <a href="/login">Login</a>
        <a href="/register">Register</a>
    </div>
</div>

<div class="hero">
    <h1>Smart Planning. Strong Foundations.</h1>
    <p>
    To become a trusted digital solution for pre-construction planning by delivering reliable insights, 
    feasibility analysis, and strategic project forecasting.
    </p>
</div>

<div class="glass-card">
<form method="POST">

<div class="account-type">
<h2>Create Account</h2>

<div class="account-buttons">

<label class="type-btn">
<input type="radio" name="account_type" value="builder" required>
<span>Builder</span>
</label>

<label class="type-btn">
<input type="radio" name="account_type" value="vendor">
<span>Vendor</span>
</label>
</div>
</div>

<input type="text" name="name" placeholder="Full Name" required>
<input type="email" name="email" placeholder="Email Address" required>
<input type="password" name="password" placeholder="Password" required>

<button type="submit">Register</button>

</form>

    <p style="text-align:center;margin-top:15px;">
        Already have an account? <a href="/login" style="color:#fff;"><b>Login</b></a>
    </p>
</div>
"""

REQUEST_QUOTE_PAGE = BASE_STYLE + """

<div class="navbar">
<strong>Request Quotation</strong>
<div>
<a href="/vendors">Back</a>
</div>
</div>

<div class="container">

<h2>Request Quotation</h2>

<form method="POST">

<label>Material Required</label>
<textarea name="material" placeholder="Enter Materials.." required></textarea>

<label>Quantity</label>
<textarea name="quantity" placeholder="Enter Quantity..." required></textarea>

<button class="btn-main">Submit Request</button>

</form>

</div>
"""

HISTORY_PAGE = BASE_STYLE + """
<div class="navbar">
    <div><strong>Project History</strong> | {{session['user_name']}}</div>
    <div><a href="/planner">New Analysis</a> <a href="/logout" style="background:#dc3545;">Logout</a></div>
</div>
<div class="container">
    <h2>Your Saved Reports</h2>
    <table>
        <thead>
            <tr>
                <th>Project Name</th>
                <th>Created Date</th>
                <th>Action</th>
            </tr>
        </thead>
        <tbody>
            {% for report in reports %}
            <tr>
                <td>{{ report[2] }}</td>
                <td>{{ report[4] }}</td>
                <td>

<a href="/view_report/{{ report[0] }}"
style="background:#17a2b8; color:white; padding:6px 10px; border-radius:4px; text-decoration:none;">
View
</a>

<a href="/delete_report/{{ report[0] }}"
style="background:#dc3545; color:white; padding:6px 10px; border-radius:4px; text-decoration:none; margin-left:8px;"
onclick="return confirm('Are you sure you want to delete this report?')">
Delete
</a>

</td>
            </tr>
            {% endfor %}
            {% if not reports %}
            <tr><td colspan="3" style="text-align:center;">No reports found.</td></tr>
            {% endif %}
        </tbody>
    </table>
</div>
"""

PLANNER_PAGE = BASE_STYLE + """
<div class="navbar">
    <div><strong>Project Planning Tool</strong> | Logged in as: {{session['user_name']}}</div>
    <div><a href="/history">Analysis Report History</a> <a href="/logout" style="background:#dc3545;">Logout</a></div>
</div>
<div class="container">
    <h1 style="text-align:center;">Building pre-Project Analyser</h1>
    <h2>Enter Project Details</h2>
    <form action="/analyze" method="POST">
        <label>Project Name</label><input type="text" name="p_name" value="Green Valley Residency" required>
<div style="display:flex; gap:15px;">
    <div style="flex:1;">
        <label>Location</label>
        <input type="text" name="location" value="Pune, Maharashtra" required>
    </div>
    <div style="flex:1;">
        <label>Project Start Date</label>
        <input type="date" name="start_date" required>
    </div>
</div>
        <div style="display:flex; gap:15px;">
            <div style="flex:1;"><label>Project Type</label><select name="p_type"><option>Residential</option><option>Commercial</option><option>Industrial</option><option>Mixed-use</option></select></div>
            <div style="flex:1;"><label>Building Type</label><select name="b_type"><option>composite</option><option>RCC</option><option>Glass Structured</option><option>Mixed-use</option></select></div>
        </div>
        <div style="display:flex; gap:15px;">
        <div style="flex:1;"><label>Building Shape</label><select name="s_shape"><option>Rectangular</option><option>Square</option><option>Triangular</option><option>Circular</option><option>Linear</option><option>Other</option></select></div>
        <div style="flex:1;"><label>Number of Floors</label><input type="number" name="floors" value="10"></div>
        </div>
        <div style="display:flex; gap:15px;">
            <div style="flex:1;"><label>Number of Basements</label><input type="number" name="basements" value="2"></div>
            <div style="flex:1;"><label>Total Built-up Area (sq.ft.)</label><input type="number" name="area" value="120000"></div>
        </div>
        <div style="display:flex; gap:15px;">
            <div style="flex:1;"><label>Estimated Budget (₹ Cr)</label><input type="number" name="budget" value="50"></div>
            <div style="flex:1;"><label>Project Duration (months)</label><input type="number" name="duration" value="24"></div>
        </div>
        <label>Special Notes or Amenities</label>
        <textarea name="notes" rows="3">Swimming pool, landscape garden, rooftop solar</textarea>
        <button type="submit" class="btn-main">Generate Analysis Report</button>
    </form>
</div>
"""
REPORT_PAGE = BASE_STYLE + """
<div class="navbar">
    <div><strong>PROJECT ANALYSIS</strong> — {{data.p_name}}</div>
    <div>
        <button onclick="downloadPDF()">Download Report as PDF</button>
        <a href="/planner" style="background:#6c757d;">Back to Planner</a>
    </div>
</div>

<!-- FLOATING VENDOR QUOTE CARD -->
<div class="quote-glass-card">
    <h4>Vendor Marketplace</h4>

    <a href="/vendors">
        <button class="quote-btn">
            View Vendors
        </button>
    </a>
</div>
<div class="pdf-page">
<div class="report-container">

    <h1 style="text-align:center;">PROJECT ANALYSIS — {{data.p_name}}</h1>
    <p style="text-align:center; color:#666;">Created: {{date}}</p>
    <hr>

    <!-- 1️⃣ PROJECT OVERVIEW -->
    <h3>Project Overview</h3>
    <div class="overview-box">
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
            <div><strong>Project Name:</strong> {{data.p_name}}</div>
            <div><strong>Location:</strong> {{data.location}}</div>
      <div><strong>Project Start Date:</strong> {{data.start_date}}</div>
            <div><strong>Project Type:</strong> {{data.p_type}}</div>
            <div><strong>Building Type:</strong> {{data.b_type}}</div>
            <div><strong>Building Shape:</strong> {{data.s_shape}}</div>
            <div><strong>Floors:</strong> {{data.floors}}</div> 
      <div><strong>Basements:</strong> {{data.basements}}</div>
            <div><strong>Built-up Area:</strong> {{data.area}} sq.ft.</div>
            <div><strong>Estimated Budget:</strong> ₹{{data.budget}} Cr</div>
            <div><strong>Project Duration:</strong> {{data.duration}} Months</div>
            <div><strong>Notes:</strong> {{data.notes}}</div>
        </div>
    </div>

    <!-- 2️⃣ RESOURCE PLANNING -->
    <h3>Resource Planning</h3>
    <div class="chart-box">
        <table>
            <thead>
                <tr>
                    <th>Phase</th>
                    <th>Labour</th>
                    <th>Materials</th>
                    <th>Equipment</th>
                </tr>
            </thead>
            <tbody>
                <tr><td>Site Preparation</td><td>40–60</td><td>Temporary Utilities</td><td>Survey Tools</td></tr>
                <tr><td>Excavation</td><td>60–80</td><td>Earthwork</td><td>Excavator</td></tr>
                <tr><td>Foundation</td><td>80–100</td><td>Steel, Concrete</td><td>Crane</td></tr>
                <tr><td>RCC Frame</td><td>100–150</td><td>Concrete, Rebar</td><td>Tower Crane</td></tr>
                <tr><td>MEP</td><td>70–90</td><td>Cables, Pipes</td><td>Power Tools</td></tr>
                <tr><td>Finishing</td><td>120–180</td><td>Tiles, Paint</td><td>Interior Tools</td></tr>
            </tbody>
        </table>
    </div>

    <!-- 3️⃣ BUDGET + TOTAL COST -->
    <div class="chart-flex">

        <div class="chart-box">
            <h3>Budget Allocation (%)</h3>
            <canvas id="budgetChart"></canvas>
        </div>

        <div class="chart-box">
            <h3>Total Estimated Cost (₹ Cr)</h3>
            <canvas id="costChart"></canvas>
        </div>
    </div>

    <!-- 4️⃣ TIMELINE TRACKING (UPDATED DYNAMIC HORIZONTAL) -->
    <h3>Timeline Tracking</h3>
    <div class="chart-box" style="height:600px;">
        <canvas id="timelineChart"></canvas>
    </div>
   </div>

<div class="pdf-page">
<div class="report-container">

    <!-- 5️⃣ MILESTONE TRACKING -->
    <h3>Milestone Tracking</h3>
    <table>
        <thead>
            <tr><th>Milestone</th><th>Expected Completion</th></tr>
        </thead>
        <tbody>
            {% for phase in wbs %}
            <tr>
                <td>{{phase.name}}</td>
                <td>{{phase.end}}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

<!-- 6️⃣ MATERIAL COST BREAKDOWN -->
<h3>Material Cost Breakdown</h3>
<div class="chart-box">
    <table>
        <thead>
            <tr>
                <th>Material</th>
                <th>Allocation % (of Material Cost)</th>
                <th>Estimated Cost (₹ Cr)</th>
            </tr>
        </thead>
        <tbody id="materialTableBody">
        </tbody>
    </table>
</div>

    <!-- 6️⃣ RISK ASSESSMENT -->
    <h3>Risk Assessment</h3>
    <table>
        <thead>
            <tr>
                <th>Risk</th>
                <th>Likelihood</th>
                <th>Impact</th>
                <th>Score</th>
            </tr>
        </thead>
        <tbody>
            <tr><td>Material Price Escalation</td><td>4</td><td>4</td><td>16 (High)</td></tr>
            <tr><td>Labour Shortage</td><td>3</td><td>4</td><td>12 (Medium)</td></tr>
            <tr><td>Site Delays</td><td>3</td><td>3</td><td>9 (Medium)</td></tr>
            <tr><td>Approval Delays</td><td>2</td><td>3</td><td>6 (Low)</td></tr>
        </tbody>
    </table>

</div>

</div>

<!-- ============================= -->
<!-- PAGE 3 : ARCHITECTURAL VIEW  -->
<!-- ============================= -->

<div class="pdf-page">
<div class="report-container">

<h3 style="text-align:center;">Architectural Section View</h3>

<div class="diagram-wrapper">

    <div class="diag-side">
        <h4>Specifications</h4>
        <div><strong>Total Area:</strong> {{data.area}} sq.ft.</div>
        <div><strong>Bldg Shape:</strong> {{data.s_shape}}</div>
        <div><strong>Bldg Type:</strong> {{data.b_type}}</div>
        <div><strong>Budget:</strong> ₹{{data.budget}} Cr</div>
    </div>

    <div class="diag-center">

        <div class="level-head">TOP ROOF LEVEL</div>

        {% for i in range(data.floors|int, 0, -1) %}
        <div class="floor-item">Floor {{i}} (H: 3.0m)</div>
        {% endfor %}

        <div class="ground-sep">
            <div class="ground-text">GROUND LEVEL (±0.00)</div>
        </div>

        {% for i in range(1, data.basements|int + 1) %}
        <div class="basement-item">Basement {{i}} (H: 3.5m)</div>
        {% endfor %}

        <div class="found-text">FOUNDATION DEPTH</div>

    </div>

    <div class="diag-side">
        <h4>Calculated Heights</h4>
        <div><strong>Superstructure:</strong> {{ data.floors|int * 3.0 }} meters</div>
        <div><strong>Substructure:</strong> {{ data.basements|int * 3.5 }} meters</div>
        <div><strong>Total Vertical Span:</strong> {{ (data.floors|int * 3.0) + (data.basements|int * 3.5) }} m</div>
        <div><strong>Estimated Footprint:</strong> ~{{ "%.2f"|format(data.area|float / (data.floors|float if data.floors|float>0 else 1)) }} sq.ft/floor</div>
    </div>

</div>

</div>
</div>

<script>

const totalBudget = parseFloat("{{data.budget}}");

// Budget percentages
const labels = ['Civil','Materials','Labor','MEP','Finishes','Contingency'];
const percentData = [35,20,18,12,10,5];

// PIE CHART
new Chart(document.getElementById('budgetChart'), {
    type: 'pie',
    data: {
        labels: labels,
        datasets: [{
            data: percentData,
            backgroundColor: ['#2c3e50','#17a2b8','#ffc107','#dc3545','#28a745','#6c757d']
        }]
    },
    options:{ plugins:{ legend:{ position:'bottom' } } }
});

// DOUGHNUT CHART
const actualValues = percentData.map(p => ((p/100)*totalBudget).toFixed(2));

new Chart(document.getElementById('costChart'), {
    type: 'doughnut',
    data: {
        labels: labels,
        datasets: [{
            data: actualValues,
            backgroundColor:['#2c3e50','#17a2b8','#ffc107','#dc3545','#28a745','#6c757d']
        }]
    },
    options:{ plugins:{ legend:{ position:'right' } } }
});


// ==========================
// UPDATED TIMELINE LOGIC
// ==========================

// Convert months to days dynamically
const projectMonths = parseInt("{{data.duration}}");
const totalProjectDays = projectMonths * 30;

const phases = [
    "Home Design & Approval",
    "Excavation",
    "Footing & Foundation",
    "RCC Work - Columns & Slabs",
    "Roof Slab",
    "Brickwork and Plastering",
    "Flooring & Tiling",
    "Electric Wiring",
    "Water Supply & Plumbing",
    "Doors & Windows"
];

const phasePercent = [8,5,15,20,10,10,8,7,9,8];

const durationDays = phasePercent.map(p => 
    Math.round((p/100) * totalProjectDays)
);

const phaseCost = durationDays.map(d => 
    "₹ " + (d * 15000).toLocaleString()
);

new Chart(document.getElementById('timelineChart'), {
    type: 'bar',
    data: {
        labels: phases,
        datasets: [{
            label: "Duration (Days)",
            data: durationDays,
            backgroundColor: '#e6e29c',
            borderRadius: 5,
            barThickness: 20
        }]
    },
    options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        const i = context.dataIndex;
                        return durationDays[i] + 
                               " Days | Cost: " + 
                               phaseCost[i];
                    }
                }
            },
            title: {
                display: true,
                text: 'Timeline Tracking',
                font: { size: 20 }
            },
            subtitle: {
                display: true,
                text: 'Overall Project Duration: ' + totalProjectDays + ' Days'
            }
        },
        scales: {
            x: {
                beginAtZero: true,
                title: {
                    display: true,
                    text: 'Duration (Days)'
                }
            },
            y: {
                grid: { display: false }
            }
        }
    }
});

// ==========================
// MATERIAL COST CALCULATION
// ==========================

const totalBudgetValue = parseFloat("{{data.budget}}");

// 20% material cost from total budget
const totalMaterialCost = totalBudgetValue * 0.20;

// Material distribution inside 20%
const materialBreakdown = [
    { name: "Cement", percent: 15 },
    { name: "Steel", percent: 20 },
    { name: "Bricks & Blocks", percent: 10 },
    { name: "Sand & Aggregates", percent: 8 },
    { name: "Glass", percent: 7 },
    { name: "Wood", percent: 8 },
    { name: "Paint", percent: 6 },
    { name: "Pipes (Plumbing)", percent: 10 },
    { name: "Electric Wires & Cables", percent: 8 },
    { name: "Tiles & Finishing Materials", percent: 8 }
];

const materialTable = document.getElementById("materialTableBody");

// Populate Material Breakdown Table
materialBreakdown.forEach(item => {
    const cost = ((item.percent / 100) * totalMaterialCost).toFixed(2);

    const row = `
        <tr>
            <td>${item.name}</td>
            <td>${item.percent}%</td>
            <td>₹ ${cost}</td>
        </tr>
    `;
    materialTable.innerHTML += row;
});


// ==========================
// PDF DOWNLOAD FUNCTION
// ==========================

async function downloadPDF(){
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF('p', 'mm', 'a4');

    const pages = document.querySelectorAll('.pdf-page');

    for (let i = 0; i < pages.length; i++) {

        const canvas = await html2canvas(pages[i], {
            scale: 2,
            useCORS: true
        });

        const imgData = canvas.toDataURL('image/png');

        const imgWidth = 210;
        const imgHeight = (canvas.height * imgWidth) / canvas.width;

        if (i > 0) doc.addPage();

        doc.addImage(imgData, 'PNG', 0, 0, imgWidth, imgHeight);
    }

    doc.save('Analysis_Report_{{data.p_name}}.pdf');
}</script>
"""

VENDOR_PROFILE_PAGE = BASE_STYLE + """

<style>

.vendor-card{
    background:white;
    border-radius:10px;
    padding:25px;
    margin-bottom:25px;
    box-shadow:0 6px 18px rgba(0,0,0,0.08);
}

.vendor-card h3{
    margin-top:0;
    border-left:5px solid #17a2b8;
    padding-left:10px;
}

.grid-2{
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:20px;
}

.file-box{
    border:2px dashed #ccc;
    padding:20px;
    text-align:center;
    border-radius:8px;
    background:#fafafa;
}

.submit-btn{
    margin-top:25px;
    padding:15px;
    width:100%;
    font-size:18px;
    border:none;
    border-radius:8px;
    background:#28a745;
    color:white;
}

.submit-btn:hover{
    background:#218838;
}

</style>

<div class="navbar">
<strong>Vendor Registration Portal</strong>
<div>
<a href="/logout" style="background:#dc3545;">Logout</a>
</div>
</div>

<div class="container">

<h2 style="text-align:center;margin-bottom:30px;">
Vendor Business Profile
</h2>

<form method="POST" enctype="multipart/form-data">

<!-- BASIC INFO -->
<div class="vendor-card">
<h3>1. Basic Vendor Information</h3>

<div class="grid-2">

<div>
<label>Vendor / Company Name</label>
<input type="text" name="vendor_company_name" value="{{vendor[2] if vendor else ''}}">
</div>

<div>
<label>Contact Person</label>
<input type="text" name="contact_person" value="{{vendor[3] if vendor else ''}}">
</div>

<div>
<label>Phone Number</label>
<input type="text" name="phone" value="{{vendor[4] if vendor else ''}}">
</div>

<div>
<label>Email</label>
<input type="email" name="email" value="{{vendor[5] if vendor else ''}}">
</div>

<div>
<label>City / State</label>
<input type="text" name="city_state" value="{{vendor[7] if vendor else ''}}">
</div>

<div>
<label>Service Area</label>
<input type="text" name="service_area" value="{{vendor[29] if vendor else ''}}">
</div>

</div>

<label>Office Address</label>
<textarea name="office_address">{{vendor[6] if vendor else ''}}</textarea>

</div>


<!-- BUSINESS REGISTRATION -->
<div class="vendor-card">
<h3>2. Business Registration</h3>

<div class="grid-2">

<div>
<label>GST Number</label>
<input type="text" name="gst_number" value="{{vendor[8] if vendor else ''}}">
</div>

<div>
<label>PAN Number</label>
<input type="text" name="pan_number" value="{{vendor[9] if vendor else ''}}">
</div>

<div>
<label>Company Registration No</label>
<input type="text" name="company_reg_no" value="{{vendor[10] if vendor else ''}}">
</div>

<div>
<label>Trade License</label>
<input type="text" name="trade_license" value="{{vendor[11] if vendor else ''}}">
</div>

</div>

</div>


<!-- BANKING DETAILS -->
<div class="vendor-card">
<h3>3. Banking Details</h3>

<div class="grid-2">

<div>
<label>Bank Name</label>
<input type="text" name="bank_name" value="{{vendor[12] if vendor else ''}}">
</div>

<div>
<label>Account Number</label>
<input type="text" name="account_number" value="{{vendor[13] if vendor else ''}}">
</div>

<div>
<label>IFSC Code</label>
<input type="text" name="ifsc_code" value="{{vendor[14] if vendor else ''}}">
</div>

<div class="file-box">
<label>Cancelled Cheque</label>
<input type="file" name="cancelled_cheque_doc">
{% if vendor and vendor[15] %}
<p>Existing: {{vendor[15]}}</p>
{% endif %}
</div>

</div>

</div>


<!-- SERVICES -->
<div class="vendor-card">
<h3>4. Work Category / Services</h3>

<select name="services">

<!-- 🏗️ CORE CONSTRUCTION -->
<option {{'selected' if vendor and vendor[16]=='Civil Contractor' else ''}}>Civil Contractor</option>
<option {{'selected' if vendor and vendor[16]=='Labour Contractor' else ''}}>Labour Contractor</option>
<option {{'selected' if vendor and vendor[16]=='Structural Contractor' else ''}}>Structural Contractor</option>

<!-- 🧱 MATERIAL SUPPLIERS -->
<option {{'selected' if vendor and vendor[16]=='Material Supplier' else ''}}>Material Supplier (Cement, Steel, Sand)</option>
<option {{'selected' if vendor and vendor[16]=='Concrete Supplier' else ''}}>Ready Mix Concrete (RMC) Supplier</option>

<!-- ⚡ MEP SERVICES -->
<option {{'selected' if vendor and vendor[16]=='Electrical Contractor' else ''}}>Electrical Contractor</option>
<option {{'selected' if vendor and vendor[16]=='Plumbing Contractor' else ''}}>Plumbing Contractor</option>
<option {{'selected' if vendor and vendor[16]=='HVAC Contractor' else ''}}>HVAC / Air Conditioning</option>

<!-- 🏠 FINISHING -->
<option {{'selected' if vendor and vendor[16]=='Interior Contractor' else ''}}>Interior Contractor</option>
<option {{'selected' if vendor and vendor[16]=='Tile & Flooring Vendor' else ''}}>Tile & Flooring Vendor</option>
<option {{'selected' if vendor and vendor[16]=='Painting Contractor' else ''}}>Painting Contractor</option>

<!-- 🛠️ SPECIALIZED -->
<option {{'selected' if vendor and vendor[16]=='Waterproofing Contractor' else ''}}>Waterproofing Contractor</option>
<option {{'selected' if vendor and vendor[16]=='Lift & Elevator Supplier' else ''}}>Lift & Elevator Supplier</option>
<option {{'selected' if vendor and vendor[16]=='Solar System Vendor' else ''}}>Solar System Vendor</option>

</select>

</div>


<!-- EXPERIENCE -->
<div class="vendor-card">
<h3>5. Experience Details</h3>

<div class="grid-2">

<div>
<label>Years of Experience</label>
<input type="number" name="years_experience" value="{{vendor[17] if vendor else ''}}">
</div>

<div>
<label>Projects Completed</label>
<input type="number" name="projects_completed" value="{{vendor[18] if vendor else ''}}">
</div>

</div>

<label>Major Clients</label>
<textarea name="major_clients">{{vendor[19] if vendor else ''}}</textarea>

</div>


<!-- COMPLIANCE -->
<div class="vendor-card">
<h3>6. Compliance</h3>

<div class="grid-2">

<div>
<label>EPF Registration</label>
<input type="text" name="epf_registration" value="{{vendor[20] if vendor else ''}}">
</div>

<div>
<label>ESIC Registration</label>
<input type="text" name="esic_registration" value="{{vendor[21] if vendor else ''}}">
</div>

<div>
<label>Labour License</label>
<input type="text" name="labour_license" value="{{vendor[22] if vendor else ''}}">
</div>

</div>

</div>


<!-- PRICING -->
<div class="vendor-card">
<h3>7. Pricing Information</h3>

<label>Material Price List</label>
<textarea name="material_price_list">{{vendor[23] if vendor else ''}}</textarea>

<label>Labour Rates</label>
<textarea name="labour_rates">{{vendor[24] if vendor else ''}}</textarea>

<label>Estimated Project Cost</label>
<input type="text" name="estimated_project_cost" value="{{vendor[25] if vendor else ''}}">

</div>


<!-- CAPACITY -->
<div class="vendor-card">
<h3>8. Vendor Capacity</h3>

<div class="grid-2">

<div>
<label>Number of Workers</label>
<input type="number" name="number_of_workers" value="{{vendor[26] if vendor else ''}}">
</div>

<div>
<label>Monthly Supply Capacity</label>
<input type="text" name="monthly_supply_capacity" value="{{vendor[28] if vendor else ''}}">
</div>

</div>

<label>Machinery Available</label>
<textarea name="machinery_list">{{vendor[27] if vendor else ''}}</textarea>

</div>


<!-- DOCUMENTS -->
<div class="vendor-card">
<h3>9. Document Uploads</h3>

<div class="grid-2">

<div class="file-box">
<label>GST Certificate</label>
<input type="file" name="gst_certificate">
{% if vendor and vendor[30] %}
<p>Existing: {{vendor[30]}}</p>
{% endif %}
</div>

<div class="file-box">
<label>PAN Card</label>
<input type="file" name="pan_card_doc">
{% if vendor and vendor[31] %}
<p>Existing: {{vendor[31]}}</p>
{% endif %}
</div>

<div class="file-box">
<label>Labour License</label>
<input type="file" name="labour_license_doc">
{% if vendor and vendor[32] %}
<p>Existing: {{vendor[32]}}</p>
{% endif %}
</div>

<div class="file-box">
<label>Completion Certificate</label>
<input type="file" name="completion_certificate_doc">
{% if vendor and vendor[33] %}
<p>Existing: {{vendor[33]}}</p>
{% endif %}
</div>

</div>

</div>


<button class="submit-btn">
Update / Submit Vendor Profile
</button>

</form>

</div>
"""
VENDOR_DASHBOARD = BASE_STYLE + """

<div class="navbar">
<strong>Vendor Dashboard</strong>
<div>
<a href="/logout" style="background:#dc3545;">Logout</a>
</div>
</div>

<div class="container">

<h2>Welcome {{session['user_name']}}</h2>

<p>Your vendor account has been successfully registered.</p>

<p>You can now participate in project quotations.</p>
<br>

<a href="/vendor_profile" class="edit-btn">
    ✏️ Edit Profile
</a>
<h3>📨 Incoming Requests</h3>

<table>
<tr>
<th>Builder</th>
<th>Material</th>
<th>Quantity</th>
<th>Status</th>
<th>Action</th>
</tr>

{% for r in requests %}
<tr>
<td>{{r[8]}}</td>
<td>{{r[4]}}</td>
<td>{{r[5]}}</td>
<td>{{r[6]}}</td>

<td>
<a href="/accept_quote/{{r[0]}}">✅Accept</a>
<a href="/reject_quote/{{r[0]}}"> ❌Reject</a>
<a href="/quote_view/{{r[0]}}"> 👁️View</a>
</td>

</tr>
{% endfor %}
</table>

</div>

"""
VENDOR_LIST_PAGE = BASE_STYLE + """

<div class="navbar">
<strong>Vendor Marketplace</strong>

<div>
<a href="/planner">Back</a>
<a href="/logout" style="background:#dc3545;">Logout</a>
</div>

</div>

<div class="container">

<h2>Registered Vendors</h2>

<table>

<thead>
<tr>
<th>Company</th>
<th>Service</th>
<th>Experience</th>
<th>City</th>
<th>Action</th>
</tr>
</thead>

<tbody>

{% for v in vendors %}

<tr>
<td>{{v[2]}}</td>
<td>{{v[16]}}</td>
<td>{{v[17]}} Years</td>
<td>{{v[7]}}</td>

<td style="text-align:center; vertical-align:middle;">

<div style="
    display:flex;
    flex-direction:column;
    align-items:center;
    gap:10px;
">

<a href="/vendor_view/{{v[0]}}"
style="background:#17a2b8;color:white;padding:6px 12px;border-radius:4px;text-decoration:none;">
View Vendor
</a>

{% for q in quotes %}
    {% if q[2] == v[1] %}

        {% if q[6] == 'Pending' %}
            <span>🕒 Pending</span>
        {% elif q[6] == 'Accepted' %}
            <span>✅ Accepted</span>
        {% elif q[6] == 'Rejected' %}
            <span>❌ Rejected</span>
        {% endif %}

        <a href="/quote_view/{{q[0]}}"
        style="font-size:13px; color:#007bff;">
        View Quotation
        </a>

    {% endif %}
{% endfor %}

</div>

</td>
</tr>

{% endfor %}

</tbody>

</table>

</div>
"""
VENDOR_VIEW_PAGE = BASE_STYLE + """

<style>

.profile-header{
    background: linear-gradient(135deg, #0f2027, #2c5364, #00c6ff);
    color: white;
    padding: 28px;
    border-radius: 14px;
    margin-bottom: 30px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.25);
    border: 1px solid rgba(255,255,255,0.2);
}

.profile-header h2{
    margin:0;
}

.section-card{
    background:white;
    border-radius:10px;
    padding:20px;
    margin-bottom:20px;
    box-shadow:0 5px 15px rgba(0,0,0,0.08);
}

.section-title{
    font-size:18px;
    margin-bottom:15px;
    border-left:5px solid #17a2b8;
    padding-left:10px;
    font-weight:bold;
}

.info-grid{
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:15px;
}

.info-box{
    background: linear-gradient(135deg, #e6f7ff, #ccf2ff);
    padding:14px;
    border-radius:8px;
    border-left:5px solid #17a2b8;
    box-shadow:0 4px 10px rgba(0,0,0,0.1);
    transition:0.3s ease;
}

.info-box:hover{
    transform: translateY(-3px);
    box-shadow:0 6px 18px rgba(0,0,0,0.2);
}

.info-box b{
    display:block;
    color:#555;
    font-size:13px;
}

.info-box span{
    font-size:15px;
}

.doc-link{
    display:inline-block;
    margin-top:5px;
    padding:6px 10px;
    background:#17a2b8;
    color:white;
    border-radius:5px;
    text-decoration:none;
    font-size:13px;
}

.doc-link:hover{
    background:#138496;
}

</style>

<div class="navbar">
<strong>Vendor Profile</strong>
<div>
<a href="/vendors">Back</a>
<a href="/logout" style="background:#dc3545;">Logout</a>
</div>
</div>

<div class="container">

<!-- HEADER -->
<div class="profile-header">
    <h2>{{vendor[2]}}</h2>
    <p>{{vendor[16]}} | {{vendor[7]}}</p>
</div>

<!-- BASIC INFO -->
<div class="section-card">
<div class="section-title">📌 Basic Information</div>

<div class="info-grid">
<div class="info-box"><b>Company</b><span>{{vendor[2]}}</span></div>
<div class="info-box"><b>Contact Person</b><span>{{vendor[3]}}</span></div>
<div class="info-box"><b>Phone</b><span>{{vendor[4]}}</span></div>
<div class="info-box"><b>Email</b><span>{{vendor[5]}}</span></div>
<div class="info-box"><b>City / State</b><span>{{vendor[7]}}</span></div>
<div class="info-box"><b>Service Area</b><span>{{vendor[29]}}</span></div>
</div>

<br>
<div class="info-box">
<b>Office Address</b>
<span>{{vendor[6]}}</span>
</div>

</div>

<!-- BUSINESS -->
<div class="section-card">
<div class="section-title">🏢 Business Registration</div>

<div class="info-grid">
<div class="info-box"><b>GST Number</b><span>{{vendor[8]}}</span></div>
<div class="info-box"><b>PAN Number</b><span>{{vendor[9]}}</span></div>
<div class="info-box"><b>Company Reg No</b><span>{{vendor[10]}}</span></div>
<div class="info-box"><b>Trade License</b><span>{{vendor[11]}}</span></div>
</div>

</div>

<!-- BANK -->
<div class="section-card">
<div class="section-title">🏦 Banking Details</div>

<div class="info-grid">
<div class="info-box"><b>Bank</b><span>{{vendor[12]}}</span></div>
<div class="info-box"><b>Account No</b><span>{{vendor[13]}}</span></div>
<div class="info-box"><b>IFSC</b><span>{{vendor[14]}}</span></div>
</div>

{% if vendor[15] %}
<a class="doc-link" href="/uploads/{{vendor[15]}}" target="_blank">View Cancelled Cheque</a>
{% endif %}

</div>

<!-- SERVICES -->
<div class="section-card">
<div class="section-title">🛠 Services</div>
<p>{{vendor[16]}}</p>
</div>

<!-- EXPERIENCE -->
<div class="section-card">
<div class="section-title">📊 Experience</div>

<div class="info-grid">
<div class="info-box"><b>Years</b><span>{{vendor[17]}}</span></div>
<div class="info-box"><b>Projects Completed</b><span>{{vendor[18]}}</span></div>
</div>

<br>
<div class="info-box">
<b>Major Clients</b>
<span>{{vendor[19]}}</span>
</div>

</div>

<!-- COMPLIANCE -->
<div class="section-card">
<div class="section-title">⚖ Compliance</div>

<div class="info-grid">
<div class="info-box"><b>EPF</b><span>{{vendor[20]}}</span></div>
<div class="info-box"><b>ESIC</b><span>{{vendor[21]}}</span></div>
<div class="info-box"><b>Labour License</b><span>{{vendor[22]}}</span></div>
</div>

</div>

<!-- PRICING -->
<div class="section-card">
<div class="section-title">💰 Pricing</div>

<div class="info-box"><b>Material Price List</b><span>{{vendor[23]}}</span></div>
<br>
<div class="info-box"><b>Labour Rates</b><span>{{vendor[24]}}</span></div>
<br>
<div class="info-box"><b>Estimated Cost</b><span>{{vendor[25]}}</span></div>

</div>

<!-- CAPACITY -->
<div class="section-card">
<div class="section-title">🏗 Capacity</div>

<div class="info-grid">
<div class="info-box"><b>Workers</b><span>{{vendor[26]}}</span></div>
<div class="info-box"><b>Monthly Supply</b><span>{{vendor[28]}}</span></div>
</div>

<br>
<div class="info-box">
<b>Machinery</b>
<span>{{vendor[27]}}</span>
</div>

</div>

<!-- DOCUMENTS -->
<div class="section-card">
<div class="section-title">📂 Documents</div>

{% if vendor[30] %}
<a class="doc-link" href="/uploads/{{vendor[30]}}" target="_blank">GST Certificate</a>
{% endif %}

{% if vendor[31] %}
<a class="doc-link" href="/uploads/{{vendor[31]}}" target="_blank">PAN Card</a>
{% endif %}

{% if vendor[32] %}
<a class="doc-link" href="/uploads/{{vendor[32]}}" target="_blank">Labour License</a>
{% endif %}

{% if vendor[33] %}
<a class="doc-link" href="/uploads/{{vendor[33]}}" target="_blank">Completion Certificate</a>
{% endif %}

</div>
<br><br>

<a href="/request_quote/{{vendor[1]}}"
style="background:#28a745;color:white;padding:10px 15px;border-radius:6px;text-decoration:none;">
📨 Request Quotation
</a>
</div>
"""
QUOTE_VIEW_PAGE = BASE_STYLE + """

<div class="navbar">
<strong>Quotation Detail</strong>
<div>
{% if session['account_type'] == 'vendor' %}
    <a href="/vendor_dashboard">Back</a>
{% else %}
    <a href="/vendors">Back</a>
{% endif %}
</div>
</div>

<div class="container">

<h2>Quotation Request Detail</h2>

<p><b>Builder Name:</b> {{data.name}}</p>
<p><b>Email:</b> {{data.email}}</p>

<p><b>Material:</b></p>
<p>{{data.material}}</p>

<p><b>Quantity:</b></p>
<p>{{data.quantity}}</p>

<p><b>Status:</b> {{data.status}}</p>

</div>
"""

# --- ROUTES ---

@app.route('/')
def index():
    if 'user_id' in session: return redirect(url_for('planner'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        pw = request.form['password']

        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE email=?", (email,))
        user = c.fetchone()

        conn.close()

        if user and check_password_hash(user[3], pw):

            session['user_id'] = user[0]
            session['user_name'] = user[1]
            session['account_type'] = user[4]

            if user[4] == "vendor":
                return redirect(url_for('vendor_profile'))

            return redirect(url_for('planner'))

        flash("Invalid Credentials")

    return render_template_string(LOGIN_PAGE)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        account_type = request.form['account_type']

        try:
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()

            c.execute("""
            INSERT INTO users (name,email,password,account_type)
            VALUES (?,?,?,?)
            """,(name,email,password,account_type))

            conn.commit()
            conn.close()

            flash("Registered successfully!")
            return redirect(url_for('login'))

        except:
            flash("Email already exists")

    return render_template_string(REGISTER_PAGE)

@app.route('/planner')
@login_required
def planner():
    return render_template_string(PLANNER_PAGE, datetime=datetime)

from dateutil.relativedelta import relativedelta

@app.route('/analyze', methods=['POST'])
@login_required
def analyze():
    form_data = request.form.to_dict()

    phases = [
        "Site Preparation & Mobilization",
        "Excavation & Basement Works",
        "Foundation & Waterproofing",
        "RCC Frame Construction",
        "Masonry & Plastering",
        "MEP Installation",
        "Finishes & Interiors",
        "Testing & Handover"
    ]

    project_start = datetime.strptime(form_data['start_date'], "%Y-%m-%d")
    total_months = int(form_data['duration'])

    months_per_phase = total_months // len(phases)   # FIXED (integer division)

    wbs = []
    current_date = project_start

    for p in phases:
        current_date += relativedelta(months=months_per_phase)
        wbs.append({
            "name": p,
            "end": current_date.strftime('%Y-%m-%d')
        })

    # Save to DB
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute(
        "INSERT INTO reports (user_id, project_name, data, created_at) VALUES (?, ?, ?, ?)",
        (
            session['user_id'],
            form_data['p_name'],
            json.dumps({'form': form_data, 'wbs': wbs}),
            datetime.now().strftime('%Y-%m-%d %H:%M')
        )
    )

    report_id = c.lastrowid
    conn.commit()
    conn.close()

    # ✅ Fetch vendors INSIDE function
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM vendor_details")
    vendors = c.fetchall()
    conn.close()

    return render_template_string(
        REPORT_PAGE,
        data=form_data,
        wbs=wbs,
        date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        report_id=report_id,
        vendors=vendors
    )

@app.route('/delete_report/<int:report_id>')
@login_required
def delete_report(report_id):

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute(
        "DELETE FROM reports WHERE id=? AND user_id=?",
        (report_id, session['user_id'])
    )

    conn.commit()
    conn.close()

    return redirect(url_for('history'))

@app.route('/history')
@login_required
def history():
    conn = sqlite3.connect(DATABASE); c = conn.cursor()
    c.execute("SELECT * FROM reports WHERE user_id=? ORDER BY id DESC", (session['user_id'],))
    reports = c.fetchall(); conn.close()
    return render_template_string(HISTORY_PAGE, reports=reports)

@app.route('/view_report/<int:report_id>')
@login_required
def view_report(report_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM reports WHERE id=? AND user_id=?", (report_id, session['user_id']))
    report = c.fetchone()

    # ✅ Fetch vendors here also
    c.execute("SELECT * FROM vendor_details")
    vendors = c.fetchall()

    conn.close()

    if report:
        payload = json.loads(report[3])
        return render_template_string(
            REPORT_PAGE,
            data=payload['form'],
            wbs=payload['wbs'],
            date=report[4],
            report_id=report_id,
            vendors=vendors
        )

    return redirect(url_for('history'))

@login_required
def visualize(report_id):
    conn = sqlite3.connect(DATABASE); c = conn.cursor()
    c.execute("SELECT * FROM reports WHERE id=?", (report_id,))
    report = c.fetchone(); conn.close()
    if report:
        payload = json.loads(report[3])
        return render_template_string(VISUAL_PAGE, data=payload['form'])
    return redirect(url_for('planner'))

from werkzeug.utils import secure_filename

@app.route('/vendor_profile', methods=['GET','POST'])
@login_required
def vendor_profile():

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # 🔍 Check if vendor already exists
    c.execute("SELECT * FROM vendor_details WHERE user_id=?", (session['user_id'],))
    vendor = c.fetchone()

    if request.method == 'POST':

        def save_file(field, old_file=""):
            file = request.files.get(field)
            if file and file.filename != "":
                filename = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                return filename
            return old_file  # keep old file if not uploaded

        # Keep old files if not changed
        cheque = save_file('cancelled_cheque_doc', vendor[15] if vendor else "")
        gst_cert = save_file('gst_certificate', vendor[30] if vendor else "")
        pan_doc = save_file('pan_card_doc', vendor[31] if vendor else "")
        labour_doc = save_file('labour_license_doc', vendor[32] if vendor else "")
        completion_doc = save_file('completion_certificate_doc', vendor[33] if vendor else "")

        data = (
            request.form['vendor_company_name'],
            request.form['contact_person'],
            request.form['phone'],
            request.form['email'],
            request.form['office_address'],
            request.form['city_state'],
            request.form['gst_number'],
            request.form['pan_number'],
            request.form['company_reg_no'],
            request.form['trade_license'],
            request.form['bank_name'],
            request.form['account_number'],
            request.form['ifsc_code'],
            cheque,
            request.form['services'],
            request.form['years_experience'],
            request.form['projects_completed'],
            request.form['major_clients'],
            request.form['epf_registration'],
            request.form['esic_registration'],
            request.form['labour_license'],
            request.form['material_price_list'],
            request.form['labour_rates'],
            request.form['estimated_project_cost'],
            request.form['number_of_workers'],
            request.form['machinery_list'],
            request.form['monthly_supply_capacity'],
            request.form['service_area'],
            gst_cert,
            pan_doc,
            labour_doc,
            completion_doc,
            datetime.now().strftime('%Y-%m-%d %H:%M'),
            session['user_id']
        )

        if vendor:
            # 🔁 UPDATE EXISTING
            c.execute("""
            UPDATE vendor_details SET
            vendor_company_name=?,contact_person=?,phone=?,email=?,
            office_address=?,city_state=?,gst_number=?,pan_number=?,
            company_reg_no=?,trade_license=?,bank_name=?,account_number=?,
            ifsc_code=?,cancelled_cheque_doc=?,services=?,years_experience=?,
            projects_completed=?,major_clients=?,epf_registration=?,
            esic_registration=?,labour_license=?,material_price_list=?,
            labour_rates=?,estimated_project_cost=?,number_of_workers=?,
            machinery_list=?,monthly_supply_capacity=?,service_area=?,
            gst_certificate=?,pan_card_doc=?,labour_license_doc=?,
            completion_certificate_doc=?,created_at=?
            WHERE user_id=?
            """, data)

        else:
            # ➕ INSERT NEW
            c.execute("""
            INSERT INTO vendor_details(
            user_id,vendor_company_name,contact_person,phone,email,
            office_address,city_state,gst_number,pan_number,company_reg_no,
            trade_license,bank_name,account_number,ifsc_code,
            cancelled_cheque_doc,services,years_experience,projects_completed,
            major_clients,epf_registration,esic_registration,labour_license,
            material_price_list,labour_rates,estimated_project_cost,
            number_of_workers,machinery_list,monthly_supply_capacity,
            service_area,gst_certificate,pan_card_doc,
            labour_license_doc,completion_certificate_doc,created_at
            )
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (session['user_id'],) + data[:-1])

        conn.commit()
        conn.close()

        return redirect(url_for('vendor_dashboard'))

    conn.close()

    return render_template_string(VENDOR_PROFILE_PAGE, vendor=vendor)

@app.route('/vendor_dashboard')
@login_required
def vendor_dashboard():

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute("""
    SELECT q.*, u.name 
    FROM quotation_requests q
    JOIN users u ON q.builder_id = u.id
    WHERE q.vendor_id=?
    """, (session['user_id'],))

    requests = c.fetchall()

    conn.close()

    return render_template_string(
        VENDOR_DASHBOARD,
        requests=requests
    )

@app.route('/vendors')
@login_required
def vendors():

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute("SELECT * FROM vendor_details")
    vendors = c.fetchall()

    # Fetch quotation requests of this builder
    c.execute("""
    SELECT * FROM quotation_requests 
    WHERE builder_id=?
    """, (session['user_id'],))

    quotes = c.fetchall()

    conn.close()

    return render_template_string(
        VENDOR_LIST_PAGE,
        vendors=vendors,
        quotes=quotes
    )

@app.route('/vendor_view/<int:vendor_id>')
@login_required
def vendor_view(vendor_id):

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute("SELECT * FROM vendor_details WHERE id=?", (vendor_id,))
    vendor = c.fetchone()

    conn.close()

    return render_template_string(
        VENDOR_VIEW_PAGE,
        vendor=vendor
    )


@app.route('/request_quote/<int:vendor_id>', methods=['GET','POST'])
@login_required
def request_quote(vendor_id):

    # ❌ Only builder allowed
    if session.get("account_type") != "builder":
        return redirect(url_for('planner'))

    if request.method == 'POST':

        material = request.form['material']
        quantity = request.form['quantity']

        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()

        # 🔥 IMPORTANT FIX: Get vendor USER ID (not vendor table ID)
        c.execute("SELECT user_id FROM vendor_details WHERE id=?", (vendor_id,))
        vendor_user = c.fetchone()

        if not vendor_user:
            conn.close()
            return "Vendor not found"

        vendor_user_id = vendor_user[0]

        # ✅ Insert correct data
        c.execute("""
        INSERT INTO quotation_requests
        (builder_id, vendor_id, project_id, material, quantity, status, created_at)
        VALUES (?,?,?,?,?,?,?)
        """, (
            session['user_id'],      # builder ID
            vendor_user_id,          # ✅ FIXED vendor USER ID
            0,
            material,
            quantity,
            "Pending",
            datetime.now().strftime('%Y-%m-%d %H:%M')
        ))

        conn.commit()
        conn.close()

        return redirect(url_for('vendors'))

    return render_template_string(REQUEST_QUOTE_PAGE)


from flask import send_from_directory

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/accept_quote/<int:qid>')
@login_required
def accept_quote(qid):

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute("UPDATE quotation_requests SET status='Accepted' WHERE id=?", (qid,))
    conn.commit()
    conn.close()

    return redirect(url_for('vendor_dashboard'))


@app.route('/reject_quote/<int:qid>')
@login_required
def reject_quote(qid):

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute("UPDATE quotation_requests SET status='Rejected' WHERE id=?", (qid,))
    conn.commit()
    conn.close()

    return redirect(url_for('vendor_dashboard'))

@app.route('/quote_view/<int:qid>')
@login_required
def quote_view(qid):

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute("""
    SELECT q.*, u.name, u.email 
    FROM quotation_requests q
    JOIN users u ON q.builder_id = u.id
    WHERE q.id=?
    """, (qid,))

    q = c.fetchone()
    conn.close()

    if q:
        data = {
            "material": q[4],
            "quantity": q[5],
            "status": q[6],
            "name": q[8],
            "email": q[9]
        }
        return render_template_string(QUOTE_VIEW_PAGE, data=data)

    return redirect(url_for('vendor_dashboard'))

@app.route('/logout')
def logout():
    session.clear(); return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)