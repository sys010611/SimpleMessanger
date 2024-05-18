from socket import *
import os.path
from os import path

serverPort = 10000
serverName = 'localhost'

def AddUser():
    print(message.decode())
    ID = message.decode().split(' ')[1]
    newUserList = []

    if path.exists("UserList.txt"):
        with open("UserList.txt", 'r') as f:
            users = f.readlines()
            for user in users:
                if user.split(',')[0] == ID:  # 동일 ID 유저 접속, 이전 정보는 제거
                    continue
                else:
                    newUserList.append(user)

    newUserList.append(ID + ',' + str(clientAddr[0]) + ',' + str(clientAddr[1]))  # 새로 접속한 유저 리스트에 추가

    with open("UserList.txt", 'w') as f:
        for idx, user in enumerate(newUserList):
            if idx != len(newUserList)-1:
                f.write(user + '\n')
            else:
                f.write(user)

def GiveOnlineUserList():
    print(message.decode())

    with open("UserList.txt", 'r') as f:
        serverSocket.sendto(f.read().encode(), clientAddr)

if __name__ == '__main__':
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    serverSocket.bind((serverName, serverPort))

    print("Server Online")

    with open("UserList.txt", 'w') as f: #유저 목록 비우기
        f.write("")

    while True:
        message, clientAddr = serverSocket.recvfrom(2048)

        if message.decode().split(' ')[0] == "LOGIN":
            AddUser()

        elif message.decode().split(' ')[0] == "USERLIST":
            GiveOnlineUserList()
