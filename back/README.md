## Backend (FastAPI + Motor + MongoDB)

### Requisitos
- Python 3.11+
- MongoDB local (ej: mongodb://localhost:27017)

### Setup
```bash
cd back
python -m venv .venv # Crea el entorno virtual
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
pip install -U pip
pip install -e .
```

- Ejecutar el proyecto
uvicorn app.main:app --reload
