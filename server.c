#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>

#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <dirent.h>
#include <netdb.h>

/*  ALL SOCKET RELATED CODE WAS ADAPTED FROM BEEJS GUIDE  */
/*                 UNLESS OTHERWISE NOTED                 */


void argError(char *exeName) {
    printf("Incorrect argument!\n");
    printf("Correct Usage:\n\n%s <PORT>\n\n", exeName);
    exit(1);
}


void validateCLA(int len, char **cla, int* portP) {

    if (len != 2) {
        argError(cla[0]);
    }

    int temp;
    temp = atoi(cla[1]);

    if (temp <= 0 || temp > 65535) {
        printf("Bad Port Number!\n");
        printf("Exiting!\n");
        exit(1);
    }

    *portP = temp;

}


void listenP(int* sockListener, int* portP) {

    int listener;
    struct sockaddr_in server_address;

    // set up the servers address info
    memset(&server_address, '0', sizeof server_address);
    server_address.sin_family = AF_INET;
    server_address.sin_addr.s_addr = htonl(INADDR_ANY);
    server_address.sin_port = htons(*portP);

    listener = socket(AF_INET, SOCK_STREAM, 0);

    if (listener == -1) {
        printf("SOCKET ERROR!\n");
        exit(1);
    }

    bind(listener, (struct sockaddr*)&server_address, sizeof(server_address));
    listen(listener, 10);

    *sockListener = listener;

    printf("Server open on %d\n", *portP);


    // HANDLE SOCKET IN USE ERROR

}


/* Retreiving the clients IP was adapted from a response on stack overflow */
/*
    Link:
    https://stackoverflow.com/questions/3060950/how-to-get-ip-address-from-sock-structure-in-c
*/
void acceptClient(int* sockP, int sockListener, char* buffer) {

    struct sockaddr_storage client_addr;
    int addr_size = sizeof client_addr;

    // accept the clients connection
    *sockP = accept(sockListener, (struct sockaddr*)&client_addr, &addr_size);

    // store the clients IP address into the buffer
    struct sockaddr_in* pV4Addr = (struct sockaddr_in*)&client_addr;
    struct in_addr ipAddr = pV4Addr->sin_addr;
    inet_ntop(AF_INET, &ipAddr, buffer, INET_ADDRSTRLEN);

    printf("\nConnection from %s\n", buffer);


}


void processCommand(char* buffer, char* command, char* dataport, char* filename) {
   
    // empty the strings
    memset(command, '\0', sizeof command);
    memset(dataport, '\0', sizeof dataport);
    memset(filename, '\0', sizeof filename);


    char temp[sizeof buffer];

    int i=0;

    // parse the command from the message
    while (*buffer != ' ') {
        command[i] = *buffer;
        buffer++;
        i++;
    }

    i=0;
    buffer++;

    //check if list request
    if (strcmp(command, "-l") == 0) {
        while (*buffer != '\0') {
            dataport[i] = *buffer;
            buffer++;
            i++;
        }

        // tell user about the request
        printf("List directory requested on port %s.\n", dataport);
    }

    // otherwise a file request
    else {
        while (*buffer != ' ') {
            filename[i] = *buffer;
            buffer++;
            i++;
        }
        i=0;
        buffer++;
        while (*buffer != '\0') {
            dataport[i] = *buffer;
            buffer++;
            i++;
        }

        // tell user about the request
        printf("File \"%s\" requested on port %s.\n", filename, dataport);

    }

}


void openQ(int* sockQ, char* clientIP, char* dataport) {

    // wait for 1 second to ensure client is listening to the port
    sleep(1);

    int status;
    struct addrinfo hints, *res;
    
    // fill in struct
    memset(&hints, 0, sizeof hints);
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_STREAM;

    // get info about the client
    if ((status = getaddrinfo(clientIP, dataport, &hints, &res)) != 0) {
        fprintf(stderr, "GetAddrInfo error: %s\n", gai_strerror(status));
    }

    // open socket and conenect to the host
    *sockQ = socket(res->ai_family, res->ai_socktype, res->ai_protocol);
    connect(*sockQ, res->ai_addr, res->ai_addrlen);

    // free space allocated in the response object
    freeaddrinfo(res);

}


void getList(int sockQ, char* clientIP, char* dataport) {

    DIR *dir;
    char buffer[64];
    struct dirent *currentContent;
    dir = opendir("./");

    // successful open
    if (dir != NULL) {

        printf("Sending directory contents to %s:%s\n", clientIP, dataport);

        // loop over dir contents
        while (currentContent = readdir(dir)) {

            // clear buffer and copy name into it
            memset(buffer, '\0', sizeof buffer);
            strcpy(buffer, currentContent->d_name);

            if (buffer[0] == '.') {
                // do nothing
            }
            else {
                // send to the client
                buffer[strlen(buffer)] = '\n';
                send(sockQ, buffer, strlen(buffer), 0);
            }
        }
    }

    // error
    else {
        strcpy(buffer, "ERROR OPENING DIRECTORY!");
        send(sockQ, buffer, strlen(buffer), 0);
    }

    // close the directory
    closedir(dir);

}


void getFile(char *filename, int sockQ, char* clientIP, char* dataport) {

    // open file
    FILE *fp;
    char buffer[1024];
    memset(buffer, '\0', sizeof buffer);

    // file exists
    if (access(filename, F_OK) != -1) {

        fp = fopen(filename, "r");
        
        // loop over the file, reading in each time
        while(fgets(buffer, sizeof buffer, (FILE*)fp)) {

            // send the data
            send(sockQ, buffer, strlen(buffer), 0);

            // clear the buffer
            memset(buffer, '\0', sizeof buffer);
        }

        // close the file
        fclose(fp);

    }

    // file does not exist
    else {
        printf("File not found. Sending error message to %s:%s\n", clientIP, dataport);
        strcpy(buffer, "FILE NOT FOUND");
        send(sockQ, buffer, strlen(buffer), 0);
    }


}


void respond(int sockQ, char* command, char* filename, char* clientIP, char* dataport) {

    if (strcmp(command, "-l") == 0) {
        getList(sockQ, clientIP, dataport);
    }
    else {
        getFile(filename, sockQ, clientIP, dataport);
    }

}



int main (int argc, char **argv) {

    /*       VARIABLES       */
    int portP;                          // port number from command line
    int sockP;                          // COMMAND socket
    int sockQ;                          // DATA socket
    int sockListener;                   // listener socket
    char command[8];                    // string for clients command
    char dataport[8];                   // string for clients data port
    char filename[64];                  // string for requested filename
    char buffer[2048];                  // TCP recv buffer
    char clientIP[INET_ADDRSTRLEN];     // string for client IP address


    
    // Validate the command line arguments
    validateCLA(argc, argv, &portP);

    // listen to specified port
    listenP(&sockListener, &portP);

    // wait for client, process request, repeat
    while(1) {

        // accept the clients connection
        acceptClient(&sockP, sockListener, clientIP);
        
        // receive the clients request
        recv(sockP, buffer, sizeof buffer, 0);

        // process the clients request
        processCommand(buffer, command, dataport, filename);

        // open TCP connection on DATA port
        openQ(&sockQ, clientIP, dataport);

        // respond to the client over the DATA connection
        respond(sockQ, command, filename, clientIP, dataport);

        // close the DATA socket
        close(sockQ);

        printf("\nRequest complete!\n");
    }
    
    // close the CONTROL socket
    close(sockP);

    return 0;

}