#!/usr/bin/env python

import time
import os

class server_state:
	numRoutes = 0
	actuatorNames = []
	routeNames = []
	commands = []
	commandsPrev = []
	commandsTS = []
	commandsReceived = []
	states = []
	statesTS = []

	write_lock = False

	cfg_path = ""

	def __init__(self):
		self.addRoute("Base Wheel Left", "/cmd/b0", "nc;")
		self.addRoute("Base Wheel Right", "/cmd/b1", "nc;")
		self.addRoute("Arm Actuator 0", "/cmd/a0", "nc;")
		self.addRoute("Arm Actuator 1", "/cmd/a1", "nc;")
		self.addRoute("Arm Actuator 2", "/cmd/a2", "nc;")
		self.addRoute("Arm Actuator 3", "/cmd/a3", "nc;")
		self.addRoute("Arm Actuator 4", "/cmd/a4", "nc;")
		self.addRoute("Gripper Actuator 0", "/cmd/g0", "nc;")
		self.addRoute("Head Actuator Pan", "/cmd/h0", "nc;")
		self.addRoute("Head Actuator Tilt", "/cmd/h1", "nc;")
		self.addRoute("Sensor: Battery Voltage", "/cmd/s0", "nc;")

		self.cfg_path = os.path.dirname(os.path.abspath(__file__)) + "/cfg/";

	def updateConfig(self, act_id, cfg):
		if len(cfg.split(',')) == 4:
			try:
				with open(self.cfg_path + act_id, "w+") as f:
					f.write(cfg)
					f.flush()
					os.fsync(f.fileno())
			except Exception as e:
				print(e)

	def readConfig(self, act_id):
		try:
			with open(self.cfg_path + act_id, "r+") as f:
				return f.read()
		except Exception as e:
			print(e)
		return ''

	def getNumRoutes(self):
		return self.numRoutes

	def getRouteName(self, i):
		return self.routeNames[i]

	def setActuatorState (self, routeName, state):
		for i in range(len(self.states)):
			if self.routeNames[i] == routeName:
				self.states[i] = state
				self.statesTS[i] = time.time()

	def getActuatorState (self, routeName):
		for i in range(self.numRoutes):
			if self.routeNames[i] == routeName:
				return self.states[i]
		return ''

	def isStateActive(self, routeName):
		for i in range(self.numRoutes):
			if self.routeNames[i] == routeName:
				if time.time() - self.statesTS[i] < 2.0:
					return True
		return False

	def addRoute(self, actuatorName, routeName, cmd):
		self.actuatorNames.append(actuatorName)
		self.routeNames.append(routeName)
		self.states.append('')
		self.statesTS.append(time.time())
		self.commands.append(cmd)
		self.commandsPrev.append(cmd)
		self.commandsReceived.append(False)
		self.commandsTS.append(time.time())
		self.numRoutes += 1

	def getRouteCommandPrev(self, routeName):
		for i in range(self.numRoutes):
			if self.routeNames[i] == routeName:
				return self.commandsPrev[i]
		return ''

	def getRouteCommand(self, routeName):
		for i in range(self.numRoutes):
			if self.routeNames[i] == routeName:
				cmd = self.commands[i]
				self.commands[i] = ''
				return cmd
		return ''

	def editRouteCommand(self, routeName, cmd):
		for i in range(self.numRoutes):
			if self.routeNames[i] == routeName:
				self.commands[i] = self.commands[i] + cmd
				self.commandsPrev[i] = cmd
				self.commandsReceived[i] = False
				self.commandsTS[i] = time.time()
