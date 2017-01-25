import random as rand
import sys
from UnitNumber import *
from AstroObject import *
import Station as station
import Spacecraft as spacecraft

'''
Things to add later
___________________
	Space Ship class
		movement types class
	Sub-classes of galaxies with different structures
	Sub-classes/variations of stars systems with different setups like binary
		https://en.wikipedia.org/wiki/Planetary_system#Components
	Sub-classes of star types like pulsar
	Sub-classes or properties of planets to represent different types
		https://en.wikipedia.org/wiki/Planet
		https://en.wikipedia.org/wiki/List_of_exoplanet_extremes
		https://en.wikipedia.org/wiki/Exoplanet
		http://jilawww.colorado.edu/~pja/planets/extrasolar.html
		http://exoplanets.org/table
	Natural Satellites
		https://en.wikipedia.org/wiki/Natural_satellite
	Other Objects
		https://en.wikipedia.org/wiki/Astronomical_object#Categories_by_location
	possible galaxy motion
		nope that's lame
'''

class Galaxy:
	def __init__(self, numsystems=200):
		self.name = 'Disc Galaxy'
		self.real_position = UVector2D()
		self.color = 'pink'
		self.draw_radius = 3
		self.moving = False
		#rand.seed('seednumberone')
		self.systems = []
		self.radius = UNum(5.4842, ly=1) * float(numsystems)**0.5
		self.name_array = []
		for i in range(676):
			self.name_array.append(0)

		print('Generating', numsystems, 'System Galaxy...')
		#print('0 Systems', end='')
		sys.stdout.flush()
		for i in range(numsystems):
			position_vector = UVector2D(value=self.radius)
			while position_vector.value >= self.radius:
				x = self.radius * (2 * (rand.random() - 0.5) + 0.01)
				y = self.radius * (2 * (rand.random() - 0.5) + 0.01)
				position_vector = UVector2D(x=x, y=y)
			#print(position_vector)
			angle = position_vector.angle
			if angle < 0:
				angle = 2 * math.pi + angle
			name_num = math.floor((angle) * 676 / (2 * math.pi))
			self.name_array[name_num] += 1
			self.systems.append(StarSystem(position_vector, number=self.name_array[name_num]))
			'''if (i+1)%100==0:
				print('\b\b\b\b\b\b\b\b\b\b\b\b\b\b', end='')
				print(i + 1, 'Systems', end='')'''
			sys.stdout.flush()
		#print()
		print('Done.')

	def avgdist(self, sample_size=0):
		totaldist = UNum(0, ly=1)
		values = 0
		if sample_size==0:
			sample_size = len(self.systems)
		print('Computing Average Distance. Sample size:', sample_size, '...')
		for system in self.systems[:sample_size]:
			min_dist = self.radius
			for othersystem in self.systems:
				dist = system.dist(othersystem)
				if dist < min_dist and system.id!=othersystem.id:
					min_dist = dist
			totaldist += min_dist
			values += 1
		return totaldist / values

	def mindist(self, sample_size=0):
		if sample_size==0:
			sample_size = len(self.systems)
		print('Computing Minimum Distance. Sample size:', sample_size, '...')
		max_min_dist = UNum(1, ly=1)
		min_min_dist = UNum(10, ly=1)
		i=0
		for system in self.systems[:sample_size]:
			i+=1
			min_dist = self.radius
			for othersystem in self.systems:
				dist = system.dist(othersystem)
				if dist < min_dist and system.id!=othersystem.id:
					min_dist = dist
			if min_dist > max_min_dist:
				max_min_dist = min_dist
			if min_dist < min_min_dist:
				min_min_dist = min_dist
		return (min_min_dist, max_min_dist)

class Alphabets:
	greek_alph = ['Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon', 'Zeta', 'Eta', 'Theta']
	capital_letters = (
	'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
	'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z')
	lowercase_letters = (
	'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
	'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z')

class StarSystem(StationaryObject):
	def __init__(self, position_vector, number=0, clockwise=None):
		super().__init__(position=position_vector)
		if clockwise is None:
			clockwise = bool(rand.getrandbits(1))
		self.clockwise = clockwise
		angle = self.real_position.angle
		if angle < 0:
			angle = 2*math.pi + angle
		name_num = math.floor((angle) * 676 / (2*math.pi))

		self.name = Alphabets.capital_letters[math.floor(name_num/26)] + \
					Alphabets.capital_letters[name_num % 26] + \
					str(number)
		self.type_name = 'Star System'
		self.color = 'white'
		self.moving = False
		self.draw_radius = 0

		self.id = name_num*10^(len(str(number))) + number

		#STARS
		num_stars = 1
		'''if rand.random() < 0.2:
			num_stars = 2'''
		self.stars = []
		if num_stars>1:
			for i in range(num_stars):
				self.stars.append(Star(self,
									   UNum(1, suns=1),
									   self.name+' '+Alphabets.greek_alph[i],
									   self.id*10+i))
		elif num_stars==1:
			self.stars = [Star(self,
							   UNum(1, suns=1),
							   self.name,
							   self.id*10)]
		for star in self.stars:
			self.mass += star.mass

	def __getattr__(self, attr):
		if attr == 'planets':
			core = station.Core(0, 100, spacecraft.Shield(2, 'Core Shield', UNum(5, hrs=-1), 100))
			design = station.Design(core, [spacecraft.Generator(3, 'Basic Generator', UNum(10, J=1, s=-1))], [], [])
			#PLANETS
			num_planets = math.ceil(10 * rand.random())
			#num_planets = 26
			self.planets = []
			for i in range(num_planets):
				e = (rand.random()*0.8)**2
				semimajor_axis = UNum(1, AU=1) * 10**((rand.random()**1.1) * 2 - 0)
				mass = UNum(1, earths=1) * 10**((rand.random()**0.5) * 3.5 - 1)
				self.planets.append(Planet(self, semimajor_axis, mass=mass, eccentricity=e, clockwise=self.clockwise))
			self.planets.sort(key=lambda x: x.orbit.semimajor_axis, reverse=False)
			#print('______________'+self.name+'______________')
			for i in range(len(self.planets)):
				self.planets[i].name = self.name + ' ' + Alphabets.lowercase_letters[i]
				self.planets[i].id = self.id + i * 10**(-len(str(i)))
				self.planets[i].orbiters.append(design.build(self.planets[i], UNum(100000, km=1), 0, name='Test Station'))
				self.planets[i].orbiters[0].id = self.planets[i].id * 10
			#self.planets[i].print(units=['AU', 'yrs', 'earths'])
			return self.planets
		else:
			raise AttributeError("%r object has no attribute %r" % (self.__class__, attr))

	def get_pos(self, time):
		return self.real_position

	def dist(self, othersystem):
		return (self.real_position - othersystem.real_position).value

#later can change this to orbit around system center for binary systems
class Star(Orbiter):
	def __init__(self, orbit_focus, mass, name, id, eccentricity=0.):
		semimajor_axis = UNum(0, ly=1)
		self.type_name = 'Star'
		self.name = name
		self.id = id
		super().__init__(orbit_focus, semimajor_axis, mass=mass, eccentricity=eccentricity)
		self.luminosity = 0.
		self.draw_radius = 4
		self.color = 'yellow'
		self.orbiters = []

class Planet(Orbiter):
	def __init__(self, orbit_focus, semimajor_axis, mass=UNum(1, earths=1), eccentricity=0., clockwise=False):
		self.type_name = 'Planet'
		super().__init__(orbit_focus, semimajor_axis, mass=mass, eccentricity=eccentricity, clockwise=clockwise)
		self.color = 'green'
		self.draw_radius = 3
		self.id = -1
		self.orbiters = []

class Asteroid(Orbiter):
	def __init__(self, orbit_focus, semimajor_axis):
		self.type_name = 'Asteroid'
		super().__init__(orbit_focus, semimajor_axis)
		self.color = 'brown'
		self.draw_radius = 2

class Station(Orbiter):
	def __init__(self, orbit_focus, semimajor_axis):
		self.type_name = 'Station'
		super().__init__(orbit_focus, semimajor_axis)
		self.color = 'white'
		self.draw_radius = 2

def main():
	'''n = 1000
	galaxy = Galaxy(n)
	mindist = galaxy.mindist(sample_size=50)
	print(round(mindist[0], 2), '-', round(mindist[1], 2))
	print(round(galaxy.avgdist(sample_size=50), 2))
	'''

	focus = StationaryObject(mass=UNum(1, suns=1))
	#orbit = Orbit(focus, )

	#print(orbit.get_pos(UNum(0, yrs=1)))
	#print(orbit.get_vel(UNum(0, yrs=1)))

	'''for planet in galaxy.systems[0].planets:
		print()
		print('Eccentricity:', planet.orbit.eccentricity)
		print('Period:', planet.orbit.period)
		for t in range(2):
			time = planet.orbit.period * t / 2
			print(round(time, 3), planet.orbital_position(time).convert(['AU']).polarstr())
	'''

if __name__=="__main__":
	main()
	input('Hit Enter to Exit')
