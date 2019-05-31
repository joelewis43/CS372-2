from socket import *
import sys



#--------------------ERROR HANDLING--------------------#
def argError(msg):
    print(msg)
    print("Correct Usage:\n\npython {} <serverName> <PORT> -l <dataPort>".format(sys.argv[0]))
    print("OR")
    print("python {} <serverName> <PORT> -g <fileName> <dataPort>\n".format(sys.argv[0]))
    exit(1)

def errorMsg(msg):
    print(msg)
    exit(1)



#--------------------CLA VALIDATION--------------------#
def validateArgs():

    if '-l' == sys.argv[3]:
        return parseListArgs()
    elif '-g' == sys.argv[3]:
        return parseGetArgs()
    else:
        argError("Bad Command!")

def parseListArgs():
    # ./prog server port -l dataPort              length: 5

    if len(sys.argv) != 5:
        argError("Bad Arguments")

    args = {}

    try:
        args['server'] = sys.argv[1]
        args['port'] = int(sys.argv[2])
        args['command'] = '-l'
        args['dataPort'] = int(sys.argv[4])
    except ValueError:
        errorMsg("Bad port number(s)")

    return args

def parseGetArgs():
    # ./prog server port -g fileName dataPort     length: 6

    if len(sys.argv) != 6:
        argError("Bad Arguments")

    args = {}

    try:
        args['server'] = sys.argv[1]
        args['port'] = int(sys.argv[2])
        args['command'] = '-g'
        args['fileName'] = sys.argv[4]
        args['dataPort'] = int(sys.argv[5])
    except ValueError:
        errorMsg("Bad port number(s)")

    return args



#----------------------SOCKER PREP---------------------#
def openPSocket(args):
    P = socket(AF_INET, SOCK_STREAM)
    P.connect((args['server'], args['port']))
    return P

def lsitenQSocket(args):
    Q = socket(AF_INET, SOCK_STREAM)
    Q.bind(('', args['dataPort']))
    Q.listen(1)
    Qconnection, clientAddress = Q.accept()

    if args['command'] == '-g':
        print("Receiving directory structure from {}:{}".format(clientAddress[0], clientAddress[1]))
    else:
        print("Receiving "{}" from {}:{}".format(args['fileName'], clientAddress[0], clientAddress[1]))
        
    return Q, Qconnection

def closeSocket(s):
    s.close()



#---------------------COMMUNICATION--------------------#
def sendCommand(args, P):
    
    if args['command'] == '-l':
        command = '-l'
    else:
        command = "-g " + args['fileName']

    command = command + " " + str(args['dataPort'])

    P.send(command)

def finalThoughts(args):

    if args['command'] == '-g':
        print("Something about the files")
    else:
        print("File transfer complete")







if __name__ == '__main__':

    # make sure user provided correct commands
    args = validateArgs()

    # open the CONTROL socket (server is listening)
    P = openPSocket(args)

    # send the command
    sendCommand(args, P)

    # listen on DATA port (server will initialize)
    Q, Qconnection = lsitenQSocket(args)

    # get data (NEEDS TO BE REFACTORED TO PROCESS DATA BASED ON COMMAND)
    while 1:
        msg = Qconnection.recv(2048)
        if not msg: break
        print(msg)
    
    # close CONTROL socket
    closeSocket(P)

    # close DATA socket
    closeSocket(Qconnection)

    # print closing message
    finalThoughts(args)