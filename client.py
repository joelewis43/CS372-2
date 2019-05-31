from socket import *
import sys




class FTPclient:

    #---------------------INITIALIZER----------------------#
    def __init__(self, cla):
        self.validateArgs(cla)
        self.openP()
        self.sendCommand()
        self.listenQ()
        self.recvResponse()
        self.closeSocket(self.P)
        self.closeSocket(self.Q)
        self.finalThoughts()

    
    
        

    #--------------------CLA VALIDATION--------------------#
    def validateArgs(self, cla):

        # check for list sommand
        if '-l' == sys.argv[3]:
            self.parseListArgs(cla)

        # check for get command
        elif '-g' == sys.argv[3]:
            self.parseGetArgs(cla)

        # error in command
        else:
            self.argError(cla[0])


    def parseListArgs(self, cla):
        # ./prog server port -l dataPort              length: 5

        # check the length of the commands
        if len(cla) != 5:
            argError(cla[0])

        # parse command
        try:
            self.host = cla[1]
            self.portP = int(cla[2])
            self.command = '-l'
            self.portQ = int(cla[4])

            # make sure both ports are in range
            self.checkPorts()

        # prot numebrs were non-integers
        except ValueError:
            errorMsg("Bad port number(s)")


    def parseGetArgs(self, cla):
        # ./prog server port -g fileName dataPort     length: 6

        # check the length of the commands
        if len(cla) != 6:
            argError(cla[0])

        # parse command
        try:
            self.host = cla[1]
            self.portP = int(cla[2])
            self.command = '-g'
            self.fileName = cla[4]
            self.portQ = int(cla[5])
        
            # make sure both ports are in range
            self.checkPorts()

        # prot numebrs were non-integers
        except ValueError:
            errorMsg("Bad port number(s)")


    def checkPorts(self):

        # check the CONTROL port bounds
        if self.portP < 0 or self.portP > 65535:
            errorMsg("Bad port number(s)")

        # check the DATA port bounds
        elif self.portQ < 0 or self.portQ > 65535:
            errorMsg("Bad port number(s)")




    #----------------------SOCKER PREP---------------------#
    def openP(self):

        # open a TCP socket on CONTROL port and reach out to the server
        self.P = socket(AF_INET, SOCK_STREAM)
        self.P.connect((self.host, self.portP))


    def listenQ(self):
        
        # open a TCP socket on DATA port and wait to be contacted
        Q = socket(AF_INET, SOCK_STREAM)
        Q.bind(('', self.portQ))
        Q.listen(1)

        # connection received
        self.Q, clientAddress = Q.accept()

        # let the user know what is coming
        if self.command == '-l':
            print("Receiving directory structure from {}:{}".format(clientAddress[0], clientAddress[1]))
        else:
            print("Receiving '{}' from {}:{}".format(self.fileName, clientAddress[0], clientAddress[1]))
            

    @staticmethod
    def closeSocket(s):
        s.close()

    


    #---------------------COMMUNICATION--------------------#
    def sendCommand(self):
        
        # get command string
        if self.command == '-g':
            command = "-g " + self.fileName + " " + str(self.portQ)

        # list command string
        else:
            command = "-l " + str(self.portQ)

        # send the command with the data port number
        self.P.send(command)


    def recvResponse(self):
        # get data (NEEDS TO BE REFACTORED TO PROCESS DATA BASED ON COMMAND)
        while 1:
            self.msg = self.Q.recv(2048)
            if not self.msg: break
            print(self.msg)


    def finalThoughts(self):

        if self.command == '-l':
            print("Something about the files")
        else:
            print("File transfer complete")




    #--------------------ERROR HANDLING--------------------#
    @staticmethod
    def argError(exeName):
        print("Incorrect argument!")
        print("Correct Usage:\n\npython {} <serverName> <PORT> -l <dataPort>".format(exeName))
        print("OR")
        print("python {} <serverName> <PORT> -g <fileName> <dataPort>\n".format(exeName))
        exit(1)

    @staticmethod
    def errorMsg(msg):
        print(msg)
        exit(1)



if __name__ == "__main__":

    a = FTPclient(sys.argv)