from pwn import *
context(arch = 'i386', os = 'linux')

origin = "\x31\xc0\x50\x68\x2f\x2f\x73\x68"

for i in range(4):
	for index in range(256):
		modify = [c for c in origin]
		modify[i] = chr(index)

		asm_code = "".join(modify)
		print "--------------"
		print disasm(asm_code)
