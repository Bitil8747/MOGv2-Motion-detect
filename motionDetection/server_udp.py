import socket

udp_ip = 'localhost'
udp_port = 7070

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((udp_ip, udp_port))

while True:
    data, addr = sock.recvfrom(1024)
    print(data)