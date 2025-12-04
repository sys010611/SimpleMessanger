import random
import threading
from socket import *
from threading import Thread
import time

################################
# サーバー情報
##############################
serverIP = '192.168.0.9'
serverPort = 10000

ID = ""
sessionUserList = []
socketLock = threading.Lock()
onlineUsers = ''
exitFlag = False

def ReadSocket():
    socketContent = clientSocket.recvfrom(2048)

    return socketContent


def GetUserInfoByID(ID):
    ip, port = '', ''

    for user in onlineUsers.split('\n'):
        userId = user.split(',')[0]
        if userId == ID:
            ip = user.split(',')[1]
            port = user.split(',')[2]
            break

    return ip, port

def RequestUserList():
    # 現在オンラインのユーザーリストを要求
    message = "USERLIST "
    clientSocket.sendto(message.encode(), (serverIP, serverPort))

    # ユーザーリストを確実に受信してから次へ進む
    while True:
        try:
            userList, serverAddr = clientSocket.recvfrom(2048)
            break
        except OSError as e:
            pass


    userList = userList.decode()
    onlineUsers = userList.split('\n\n')[1]
    return onlineUsers


def MakeSession():
    onlineUsers = RequestUserList()

    invitingUserList = []
    myIP, myPort = GetUserInfoByID(ID)
    message = "INVITE "
    message += (ID + ',' + myIP + ',' + str(myPort))
    message += '\n\n '

    while True:  # 好きなだけセッションに招待
        oppositeID = input("セッションに招待する相手のIDを入力してください（招待を終わるには '.' を入力）: ")

        if oppositeID == '.':
            break

        ip, port = "", ""
        ip, port = GetUserInfoByID(oppositeID)

        if ip == "" and port == "":
            print("存在しないIDです.")
        else:
            invitingUserList.append((oppositeID, ip, port))

    for user in invitingUserList:
        # 招待状を送信
        userAddr = (user[1], int(user[2]))
        clientSocket.sendto(message.encode(), userAddr)

    return


def send():
    global sessionUserList
    global onlineUsers
    global exitFlag
    while True:  # セッションのユーザーたちにメッセージを送信
        message = "MESSAGE "
        message = message + ID + ' '
        content = input()

        if content[0] == '!': # 特殊コマンド（招待、退出）
            if content == '!invite':
                oppositeID = input("招待するユーザーのID（キャンセルするには . を入力）: ")

                if oppositeID != '.':
                    ip, port = "", ""
                    ip, port = GetUserInfoByID(oppositeID)

                    if ip == "" and port == "":
                        print("存在しないIDです.")
                    else:
                        myIP, myPort = GetUserInfoByID(ID)
                        message = "INVITE "
                        message += (ID + ',' + myIP + ',' + str(myPort))
                        message += '\n\n '
                        
                        userAddr = (ip, int(port))
                        clientSocket.sendto(message.encode(), userAddr)

            if content == '!exit':
                message = "EXIT "
                message += ID
                message += '\n\n '

                #  サーバーとユーザーたちに退出を通知
                clientSocket.sendto(message.encode(), (serverIP, serverPort))
                for user in sessionUserList:
                    id = user.split(',')[0]
                    if id == ID:
                        continue
                    ip = user.split(',')[1]
                    port = user.split(',')[2]
                    userAddr = (ip, int(port))
                    clientSocket.sendto(message.encode(), userAddr)

                exitFlag = True

            if content == '!userlist':
                message = "USERLIST "
                clientSocket.sendto(message.encode(), (serverIP, serverPort))


        else: # 一般メッセージ
            message = message + '\n\n'
            message = message + content
            for user in sessionUserList:
                user_id = user.split(',')[0]
                if user_id == ID:  # 自分自身には送信しない
                    continue
                user_ip = user.split(',')[1]
                user_port = user.split(',')[2]
                userAddr = (user_ip, int(user_port))
                clientSocket.sendto(message.encode(), userAddr)


def recv():
    global sessionUserList
    global onlineUsers
    while True:
        try:
            message, userAddr = ReadSocket()
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

                onlineUsers = RequestUserList()
                joinerIp, joinerPort = GetUserInfoByID(joinerId)

                sessionUserList.append(joinerId + ',' + joinerIp + ',' + str(joinerPort))
                print(joinerId + 'さんがセッションに参加しました。')

                # sessionUserList を再配布
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

            if header.split(' ')[0] == "USERLIST":
                onlineUsers = content
                print("ユーザーリスト")
                print(onlineUsers)

            if header.split(' ')[0] == "EXIT":
                for user in sessionUserList:
                    if user.split(',')[0] == header.split(' ')[1]:
                        sessionUserList.remove(user) # 退出したと知らせたユーザーをリストから削除
                        break
                print(header.split(' ')[1] + 'さんが退室しました。')

        except OSError as e:
            pass


if __name__ == '__main__':
    clientSocket = socket(AF_INET, SOCK_DGRAM)

    sender = Thread(target=send, args=())
    receiver = Thread(target=recv, args=())

    sender.daemon = True
    receiver.daemon = True

    ID = input("Enter Your ID : ")

    # サーバーにIDを送信
    message = "LOGIN "
    message += (ID + ' ')
    clientSocket.sendto(message.encode(), (serverIP, serverPort))

    onlineUsers = RequestUserList()
    print("ユーザーリスト")
    print(onlineUsers)

    while True:
        print("コマンド一覧")
        print("1. UserList : ユーザーリスト再読み込み")
        print("2. MakeSession : セッション作成")
        print("3. Stay : 招待を待機")
        command = input(">> ")

        if command == 'UserList' or command == '1':
            onlineUsers = RequestUserList()
            print("ユーザーリスト")
            print(onlineUsers)
            continue

        elif command == 'MakeSession' or command == '2':
            onlineUsers = RequestUserList()
            myIP, myPort = GetUserInfoByID(ID)

            sessionUserList.append(ID + ',' + myIP + ',' + str(myPort))

            MakeSession()

            print("内容を入力してENTERで送信")

            sender.start()
            receiver.start()

        elif command == 'Stay' or command == '3':
            print("待機中...")
            while True:
                message, userAddr = ReadSocket()
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

                    print(inviterID + 'からのセッション招待 (y/n)')

                    accept = input('>> ')
                    if accept == 'Y' or accept == 'y':
                        print("招待を承諾")

                        # セッションホストに参加したことを知らせる
                        message = 'JOIN '
                        message += ID
                        message += '\n\n'

                        inviterAddr = (inviterIP, int(inviterPort))
                        clientSocket.sendto(message.encode(), inviterAddr)

                        sender.start()
                        receiver.start()
                        break
                    else:
                        print("招待を拒否")
                        continue

        else:
            continue

        while True:
            time.sleep(1)
            if exitFlag == True:
                exit(0)
