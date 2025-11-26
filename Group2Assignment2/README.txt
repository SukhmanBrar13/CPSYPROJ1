How to start the app:

cd Group2Assignment2/backend
venv\Scripts\activate
uvicorn app.main:app --reload

cd Group2Assignment2/frontend
npm run dev

----
UPDATED VERSION FOR ASSIGNMENT 3

cd Group2Assignment2/backend
az login
$env:AZURE_SUBSCRIPTION_ID = "98322b17-807f-40d8-b005-597ea043aa9b"
$env:AZURE_RESOURCE_GROUP  = "group2assn3"
uvicorn app.main:app --reload

cd Group2Assignment2/frontend
npm run dev