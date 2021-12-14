import pygame
from pygame.math import Vector2 as vec

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

IMAGE_DIR = "resources//images//"

HOTKEYS = [] # should be eliminated at some point, but button functionality depends on this apparently

class Menu(pygame.Surface):
	loc = vec(0, 0)

class UI:
	"""
	A collection of all the buttons, hotkeys (means of user input)
	used in the program. Basically the only class here that needs to be called from outside - 
	provides buttons overlay, hotkeys and the interface to work with them
	"""
	def __init__(self, surface, hotkeys, controls):
		"""Takes a parent surface (on which the overlay will be blitted), and the starting set of controls and hotkeys"""
		self.hotkeys = hotkeys
		self.controls = controls

		self.additional_elements = []

		self.menu = Menu((surface.get_width(), surface.get_height()))
		self.menu.set_colorkey((0, 0, 0))
		self.parent = surface
		self.labelled = {}

	def __getitem__(self, label):
		return self.labelled[label]

	def update(self):
		for btn in self.controls:
			btn.update()
		for el, loc in self.additional_elements:
			el.blit(self.menu, loc)
		self.parent.blit(self.menu, (0, 0))

	def click(self):
		click_loc = pygame.mouse.get_pos()
		for btn in self.controls:
			btn(click_loc)

	def listen(self, key_pressed):
		for hotk in self.hotkeys:
			hotk(key_pressed)

	def add_hotkey(self, *args):
		self.hotkeys.append(Hotkey(*args))

	def add_button(self, label, **kwargs):
		self.controls.append(Button(self.menu, **kwargs))
		self.labelled[label] = self.controls[-1]

	def add_element(self, elem, loc):
		self.additional_elements.append((elem, loc))

	def get_button(self, label):
		return self.labelled[label]


def init_ui(surface, STATE):
	hotkeys = []
	hotkeys.append(Hotkey(pygame.K_p, STATE.switch_pause))
	#hotkeys.append(Hotkey(pygame.K_g, lambda x: STATE.pause = True, 42))
	hotkeys.append(Hotkey(pygame.K_MINUS, STATE.zoom_out))
	hotkeys.append(Hotkey(pygame.K_EQUALS, STATE.zoom_in))

	buttons = []

	return UI(surface, hotkeys, buttons)

class Hotkey:
	def __init__(self, key, func=None, params=[]):
		self.key = key
		self.func = func
		self.params = params

	def connect(self, func=None, params=[]):
		self.func = func
		self.params = params

	def __call__(self, key_pressed):
		if key_pressed == self.key:
			self.func(*self.params)

class Button:
	"""Кнопка на экране pygame, по нажатию вызывается функция с предопределёнными параметрами
		-parent: Объект с полем loc, на который можно blit'ить 
		-loc: Положение относительно елвого верхнего угла родительского объекта
		-size: Размер кнопки в единицах pygame

		-image_path: путь до изображения, которое будет рендерится в размер кнопки
		-text: Текст, который будет рендерится на кнопке поверх изображения
		-func: Slot-функция, которая вызывается в случае нажатия
		-params: Параметры функции func

	"""
	#font = pygame.font.Font(None, 16)
	def __init__(self, parent, text = "", loc=vec(0, 0), size=vec(50, 50), image_path="", func=None, params=[]):
		""""""
		self.size = size
		self.loc = loc
		self.parent = parent
		self.shift = self.parent.loc

		self.func = func
		self.params = params
		
		self.img_file = image_path

		self.surf = pygame.Surface(size)
		self.embed()

		self.pending_reembed = False

	def __call__(self, click_loc=None):
		"""По вызову кнопки происходит проверка попадания, если оно было - вызывается функция"""

		if click_loc is None or self.surf.get_rect(topleft=(self.shift + self.loc)).collidepoint(click_loc):
			self.func(*self.params)
			self.change_on_click()

	def change_on_click(self):
		'''Change the parameters of the button itself when clicked'''
		pass

	def connect(self, func=None, params=[]):
		self.func = func
		self.params = params

	def update(self):
		if self.pending_reembed:
			self.embed()
		self.parent.blit(self.surf, self.loc)
		#print("updated ", self.img_file)

	def embed(self):
		'''Initialise the surface of the button'''
		self.surf = pygame.image.load(IMAGE_DIR + self.img_file)
		if self.size is not None:
			self.surf = pygame.transform.scale(self.surf, tuple(map(int, self.size)))
		self.pending_reembed = False

	def bind(self, key):
		self.hotkey = Hotkey(key, func=self, params=[None])
		

class SwitchButton(Button):
	def __init__(self, var_image_path):
		super().__init__()
		self.var_img_file = var_image_path
		self.is_down = False

	def change_on_click(self):
		self.img_file, self.var_img_file = self.var_img_file, self.img_file
		self.is_down = not self.is_down



