import os
import sys
from pathlib import Path

# Force stdout to flush immediately
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

print("--> [1/5] Initializing script...")

# Dynamically add project root directory to Python path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

print("--> [2/5] Setting up Django environment...")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_guidance_system.settings')

try:
    import django
    django.setup()
    print("--> [3/5] Django initialized successfully.")
except Exception as err:
    print(f"FAILED at Django setup: {err}")
    sys.exit(1)

try:
    print("--> [4/5] Importing Celery application...")
    from student_guidance_system.celery import app
except Exception as err:
    print(f"FAILED at Celery import: {err}")
    sys.exit(1)

if __name__ == '__main__':
    print("--> [5/5] Launching Celery worker process...")
    # Using 'solo' pool for Windows compatibility
    worker = app.Worker(
        loglevel='INFO',
        pool='solo',
    )
    worker.start()