How to start the app:

# backend
cd Group2Assignment2/backend

venv\Scripts\activate

az login

$env:AZURE_SUBSCRIPTION_ID = 
$env:AZURE_RESOURCE_GROUP  = "group2assn3"

$env:GITHUB_CLIENT_ID=
$env:GITHUB_CLIENT_SECRET=

$env:GOOGLE_CLIENT_ID=
$env:GOOGLE_CLIENT_SECRET=

$env:TWOFA_SMTP_HOST="smtp.gmail.com"
$env:TWOFA_SMTP_PORT="587"

$env:TWOFA_SMTP_USER=
$env:TWOFA_SMTP_PASS=

$env:TWOFA_EMAIL_TO=

uvicorn app.main:app --reload

# frontend
cd Group2Assignment2/frontend
npm run dev