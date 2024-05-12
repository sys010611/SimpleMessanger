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
