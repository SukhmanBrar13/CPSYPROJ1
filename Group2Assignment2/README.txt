How to start the app:

cd Group2Assignment2/backend
venv\Scripts\activate
uvicorn app.main:app --reload

cd Group2Assignment2/frontend
npm run dev

----
UPDATED VERSION FOR ASSIGNMENT 3

# backend
cd Group2Assignment2/backend

venv\Scripts\activate

az login
$env:AZURE_SUBSCRIPTION_ID = 
$env:AZURE_RESOURCE_GROUP  = 

$env:GITHUB_CLIENT_ID=
$env:GITHUB_CLIENT_SECRET=

$env:GOOGLE_CLIENT_ID=
$env:GOOGLE_CLIENT_SECRET=

uvicorn app.main:app --reload

# frontend
cd Group2Assignment2/frontend
npm run dev