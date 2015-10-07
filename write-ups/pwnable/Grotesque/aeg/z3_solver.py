from z3 import *
a1 = BitVec('a1', 8)
a2 = BitVec('a2', 8)
a3 = BitVec('a3', 8)
edx = BitVec('edx', 8)
eax = BitVec('eax', 8)
tmp0 = BitVec('tmp0', 8)
ecx = BitVec('ecx', 8)
s = Solver()
s.add(a1 == 0x20)
edx = a1
eax = edx
eax <<= 0x2
eax += edx
edx = 0x0+eax*4
eax += edx
eax -= a2
s.add(eax == 0x21)
eax = a1
tmp0 = eax
edx = 0x31
eax = tmp0
eax *= edx
ecx = eax
edx = a2
eax = edx
eax <<= 0x6
eax += edx
eax += ecx
eax -= a3
s.add(eax == 0x22)
print s.check()
print s.model()[a1], s.model()[a2], s.model()[a3]