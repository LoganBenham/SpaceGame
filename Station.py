from Spacecraft import *
from UnitNumber import *

class Module(Part):
	def __init__(self, size, hp, shield):
		super().__init__(size, 'unused module name attr')
		self.type = 'Module'
		del self.name
		self.max_hp = hp
		self.hp = hp
		self.shield = shield

	def __str__(self):
		if self.hp==self.max_hp:
			return Component.sizes[self.size] + ' ' + self.type
		else:
			return Component.sizes[self.size]+' '+self.type+' ['+str(self.hp)+'/'+str(self.max_hp)+']'

	def __hash__(self):
		return hash((self.type, self.size, self.max_hp, self.shield))

class Docking_Bay(Module):
	def __init__(self, size, hp, shield):
		super(). __init__(size, hp, shield)

class Core(Module):
	def __init__(self, size, hp, shield):
		super().__init__(size, hp, shield)
		self.docking_bay = Docking_Bay(size, 1, Shield(0, 'unused', UNum(0, hrs=-1), 0))
		self.type = 'Core Module'

	def copy(self):
		return Core(self.size, self.hp, self.shield.copy())

class Design:
	def __init__(self, core, gens, sensors, weapons):
		self.core = core
		self.gens = gens
		self.sensors = sensors
		self.weapons = weapons

	def build(self, focus, dist, team, name=None):
		station = Station(self.core, focus, dist, team, name=name)
		station.gens += self.gens
		station.sensors += self.sensors
		station.weapons += self.weapons
		return station

class Station(Spacecraft):
	def __init__(self, core, focus, dist, team, name=None):
		super().__init__(core.size, focus, dist, team)
		self.orbiters = []
		if name:
			self.name = name
		self.type_name = self.size_str + ' Station'
		self.core = core.copy()
		self.modules = []
		self.gens = []
		self.sensors = []
		self.weapons = []

def main():  #Test Run
	from Simulation import StationaryObject
	core = Core(0, 100, Shield(2, 'Core Shield', UNum(5, hrs=-1), 100))
	design = Design(core, [Generator(3, 'OP Generator', UNum(10, J=1, s=-1))], [], [])
	station = design.build(StationaryObject(), UNum(100, km=1), 0, name='My Cool Station')
	print(station.name)
	print(station.type_name)
	print(station.core)
	print(station.gens[0])

if __name__=="__main__":
	main()