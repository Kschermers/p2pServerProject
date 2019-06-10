#### Client.py ####
# Written by Kadin Schermers
# For CSCI 4211
# UMN Spring 2019
# Prof David Du

#imports
import socket
import os

###LOOK HERE FOR CHANGING TIMEOUT VALUE###
timeout = 30
###STOP LOOKING###

#Global varaibles used at multiple spots in the project
name = ''
connectMSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
p2pServSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
p2pClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
fileServSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
fileClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
localTopo = []  #connected port number list
localNames = [] #connected name list
attemptedConnects = 0
myPort = ''
referredPort = ''

def main():
    #main method that handles user choices for joining/downloading/quitting
    global p2pClientSocket
    global p2p2pServSocket
    global connectMSocket
    global fileServSocket
    global myPort
    global timeout

    print('Select Option:')
    print('\nAdd Server to P2P (1) or Download File (2):')
    option = input()
    alreadyConnected = False

    while (option != 'Stop'): # user wants to continue with some action
        if (not alreadyConnected): # isnt part if P2P yet
            if (option == '1'):
                connectToP2P()
                alreadyConnected = True
                print('***Stay on P2P (1), Download File (2), or Quit (Stop)?***')
                option = input()

            elif (option == '2'):
                connectToM()
                downloadFile()
            else: #invalid choice
                print('\n***Pick Either 1 or 2***\n')
                main()
        else: #already joined P2P Network
            if (option == '2'):
                downloadFile()
                print('***Stay on P2P (1), Download File (2), or Quit (Stop)?***')
                option = input()
            if (option == '1'):
                #this was removed from its own method due to issues when a user
                #does not want to download again, I had trouble properly handling
                #the cross over of information from one method to another
                # (look at line 85 to see I use option var within code)
                print('\n***Connected to P2P Network***')
                fileServSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                fileServSocket.bind(('127.0.0.1', (myPort+50)))
                fileServSocket.listen(1)
                fileServSocket.settimeout(timeout)

                while (True): #loops while user wants to allow other processes to download its files
                    print('***Allowing Downloads***')

                    try: # error checking for timeouts on accept calls. discussed in README
                        c, a = fileServSocket.accept()
                    except socket.timeout:
                        pass
                        print("\nDo you want to continue waiting for download requests? (y/n)")
                        confInput = input()
                        if (confInput == 'y' or confInput == 'Y'):
                            continue
                        else:
                            print('***Stay on P2P (1), Download File (2), or Quit (Stop)?***')
                            option = input()
                            fileServSocket.close()
                            fileServSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            break
                    else: #connection for download accepted. 'Download' and send file
                        fileName = c.recv(64)
                        fileName = fileName.decode()
                        print('\n***File Request:', a[1], ',', fileName, '***')
                        fileName = 'ServerFiles/' + fileName + '.txt'
                        if (os.path.exists(fileName)):
                            file = open(fileName,'r')
                            c.send(file.read().encode())
                        else:
                            c.send('No File Found'.encode())
                            print('\n***Requested File Does Not Exist***')
            if (option == 'Stop'):
                print('Thank you for being a part of the P2P Network!')

    fileServSocket.close()
    fileClientSocket.close()
    p2pServSocket.close()
    p2pClientSocket.close()
    print('\n***Ending Client Process***')

def connectToM():
    #method that handles connection to M and getting port info
    global connectMSocket
    global myPort
    global referredPort
    global name

    print('\nGive your server on ID (i.e. S1):')
    name = input()
    localNames.append(name)
    connectMSocket.connect(('localhost', 5000))

    messageToM = name
    connectMSocket.send(messageToM.encode())
    messageFromM = ''

    while (True): # loops until valid flag is sent

        print('\nAwaiting message input (q to quit): ')
        messageToM = input()
        connectMSocket.send(messageToM.encode())

        if (messageToM == 'P2P'):

            messageFromM = connectMSocket.recv(64)
            messageFromM = messageFromM.decode()
            myPort, referredPort = messageFromM.split(',')
            myPort = int(myPort)
            referredPort = int(referredPort)
            break
        else:
            continue

    connectMSocket.close()

def connectToP2P():
    # called when a user wants to join P2P network
    connectToM()

    global p2pServSocket
    global p2pClientSocket
    global myPort
    global referredPort
    global timeout
    connectCount = 0
    hasClientConnection = False
    isFirstServ = False
    wantsQuit = False

    p2pServSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    p2pServSocket.bind(('127.0.0.1', myPort))
    p2pServSocket.settimeout(timeout);
    p2pClientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    p2pClientSocket.bind(('127.0.0.1', myPort+1))

    print('\n***Server Scoket Binded to: 127.0.0.1:', myPort, '***')
    print('***Client Socket Binded to: 127.0.0.1:',myPort+1, '***')
    localTopo.append(('127.0.0.1', myPort))

    if (myPort == referredPort): # this means its the first server to connect
        # set First Server values
        p2pServSocket.listen(2)
        isFirstServ = True
        totalConnects = 1;
        serverNum = 1;
    else:

        p2pServSocket.listen(1)
        totalConnects = ((myPort - 5001) / 2) + 1
        serverNum = ((myPort - 5001) / 2) + 1

    while(True): #loops for as long as user wants to alllow new connections
        if (isFirstServ): #The first server to join the P2P network
            maxConnects = 2
            if (connectCount < maxConnects):
                print('\n***Waiting to Fill Connections***')

                try: # error checking for timeouts on accept calls. discussed in README
                    c, a = p2pServSocket.accept()
                except socket.timeout:
                    pass
                    print("\nDo you want to continue waiting for connections? (y/n)")
                    confInput = input()
                    if (confInput == 'y' or confInput == 'Y'):
                        continue
                    else:
                        callForTopo()
                        break
                except:
                    raise
                else:
                    totalConnects += 1

                    print('\n***Connection Granted to 127.0.0.1:', a[1], '***')
                    connectCount += 1
                    localTopo.append((a[1]-1))
                    connectConfMessage = '***Connected***'
                    c.send(connectConfMessage.encode())
                    nameRecv = c.recv(64)
                    localNames.append(nameRecv.decode())
            else:
                print('\n***Waiting to Forward Connections***')

                try: # error checking for timeouts on accept calls. discussed in README
                    c, a = p2pServSocket.accept()
                except socket.timeout:
                    pass
                    print("\nDo you want to continue waiting for connections? (y/n)")
                    confInput = input()
                    if (confInput == 'y' or confInput == 'Y'):
                        continue
                    else:
                        callForTopo()
                        break
                except:
                    raise
                else:
                    totalConnects += 1

                    print('\n***Connection Attempted by 127.0.0.1:', a[1], '***')

                    connectConfMessage = '5003'
                    c.send(connectConfMessage.encode())
        else: #Servers that aren't the first to connect to P2P network
            if (not wantsQuit):
                maxConnects = 1
                print('\n***Attempting Connection to: 127.0.0.1:', referredPort , '***')
                p2pClientSocket.connect(('127.0.0.1',referredPort))
                connectConfMessage = p2pClientSocket.recv(64)
                connectConfMessage = connectConfMessage.decode()
                if (connectConfMessage == '***Connected***'): #Allowed to connect to server

                    print('\n***Connection to: 127.0.0.1:', referredPort , 'Successful***')
                    p2pClientSocket.send(name.encode());
                    hasClientConnection = True
                else: #server is full and given next port to connect to

                    print('\n***Connection to: 127.0.0.1:', referredPort, 'Forwarded***')
                    referredPort = connectConfMessage
                    referredPort = int(referredPort)

                    p2pClientSocket.close()
                    p2pClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    p2pClientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    p2pClientSocket.bind(('127.0.0.1',myPort+1))

                if(hasClientConnection):

                    while (True): #loops until user no longer wishes to accept new connections

                        if (connectCount < maxConnects):

                            print('***\nWaiting to Fill Connection***')

                            try: # error checking for timeouts on accept calls. discussed in README
                                c, a = p2pServSocket.accept()
                            except socket.timeout:
                                pass
                                print("\nDo you want to continue waiting for connections? (y/n)")
                                confInput = input()
                                if (confInput == 'y' or confInput == 'Y'):
                                    continue
                                else:
                                    callForTopo()
                                    wantsQuit = True
                                    break
                            except:
                                raise
                            else:
                                print('***\nConnection Granted to: 127.0.0.1:', a[1], '***')
                                connectCount += 1

                                totalConnects += 1

                                localTopo.append((a[1]-1))
                                connectConfMessage = '***Connected***'
                                c.send(connectConfMessage.encode())
                                nameRecv = c.recv(64)
                                localNames.append(nameRecv.decode())


                        else:

                            print('***\nWaiting to Forward Connections***')

                            try: # error checking for timeouts on accept calls. discussed in README
                                c, a = p2pServSocket.accept()
                            except socket.timeout:
                                pass
                                print("\nDo you want to continue waiting for connections? (y/n)")
                                confInput = input()
                                if (confInput == 'y' or confInput == 'Y'):
                                    continue
                                else:
                                    callForTopo()
                                    wantsQuit = True
                                    break
                            except:
                                raise
                            else:

                                totalConnects += 1

                                print('***\nConnection Attempted by: 127.0.0.1:', a[1], '***')
                                connectConfMessage = str(localTopo[1])
                                c.send(connectConfMessage.encode())
            else:
                break

def downloadFile():
    #Method is called when a user wants to download a file from P2P network
    global fileClientSocket
    global myPort
    global referredPort

    myPort = int(myPort)
    fileClientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    fileClientSocket.bind(('127.0.0.1', myPort + 51))

    while (True): #loops as long as user wants to request files to download
        print('\nName of File:')
        file = input()
        fileNum = file[-1:]
        fileNum = int(fileNum)

        while (not file.islower() or fileNum > 6): #varifies file is valid
            print('\n***File is Not Valid Format***')
            print('Name of File:')
            file = input()
            fileNum = file[-1:]
            fileNum = int(fileNum)
        # 'switch' statement to determine which server to connect to for download
        if (fileNum == 1):
            servNum = 5051
        elif (fileNum == 2):
            servNum = 5053
        elif (fileNum == 3):
            servNum = 5055
        elif (fileNum == 4):
            servNum = 5057
        elif (fileNum == 5):
            servNum = 5059
        elif (fileNum == 6):
            servNum = 5061

        if (servNum == myPort - 50): #you are the server youre requesting file from
            print('\n***This File is Already Downloaded***')
        else:
            try: # error checking valid connection
                fileClientSocket.connect(('127.0.0.1',servNum))
            except socket.error:
                print('***Server For Specified File Is Not Online***')
                break
            else:
                print('**File Request:', servNum, ',', file, '***')
                fileClientSocket.send(file.encode())
                contents = fileClientSocket.recv(64)
                contents = contents.decode()
                print('***File Contents:\n***', contents)
                fileClientSocket.close()

                print('Download Another File (y) or Quit (Stop)?')
                response = input()
                if (response == 'y'): #reestablish socket to download again
                    fileClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    myPort = int(myPort)
                    fileClientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    fileClientSocket.bind(('127.0.0.1', myPort + 51))
                    continue
                else:
                    break
    print('***Leaving File Downloader***')

def callForTopo():
    #prints out Topo info for Server
    if (len(localNames) == 3):
        print(localNames[0], ': ', localNames[1], ', ', localNames[2])
    elif (len(localNames) == 2):
        print(localNames[0], ': ', localNames[1])
    else:
        print(localNames[0], ':')

if __name__=='__main__':
    main()
