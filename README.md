Introduction to Computer Networks - Program 2

Server
  - Written in C
  - Process commands sent by the client received on the Control port
  - Returns a list of the current directory OR the contents of a file on the Data port provided in the clients command
  - Compile
    - gcc server.c -o ftserver
  - Execute
    ./ftserver <control port number>


Client
  - Written in Python
  - Processes user's command line arguments
  - Prints the servers response in the case of a list OR stores the response in a file in the case of a file request
  - Execution options
    - LIST
      - python client.py [server name] [control port number] -l [data port number]
    - FILE
      - python client.py [server name] [control port number] -g [file name] [data port number]

