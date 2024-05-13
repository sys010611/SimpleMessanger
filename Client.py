from socket import *

serverName = 'localhost'
serverPort = 10000

ID = ""
ID = input("Enter Your ID : ")

clientSocket = socket(AF_INET, SOCK_DGRAM)
message = ID
clientSocket.sendto(message.encode(), (serverName, serverPort))

userList, serverAddr = clientSocket.recvfrom(2048)
userList = userList.decode()
print("유저 목록 : ")
print(userList)

users = userList.split('\n')

sessionUserList = []
while True: # 원하는 만큼 세션에 초청
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

    print("현재 세션 유저 목록: ")
    for user in sessionUserList:
        print(user)

while True: #세션의 사용자들에게 메시지 보내기
    message = input("메시지 전송 : ")
    for user in sessionUserList:
        ip = user.split(',')[1]
        port = user.split(',')[2]

        userAddr = (ip, int(port))

        userSocket = socket(AF_INET, SOCK_DGRAM)
        userSocket.sendto(message.encode(), userAddr)