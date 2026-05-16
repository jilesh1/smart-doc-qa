# Smart Document Q&A

## Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
copy .env.example .env
# add your ANTHROPIC_API_KEY in .env
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Frontend
```bash
cd frontend
npm install
npm start
```

Open: http://localhost:3000
