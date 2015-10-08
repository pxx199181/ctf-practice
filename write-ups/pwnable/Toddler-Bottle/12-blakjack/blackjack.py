from zio import *
import random

target = ("pwnable.kr", 9009)

io = zio(target, timeout = 9999)

io.read_until("(Y/N)\n")
io.write("Y\n")
io.read_until("Choice: ")
io.write("1\n")

def read_timeout(io, timeout = 9999):
	while True:
		data = io.read_timeout(timeout)
		if data.strip() != '':
			continue
		else:
			return data



def get_status(data):
	pos_s = data.find("Your Total is ") + len("Your Total is ")
	pos_e = data.find("\n", pos_s)
	my_value = int(data[pos_s:pos_e])
	pos_s = data.find("The Dealer Has a Total of ") + len("The Dealer Has a Total of ")
	pos_e = data.find("\n", pos_s)
	dealer_value = int(data[pos_s:pos_e])
	return my_value, dealer_value

def do_bet(io):
	io.read_until("Cash: $")
	money = int(io.read_until("\n").strip())
	data = io.read_until("Enter Bet: $")
	#io.write("%d\n"%(money / 2))
	io.write("%d\n"%(100))
	io.read_until("to Stay.\n")
	return get_status(data)

def make_decision(io, my_value, dealer_value):
	if my_value < dealer_value:
		io.write("H\n")
	else:
		if my_value >= 17:
			io.write("S\n")
		else:
			io.write("H\n")

def go_bet(io):
	my_value, dealer_value = do_bet(io)
	make_decision(io, my_value, dealer_value)
	while True:
		#data = read_timeout(io, 0.5)
		io.read_until("to Stay.\n")
		#data = io.read_until_timeout(0.5)
		if "Wins and " in data:
			io.write("Y\n")
			return 
		my_value, dealer_value = get_status(data)
		make_decision(io, my_value, dealer_value)
	return 

while True:
	go_bet(io)