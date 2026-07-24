# Implements a simple HTTP client 
import socket 

SERVER_HOST = '127.0.0.1' 
SERVER_PORT = 8000 

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
client_socket.settimeout(5.0)
client_socket.connect((SERVER_HOST, SERVER_PORT)) 
request = input('Input HTTP request command:\n') 

if 'connection' not in request.lower():
    if not request.rstrip().endswith('\r\n\r\n'):
        request = request.rstrip() + '\r\n'
    request = request.rstrip() + '\r\nConnection: close\r\n\r\n'

client_socket.send(request.encode()) 
response = b""
try:
    while True:
        chunk = client_socket.recv(4096)
        if not chunk:
            break
        response += chunk
except socket.timeout:
    pass
finally:
    client_socket.close()

print('Server response:\n')
print(response.decode())