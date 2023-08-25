from django.urls import path
from .views import make_rmq_user, index, add_task_to_queue, stop_providing, ready, not_ready,  job_ack

urlpatterns = [
    path('make_rmq_user/', make_rmq_user, name='make_rmq_user'),
    path('add_task_to_queue/', add_task_to_queue, name='add_task_to_queue'),
    path('index/', index, name='index'),
    path('stop_providing/', stop_providing, name='stop_providing'),
    path('ready/', ready, name='ready'),
    path('not_ready/', not_ready, name='not_ready'),
    path('job_ack/', job_ack, name='job_ack')
]