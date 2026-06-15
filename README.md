How to Run the Project
    1️. Clone / Extract the project----
    cd project_folder

Backend Setup (Flask)
    2️. Create virtual environment----
    cd Backend
    python -m venv venv
    source venv/bin/activate      # Mac/Linux
    venv\Scripts\activate         # Windows

3️. Install dependencies----
    pip install -r requirements.txt

4️. Run Redis server(Required for caching + Celery)[on a seperate terminal] !!VERY IMPORTANT IT RUNS BEFORE STARTING THE APP AND THROUGHOUT THE TESTING!!
    redis-server
    if port busy then kill the redis with: sudo service redis-server stop
        Then run redis-server again

5️. Start Flask backend
    python3 app.py

Backend will run at:
    http://127.0.0.1:5000


Frontend Setup (Vue 3)
    6️. Install dependencies
    cd ../Frontend
    npm install

7️. Run development server
    npm run dev

Frontend will run at:
    http://localhost:5173

Default Login Accounts (Sample)

    Admin: batman@admin.com

    Doctor: robin@doctor.com

    Patient: bane@patient.com

    Passwords for all of them are same: 12345

FOR BACKEND SCHEDULE TASKS:

    Make sure the redis server is on at all times!!

    In the vscode where the backend is running, open another terminal and start celery
        celery -A app.celery worker --loglevel=info

    In another terminal open mailhog and run the command
        MailHog
        Then open the MailHog UI (usually port 8025)

    In another terminal we want celery beat
        celery -A app.celery beat --loglevel=INFO

To test caching, do this on another terminal on the backend.
The caching has been applied to admin dashboard cause of the heavy and unchanging nature of the payload. The cache has been deleted and refetched at appropriate place/routes

    Run these commands below one by one: 
    redis-cli -n 2
    KEYS *  (this command to check the keys)
    
