from fabric import Connection, transfer
import time 
import subprocess
from multiprocessing import Process
import os

prev_ip = "10.8.1.46"

def start_server(ip):
    c = Connection (host=ip, port=222, user="user", connect_kwargs={'password': 'user123'})
    if(prev_ip != ip):    
        try:
            local_path = "/home/user/Documents/Serverless_Scheduler/SchedInfo.csv"
            remote_path = "/home/user/Documents/Serverless_Scheduler/SchedInfo.csv"

            # Create an SCP transfer object
            transfer_var = transfer.Transfer(c)

            # Use the SCP transfer object to upload the file to the remote server
            transfer_var.put(local=local_path, remote=remote_path)
        except Exception as e:
            print(f"Error in copying the file from {ip}: {str(e)}")
    try:
        print("Starting ",ip)
        c.run("/home/user/Documents/Serverless_Scheduler/script.sh")
    except Exception as e:
        print(f"Error starting server on {ip}: {str(e)}")
    
def stop_server(ip):
    c = Connection (host=ip, port=222, user="user", connect_kwargs={'password': 'user123'})
    try:
        c.run('fuser -k 8000/tcp')

    except Exception as e:
        print(f"Error stopping server on {ip}: {str(e)}")

def round_robin():
    ips = ['10.8.1.46', '10.8.1.48', '10.8.1.45']
  
    # while True:
    for ip in ips:            
        p = Process(target=start_server, args=(ip,))
        p.start()
        print("Going to sleep")
        data = '{"chained": false, "numberOfInvocations": 2, "input": "None", "runMultipleInvocations": false}'
        curl_command = [
            'curl',
            '-X', 'POST',                  # HTTP POST method (adjust as needed)
            'http://' + ip + ':8000/developers/run_service/3',       # URL of the API you want to call
            '-H', 'Content-Type: application/json',  # Headers (adjust as needed)
            '-H', 'User-Agent: Thunder Client (https://www.thunderclient.com)',
            '-d', data       # JSON data to send in the request body
        ]
        # time.sleep(100) 
        time.sleep(7)
        try:
            response = subprocess.check_output(curl_command, stderr=subprocess.STDOUT)
            print(response.decode('utf-8'))  # Print the response from the server
        except subprocess.CalledProcessError as e:
            print(f"Error: {e.returncode}\n{e.output.decode('utf-8')}") 
        print("Stoping ",ip)
        stop_server(ip)
        prev_ip = ip

round_robin()
