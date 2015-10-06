from z3 import *
a1 = BitVec('a1', 8)
a2 = BitVec('a2', 8)
a3 = BitVec('a3', 8)
eax = BitVec('eax', 8)
edx = BitVec('edx', 8)
tmp0 = BitVec('tmp0', 8)
ecx = BitVec('ecx', 8)
s = Solver()
s.add(a1 == 0xbf)
eax = a1
edx = 0x47
eax *= edx
eax -= a2
s.add(eax == 0x25)
eax = a1
tmp0 = eax
edx = 0x5b
eax = tmp0
eax *= edx
edx = eax
eax = a2
ecx = 0x37
eax *= ecx
eax += edx
eax -= a3
s.add(eax == 0x28)
print s.check()
print s.model()[a1], s.model()[a2], s.model()[a3]