import pygame as pg
import pygame.gfxdraw

from Menu import *
from Simulation import *
from UnitNumber import *

'''
Things to add later
___________________
	Selection
		display info on object selected
		right click to select and bring up options
			check if click is near selected object first and prioritize that
			options will be an empty container for any use
				simple map view could
'''

'''
TO DO
___________________

'''

#k-d tree (2d) class to partition objects for faster location searching
#currently bugged out and not worth fixing
class PositionTree:
	def __init__(self, objects_input, axis='x'):
		self.axis = axis
		#sort by axis
		objects = objects_input.copy()
		objects.sort(key=lambda obj: getattr(obj.position, axis), reverse=False)
		median_i = math.floor(len(objects)/2)  #remember indices start at 0
		#print(len(objects), median_i)
		self.median_index = objects[median_i].index
		self.median_position = objects[median_i].position
		if axis=='x':
			new_axis = 'y'
		elif axis=='y':
			new_axis = 'x'
		if len(objects)>2:
			self.lessChild = Map.PositionTree(objects[:median_i], axis=new_axis)
			self.greaterChild = Map.PositionTree(objects[median_i+1:], axis=new_axis)
		elif len(objects)==2:
			self.lessChild = Map.PositionTree([objects[0]], axis=new_axis)

	def nn(self, pos_vec, current_min):
		dist = (self.median_position - pos_vec).value
		if dist < current_min:
			less_nn = None
			greater_nn = None
			if hasattr(self, 'lessChild'):
				less_nn = self.lessChild.nn(pos_vec, dist)
			if hasattr(self, 'greaterChild'):
				greater_nn = self.greaterChild.nn(pos_vec, dist)

			if less_nn is not None:
				return less_nn
			elif greater_nn is not None:
				return greater_nn
			else:
				return self.median_index
		else:
			return None

	def render(self, surface, rect, scale, center):
		x = int(rect.centerx + scale * (self.median_position - center).x)
		y = int(rect.centery - scale * (self.median_position - center).y)
		if self.axis=='x':
			pg.draw.line(surface, pg.Color('grey'), (x, rect.top), (x, rect.bottom))
			less_rect = pg.Rect(rect.left, rect.top, x-rect.left, rect.bottom)
			greater_rect = pg.Rect(x, rect.top, rect.right-x, rect.height)
		elif self.axis=='y':
			pg.draw.line(surface, pg.Color('grey'), (rect.left, y), (rect.right, y))
			less_rect = pg.Rect(rect.left, y, rect.width, rect.bottom-y)
			greater_rect = pg.Rect(rect.left, rect.top, rect.width, y-rect.top)
		if hasattr(self, 'lessChild'):
			self.lessChild.render(surface, less_rect, scale, center)
		if hasattr(self, 'greaterChild'):
			self.greaterChild.render(surface, greater_rect, scale, center)

	def __len__(self):
		length = 1
		if hasattr(self, 'lessChild'):
			length += len(self.lessChild)
		if hasattr(self, 'greaterChild'):
			length += len(self.greaterChild)
		return length

class Map:
	def __init__(self, focus, surface, time=UNum(0, yrs=1), rect=None, trail=False, parent=None, draw_orbits=True):
		self.objects = []
		self.selected = None
		self.font = pg.font.SysFont('Arial', 14)
		self.surface = surface
		self.rect = rect
		self.trail = trail
		self.parent = parent
		self.tracking = None
		self.draw_orbits = draw_orbits
		if rect is None:
			#print('automatic rect creation')
			self.rect = self.surface.get_rect()
		else:
			print('map rect:', self.rect)
		self.update_rect()
		if isinstance(focus, Galaxy):
			self.type = 1
			self.position_unit = 'ly'
			self.objects = focus.systems
			self.default_dim = focus.radius.convert(['ly']).number * 2.4
			self.max_dim = self.default_dim
			self.min_dim = 2
		elif isinstance(focus, StarSystem):
			self.type = 2
			self.position_unit = 'AU'
			self.default_dim = 10
			for planet in focus.planets+focus.orbiters:
				num = planet.orbit.apoapsis_dist.convert(['AU']).number
				if num > self.default_dim:
					self.default_dim = num
			self.objects = focus.planets
			self.objects += focus.stars
			self.default_dim *= 2.4
			self.max_dim = self.default_dim
			self.min_dim = 0.05
		elif hasattr(focus, 'orbiters'):
			print(focus)
			self.focus = focus
			self.type = 3
			self.position_unit = 'km'
			self.default_dim = 4000
			self.focus.set_pos(time)
			if focus.orbiting:
				self.tracking = self.focus
			for orbiter in focus.orbiters:
				num = orbiter.orbit.apoapsis_dist.convert(['km']).number
				if num > self.default_dim:
					self.default_dim = num
			self.objects = [focus] + focus.orbiters
			self.default_dim *= 2.4
			self.max_dim = self.default_dim
			self.min_dim = 10
		else:
			raise TypeError('Invalid Focus')

		self.time = time
		self.current_dim = self.default_dim
		self.scale = self.rect.height / self.current_dim
		self.center = focus.real_position.convert([self.position_unit]).number()
		self.focus_center = self.center.copy()
		self.find_orbits()

		self.focus_text_surface = self.font.render(focus.name, True, pg.Color('white'))
		self.update_scale_ruler()

		for object in self.objects:
			if object.moving:
				vec = object.get_pos(time).convert([self.position_unit])
				object.position = vec.number()
				object.renderable = False
			else:
				vec = object.real_position.convert([self.position_unit])
				object.position = vec.number()
				object.renderable = False
		'''
		if self.type==1:
			for i in range(len(self.objects)):
				self.objects[i].index = i  #for use in tree
			self.tree_time = self.time
			self.tree = PositionTree(self.objects)
			#print(len(self.tree))'''

	def update_rect(self):
		'''if self.rect.width > self.rect.height:
			self.rect.width = self.rect.height
		elif self.rect.width < self.rect.height:
			self.rect.height = self.rect.width'''
		if hasattr(self, 'scale'):
			if self.rect.height < self.rect.width:
				self.scale = self.rect.height / self.current_dim
			else:
				self.scale = self.rect.width / self.current_dim
			self.update_scale_ruler()
		self.translate_positions()
		self.find_orbits()

	def reset_view(self):
		if self.tracking is None:
			self.center = self.focus_center.copy()
		else:
			self.center = self.tracking.get_pos(self.time).convert([self.position_unit]).number()
		self.current_dim = self.default_dim
		self.scale = self.rect.height / self.current_dim
		self.translate_positions()
		self.find_orbits()
		self.update_scale_ruler()

	def update_scale_ruler(self):
		self.pixels = int(self.rect.width / 8)
		scale_text = UNum(self.pixels / self.scale, **{self.position_unit: 1}).nice_str(2)
		self.scale_text_surface = self.font.render(scale_text, True, pg.Color('white'))
		width = self.scale_text_surface.get_rect().width
		self.scale_text_left = self.rect.left + 2 + int(self.pixels / 2) - int(width / 2)
		if self.scale_text_left < self.rect.left + 2:
			self.scale_text_left = self.rect.left + 2

	def zoom(self, factor, mousepos):
		self.scale *= factor
		#print(self.scale)
		if self.rect.height < self.rect.width:
			self.current_dim = self.rect.height / self.scale
		else:
			self.current_dim = self.rect.width / self.scale
		limited = False
		if self.current_dim > self.max_dim:
			self.current_dim = self.max_dim
			limited = True
		elif self.current_dim < self.min_dim:
			self.current_dim = self.min_dim
			limited = True
		if limited:
			if self.rect.height < self.rect.width:
				self.scale = self.rect.height / self.current_dim
			else:
				self.scale = self.rect.width / self.current_dim
		if self.rect.collidepoint(mousepos) and self.tracking is None and not limited:
			mouse_relative_x = (mousepos[0] - self.rect.centerx)/self.scale
			mouse_relative_y = (self.rect.centery - mousepos[1])/self.scale
			mouse_relative_vec = Vector2D(x=mouse_relative_x, y=mouse_relative_y)
			self.center += mouse_relative_vec - mouse_relative_vec/factor
		self.translate_positions()
		self.find_orbits()
		self.update_scale_ruler()

	def render(self, time_increment):
		#pg.draw.rect(self.surface, pg.Color('grey'), self.rect, 1)
		#if self.type==1:
		#	self.tree.render(self.surface, self.rect, self.scale, self.center)
		white = pg.Color('white')
		if self.type==3:
			orbit_rendered_objects = self.objects[1:]
		else:
			orbit_rendered_objects = self.objects
		for object in orbit_rendered_objects:
			if self.draw_orbits and not isinstance(object, StarSystem):
				if object.orbit.period.number==0.:
					continue
				#print(object.orbit_points_list)
				#print('rendering orbit')
				pg.draw.aalines(self.surface,
								pg.Color('grey'),
								True,
								object.orbit_points_list)
		for object in self.objects:
			if object.renderable:
				if object.orbiting:
					if self.type==3 and object==self.focus:
						pass
					elif object.orbit.period / 20 < time_increment and object.orbit.period.number!=0.:
						continue #too fast
				if self.trail and object.can_trail:
					pg.draw.aaline(self.surface,
								   pg.Color(object.color),
								   (object.oldx, object.oldy),
								   (object.x, object.y))
				if object.draw_radius > 0:
					pg.draw.circle(self.surface,
								   pg.Color(object.color),
								   (object.x, object.y),
								   object.draw_radius)
				else:
					pg.gfxdraw.pixel(self.surface,
									 object.x,
									 object.y,
									 pg.Color(object.color))
		if self.selected is not None:
			too_fast = False
			if self.selected.orbiting:
				if self.type==3 and self.selected==self.focus:
					pass
				elif self.selected.orbit.period / 20 < time_increment and self.selected.orbit.period.number!=0.:
					too_fast = True
			if not too_fast:
				pg.draw.circle(self.surface,
							   white,
							   (self.selected.x, self.selected.y),
							   self.selected.draw_radius + 3, 1)
				self.surface.blit(self.selected_text_surface,
								  (self.selected.x + 2,
								   self.selected.y + 2))
		self.surface.blit(self.focus_text_surface, (self.rect.left + 2, self.rect.top))
		y = self.focus_text_surface.get_rect().bottom + self.rect.top

		y_line = y + 2
		start = (self.rect.left + 2, y_line)
		end = (self.rect.left + self.pixels, y_line)
		pg.draw.line(self.surface, white, start, end)
		pg.draw.line(self.surface, white, (start[0], y_line-2), (start[0], y_line+2))
		pg.draw.line(self.surface, white, (end[0], y_line-2), (end[0], y_line+2))

		self.surface.blit(self.scale_text_surface, (self.scale_text_left, y_line + 2))

	def translate_positions(self, trail=False): #from unitless to screen pos
		for object in self.objects:
			if trail and object.renderable:
				object.oldx = object.x
				object.oldy = object.y
				object.can_trail = True
			else:
				object.can_trail = False
			object.x = int(self.rect.centerx + self.scale*(object.position-self.center).x)
			object.y = int(self.rect.centery - self.scale*(object.position-self.center).y)
			object.renderable = True
			if object.x < self.rect.left or object.x > self.rect.right or object.y < self.rect.top or object.y > self.rect.bottom:
				object.renderable = False

	def find_orbits(self, n=100):
		if not self.draw_orbits:
			return
		for object in self.objects:
			if object.orbiting:
				if object.orbit.period.number==0.:
					continue
				object.orbit_points_list = []
				for point in object.orbit.orbit_points(self.position_unit, n=n):
					vec = point
					x = int(self.rect.centerx + self.scale * (vec - self.center).x)
					y = int(self.rect.centery - self.scale * (vec - self.center).y)
					object.orbit_points_list.append((x, y))

	def update(self, time):
		if self.type==3:
			if self.focus.moving:
				self.focus.set_pos(time)
		moved = False
		if self.tracking is not None:
			self.center = self.tracking.get_pos(time).convert([self.position_unit]).number()
			self.find_orbits(n=100)
			moved = True
		for object in self.objects:
			if object.moving:
				object.position = object.get_pos(time).convert([self.position_unit]).number()
				moved = True
		if moved:
			self.translate_positions(trail=self.trail)
		self.time = time
		return moved

	def select(self, time, mousepos, doubleclick_time):
		#self.update(time)
		mouse_real_x = (mousepos[0] - self.rect.centerx) / self.scale + self.center.x
		mouse_real_y = (self.rect.centery - mousepos[1]) / self.scale + self.center.y
		mouse_vec = Vector2D(x=mouse_real_x, y=mouse_real_y)
		max_pixels = 13
		min_dist = max_pixels / self.scale
		selected = None
		if False: #self.type==1:
			if time!=self.tree_time:
				if self.update(time):
					self.tree = Map.PositionTree(self.objects)
			result = self.tree.nn(mouse_vec, 10**3)
			if result is not None:
				selected = self.objects[result]
		else:
			for object in self.objects:
				dist = (object.position - mouse_vec).value
				if dist < min_dist:
					selected = object
					min_dist = dist

		open_bool = False
		if selected is not None:
			if self.selected is not None:
				if selected.id==self.selected.id and self.time-self.selection_time < doubleclick_time:
					#print('double selected..')
					open_bool = True
			#print(selected.name)
			self.selected_text_surface = pg.Surface(self.font.size(selected.name))
			self.selected_name_surface = self.font.render(selected.name, True, pg.Color('white'))
			self.selected_text_surface.blit(self.selected_name_surface, (0, 0))
		'''if selected.orbiting:
			print((selected.get_pos(time) - selected.orbit.focus.get_pos(time)).reduced())
		else:
			print(selected.get_pos(time).reduced())'''
		self.selected = selected
		self.selection_time = self.time.copy()
		return (selected, open_bool)

def main():  # Test Run
	import tkinter as tk
	import sys
	import os

	class App:
		def __init__(self):
			self.clock = pg.time.Clock()
			self.fps = 60
			self.actual_fps = self.fps
			self.done = False
			self.surface = pg.display.get_surface()
			self.time = UNum(0, yrs=1)
			self.time_increment = UNum(10, days=1) / self.fps
			self.menu = None

			galaxy = Galaxy(numsystems=4000)
			'''system = StarSystem(UVector2D())
			system.planets = [Planet(system.center_of_mass,
									 UNum(1, AU=1),
									 mass=UNum(1, earths=1),
									 eccentricity=0.5)]'''
			self.map = Map(galaxy, self.surface, trail=False)
			self.paused = False

			#self.update_surfaces()
			#not necessary because resize event always occurs at star

		def update_surfaces(self):
			self.surface = pg.display.get_surface()
			self.surface_rect = self.surface.get_rect()
			self.map.rect = self.surface_rect.copy()
			#self.map.rect.height = self.map.rect.height - 100
			#self.map.rect.bottom = self.surface_rect.bottom
			self.map.update_rect()
			self.surface.fill(pg.Color("black"))

		def event_loop(self):
			for event in pg.event.get():
				if event.type==pg.QUIT:
					self.done = True
				#RESIZE
				elif event.type==pg.VIDEORESIZE:
					#print('resize')
					pg.display.set_mode((event.w, event.h), pg.RESIZABLE)
					self.update_surfaces()
				#MOUSE
				elif event.type==pg.MOUSEBUTTONDOWN:

					if event.button==4:  #scroll up
						if pg.key.get_mods() & pg.KMOD_CTRL: #speed up time
							if pg.KMOD_SHIFT:
								self.time_increment *= 1.1
							else:
								self.time_increment *= 1.35
						else: #zoom in
							if pg.key.get_mods() & pg.KMOD_SHIFT:
								self.map.zoom(1.05, event.pos)
							else:
								self.map.zoom(1.2, event.pos)
							self.surface.fill(pg.Color("black"))
					elif event.button==5:  #scroll down
						if pg.key.get_mods() & pg.KMOD_CTRL: #slow down time
							if pg.KMOD_SHIFT:
								self.time_increment /= 1.1
							else:
								self.time_increment /= 1.35
						else: #zoom out
							if pg.key.get_mods() & pg.KMOD_SHIFT:
								self.map.zoom(1/1.05, event.pos)
							else:
								self.map.zoom(1/1.2, event.pos)
							self.surface.fill(pg.Color("black"))
					elif event.button==2:  #middle click
						if pg.key.get_mods() & pg.KMOD_CTRL:
							self.time_increment = UNum(10, days=1) / self.fps
						else:
							self.map.reset_view()
						#print('reset view')
					elif event.button==1: #left click
						if self.menu is not None:
							if self.menu.select(event.pos):
								self.menu = None
								continue
						self.menu = None

						selection = self.map.select(self.time, event.pos, self.time_increment*self.actual_fps * 0.7)

						if selection[1]: #open
							mybool = False
							for myclass in [StarSystem, Star, Planet, station.Station]:
								if isinstance(selection[0], myclass):
									mybool = True
							if mybool:
								if self.map.type==3 and selection[0]==self.map.focus:
									continue
								self.map = Map(selection[0], self.surface, time=self.time, trail=self.map.trail, parent=self.map)
								self.update_surfaces()
							else:
								print(type(selection[0]))
					elif event.button==3: #right click
						selection = self.map.select(self.time, event.pos, UNum(0, yrs=1))
						if selection[0] is None:
							self.menu = None
							continue
						selected = selection[0]

						'''if selected.orbiting:
							position = (selected.get_pos(self.time)-selected.orbit.focus.get_pos(self.time)).reduced().roundstr()
						else:
							position = selected.get_pos(self.time).reduced().roundstr()'''
						info_options = [Option(selected.type_name)]
						if selected.orbiting:
							orbit_options = [Option('Focus: '+str(selected.orbit.focus.name)),
											 Option('SemiMajor: '+selected.orbit.semimajor_axis.nice_str(1)),
											 Option('Eccentricity: '+str(round(selected.orbit.eccentricity, 2))),
											 Option('Period: '+selected.orbit.period.nice_str(1))]
							info_options.append(Option('Orbit', None, orbit_options))
						options = [Option(selected.name, None, info_options)]
						font = self.font = pg.font.SysFont('Arial', 10)
						self.menu = Menu(self.surface, self.surface_rect, (event.pos[0]+1, event.pos[1]+1), font, *options)
				#EXIT
				if event.type==pg.KEYDOWN:
					if event.key==27: #escape i think
						self.done = True
					elif event.key==32: #space
						self.paused = not self.paused
					elif event.key==8: #backspace
						if self.map.parent is not None:
							if hasattr(self.map, 'focus'):
								self.map.focus.position = self.map.focus.get_pos(self.time).convert([self.map.parent.position_unit]).number()
							self.map = self.map.parent
							self.update_surfaces()
					elif event.key in [303, 304, 305, 306, 0]: #ctrl or shift
						pass
					else:
						print(event.key)

		def render(self):
			white = pg.Color('white')

			self.surface.fill(pg.Color("black"))

			if self.paused: time_increment = UNum(0, yrs=1)
			else: time_increment = self.time_increment
			self.map.render(time_increment)

			fps_surface = self.map.font.render(str(round(self.clock.get_fps()))+' FPS', True, white)
			fps_rect = fps_surface.get_rect()
			fps_dest = (self.map.rect.right - fps_rect.width, self.map.rect.top)
			self.surface.blit(fps_surface, fps_dest)

			speed = (self.time_increment * self.fps).reduced()
			if self.paused:
				speed.number = 0
			if speed.number >= 10:
				speed_surface = self.map.font.render(str(round(speed)) + '/s', True, white)
			else:
				speed_surface = self.map.font.render(str(round(speed, 1)) + '/s', True, white)
			speed_rect = speed_surface.get_rect()
			speed_dest = (self.map.rect.right - speed_rect.width,
						  self.map.rect.top + fps_rect.height + 2)
			self.surface.blit(speed_surface, speed_dest)

			time = self.time.convert(['yrs']).number
			time_surface = self.map.font.render(str(round(time))+' AD',
												True, white)
			time_dest = (self.map.rect.right - time_surface.get_rect().width,
						 speed_dest[1] + speed_rect.height + 2)
			self.surface.blit(time_surface, time_dest)

			if self.menu is not None:
				self.menu.render(pg.mouse.get_pos())

			pg.display.update()

		def main_loop(self):
			while not self.done:
				self.clock.tick(self.fps)
				self.actual_fps = 1000 / self.clock.get_time()
				self.event_loop()
				if not self.paused:
					if self.actual_fps!=0:
						self.time += self.time_increment * self.fps / self.actual_fps
					else:
						self.time += self.time_increment * self.fps / 1
				self.map.update(self.time)
				self.render()

	root = tk.Tk()
	root.withdraw()
	os.environ['SDL_VIDEO'] = '1'
	pg.init()
	pg.display.set_caption('Map Viewer Test')
	pg.display.set_mode((900, 900), pg.RESIZABLE)
	App().main_loop()
	pg.quit()
	sys.exit()

if __name__=="__main__":
	main()
