from zio import *
import random

target = ("pwnable.kr", 9007)

io = zio(target, timeout = 9999)

io.read_until("... -")

def get_N_C(io):	
	io.read_until("N=")
	data = io.read_until("\n").strip()
	value = data.split(" C=")
	N = int(value[0])
	C = int(value[1])
	#print "get n:%d, c:%d"%(N, C)
	return N, C


def generate_buff(start, end):
	data_v = ["%d "%c for c in range(start, end + 1)]
	return "".join(data_v)

def get_coin(io, N, C):
	start = 0
	end = N - 1
	times = 0
	while times < C:
		half = (start  + end)/2
		#print "times:%d, start:%d, end:%d"%(times, start, end)
		data  = generate_buff(start, half)
		io.write(data + "\n")
		value = int(io.read_until("\n").strip())
		if value % 10 == 0:
			start = half + 1
			if start > end:
				start = end
		else:
			end = half
			if start > end:
				end = start
		times += 1
	if start == end:
		io.write("%d\n"%start)
		io.read_until("\n")
	else:
		value = random.randint(start, end)
		print "guess one:", value
		io.write("%d\n"%start)
		io.read_until("\n")

	return True


while True:
	N, C = get_N_C(io)
	get_coin(io, N, C)