import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotel_api.settings')


app = Celery('hotel_api')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


# For test purposes
@app.on_after_configure.connect
def startup_tasks(sender, **kwargs):
    sender.send_task('bookings.tasks.expire_pending_bookings')

    sender.send_task('bookings.tasks.manage_room_availability')
