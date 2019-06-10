#### Server.py ####
# Written by Kadin Schermers
# For CSCI 4211
# UMN Spring 2019
# Prof David Du

#imports
import socket
from _thread import *
import threading

#global variables
print_lock = threading.Lock()
port_lock = threading.Lock()
peer_lock = threading.Lock()
peers = []
peerCount = 0
portNum = 5001
staticPort = 5001

# thread fuction for each connection to M
def threaded(c):

    global portNum
    global staticPort
    global peerCount
    cname = ''
    cname = c.recv(64)
    cname = cname.decode()

    while (True): #runs until valid flag is received and port info gets sent
        buf = c.recv(64)
        buf = buf.decode()
        print_lock.acquire()
        print('***Message Received From Client', cname , ':', buf, '***')
        print_lock.release()
        if (buf == 'P2P'):
            print_lock.acquire()
            print('***Valid Flag***')
            print_lock.release()
            message = ''
            message = str(portNum) + ','  + str(staticPort)
            port_lock.acquire()
            portNum += 2
            port_lock.release()
            c.send(message.encode())
            break
        else:
            print('***Invalid Flag***')
            continue

    c.close()

#main method. handles incoming connections
def main():

    global peerCount

    print('***Server Process Starting***')
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serversocket.bind(('localhost', 5000))
    serversocket.listen(5) # become a server socket, maximum 5 connections

    while (True): #loop to spawn threads for each new connection
        print('***Waiting for Connection***')
        connection, address = serversocket.accept()
        print('***Connected to', address[0], '***')
        start_new_thread(threaded, (connection,))

    serversocket.close()


if __name__=='__main__':
    main()
