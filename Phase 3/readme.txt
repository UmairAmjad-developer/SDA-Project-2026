Phase 3 - Generic Concurrent Real-Time Pipeline

Main file:
- main.py

Where to place files:
- config file path: Phase3/config.json
- dataset location: Phase3/data/

How to run:
1) cd Phase3
2) python main.py

Output behavior:
- Existing live dashboard image is still generated in out/live_dashboard_latest.png
- After CSV processing completes, final data summary is printed on console
- Additional summary graphs are generated in out/summary_*.png

Core guarantees:
- Generic schema mapping from config.json
- Multiprocessing producer-consumer pipeline with bounded queues
- Stateless cryptographic signature verification (PBKDF2-HMAC SHA256)
- Stateful stream re-sequencing + running average
- Telemetry observer with queue backpressure color states

Signature reference:
SECRET_KEY = "sda_spring_2026_secure_key"
ITERATIONS = 100000
raw_value = sensor data rounded to two decimal places

Formula:
hashlib.pbkdf2_hmac(
    hash_name='sha256',
    password=SECRET_KEY.encode('utf-8'),
    salt=raw_value_str.encode('utf-8'),
    iterations=ITERATIONS
).hex()
