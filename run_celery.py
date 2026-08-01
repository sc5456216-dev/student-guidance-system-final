import os
import sys

print('--> [1/3] Script starting...')

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_guidance_system.settings')
django.setup()
print('--> [2/3] Django loaded successfully.')

from student_guidance_system.celery import app

if __name__ == '__main__':
    print('--> [3/3] Starting Celery worker...')
    worker = app.Worker(loglevel='INFO', pool='solo')
    worker.start()
