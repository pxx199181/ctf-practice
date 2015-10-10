from z3 import *
from zio import *
x = BitVec('x', 64)
num = BitVec('num', 64)
flag = BitVec('flag', 64)
answ = BitVec('answ', 64)

x = 0x3CC6C7B7 * num
answ = l64("ASIS{\x00\x00\x00")
flag = x&0x000000ffffffffff

print answ
print flag
s = Solver()
s.add(flag == answ)
s.add(num < 0x7fffffffffffffff)
print s.check()
print s.model()
#x=6215896560533655570
