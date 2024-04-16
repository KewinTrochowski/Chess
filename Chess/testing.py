import subprocess

ip = '127.0.0.1'
port = 55555
command = f'start cmd.exe /k python tcp_server.py {ip} {port}'
subprocess.Popen(command, shell=True)