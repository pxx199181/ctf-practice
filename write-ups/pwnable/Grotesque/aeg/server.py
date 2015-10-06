# Echo server program
import socket
import sys

HOST = None               # Symbolic name meaning all available interfaces
PORT = 7777              # Arbitrary non-privileged port
s = None
for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC,
                              socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
    af, socktype, proto, canonname, sa = res
    try:
        s = socket.socket(af, socktype, proto)
    except socket.error, err_msg:
        print err_msg 
        s = None
        continue
    try:
        s.bind(sa)
        s.listen(1)
    except socket.error, err_msg:
        print err_msg
        s.close()
        s = None
        continue
    break
if s is None:
    print 'could not open socket'
    sys.exit(1)
    
conn, addr = s.accept()
print 'Connected by', addr

while 1:
    data = raw_input("$:")
    conn.send(data)
    data = conn.recv(1024)
    print data
    if not data: 
        break
conn.close()
