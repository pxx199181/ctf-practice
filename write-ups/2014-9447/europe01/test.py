from zio import *
io = zio("./main", timeout = 9999)
io.write("1111\x002222\x003333\n123123")
io.interact()