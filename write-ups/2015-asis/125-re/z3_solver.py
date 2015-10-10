from z3 import *
x = BitVec('x', 64)
a = BitVec('a', 64)
b = BitVec('b', 64)
c = BitVec('c', 64)
d = BitVec('d', 64)
e = BitVec('e', 64)

a = -59762*x
b = 14392*x*x
c = 1256*x*x*x
d = 45235*x*x*x*x
e = 44242*x*x*x*x*x
s = Solver()
s.add(x < 3000000)
s.add(a + b + c + d + e == 1949670109068)
print s.check()
print s.model()
#x=6215896560533655570
