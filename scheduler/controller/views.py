from django.shortcuts import render
from profiles.models import User
from providers.models import Job
from providers.views import add_task_to_queue
from datetime import datetime, timedelta
from pytz import timezone
from scheduler.settings import TIME_ZONE
from random import randint 

# Create your views here.
def request_handler(request,service,start_time,run_async = False):
    print("Request handler called", request, service, start_time)
    provider = find_provider()
    if provider is None : 
        return None,None,None,None
    
    job = Job.objects.create(provider = provider,service = service , start_time = start_time)
    job.save()
    task_link = service.docker_container 
    task_developer = service.developer
    task = {"task_link" : task_link, "task_developer" : task_developer}
    provider_username = 'username' + str(provider.user_id)
    print(request, task, provider_username)
    response = add_task_to_queue(request, task, provider_username)

    print("response from provider: ", response)
    job.refresh_from_db()
    job.pull_time = response['pull_time']
    job.run_time = response['run_time']
    job.total_time = response['total_time']
    job.cost = calculate_cost(response['total_time'])
    job.finished = True
    job.save()
    providing_time = int(((job.ack_time - job.start_time)/timedelta(microseconds=1))/1000) # Providing time in milliseconds
    return response, provider.user_id, providing_time, str(job.id)
    
def calculate_cost(total_time):
    return total_time*0.01

def find_provider():

    ready_providers = User.objects.filter(
        active = True , ready = True , 
        last_ready_signal__gte = datetime.now(tz=timezone(TIME_ZONE)) - timedelta(minutes=1)
    )
    
    if len(ready_providers) == 0: 
        return

    return ready_providers[randint(0,len(ready_providers)-1)]

#have to add job_status get method 
