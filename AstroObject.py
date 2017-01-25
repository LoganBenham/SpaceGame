from UnitNumber import *
import random as rand

class StationaryObject:  # Newtonian object, mainly for centers of galaxies
	def __init__(self, mass=UNum(0, suns=1), position=UVector2D(value=UNum(0, ly=1), angle=0.)):
		self.mass = mass
		if type(position)!=UVector2D:
			raise TypeError('Position must be UVector2D')
		self.real_position = position
		self.orbiters = []
		self.type_name = 'Newtonian Object'
		self.orbiting = False

	def get_pos(self, time):
		return self.real_position

class Orbit:
	def __init__(self, focus, semimajor_axis, eccentricity, periapsis=None, angle=None, time=UNum(0, yrs=1), clockwise=False):
		if type(semimajor_axis)!=UNum:
			raise TypeError('Semimajor Axis has no units')
		if eccentricity >= 1 or eccentricity < 0:
			raise ValueError('Eccentricity can only be from 0-0.999...', eccentricity)
		self.focus = focus
		self.semimajor_axis = semimajor_axis
		self.eccentricity = eccentricity
		self.start_time = time
		self.clockwise = clockwise

		if periapsis is not None:
			self.periapsis = periapsis
		else:
			self.periapsis = 2 * math.pi * rand.random()  # angle
		if angle is not None:
			self.initial_angle = angle
		else:
			self.initial_angle = 2 * math.pi * rand.random()

		self.mu = Physics.G_myunits * self.focus.mass
		self.period = UNum(0, yrs=1)
		if not self.mu.number==0:
			self.period = (((self.semimajor_axis**3) / self.mu)**0.5) * 2 * math.pi
		return

	# noinspection PyPep8Naming
	def get_pos(self, time, debug=False):
		if self.semimajor_axis.number==0.:
			return self.focus.real_position
		elif self.focus.mass.number==0:
			raise ValueError('Orbiting something with no mass')
		mean_anomaly = (self.period**-1 * (time - self.start_time - self.period) * 2 * math.pi).number
		eccentric_anomaly = self.inversekepler(mean_anomaly)
		#print('mean anomaly:', mean_anomaly)
		#print('eccentric anomaly:', eccentric_anomaly)
		cos_E = math.cos(eccentric_anomaly)
		sin_E = math.sin(eccentric_anomaly)
		e = self.eccentricity
		cos_true = (cos_E - e) / (1 - e * cos_E)
		sin_true = math.sqrt(1 - e**2) * sin_E / (1 - e * cos_E)
		true_anomaly = math.atan2(sin_true, cos_true)
		if self.clockwise:
			true_anomaly = -true_anomaly
		distance = self.semimajor_axis * (1 - e**2) / (1 + (e * math.cos(true_anomaly)))
		return UVector2D(value=distance,
						 angle=true_anomaly + self.initial_angle + self.periapsis) + self.focus.real_position

	def get_vel(self, time):
		x = self.get_pos(time, debug=True) - self.focus.get_pos(time)
		dx = self.get_pos(time + self.period/100) - self.get_pos(time - self.period/100)
		angle = dx.angle
		term1 = x.value**-1
		term2 = self.semimajor_axis**-1
		speed = (self.mu*(term1*2 - term2))**0.5
		return UVector2D(value=speed, angle=angle)

	def orbital_position(self, time):
		return (self.get_pos(time)-self.focus.position).rotate(-self.periapsis)

	def orbit_points(self, position_unit, n=30):
		points = []
		for i in range(n):
			eccentric_anomaly = 2 * math.pi * i / n
			cos_E = math.cos(eccentric_anomaly)
			sin_E = math.sin(eccentric_anomaly)
			e = self.eccentricity
			cos_true = (cos_E - e) / (1 - e * cos_E)
			sin_true = math.sqrt(1 - e**2) * sin_E / (1 - e * cos_E)
			true_anomaly = math.atan2(sin_true, cos_true)
			if self.clockwise:
				true_anomaly = -true_anomaly
			distance = self.semimajor_axis * (1 - self.eccentricity**2) / (1 + (self.eccentricity * math.cos(true_anomaly)))
			vec = UVector2D(value=distance, angle=true_anomaly + self.periapsis + self.initial_angle)
			vec = (vec + self.focus.real_position).convert([position_unit])
			points.append(Vector2D(x=vec.x.number, y=vec.y.number))
		return points

	def inversekepler(self, mean_anom):
		ecc_anom = mean_anom
		for i in range(35):
			ecc_anom = mean_anom + self.eccentricity * math.sin(ecc_anom)
		return ecc_anom

	def print(self):
		#print('SM-Axis:', self.semimajor_axis)
		print('e:', self.eccentricity)
		print('periapsis:', self.periapsis)
		#print('period:', self.period)
		print('start time:', self.start_time)
		print('start angle:', self.initial_angle)

	def get_system(self):
		focus = self.focus
		while focus.type_name!='Star System':
			focus = focus.orbit.focus
		return focus

	def __getattr__(self, attr):
		if attr == 'apoapsis_dist':
			return self.semimajor_axis * (1+self.eccentricity)
		elif attr == 'periapsis_dist':
			return self.semimajor_axis * (1-self.eccentricity)
		else:
			raise AttributeError("%r object has no attribute %r" % (self.__class__, attr))

class OrbitFromVectors(Orbit):
	def __init__(self, focus, position, velocity, time=UNum(0, yrs=1)):
		pos = position - focus.get_pos(time)
		vel = velocity
		angular_momentum = pos.value * vel.value * math.sin(vel.angle - pos.angle) #in 3rd dim
		mu = Physics.G.convert(['AU', 'yrs']) * focus.mass
		term1 = pos * (vel.value**2 - mu/pos.value)
		term2 = vel * pos.dot(vel)
		e_vec = ((term1 - term2) / mu)
		e_vec = e_vec.number()
		if angular_momentum.number >= 0:
			term1_2 = Vector2D(value=(vel.value*angular_momentum/mu).number, angle=vel.angle-math.pi/2)
		else:
			term1_2 = Vector2D(value=(vel.value*angular_momentum/mu).number, angle=vel.angle+math.pi/2)
		term2_2 = Vector2D(value=1, angle=pos.angle)
		e_vec_2 = term1_2 - term2_2
		e = e_vec.value
		mech_energy = (vel.value**2)/2 - mu/pos.value
		semimajor_axis = mu / (mech_energy * -2)
		periapsis = e_vec.angle
		if angular_momentum.number < 0:
			periapsis = 2*math.pi - periapsis
		while periapsis > 2*math.pi:
			periapsis -= 2*math.pi
		true_anomaly = pos.angle - periapsis
		super().__init__(focus, semimajor_axis, e, periapsis=periapsis, angle=true_anomaly, time=time)
		self.print()

class Orbiter:
	def __init__(self, focus, semimajor_axis, mass=UNum(0, kg=1), eccentricity=0., clockwise=False):
		if not hasattr(self, 'type_name'):
			self.type_name = 'Generic Orbiter'
		if not hasattr(self, 'name'):
			self.name = 'noname'

		self.color = 'orange'
		self.draw_radius = 2
		self.mass = mass
		self.orbiting = True

		self.orbit = Orbit(focus, semimajor_axis, eccentricity, clockwise=clockwise)
		if self.orbit.period.number==0.:
			self.moving = False
			self.real_position = self.orbit.focus.real_position
		else:
			self.moving = True

	def get_pos(self, time):
		return self.orbit.get_pos(time)

	def get_vel(self, time):
		return self.orbit.get_vel(time)

	def set_pos(self, time):
		self.real_position = self.get_pos(time)

	def __str__(self):
		return self.name + ' - ' + self.type_name