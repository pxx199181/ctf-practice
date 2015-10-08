from zio import *

target = ('pwnable.kr', 9008)

def get_io(target):
	io = zio(target, timeout = 9999)
	return io

def get_data(times, N):
	left = ""
	right = ""



def generate_data(N, C):
	times = 0
	buff = ""
	partion = 1 << times
	left = []
	right = []
	left += ["%d "%c for c in xrange()]
	return 


def do_work(io):
	io.read_until("N=")
	N = int(io.read_until(" ").strip())
	C = int(io.read_until("\n").strip())

	print "N = ", N, "C = ", C

