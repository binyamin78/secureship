"""Simple load generator for the HPA demo (standard library only).

    python scripts/load_test.py                 # 3 minutes, 20 threads
    python scripts/load_test.py --seconds 60 --threads 40

Prints requests/sec and how many different pods answered - watch the number
of pods grow in Grafana while this runs.
"""
import argparse
import json
import threading
import time
import urllib.request
from collections import Counter

parser = argparse.ArgumentParser()
parser.add_argument("--url", default="http://localhost:8080/api/work?rounds=60000")
parser.add_argument("--seconds", type=int, default=180)
parser.add_argument("--threads", type=int, default=20)
args = parser.parse_args()

pods: Counter = Counter()
errors = 0
lock = threading.Lock()
stop_at = time.time() + args.seconds


def worker() -> None:
    global errors
    while time.time() < stop_at:
        try:
            with urllib.request.urlopen(args.url, timeout=10) as res:
                pod = json.load(res)["pod"]
            with lock:
                pods[pod] += 1
        except Exception:
            with lock:
                errors += 1


threads = [threading.Thread(target=worker, daemon=True) for _ in range(args.threads)]
for t in threads:
    t.start()

last_total, started = 0, time.time()
while any(t.is_alive() for t in threads):
    time.sleep(5)
    with lock:
        total = sum(pods.values())
        print(f"[{int(time.time() - started):>4}s] {(total - last_total) / 5:6.1f} req/s | "
              f"pods answering: {len(pods)} | errors: {errors}")
        last_total = total

print("\nRequests per pod:")
for pod, n in pods.most_common():
    print(f"  {pod}: {n}")
