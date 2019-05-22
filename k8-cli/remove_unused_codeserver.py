#!/usr/bin/env python3

import subprocess


def get_code_servers():

    s1 = subprocess.Popen(['kubectl', 'get','pods'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    s2 = subprocess.Popen(['awk', '{print $1}'], stdin=s1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    s3 = subprocess.Popen(['grep', 'Evicted'], stdin=s2.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    s4 = subprocess.Popen(['xargs', 'kubectl', 'delete', 'pod'], stdin=s3.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


    p1 = subprocess.Popen(['kubectl', 'get','pods'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p2 = subprocess.Popen(['awk', '{print $1}'], stdin=p1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p3 = subprocess.Popen(['grep', 'code-server*'], stdin=p2.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    stdout, stderr = p3.communicate() 
    return stdout.decode('utf-8').split("\n")[:-1]

def remove_code_servers_without_clients(code_servers):
    for pod in code_servers:
        p1 = subprocess.Popen(['kubectl', 'logs', pod], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p1.communicate()
        pod_logs = stdout.decode('utf-8').split('WebSocket ')[1:]
        if not clients_open(pod_logs):
            delete_pod(pod)
            print(pod[:20] + " deleted")
        else:
            print(pod[:20] + " NOT deleted")


def clients_open(pod_logs):
    opened = 0
    closed = 0
    for i in pod_logs:
        if "opened" in i:
            opened += 1
        elif "closed" in i:
            closed += 1
    return opened > closed or (opened==0 and closed==0)

def delete_pod(pod):
    p1 = subprocess.Popen(['kubectl', 'delete','-n', 'default', 'deployment', pod[:20]], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p2 = subprocess.Popen(['kubectl', 'delete','service', pod[:20]], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

if __name__ == '__main__':
    print('Hello, I will now remove all code-server deployments that has no clients opened.')
    code_servers = get_code_servers()
    remove_code_servers_without_clients(code_servers)
    print("Done")
        
        