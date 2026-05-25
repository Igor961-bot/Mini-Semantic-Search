# Mini Semantic Search

## Local run

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
UI: http://127.0.0.1:8000/

open:

- `http://127.0.0.1:8000`
- `http://127.0.0.1:8000/docs`

## Docker dev

```powershell
docker compose -f docker-compose.dev.yml up --build
```

## Docker / VM

```powershell
docker compose -f docker-compose.prod.yml up --build -d
```

open:

- `http://<vm_ip>:8000`
- `http://<vm_ip>:8000/docs`

## Demo data

```powershell
.\.venv\Scripts\python scripts\load_demo_data.py
```
