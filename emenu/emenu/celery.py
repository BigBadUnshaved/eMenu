import os

from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "emenu.settings")

app = Celery("emenu")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
