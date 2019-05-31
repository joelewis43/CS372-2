from socket import *
import sys
from time import sleep

def openSocket():
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('', int(sys.argv[1])))

    return serverSocket

def listResponse(server):
    Q = socket(AF_INET, SOCK_STREAM)
    Q.connect(server)
    Q.send("You there bud?")
    sleep(1)
    Q.close()

def getResponse(msg):
    pass

if __name__ == '__main__':
    
    try:

        sockID = openSocket()

        while 1:

            print("Server open on {}".format(sys.argv[1]))
            sockID.listen(1)

            Pconnection, clientAddress = sockID.accept()
            print("Connection from: {}:{}".format(clientAddress[0], clientAddress[1]))

            clientMessage = Pconnection.recv(2048)

            print(clientMessage)

            # respond to command
            if '-l' in clientMessage:

                dataPort = int(clientMessage.split(" ")[1])
                host = clientAddress[0]
                server = (host, dataPort)

                listResponse(server)
            elif '-g' in clientMessage:
                getResponse(clientMessage)

            # close CONTROL connection
            Pconnection.close()

    except KeyboardInterrupt:
        print("Exiting!")

        try:
            sockID.close()
        except:
            print("Error closing connection")
            pass

        exit(0)