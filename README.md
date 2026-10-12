# snt-
SNT — An explainable recruitment scam detection platform that helps people check job offers before they trust them.
SNT — Smart Recruitment Scam Detection Platform


Check Before You Trust.

SNT is a full-stack recruitment fraud detection website for students, job seekers, and early-career professionals. It analyzes job offers, recruiter messages, internship offers, and suspicious URLs using transparent Python rules instead of a black-box verdict.

Live preview



Open SNT


The link above is a sandbox preview. It is not a permanent production domain.

Features

•
Responsive Home, Dashboard, Analyze Offer, Results, Scan History, Safety Guide, Profile, Settings, About, Contact, Sign in, Sign up, and Logout screens.

•
User registration and login with Werkzeug password hashing.

•
HTTP-only session authentication.

•
SQLite persistence for users, scans, and contact messages.

•
Private scan history with search and risk filtering.

•
Explainable risk scores from 0–100.

•
Risk categories:

•
Low Risk: 0–29

•
Medium Risk: 30–59

•
High Risk: 60–79

•
Critical Risk: 80–100



•
Detection rules for:

•
Registration, interview, training, processing, equipment, or activation fees.

•
Unrealistic salary or compensation promises.

•
Urgent pressure and limited-time language.

•
OTP, password, passport, banking, card, or identity-data requests.

•
Guaranteed hiring, instant joining, and no-interview claims.

•
Suspicious recruiter contact patterns.

•
Unusual recruitment language.

•
Insecure HTTP URLs.

•
Risky, lookalike, or unusual domain patterns.



•
Every result includes warning signs, supporting evidence, checks performed, recommendations, limitations, and the rule version.

•
Footer copyright notice: Copyright © 2026 SNT. All rights reserved.

Technology stack

•
Frontend: React 18, Vite, Tailwind CSS, Lucide React icons.

•
Backend: Python Flask REST API.

•
Database: SQLite.

•
Authentication: Flask sessions with Werkzeug password hashing.

•
Testing: pytest and Flask test client.

•
Production packaging: Dockerfile with a Node frontend build stage and Python runtime stage.

Project structure

Plain Text


snt/
├── backend/
│   ├── __init__.py
│   └── app.py                 # Flask API, auth, SQLite, detection engine
├── frontend/
│   ├── public/
│   │   └── manus-routes.json  # Page route manifest
│   ├── src/
│   │   ├── main.jsx           # React application and views
│   │   └── styles.css         # Responsive SNT visual system
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   ├── postcss.config.js
│   ├── tailwind.config.js
│   └── vite.config.js
├── tests/
│   └── test_app.py            # Backend integration tests
├── .env.example               # Safe configuration template
├── .gitignore                 # Files excluded from Git
├── Dockerfile                 # Production container definition
├── pyproject.toml             # pytest configuration
├── requirements.txt            # Python dependencies
└── README.md



Local setup

1. Clone the repository

Bash


git clone https://github.com/YOUR_USERNAME/snt.git
cd snt



2. Create a Python environment

Bash


python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt



3. Configure environment variables

Bash


cp .env.example .env



For local development, the defaults are sufficient. Change SNT_SECRET before any shared or hosted deployment.

4. Install frontend dependencies and build

Bash


cd frontend
npm install
npm run build
cd ..



5. Start the application

Bash


python backend/app.py



Open 
http://localhost:5000.

Frontend development mode

Start the Flask API in one terminal:

Bash


PORT=5000 python backend/app.py



Start Vite in another terminal:

Bash


cd frontend
npm run dev



Vite proxies /api requests to Flask at http://127.0.0.1:5000.

Testing

Run the backend integration suite from the project root:

Bash


pytest -q



The tests cover:

•
Health reporting.

•
Account registration.

•
Login and session authentication.

•
Password verification.

•
Critical-risk fraud detection.

•
Scan persistence and history access.

•
Logout protection.

•
Profile updates.

•
Contact form validation.

Environment variables

Variable
Required
Purpose
SNT_SECRET
Yes outside local development
Secret used to sign Flask sessions. Use a long random value.
SNT_DB
No
SQLite file path. Defaults to ./snt.db.
SNT_PUBLIC_PREVIEW
No
Set to 1 when serving behind an HTTPS embedded preview.
PORT
No
Flask listening port. Defaults to 5000.




Never commit .env, passwords, session secrets, SQLite production data, or API keys.

API endpoints

Method
Endpoint
Auth
Purpose
GET
/api/health
No
API and database health status.
POST
/api/auth/register
No
Create an account.
POST
/api/auth/login
No
Start an authenticated session.
POST
/api/auth/logout
Yes
Clear the current session.
GET
/api/me
No
Return the current user or null.
PUT
/api/profile
Yes
Update name and appearance preference.
POST
/api/scan
Yes
Analyze a message or URL and save the result.
GET
/api/scans
Yes
Return the current user's scan history.
POST
/api/contact
No
Validate and save a contact message.




Detection disclaimer

SNT uses deterministic, explainable pattern rules. It is a safety aid, not a guarantee of legitimacy or fraud. Users should independently verify the employer through official channels and should never pay to access a job or share passwords, OTPs, card PINs, or banking credentials.

Docker deployment

Build and run the production container:

Bash


docker build -t snt-platform .
docker run --rm -p 5000:5000 \
  -e SNT_SECRET="replace-with-a-long-random-secret" \
  -e PORT=5000 \
  snt-platform



The Dockerfile builds the React frontend and serves the generated files through Flask. The container exposes port 5000 and honors the PORT environment variable.

Production notes

•
Use a strong randomly generated SNT_SECRET.

•
Put Flask behind HTTPS.

•
Use secure cookie settings in hosted environments.

•
Back up or replace SQLite before scaling to multiple instances.

•
Add rate limiting, email verification, CSRF protection, and a managed database before a public production launch.

•
Do not claim that the detection rules are a definitive fraud authority.

What to commit to GitHub

Keep these files and directories:

•
backend/

•
frontend/src/

•
frontend/public/

•
frontend/index.html

•
frontend/package.json

•
frontend/package-lock.json

•
frontend/postcss.config.js

•
frontend/tailwind.config.js

•
frontend/vite.config.js

•
tests/

•
.env.example

•
.gitignore

•
Dockerfile

•
pyproject.toml

•
requirements.txt

•
README.md

Do not commit:

•
frontend/node_modules/

•
frontend/dist/ unless your hosting provider specifically requires built files.

•
.env or any file containing real secrets.

•
*.db, *.db-journal, or real user data.

•
__pycache__/ and .pytest_cache/.

First GitHub push

After creating an empty GitHub repository named snt:

Bash


cd /path/to/snt
git init
git branch -M main
git add .
git commit -m "Initial SNT recruitment scam detection platform"
git remote add origin https://github.com/YOUR_USERNAME/snt.git
git push -u origin main



Replace YOUR_USERNAME with your GitHub username. Do not paste passwords or API keys into the repository, README, commit messages, or chat.

Suggested repository description

Plain Text


SNT — an explainable recruitment scam detection platform that helps people check job offers before they trust them.



License

Add a license before making the repository public. MIT is a practical choice for an open-source hackathon project. If you do not want others to reuse the code, keep the repository private and do not add an open-source license.

