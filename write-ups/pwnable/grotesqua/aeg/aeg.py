from zio import *
import base64
import struct

from pwnlib.asm import *

taget = ("pwnable.kr", 9005)

def get_io(taget):
	io = zio(taget, 9999)
	return io

def do_work(io):
	io.read_until("wait...\n")

	data = io.read_until("\n")[:-1]
	file_w = open("new_file.bin", "w")
	binary_data = base64.decodestring(data)
	file_w.write(binary_data)
	file_w.close()
	
	print "len:", len(data)
	print "begin word:", data[0:10]
	print "last word:", data[-10:]

	print disasm(binary_data, arch = 'i386', os = 'linux')

	print [chr(ord(c)) for c in binary_data]

	io.read_until("hurry up!\n")
	io.interact()

io = get_io(taget)
do_work(io)
