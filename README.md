# Abrir todo el proyecto
En terminal: ./start.ps1

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

# n8n
docker run -d --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n n8nio/n8n


# LLM Studio
Instalar Qwen2.5-VL-3B-Instruct-GGUF


# DEPLOY

Frontend: https://final-project-ironhack-mu.vercel.app/

Backend: lively-clarity-production-2458.up.railway.app