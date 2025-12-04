from socket import *
import os.path
from os import path

################################
# サーバー情報
##############################
serverPort = 10000
serverIP = '192.168.0.9'

def AddUser():
    print(message.decode())
    ID = message.decode().split(' ')[1]
    newUserList = []

    if path.exists("UserList.txt"):
        with open("UserList.txt", 'r') as f:
            users = f.readlines()
            users = [line.strip() for line in users]
            for user in users:
                if user.split(',')[0] == ID:  # 同じIDのユーザー接続、以前の情報は削除
                    continue
                else:
                    newUserList.append(user)

    newUserList.append(ID + ',' + str(clientAddr[0]) + ',' + str(clientAddr[1]))  # 新しく接続したユーザーをリストに追加

    with open("UserList.txt", 'w') as f:
        for idx, user in enumerate(newUserList):
            if idx != len(newUserList)-1:
                f.write(user + '\n')
            else:
                f.write(user)

def GiveOnlineUserList():
    print('ユーザーリスト送信中')

    message = "USERLIST \n\n"

    with open("UserList.txt", 'r') as f:
        message += f.read()
    serverSocket.sendto(message.encode(), clientAddr)


def RemoveUser():
    newUserList = []
    exitingUserId = message.decode().split('\n\n')[0].split(' ')[1]
    print(exitingUserId + ' ログアウト')
    if path.exists("UserList.txt"):
        with open("UserList.txt", 'r') as f:
            users = f.readlines()
            users = [line.strip() for line in users]
            for user in users:
                if user.split(',')[0] == exitingUserId:  # 退場ユーザー情報は削除
                    continue
                else:
                    newUserList.append(user)
    with open("UserList.txt", 'w') as f:
        for idx, user in enumerate(newUserList):
            if idx != len(newUserList) - 1:
                f.write(user + '\n')
            else:
                f.write(user)


if __name__ == '__main__':
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    serverSocket.bind((serverIP, serverPort))

    print("サーバー on")

    with open("UserList.txt", 'w') as f: # ユーザーリストを空にする
        f.write("")

    while True:
        message, clientAddr = serverSocket.recvfrom(2048)

        if message.decode().split(' ')[0] == "LOGIN":
            AddUser()

        elif message.decode().split(' ')[0] == "USERLIST":
            GiveOnlineUserList()

        elif message.decode().split(' ')[0] == "EXIT":
            RemoveUser()
