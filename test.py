#!/usr/bin/env python

import time
from random import shuffle
from random import randrange
import socket
import threading

aids = ["b0","b1","a0","a1","a2","a3","a4","g0","h0","h1"]

class test_server_actuators:
	aid = None
	state = None
	cfg = None
	socket = None

	spin_i = 0
	spin_len = 100
	spinning = False

	def __init__(self, aid):
		self.aid = aid
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.connect(("", 1738))
		self.getCfg()

	def getCfg(self):
		data = self.aid + ":?;"
		self.socket.send(data.encode())
		print(self.aid, "->", data)
		data = self.socket.recv(409).decode()
		print(self.aid, "<-", data)

	def setState(self):
		self.state = (randrange(999) + 1.0) / 1000.0 * 6.28

	def setCfg(self):
		self.cfg = str(randrange(255)) + ","
		self.cfg = self.cfg + str(randrange(255)) + ","
		self.cfg = self.cfg + str(randrange(255)) + ",;"

	def step(self):
		self.setState()
		self.setCfg()

		data = self.aid + ":" + "{0:.6f}".format(self.state) + ";" + self.cfg
		self.socket.send(data.encode())
		print(self.aid, "->", data)

		data = self.socket.recv(4096).decode()
		print(self.aid, "<-", data)

	def spin(self):
		self.spinning = True
		for i in range(self.spin_len):
			self.step()
			self.spin_i = self.spin_i + 1
		self.spinning = False

	def close(self):
		self.socket.close()

class test_server_ethernet:
	socket = None
	conn = None
	addr = None

	aids = []
	cmds = ""

	spin_i = 0
	spin_len = 100
	spinning = False

	def __init__(self, aids):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.socket.bind(("", 12345))
		self.socket.listen(2)

		self.conn, self.addr = self.socket.accept()
		self.conn.settimeout(3)

		self.aids = aids

	def setCmds(self):
		self.cmds = ""
		for aid in self.aids:
			cmd = str(randrange(255)) + ","
			cmd = cmd + str(randrange(255)) + ","
			cmd = cmd + str(randrange(255)) + ","
			cmd = cmd + str(randrange(255))
			self.cmds = self.cmds + aid + ":" + cmd + ";"

	def step(self):
		self.setCmds()
		data_send = self.cmds
		self.conn.send(data_send.encode())
		print("eth ->", data_send)
		data_recv = self.conn.recv(4096).decode()
		print("eth <-", data_recv)
		time.sleep(1 / 20.0)

	def spin(self):
		self.spinning = True
		for i in range(self.spin_len):
			self.step()
		self.spinning = False

	def close(self):
		self.conn.close()
		self.socket.close()

def test():
	global aids

	tse = test_server_ethernet(aids)
	tsa = []

	for aid in aids:
		tsa.append(test_server_actuators(aid))

	tse_thread = threading.Thread(target=tse.spin, args=())
	tse_thread.daemon = True
	tse_thread.start()

	for t in tsa:
		tsa_thread = threading.Thread(target=t.spin, args=())
		tsa_thread.daemon = True
		tsa_thread.start()

	while tse.spinning == True:
		time.sleep(0.5)

	for t in tsa:
		while t.spinning == True:
			time.sleep(0.5)

	'''test_len = 1
	for i in range(test_len):
		tse.step()
		for t in tsa:
			t.step()
		shuffle(tsa)'''

	tse.close()
	for t in tsa:
		t.close()

test()
