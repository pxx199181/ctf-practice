import pwnlib
def get_asm_data(asm_lines, arch_i = 'arm', os_i = 'linux'):
	data = ""
	for line in asm_lines:
		data += pwnlib.asm.asm(line, arch = arch_i, os = os_i)
	return data
def run_shellcode(asm_lines, arch_i = 'arm', os_i = 'linux'):
	data = ""
	for line in asm_lines:
		data += pwnlib.asm.cpp(line, arch = arch_i, os = os_i)
	return data
asm_lines  = []
#asm_lines.append("add	r6, pc, #1")
#asm_lines.append("bx	r6")
asm_lines.append("mov	r3, pc")
asm_lines.append("adds	r3, #4")
asm_lines.append("push	{r3}")
asm_lines.append("pop	{pc}")
asm_lines.append("pop	{r6}")
asm_lines.append("mov	r0, r3")
asm_lines.append("sub	sp, r11, #0")
asm_lines.append("pop	{r11}")
asm_lines.append("bx	lr")
data = get_asm_data(asm_lines, arch_i = 'arm', os_i = 'linux')
print [hex(ord(c)) for c in data]
print pwnlib.asm.disasm(data[1:], arch = 'arm', os = 'linux')

asm_lines.append("r0")
data = run_shellcode(asm_lines, arch_i = 'arm', os_i = 'linux')
print data
