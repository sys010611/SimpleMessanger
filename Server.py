from socket import *

serverPort = 10000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(("", serverPort))

while True:
    message, clientAddr = serverSocket.recvfrom(2048)

    with open("UserList.txt", 'a') as f:
        f.write(message.decode() + ',' + str(clientAddr[0]) + ',' + str(clientAddr[1]) + '\n')
    with open("UserList.txt", 'r') as f:
        serverSocket.sendto(f.read().encode(), clientAddr)
