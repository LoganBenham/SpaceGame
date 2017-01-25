import operator
import math

# Usage Examples:
# UNum(100, kg=1, ly=3)
# UNum(0.1, ly=-2)

#add method to automatically assign unit to number with only one dimension
#working with dicts can be kind of annoying when you need to sort stuff...

class Units:
	mass_units = {
		'earths': 1,
		'kg'    : 5.972 * (10**24),
		'suns'  : 1 / 332948.6
	}
	time_units = {
		'galactic years' : 1/(240*10**6),
		'millennia' : 1/1000,
		'yrs' : 1,
		'days': 365.25,
		'hrs' : 8760,
		's'   : 31557600
	}
	dist_units = {
		'ly': 1,
		'm' : 9.461 * (10**15),
		'au': 63241.0771,
		'km': 9.461 * (10**12),
		'AU': 63241.077,
		'Mm': 9.461 * (10**9)
	}
	energy_units = {
		'J': 1,
	}
	dimensions_units = {'mass'  : mass_units,
						'time'  : time_units,
						'dist'  : dist_units,
						'energy': energy_units}
	SI_units = ['m', 'kg', 's', 'J']

class UNum:
	def __init__(self, number, **units):
		self.number = number
		self.units = units  # dict

	def get_dims(self):
		mass = None
		time = None
		dist = None
		energy = None
		self.dims = {'mass': mass, 'time': time, 'dist': dist, 'energy':energy}
		for unit in self.units.keys():  # iterating through strings for units
			for dim in self.dims.keys():  # iterating through strings for each dim
				dim_units = Units.dimensions_units[dim]
				if unit in dim_units.keys():  # if object's units are of the dim
					if self.dims[dim] is not None:
						del self.units[unit]
					else:
						self.dims[dim] = unit
		return self.dims

	def copy(self):
		return UNum(self.number, **self.units)

	def convert(self, units):
		if set(units) <= set(self.units.keys()):
			return self
		#print('converting from', set(self.units.keys()), 'to', set(units))
		# print('Converting', self, 'to', units)
		# quickest way for me to code a conversion from tuple to list without learning
		new_dims = {'mass': None, 'time': None, 'dist': None, 'energy': None}
		self.get_dims()
		i = 0
		# iterating through each unit to verify dims
		while i < len(units):
			for dim in self.dims.keys():  # for each possible dim
				if units[i] in Units.dimensions_units[dim]:  # if unit matches possible units
					if new_dims[dim] is not None:  # if dim is already in place, delete unnecessary unit
						del units[i]  # note: this will delete any extra units after the first for each dim
						i -= 1  # if input is unclean and this must be done, info is lost
					else:
						new_dims[dim] = units[i]
			i += 1
		# print('New Dims:', new_dims)
		# that was necessary to ensure there is no ambiguity in this next, critical step
		new_units = {}
		new_number = self.number
		# doing the actual conversion
		for self_unit in self.units.keys():  # iterating through current units
			for dim in self.dims.keys():  # iterating through current dims
				# only proceed when self_unit matches dim, and unit is actually being used
				if self_unit!=self.dims[dim] or self.units[self_unit]==0:
					continue  # exits for loop
				# this way we ignore any conversion units that don't match the current dimensions
				dim_units = Units.dimensions_units[dim]  # possible units for this dim
				converted = False
				for new_unit in units:
					if new_unit in dim_units.keys():  # unit matches current dim
						new_units[new_unit] = self.units[self_unit]  # add dict entry for new unit
						ratio = dim_units[new_unit] / dim_units[self_unit]
						new_number *= (ratio**self.units[self_unit])  # do number conversion
						converted = True
				if not converted:
					new_units[self_unit] = self.units[self_unit]
		# print('returns:', UNum(new_number, **new_units))
		return UNum(new_number, **new_units)

	def reduce(self):
		reduced = self.reduced()
		self.number = reduced.number
		self.units = reduced.units
		return self

	# noinspection PyUnreachableCode
	def reduced(self):
		if len(self.units) > 1:
			raise TypeError('Must be a number of 1 dimension')
			return self
		elif len(self.units)==0:
			return self
		else:
			self.get_dims()
			if self.dims['mass'] is not None:
				dim_units = Units.mass_units
			elif self.dims['time'] is not None:
				dim_units = Units.time_units
			elif self.dims['dist'] is not None:
				dim_units = Units.dist_units
			elif self.dims['energy'] is not None:
				dim_units = Units.energy_units
			dim_unit_list = list(dim_units.keys())
			dim_unit_list = sorted(dim_unit_list, key=lambda x: dim_units[x])
			for dim_unit in dim_unit_list:
				converted = self.convert([dim_unit])
				if converted.number >= 1:
					return converted
			return converted

	def nice_str(self, n=None):
		return str(round(self.reduced(), n))

	def __str__(self):
		unit_str = str(self.number) + ' '
		for unit in sorted(self.units.items(), key=operator.itemgetter(1), reverse=True):
			numstr = str(unit[1])
			if numstr=='1' or numstr=='1.0':
				numstr = ''
			unit_str += str(unit[0]) + numstr
		# unit_str += ')'
		return unit_str

	def __add__(self, other):
		converted_other = other.convert(list(self.units.keys()))
		if self.units!=converted_other.units:
			raise ValueError('Different Units', self.units, converted_other.units)
		else:
			return UNum(self.number + converted_other.number, **self.units)

	def __iadd__(self, other):
		converted_other = other.convert(list(self.units.keys()))
		if self.units!=converted_other.units:
			raise ValueError('Different Units', self.units, converted_other.units)
		else:
			self.number += converted_other.number
			return self

	def __sub__(self, other):
		converted_other = other.convert(list(self.units.keys()))
		if self.units!=converted_other.units:
			raise ValueError('Different Units', self.units, converted_other.units)
		else:
			return UNum(self.number - converted_other.number, **self.units)

	def __isub__(self, other):
		converted_other = other.convert(list(self.units.keys()))
		if self.units!=converted_other.units:
			raise ValueError('Different Units', self.units, converted_other.units)
		else:
			self.number -= converted_other.number
			return self

	def __mul__(self, other):
		if type(other)==UNum:
			converted_other = other.convert(list(self.units.keys()))
			num = self.number * converted_other.number
			units = self.units.copy()
			for otherunit in converted_other.units.keys():
				included = False
				for selfunit in self.units.keys():
					if selfunit==otherunit:
						units[otherunit] += converted_other.units[otherunit]
						included = True
				if not included:
					units[otherunit] = converted_other.units[otherunit]
				if units[otherunit]==0:
					del units[otherunit]
			return UNum(num, **units)
		elif type(other)==int or type(other)==float:
			return UNum(self.number * other, **self.units)
		else:
			raise TypeError(str(type(self))+' * '+str(type(other)))

	def __imul__(self, other):
		if type(other)==UNum:
			converted_other = other.convert(list(self.units.keys()))
			self.number *= converted_other.number
			for otherunit in converted_other.units.keys():
				included = False
				for selfunit in self.units.keys():
					if selfunit==otherunit:
						self.units[otherunit] += converted_other.units
						included = True
				if not included:
					self.units[otherunit] = converted_other.units[otherunit]
			for unit in self.units.keys():
				if self.units[unit]==0:
					del self.units[unit]
			return self
		elif type(other)==int or type(other)==float:
			self.number *= other
			return self
		else:
			raise ValueError('Invalid Type')

	def __truediv__(self, other):
		if type(other)==UNum:
			converted_other = other.convert(list(self.units.keys()))
			num = self.number / converted_other.number
			units = self.units.copy()
			for otherunit in converted_other.units.keys():
				included = False
				for selfunit in self.units.keys():
					if selfunit==otherunit:
						units[otherunit] -= converted_other.units[otherunit]
						included = True
				if not included:
					units[otherunit] = converted_other.units[otherunit] * -1
				if units[otherunit]==0:
					del units[otherunit]
			return UNum(num, **units)
		elif type(other)==int or type(other)==float:
			return UNum(self.number / other, **self.units)
		else:
			raise ValueError('Invalid Type')

	def __idiv__(self, other):
		if type(other)==UNum:
			converted_other = other.convert(list(self.units.keys()))
			self.number /= converted_other.number
			for otherunit in converted_other.units.keys():
				included = False
				for selfunit in self.units.keys():
					if selfunit==otherunit:
						self.units[otherunit] -= converted_other.units[otherunit]
						included = True
				if not included:
					self.units[otherunit] = converted_other.units[otherunit] * -1
				if self.units[otherunit]==0:
					del self.units[otherunit]
			return self
		elif type(other)==int or type(other)==float:
			self.number /= other
			return self
		else:
			raise ValueError('Invalid Type')

	def __pow__(self, power, modulo=None):
		num = self.number**power
		units = self.units.copy()
		for unit in units.keys():
			units[unit] *= power
		return UNum(num, **units)

	def __eq__(self, other):
		return self.number==other.convert(list(self.units.keys())).number

	def __ne__(self, other):
		return self.number!=other.convert(list(self.units.keys())).number

	def __gt__(self, other):
		return self.number > other.convert(list(self.units.keys())).number

	def __ge__(self, other):
		return self.number >= other.convert(list(self.units.keys())).number

	def __lt__(self, other):
		return self.number < other.convert(list(self.units.keys())).number

	def __le__(self, other):
		return self.number <= other.convert(list(self.units.keys())).number

	def __round__(self, n=None):
		return UNum(round(self.number, n), **self.units)


class UVector2D:
	def __init__(self, x=UNum(0., ly=1), y=UNum(0., ly=1), value=UNum(0., ly=1), angle=0.):
		if value.number==0. and angle==0.:
			if x.units!=y.units:
				raise TypeError('X and Y must be same units')
			self.x = x
			self.y = y
			self.cartesian = True
		elif x.number==0. and y.number==0.:
			self.value = value
			self.angle = angle
			self.cartesian = False
		else:
			raise ValueError('Use one coordinate system for initialization.')

	def __getattr__(self, attr):
		if attr in ['x', 'y']:
			if self.cartesian:
				raise AttributeError('Missing attribute:', attr)
			if attr=='x':
				return self.value * math.cos(self.angle)
			if attr=='y':
				return self.value * math.sin(self.angle)
		elif attr in ['value', 'angle']:
			if not self.cartesian:
				raise AttributeError('Missing attribute:', attr)
			if attr=='value':
				return (self.x**2 + self.y**2)**0.5
			if attr=='angle':
				return math.atan2(self.y.number, self.x.number)
		else:
			raise AttributeError("%r object has no attribute %r" % (self.__class__, attr))

	def cartesian(self):
		x = self.x
		y = self.y
		return UVector2D(x=x, y=y)

	def polar(self):
		value = self.value
		angle = self.angle
		return UVector2D(value=value, angle=angle)

	def reduced(self):
		return UVector2D(value=self.value.reduced(), angle=self.angle)

	def copy(self):
		if self.cartesian:
			return UVector2D(x=self.x, y=self.y)
		else:
			return UVector2D(value=self.value, angle=self.angle)

	def number(self):
		return Vector2D(x=self.x.number, y=self.y.number)

	def normal(self):
		return UVector2D(value=UNum(1, **self.value.units), angle=self.angle)

	def rotate(self, angle):
		return UVector2D(value=self.value, angle=self.angle + angle)

	def dot(self, other):
		if type(other)!=UVector2D:
			raise TypeError(str(type(self))+' dotted with '+str(type(other)))
		else:
			return self.x*other.x + self.y*other.y

	def __add__(self, other):
		return UVector2D(x=self.x + other.x, y=self.y + other.y)

	def __iadd__(self, other):
		self.x += other.x
		self.y += other.y
		self.update_polar()
		return self

	def __sub__(self, other):
		return UVector2D(x=self.x - other.x, y=self.y - other.y)

	def __isub__(self, other):
		self.x -= other.x
		self.y -= other.y
		self.update_polar()
		return self

	def __str__(self):
		#return '(' + str(self.x) + ', ' + str(self.y) + ')'
		return '(' + str(round(self.value, 2)) + ' at ' + str(round(self.angle * 180 / math.pi)) + ' deg.)'

	def roundstr(self, n=None):
		return '(' + str(round(self.value, n)) + ' at ' + str(round(self.angle * 180 / math.pi)) + ' deg.)'

	def __imul__(self, factor):
		self.x *= factor
		self.y *= factor
		self.update_polar()
		return self

	def __mul__(self, factor):
		x = self.x * factor
		y = self.y * factor
		return UVector2D(x=x, y=y)

	def __truediv__(self, factor):
		value = self.value / factor
		return UVector2D(value=value, angle=self.angle)

	def __idiv__(self, factor):
		self.x /= factor
		self.y /= factor
		self.cartesian = True
		return self

	def convert(self, units):
		return UVector2D(value=self.value.convert(units), angle=self.angle)

class Vector2D:
	def __init__(self, x=0., y=0., value=0., angle=0.):
		if value==0. and angle==0.:
			self.x = x
			self.y = y
			self.cartesian = True
		elif x==0. and y==0.:
			self.value = value
			self.angle = angle
			self.cartesian = False
		else:
			raise ValueError('Use one coordinate system for initialization.')

	def __getattr__(self, attr):
		if attr in ['x', 'y']:
			if self.cartesian:
				raise AttributeError('Missing attribute:', attr)
			if attr=='x':
				return self.value * math.cos(self.angle)
			if attr=='y':
				return self.value * math.sin(self.angle)
		elif attr in ['value', 'angle']:
			if not self.cartesian:
				raise AttributeError('Missing attribute:', attr)
			if attr=='value':
				return (self.x**2 + self.y**2)**0.5
			if attr=='angle':
				return math.atan2(self.y, self.x)
		else:
			raise AttributeError("%r object has no attribute %r" % (self.__class__, attr))

	def cartesian(self):
		x = self.x
		y = self.y
		return Vector2D(x=x, y=y)

	def polar(self):
		value = self.value
		angle = self.angle
		return Vector2D(value=value, angle=angle)

	def reduced(self):
		return Vector2D(value=self.value.reduced(), angle=self.angle)

	def copy(self):
		if self.cartesian:
			return Vector2D(x=self.x, y=self.y)
		else:
			return Vector2D(value=self.value, angle=self.angle)

	def normal(self):
		return Vector2D(value=1, angle=self.angle)

	def rotate(self, angle):
		return Vector2D(value=self.value, angle=self.angle + angle)

	def dot(self, other):
		if type(other)!=Vector2D:
			raise TypeError(str(type(self)) + ' dotted with ' + str(type(other)))
		else:
			return self.x*other.x + self.y*other.y

	def __add__(self, other):
		return Vector2D(x=self.x + other.x, y=self.y + other.y)

	def __iadd__(self, other):
		self.x += other.x
		self.y += other.y
		self.cartesian = True
		return self

	def __sub__(self, other):
		return Vector2D(x=self.x - other.x, y=self.y - other.y)

	def __isub__(self, other):
		self.x -= other.x
		self.y -= other.y
		self.cartesian = True
		return self

	def __str__(self):
		#return '(' + str(self.x) + ', ' + str(self.y) + ')'
		return '(' + str(round(self.value, 2)) + ' at ' + str(round(self.angle, 2)) + ' rads)'

	def __imul__(self, factor):
		self.x *= factor
		self.y *= factor
		self.cartesian = True
		return self

	def __mul__(self, factor):
		x = self.x * factor
		y = self.y * factor
		return Vector2D(x=x, y=y)

	def __truediv__(self, factor):
		x = self.x / factor
		y = self.y / factor
		return Vector2D(x=x, y=y)

	def __idiv__(self, factor):
		self.x /= factor
		self.y /= factor
		self.cartesian = True
		return self

	def polarstr(self):
		return '(' + str(round(self.value, 3)) + ' at ' + str(round(self.angle * 360 / (2 * math.pi))) + ' degrees)'

class Physics:
	G = UNum(6.674 * 10**-11, m=3, kg=-1, s=-2)
	myunits = ['ly', 'earths', 'yrs']
	G_myunits = G.convert(myunits)

def main():
	dist = UNum(400000, km=1)
	print(dist.convert(['AU']))

if __name__=="__main__":
	main()
	input('Hit Enter to Exit')
