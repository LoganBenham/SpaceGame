from AstroObject import Orbiter
from UnitNumber import UNum

class Part:
	sizes = {
		-2: 'XS',
		-1: 'S',
		0 : 'M',
		1 : 'L',
		2 : 'XL',
		3 : 'VL',
		4 : 'G'
	}
	sizes_long = {
		-2: 'Extra Small',
		-1: 'Small',
		0 : 'Medium',
		1 : 'Large',
		2 : 'Extra Large',
		3 : 'Very Large',
		4 : 'Giant'
	}

	def __init__(self, size, name):
		if size not in Part.sizes.keys():
			raise ValueError('Invalid Size Number')
		self.size = size
		self.name = name
		self.type = 'Spacecraft Part'

	def __str__(self):
		result = self.name + ' '
		result += '['+Part.sizes[self.size]+']'
		return result

	def __hash__(self):
		return hash((self.name, self.type, self.size))

	def __eq__(self, other):
		return hash(self)==hash(other)

	def __getattr__(self, attr):
		if attr not in ['sizename', 'sizenamelong']:
			raise AttributeError("Component has no attribute %r" % attr)
		elif attr=='sizename':
			return Part.sizes[self.size]
		elif attr=='sizenamelong':
			return Part.sizes_long[self.size]

class Component(Part):
	def __init__(self, size, name):
		super().__init__(size, name)
		self.type = 'Spacecraft Component'
		self.type_short = 'Comp'

	def print_info(self):
		print(self.name+':', Part.sizes_long[self.size], self.type)

class Generator(Component):
	def __init__(self, size, name, gen_rate):
		super().__init__(size, name)
		self.gen_rate = gen_rate

class Shield(Component):
	def __init__(self, size, name, recharge, hp):
		super().__init__(size, name)
		self.hp = hp
		self.recharge = recharge
		self.type = 'Plasma Shield'
		self.type_short = 'Shield'

	def __hash__(self):
		return hash((self.name, self.type, self.size, self.hp, self.recharge))

	def copy(self):
		return Shield(self.size, self.name, self.recharge, self.hp)

class Weapon(Component):
	types = {
		1 : 'Projectile',
		2 : 'Missile',
		3 : 'Energy'
	}
	types_short = {
		1 : 'P',
		2 : 'M',
		3 : 'E'
	}
	def __init__(self, size, name, type):
		super().__init__(size, name)
		self.type = type
		self.hull_dmg_multiplier = 1
		self.shield_dmg_multiplier = 1
		if self.type == 1:
			def range_acc(dist):
				return 1
			def track_acc(angular_speed):
				return 1
			self.hull_dmg_multiplier = 1.5
		elif self.type == 2:
			def range_acc(dist):
				return 1
			def track_acc(angular_speed):
				return 1
			self.hull_dmg_multiplier = 2
			self.shield_dmg_multiplier = 0.75
		elif self.type == 3:
			def range_acc(dist):
				return 1
			def track_acc(angular_speed):
				return 1
			self.shield_dmg_multiplier = 1.5
		else:
			raise ValueError('Invalid Weapon Type')
		self.range_acc = range_acc
		self.track_acc = track_acc

class Sensor(Component):
	types = {
		1 : 'Radar Transceiver',
		2 : 'Microwave Transceiver',
		3 : 'Telescope'
	}
	types_short = {
		1 : 'Radar',
		2 : 'Microwave',
		3 : 'Telescope'
	}
	def __init__(self, size, name, type):
		super().__init__(size, name)
		if type not in Sensor.types.keys():
			raise ValueError('Invalid Sensor Type')
		self.type = type

class Spacecraft(Orbiter):
	def __init__(self, size, focus, dist, team):
		super().__init__(focus, dist)
		self.size = size
		self.size_str = Component.sizes[self.size]
		self.size_str_long = Component.sizes_long[self.size]
		self.name = 'Generic Spacecraft'
		self.team = team
		self.draw_radius = 2
		if team == 0:
			self.color = 'light blue'
		else:
			self.color = '#668880'