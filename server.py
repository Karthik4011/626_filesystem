import os
from fileinput import fileno

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import socket

# Used to display logging to stdout
import logging.config
import sys

from datetime import datetime

#######################################
# Global Logger
#######################################
# Set logging configuration

logging.basicConfig(filename='fileServer.log', level=logging.DEBUG, filemode='w',
                    format='%(asctime)s\tLogger: %(name)s\tLevel: %(levelname)s\tEvent: %(message)s',
                    datefmt='%Y:%m:%d %H:%M:%S')

# logging.basicConfig(filename='fileServer.log', level=logging.DEBUG, filemode='w',
# format='%(asctime)s\tLogger: %(name)s\tLevel: %(levelname)s\tEvent: %(message)s',
# datefmt='%Y:%m:%d %H:%M:%S')

# Create Logger
serverLog = logging.getLogger("SEDFS Server")

# Create Handler, set level to at least DEBUG
loggingHandler = logging.StreamHandler(stream=sys.stdout)
serverLog.addHandler(loggingHandler)
serverLog.setLevel(logging.DEBUG)

known_servers = []
listOfNo = ["no", "n", "NO", "N"]

# MainServer details
MAINSERVERHOST, MAINSEREVERPORT = "10.211.55.6", 60000

MAINSERVERHOST = input("ENTER MAINSERVER IP ADDRESS \n>>")


class SEDFS_server(FTPServer):

    # init for child class
    def __init__(self, address, childHandler):
        # init Parent Class
        FTPServer.__init__(self, address, childHandler)

        return


class SEDFS_handler(FTPHandler):
    user = ""  # save global username

    # child handler init
    def __init__(self, conn, server, ioloop):
        # Log handler event
        print(datetime.now().strftime("DATE: %Y:%m:%d\tTIME: %H:%M:%S\tEVENT: "), end="")
        serverLog.info("[+] SEDFS Handle Started")

        # parent handler init
        FTPHandler.__init__(self, conn, server)

        return

    # Polymorph of on_login
    # def on_login(self, username):
    # user = username
    # self.on_login(username)


# Configuration function for loading users
def load_users(authorizer):

    # Create a socket (SOCK_STREAM means a TCP socket)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # Connect to server and send data
        sock.connect((MAINSERVERHOST, MAINSEREVERPORT))
        sock.sendall(bytes("userdata"+ "\n", "utf-8"))

        # Receive users data from the server and shut down
        received = str(sock.recv(1024), "utf-8")
    lists = received.split(";")
    print(lists)
    try:
        file = open("configuration files/userConfig.txt", mode='r')
    except:
        serverLog.info("[*] WARNING configuration files/userConfig.txt not found, no users added")
        return

    lines = file.readlines()
    file.close()

    # Try to add NEW SYSTEM GROUP sedfs
    try:
        os.system('sudo groupadd --system sedfs')

    except Exception as E:
        print(E)

    for line in lists:

        # remove whitespaces, delimiters, append to authorizedUsers
        line = line.strip()
        user = line.split(',')

        # Create User Object and Append to "authorizedUsers"
        try:
            # USERNAME, PASSWORD, HOME, PERMISSIONS
            authorizer.add_user(user[0], user[1], user[2], user[3])
            serverLog.info("[+] SEDFS User added: %s" % user[0])

        except Exception as E:
            print(E)

        try:
            os.system(
                'sudo adduser --system --shell=/sbin/nologin --disabled-login --disabled-password --ingroup sedfs --no-create-home  --quiet ' +
                user[0])
            # serverLog.info("[+] Local System added: %s" % user[0])

        except Exception as E:
            print(E)

    return


def server_sync():
    while 1:
        print("Enter IP of server to sync\n >> ", end='')
        serverIP = input().strip()
        full_remote_path = input("Please enter the FULL REMOTE path of the directory\n >> ").strip()

        current_directory = os.getcwd()
        current_directory.replace("\\", "/")
        current_directory = current_directory + "/SEDFS"
        full_string = "csync " + current_directory + " sftp://csync@" + serverIP + ":50001" + full_remote_path

        print("Attempting csync...", full_string)

        try:
            os.system(full_string)
            known_servers.append(serverIP)
        except Exception as E:
            print(E)

        ans = input("Do you wish to continue?\n >> ")
        if ans in listOfNo:
            break


def SEDFS_setup():
    # Get local address information
    server_IP = socket.gethostbyname(socket.gethostname())
    address = (server_IP, 50000)

    # Instantiate a dummy authorizer for managing 'virtual' users
    authorizer = DummyAuthorizer()

    # if base directory doesnt exist, make it
    if not os.path.exists("SEDFS"):
        os.mkdir("SEDFS")

    # LOAD username, password, home directory, permissions
    authorizer.add_user('sudo', 'password', './SEDFS', perm='elradfmwMT')
    load_users(authorizer)

    # Instantiate FTP handler class
    handler = SEDFS_handler
    handler.authorizer = authorizer
    handler.banner = " << Welcome to SEDFS (Simple Encrypted Distributed File System)"

    # Instantiate FTP server class and listen on ??????:50000
    server = SEDFS_server(address, handler)

    # set a limit for connections
    server.max_cons = 100000
    server.max_cons_per_ip = 5

    # sending this server details to main server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # Connect to server and send data
        sock.connect((MAINSERVERHOST, MAINSEREVERPORT))
        sock.sendall(bytes("serverip:"+server_IP+"\n", "utf-8"))

    # start ftp server
    server.serve_forever()


if __name__ == '__main__':
    SEDFS_setup()
