import random
from socket import *
from threading import *
import time

serverName = 'localhost'
serverPort = 10000
ID = ""

def RequestUserList():
    # 현재 온라인인 유저 목록 요청
    message = "USERLIST "
    clientSocket.sendto(message.encode(), (serverName, serverPort))

    # 유저 리스트를 확실히 받고 넘어가기
    while True:
        try:
            userList, serverAddr = clientSocket.recvfrom(2048)
            break
        except OSError as e:
            pass

    userList = userList.decode()
    return userList


def MakeSession(users):
    sessionUserList = []
    while True:  # 원하는 만큼 세션에 초청
        oppositeID = input("세션에 초대할 상대방의 ID를 입력하시오 (초대 종료 시 '.' 입력) : ")

        if oppositeID == '.':
            break

        ip, port = "", ""

        for user in users:
            if oppositeID == user.split(',')[0]:
                ip = user.split(',')[1]
                port = user.split(',')[2]

        if ip == "" and port == "":
            print("존재하지 않는 ID입니다.")
        else:
            sessionUserList.append(oppositeID + ',' + ip + ',' + port)

    return sessionUserList

def send():
    while True:  # 세션의 사용자들에게 메시지 보내기
        message = "MESSAGE "
        message = message + ID + ' '
        content = input()
        message = message + '\n\n'
        message = message + content
        for user in sessionUserList:
            ip = user.split(',')[1]
            port = user.split(',')[2]
            userAddr = (ip, int(port))
            clientSocket.sendto(message.encode(), userAddr)
def recv():
    while True:
        try:
            message, userAddr = clientSocket.recvfrom(2048)
            message = message.decode()

            header = message.split('\n\n')[0]
            if header.split(' ')[0] == "MESSAGE":
                content = message.split('\n\n')[1]
                sender = header.split(' ')[1]

                print(sender + ' : ' + content + '\n')
            
        except OSError as e:
            pass


if __name__ == '__main__':
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    sender = Thread(target=send, args=())
    receiver = Thread(target=recv, args=())

    ID = input("Enter Your ID : ")

    #서버에 ID를 보냄
    message = "JOIN "
    message = message + ID + ' '
    clientSocket.sendto(message.encode(), (serverName, serverPort))

    userList = RequestUserList()
    print("유저 목록 : ")
    print(userList)

    users = userList.split('\n')
    
    print("커맨드 목록")
    print("1. UserList : 유저 목록 다시 받아오기")
    print("2. MakeSession : 세션 만들기")
    print("3. Stay : 초대 기다리기")

    while True:
        command = input(">>")

        if command == 'UserList':
            userList = RequestUserList()
            print("유저 목록 : " + userList)
            users = userList.split('\n')

        elif command == 'MakeSession':
            sessionUserList = MakeSession(users)
            print("만든 세션 유저 목록: ")
            for user in sessionUserList:
                print(user)

            print("내용을 입력하고 ENTER로 전송")

            sender.start()
            receiver.start()

            while True:
                time.sleep(1)

        elif command == 'Stay':
            receiver.start()

            while True:
                time.sleep(1)