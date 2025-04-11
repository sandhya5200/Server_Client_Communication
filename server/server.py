import socket

s = socket.socket()
print('socket has been created')

s.bind(('localhost',9999))

s.listen(3)
print('waiting for connection') # no of clients

while True:
    c,addr = s.accept()
    name= c.recv(1024).decode()
    print("connected with", addr, name)
    

    c.send(bytes('welcome','utf-8'))

    c.close()
