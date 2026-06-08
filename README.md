# Backend
cd backend
python -m venv venv
source venv/bin/activate   # Linux/Mac || source venv/Scripts/activate      # Windows
pip install -r requirements.txt
python ingestar.py          # Indexa los docs a ChromaDB
uvicorn main:app --reload

# Frontend (otra terminal)
cd frontend
npm install
npm run dev