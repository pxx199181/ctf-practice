import struct

def get_str(value):
	return struct.pack("I", value)

def is_can_see(value):
	for t_v in [ord(ch_t) for ch_t in value]:
		if t_v < 0x20 or t_v >= 127:
			return False
	return True

def get_can_see(value1, value2, amp):
	total = value1 + value2
	for i in range(0x20, 127):
		tmp_v = total - i * amp
		if tmp_v >= 0x20 and tmp_v < 127:
			return True, chr(i), chr(tmp_v)
	return False, 0, 0
#value = ') # ) # ) # ) # }\}l'
#value = ' # ) # ) # ) # )l}\}'

hashcode = 0x21DD09EC
print get_can_see(0, 0x121, 4)
print get_can_see(0, 0xDC, 4)
print get_can_see(0, 0x109, 4)
print get_can_see(0, 0xEC, 4)