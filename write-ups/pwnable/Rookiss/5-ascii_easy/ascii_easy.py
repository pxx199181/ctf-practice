from zio import *

target = "./ascii_easy"

def get_io(target):
	io = zio(target, timeout = 9999)
	return io

def pwn(io):
	io.read_until("Input text : ")

	io.write('a' * 400)
