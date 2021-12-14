import numpy as np
from random import random
from numpy import sin, cos, tan

import pygame

WHITE = (255, 255, 255)

R = np.array([])
V = np.array([])

class BackgroundStars:
	def __init__(self, surf, num_stars):
		self.surf = surf

		self.n = num_stars
		self.angles = np.zeros((2, num_stars))
		self.coordinates = np.zeros((3, num_stars))

		_1, _2, self.W, self.H = self.surf.get_rect()

		self.reset()

	def reset(self):
		for i in range(self.n):
			for j in range(2):
				self.angles[j][i] = (j + 1) * (random() - 0.5) * np.pi

	def update_coordinates(self, rotation_matrix):
		self.coordinates = rotation_matrix @ np.array([
				np.cos(self.angles[0]) * np.sin(self.angles[1]), 
				np.cos(self.angles[0]) * np.cos(self.angles[1]),
				np.sin(self.angles[0])
				])

	def display(self, distance_from_screen):
		theta = np.arctan2(self.coordinates[2], np.sqrt(self.coordinates[0] ** 2 + self.coordinates[1] ** 2))
		phi = np.arctan2(self.coordinates[0], self.coordinates[1])

		width, height = self.W, self.H

		for i in range(self.n):
			if sin(phi[i]) < width / (2 * distance_from_screen) * cos(phi[i]) and \
				sin(theta[i]) < height / (2 * distance_from_screen) * cos(theta[i]) * cos(phi[i]):

				x = distance_from_screen * tan(phi[i])
				y = distance_from_screen * tan(theta[i]) / cos(phi[i])
				pygame.draw.circle(self.surf, WHITE, (x + width / 2, -y + height / 2), 1)