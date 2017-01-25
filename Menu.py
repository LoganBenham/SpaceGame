import random as rand
import pygame as pg

class Option:
	def nothing(self):
		pass

	def __init__(self, text, func=None, sub_options=None, *args, **kwargs):
		self.text = str(text)
		self.highlight = False
		if func is not None or sub_options is not None:
			self.highlight = True
		if func is None:
			func = self.nothing
		self.func = func
		self.sub_options = sub_options
		self.args = args
		self.kwargs = kwargs

	def execute(self, *args, **kwargs):
		args_list = self.args + args
		kwargs_dict = self.kwargs
		for item in kwargs.items():
			kwargs_dict[item[0]] = item[1]
		return self.func(*args_list, **kwargs_dict)

class Menu:
	def __init__(self, surface, parent_rect, position, font, *options):
		self.surface = surface
		self.parent_rect = parent_rect
		self.position = position
		for option in options:
			if type(option)!=Option:
				raise TypeError('Additional arguments must be Menu Options')
		self.options = options
		self.font = font
		self.bg_color = pg.Color('black')
		self.border_color = pg.Color('white')
		self.text_color = pg.Color('white')
		self.highlight_bg = pg.Color('dark grey')
		self.child_menu = None

		width = 0
		height = 0
		for option in self.options:
			size = self.font.size(option.text)
			if size[0] > width:
				width = size[0]
			height += size[1] + 4
		width += 4
		self.rect = pg.Rect(position, (width, height))
		self.rect.clamp_ip(parent_rect)

		self.option_rects = []
		top = self.rect.top
		for i in range(len(self.options)):
			size = self.font.size(self.options[i].text)
			self.option_rects.append(pg.Rect((self.rect.left, top), (self.rect.width, size[1] + 4)))
			top += size[1] + 4

	def select(self, mouse_pos):
		if self.child_menu is not None and self.child_menu.select(mouse_pos):
			return True
		for i in range(len(self.option_rects)):
			if self.option_rects[i].collidepoint(mouse_pos):
				self.options[i].execute()
				return True
		return False

	def render(self, mouse_pos):
		pg.draw.rect(self.surface, self.bg_color, self.rect)
		for i in range(len(self.options)):
			rect = self.option_rects[i]
			option = self.options[i]
			collide = rect.collidepoint(mouse_pos)
			if option.highlight and collide:
				pg.draw.rect(self.surface, self.highlight_bg, rect)
			pg.draw.rect(self.surface, self.border_color, rect, 1)
			option_text = self.options[i].text
			text_surface = self.font.render(option_text, False, self.text_color)
			self.surface.blit(text_surface, (rect.left+2, rect.top+2))
			if option.sub_options is not None and collide:
				self.child_menu = Menu(self.surface,
									   self.parent_rect,
									   (rect.right, rect.top),
									   self.font,
									   *option.sub_options)
		if self.child_menu is not None:
			self.child_menu.render(mouse_pos)

def main():  #Test Run
	def ButtBlast(number, prefix='\b'):
		print('Hey there '+prefix+' Butt Blaster '+str(number))
	def Random(max):
		print(rand.random()*max)
	options = [Option('Hello', ButtBlast, None, 420, prefix='Fag'),
			   Option('Random', Random, None, 10)]

	for option in options:
		print(option.text)
	choice = input('?')
	for option in options:
		if choice == option.text:
			option.execute()

if __name__=="__main__":
	main()