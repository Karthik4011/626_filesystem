import socket
import sys

HOST, PORT = "10.211.55.6", 60000

# Create a socket (SOCK_STREAM means a TCP socket)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    # Connect to server and send data
    sock.connect((HOST, PORT))
    ip = socket.gethostbyname(socket.gethostname())
    sock.sendall(bytes("getlockedfiles:"+'test.txt'+ "\n", "utf-8"))

    # Receive data from the server and shut down
    received = str(sock.recv(1024), "utf-8")
lists = received.split(";")
print(lists)
