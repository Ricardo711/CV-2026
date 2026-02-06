Provisional backend: This will load a provisional model with 1 enpoint (predict). The full backend will be similar. Use it to integrate the frontend in the meantime.


How to install dependencies.
- Create virtual enviroment:
python -m venv .venv 

- activate enviroment:
.venv\Scripts\activate 

- Install dependencies:
pip install fastapi uvicorn motor pydantic-settings python-dotenv torch

- Run predict.py
uvicorn predict:app --reload

