cd C:\HW3_1
git pull https://%TESTAPP_GIT_PAT%@github.com/angelali0510/homework_3-1
venv\Scripts\python.exe -m pip install -r requirements.txt
venv\Scripts\python.exe server.py
