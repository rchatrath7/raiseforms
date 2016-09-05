from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings
from raiseforms.settings import get_env_variable

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'raiseforms.settings')
app = Celery('raiseforms')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
url = get_env_variable('REDIS_URL')
app.conf.update(BROKER_URL=url,
                CELERY_RESULT_BACKEND=url)
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))