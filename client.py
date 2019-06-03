from socket import *
import sys

# The client was built with occasional reference to stack overflow
# I work with TCP sockets in Python everyday at work so I did
# not frequently consult any of the recommended gudies in the
# assignments PDF


class FTPclient:

    #---------------------INITIALIZER----------------------#
    def __init__(self, cla):
        self.validateCLA(cla)
        self.openP()
        self.sendCommand()
        self.listenQ()
        self.recvResponse()
        self.closeSocket(self.P)
        self.closeSocket(self.Q)

    
    
    #--------------------CLA VALIDATION--------------------#
    def validateCLA(self, cla):

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
            self.argError(cla[0])

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
            self.errorMsg("Bad port number(s)")


    def parseGetArgs(self, cla):
        # ./prog server port -g fileName dataPort     length: 6

        # check the length of the commands
        if len(cla) != 6:
            self.argError(cla[0])

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
            self.errorMsg("Bad port number(s)")


    def checkPorts(self):

        # check the CONTROL port bounds
        if self.portP < 0 or self.portP > 65535:
            self.errorMsg("Bad port number(s)")

        # check the DATA port bounds
        elif self.portQ < 0 or self.portQ > 65535:
            self.errorMsg("Bad port number(s)")
    

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
            

    @staticmethod
    def closeSocket(s):
        s.close()


    #----------------------PROCESSING----------------------#
    def sendCommand(self):
        
        # get command string
        if self.command == '-g':
            command = "-g " + self.fileName + " " + str(self.portQ) + "\0"

        # list command string
        else:
            command = "-l " + str(self.portQ) + "\0"

        # send the command with the data port number
        self.P.send(command)


    def recvResponse(self):

        if self.command == "-l":
            self.recvList()
        else:
            self.recvFile()


    def recvList(self):

        print("\nReceiving directory structre from {}:{}\n".format(self.host, self.portQ))

        response = ""
        
        while 1:
            temp = self.Q.recv(2048)
            if not temp: break
            response += temp

        print(response)


    def recvFile(self):

        err = 0
        response = ""

        # copy messages into variable
        while 1:

            # store response
            temp = self.Q.recv(2048)

            # check the response
            if not temp: break
            if "FILE NOT FOUND" in temp:
                err = 1
                break

            # write response to variable
            response += temp

        # Let the user know there was an error
        if err:
            print("\n{}:{} says".format(self.host, self.portQ))
            print(temp)
            print(" ")

        # write to file if it existed
        else:
            print("\nReceiving \"{}\" from {}:{}".format(self.fileName, self.host, self.portQ))
        
            # open file
            tempFile = open(self.fileName, "w")

            # write to file
            tempFile.write(response)

            # close file
            tempFile.close()

            print("\nFile transfer complete\n")

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