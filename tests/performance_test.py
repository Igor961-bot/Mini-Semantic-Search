import time
import httpx

URL = "http://127.0.0.1:8000/"
TOTAL_REQUESTS = 100  

print(f"Rozpoczynam test wydajnościowy dla: {URL}")
print(f"Wysyłam {TOTAL_REQUESTS} zapytań sekwencyjnie...")

times = []
success_count = 0

start_suite = time.time()

with httpx.Client() as client:
    for i in range(TOTAL_REQUESTS):
        start_req = time.time()
        try:
            response = client.get(URL)
            end_req = time.time()
            
            if response.status_code == 200:
                success_count += 1
                times.append(end_req - start_req)
        except Exception as e:
            print(f"Błąd przy zapytaniu {i}: {e}")

end_suite = time.time()
total_duration = end_suite - start_suite

if times:
    avg_time = sum(times) / len(times)
    max_time = max(times)
    min_time = min(times)
    
    print("\n=== RAPORT Z TESTU WYDAJNOŚCIOWEGO ===")
    print(f"Łączny czas testu: {total_duration:.2f} sekund")
    print(f"Udane zapytania: {success_count}/{TOTAL_REQUESTS}")
    print(f"Średni czas odpowiedzi: {avg_time * 1000:.2f} ms")
    print(f"Najszybsze zapytanie: {min_time * 1000:.2f} ms")
    print(f"Najwolniejsze zapytanie: {max_time * 1000:.2f} ms")
    print("=======================================")
else:
    print("Nie udało się zebrać danych wydajnościowych. Upewnij się, że serwer działa!")