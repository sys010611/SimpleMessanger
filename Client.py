import random
from socket import *
from threading import Thread
import time

serverName = 'localhost'
serverPort = 10000
ID = ""
sessionUserList = []

def GetUserInfoByID(ID, users):
    ip, port = '', ''

    for user in users.split('\n'):
        userId = user.split(',')[0]
        if userId == ID:
            ip = user.split(',')[1]
            port = user.split(',')[2]
            break

    return ip, port

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


def MakeSession():
    while True:  # 원하는 만큼 세션에 초청
        oppositeID = input("세션에 초대할 상대방의 ID를 입력하시오 (초대 종료 시 '.' 입력) : ")

        if oppositeID == '.':
            break

        ip, port = "", ""

        users = RequestUserList()
        ip, port = GetUserInfoByID(oppositeID, users)

        if ip == "" and port == "":
            print("존재하지 않는 ID입니다.")
        else:
            # 초대장 보내기
            myIP, myPort = GetUserInfoByID(ID, users)
            message = "INVITE "
            message += (ID + ',' + myIP + ',' + str(myPort))
            message += '\n\n '

            userAddr = (ip, int(port))
            clientSocket.sendto(message.encode(), userAddr)
    return


def send():
    while True:  # 세션의 사용자들에게 메시지 보내기
        message = "MESSAGE "
        message = message + ID + ' '
        content = input()
        message = message + '\n\n'
        message = message + content
        for user in sessionUserList:
            user_id = user.split(',')[0]
            if user_id == ID:  # 자기 자신에게는 전송하지 않음
                continue
            user_ip = user.split(',')[1]
            user_port = user.split(',')[2]
            userAddr = (user_ip, int(user_port))
            clientSocket.sendto(message.encode(), userAddr)


def recv():
    global sessionUserList
    while True:
        try:
            message, userAddr = clientSocket.recvfrom(2048)
            message = message.decode()

            header = message.split('\n\n')[0]
            content = message.split('\n\n')[1]

            if header.split(' ')[0] == "MESSAGE":
                sender = header.split(' ')[1]
                print(sender + ' : ' + content + '\n')

            if header.split(' ')[0] == "JOIN":
                joinerId = header.split(' ')[1]
                joinerIp = ''
                joinerPort = ''

                users = RequestUserList()
                joinerIp, joinerPort = GetUserInfoByID(joinerId, users)

                sessionUserList.append(joinerId + ',' + joinerIp + ',' + str(joinerPort))
                print(joinerId + '님이 세션에 참가하였습니다.')

                # sessionUserList 재전파
                message = "INFORM "
                message += "\n\n"
                for idx, user in enumerate(sessionUserList):
                    joinerId = user.split(',')[0]
                    joinerIp = user.split(',')[1]
                    joinerPort = user.split(',')[2]
                    message += joinerId + ',' + joinerIp + ',' + str(joinerPort)
                    if idx != len(sessionUserList) - 1:
                        message += '\n'

                for user in sessionUserList:
                    joinerId = user.split(',')[0]
                    joinerIp = user.split(',')[1]
                    joinerPort = user.split(',')[2]
                    userAddr = (joinerIp, int(joinerPort))
                    if joinerId != ID:
                        clientSocket.sendto(message.encode(), userAddr)

            if header.split(' ')[0] == "INFORM":
                sessionUserList = []
                for user in content.split('\n'):
                    joinerId = user.split(',')[0]
                    joinerIp = user.split(',')[1]
                    joinerPort = user.split(',')[2]
                    sessionUserList.append(joinerId + ',' + joinerIp + ',' + str(joinerPort))

                print("세션에 참여 중인 유저 목록")
                for user in sessionUserList:
                    print(user)

        except OSError as e:
            pass


if __name__ == '__main__':
    clientSocket = socket(AF_INET, SOCK_DGRAM)

    sender = Thread(target=send, args=())
    receiver = Thread(target=recv, args=())

    ID = input("Enter Your ID : ")

    # 서버에 ID를 보냄
    message = "LOGIN "
    message += (ID + ' ')
    clientSocket.sendto(message.encode(), (serverName, serverPort))

    users = RequestUserList()
    print("유저 목록")
    print(users)

    while True:
        print("커맨드 목록")
        print("1. UserList : 유저 목록 새로고침")
        print("2. MakeSession : 세션 만들기")
        print("3. Stay : 초대 기다리기")
        command = input(">> ")

        if command == 'UserList' or command == '1':
            users = RequestUserList()
            print("유저 목록")
            print(users)

        elif command == 'MakeSession' or command == '2':
            users = RequestUserList()
            myIP, myPort = GetUserInfoByID(ID, users)

            sessionUserList.append(ID + ',' + myIP + ',' + str(myPort))

            MakeSession()

            print("내용을 입력하고 ENTER로 전송")

            sender.start()
            receiver.start()

            while True:
                time.sleep(1)

        elif command == 'Stay' or command == '3':
            print("대기중...")
            while True:
                message, userAddr = clientSocket.recvfrom(2048)
                message = message.decode()
                header = message.split('\n\n')[0]
                if header.split(' ')[0] == "INVITE":
                    inviter = header.split(' ')[1]
                    inviterID = inviter.split(',')[0]
                    inviterIP = ''
                    inviterPort = ''

                    userList = RequestUserList()
                    for user in userList.split('\n'):
                        if user.split(',')[0] == inviterID:
                            inviterIP = user.split(',')[1]
                            inviterPort = user.split(',')[2]
                            break

                    print(inviterID + '로부터의 세션 초대 (y/n)')

                    accept = input('>> ')
                    if accept == 'Y' or accept == 'y':
                        print("초대 수락")

                        # 세션 주인에게 자신이 참가했다는 사실 알리기
                        message = 'JOIN '
                        message += ID
                        message += '\n\n'

                        inviterAddr = (inviterIP, int(inviterPort))
                        clientSocket.sendto(message.encode(), inviterAddr)

                        sender.start()
                        receiver.start()
                        break
                    else:
                        print("초대 거절")
                        continue
            while True:
                time.sleep(1)
