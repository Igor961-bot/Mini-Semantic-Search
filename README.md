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

## Testing

Aby uruchomić testy, upewnij się, że Twoje wirtualne środowisko `.venv` jest aktywne.

**1. Testy jednostkowe (Unit Tests):**
Weryfikują poprawność działania głównych ścieżek API.
```powershell
.\.venv\Scripts\python -m pytest
```

**2. Testy wydajnościowe (Performance Tests):**
Zanim uruchomisz test wydajnościowy, upewnij się, że serwer głównej aplikacji (Local run) działa w tle. Następnie w nowym terminalu wpisz:
```powershell
.\.venv\Scripts\python tests/performance_test.py
```

## Architektura i Uzasadnienie Wyboru Komponentów

Zgodnie z założeniami projektowymi, system wykorzystuje architekturę warstwową. Wybór technologii został podyktowany optymalizacją procesu przetwarzania danych wektorowych:

* **FastAPI (Backend & API):** Wybrano ze względu na natywną asynchroniczność (niezbędną przy równoległym pobieraniu danych z zewnętrznych źródeł jak OpenAlex czy Europe PMC), szybkość działania oraz wbudowane generowanie dokumentacji (Swagger UI).
* **ChromaDB (Baza Danych):** Wektorowa baza danych idealna do wyszukiwania semantycznego. Działa jako wbudowana baza plikowa z systemem stałego wolumenu (Persistent volume), co minimalizuje narzut infrastrukturalny, zachowując wysoką wydajność przy przeszukiwaniu fragmentów tekstów.
* **Docker & Docker Compose (Środowisko Uruchomieniowe):** Zapewnia izolację i powtarzalność środowisk. Podział na środowisko deweloperskie i produkcyjne symuluje profesjonalny cykl życia oprogramowania.
* **Pytest & HTTPX (Testy):** Użyte do spełnienia wymogu testów jednostkowych oraz wydajnościowych bez konieczności instalowania ciężkich zewnętrznych narzędzi.


### Diagram Komponentów
![Diagram Komponentów](docs/component_diagram.png)

### Diagram Wdrożeniowy (Deployment)
![Diagram Wdrożeniowy](docs/deployment_diagram.png)
