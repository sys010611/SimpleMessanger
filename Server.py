from socket import *
import os.path
from os import path

serverPort = 10000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(("", serverPort))

while True:
    ID, clientAddr = serverSocket.recvfrom(2048)

    content = []
    if path.exists("UserList.txt"):
        with open("UserList.txt", 'r') as f:
            users = f.read().split('\n')

            for user in users:
                if user.split(',')[0] == ID.decode(): #동일 ID 유저 접속, 이전 정보는 제거
                    continue
                else:
                    content.append(user+'\n')

    content.append(ID.decode() + ',' + str(clientAddr[0]) + ',' + str(clientAddr[1]))

    with open("UserList.txt", 'w') as f:
        for line in content:
            f.write(line)

    with open("UserList.txt", 'r') as f:
        serverSocket.sendto(f.read().encode(), clientAddr)

