from pygame.draw import *
import sys
import os
import time as t
import platform

import matplotlib.pyplot as plt
import numpy as np
from math import sin, cos, atan2, pi

from sitnikov_phys_model import BackgroundStars
from sitnikov_gui import *
from sitnikov_files import load_configuration

class State:
    """
    Basically a namespace to share the values held within with other files, 
    and an assortment of methods to modify these 'state parameters'
    """
    pause = False
    statistics = False
    zoom = 0

    fps = 300

    @property
    def sys_state(self):
        return self.z, self.v, self.t

    def switch_pause(self):
        self.pause = not self.pause

    def switch_stats(self):
        self.statistics = not self.statistics

    def zoom_in(self):
        self.zoom = 1

    def zoom_out(self):
        self.zoom = -1

class Sitnikov:
    def __init__(self, STATE, surface):
        self.font = pygame.font.Font(None, 30)
        self.width = surface.get_width()
        self.height = surface.get_height()
        self.surface = surface

        CFG = load_configuration('sitnikov_config.json')

        self.scale = CFG['scale']
        self.last_time = t.time()

        self.dist = max(self.width, self.height) * 0.4  # Расстояние от точки наблюдателя до экрана

        self.color = tuple(map(lambda s: [int(x) for x in s.split()], [CFG['color1'], CFG['color2'], CFG['color3']]))

        self.direction = {pygame.K_LEFT: [1, 0], pygame.K_RIGHT: [-1, 0], pygame.K_UP: [0, 1], pygame.K_DOWN: [0, -1]}

        self.distant_stars = BackgroundStars(surface, CFG['num_stars'])

        self.stars = np.zeros((3, 3))
        self.trail = []
        self.trail_len = CFG['trail_len']
        self.points_between = CFG['points_between']
        self.ts = []
        self.zs = []
        self.vs = []

        INIT = load_configuration('init_values.json')
        self.z_0 = INIT['z0']
        self.v_0 = INIT['v0']
        self.t_0 = INIT['t0'] * pi
        self.e = INIT['e']

        self.z = self.z_0
        self.v = self.v_0
        self.time = self.t_0
        self.scale_time = CFG['scale_time']

        self.dt = 0
        self.angle = [0, 0]
        self.m_turn = np.eye(3)
        self.touched = False
        self.arrows = False
        self.STATE = STATE

        self.stars, self.trail, self.z, self.v = self.move(self.stars, self.trail, self.time, self.dt, self.z, self.v, self.e)

    def bin_search(self, f, a, b):
        "Basic binary search for the function f's root between a and b"
        m = (a + b) / 2
        if b - a < 10 ** (-7):
            return m
        elif f(m) > 0:
            return self.bin_search(f, a, m)
        elif f(m) < 0:
            return self.bin_search(f, m, b)
        elif f(m) == 0:
            return m

    def move(self, stars, trail, t, dt, z, v, e):
        "Moves the main astronomical objects by one discretisation step"
        f = lambda x: x - e * sin(x) - t
        E = self.bin_search(f, t - e, t + e)

        nu = 2 * atan2(((1 + e) / (1 - e)) ** 0.5 * sin(E / 2), cos(E / 2))

        rho = (1 - e ** 2) / (1 + e * cos(nu))

        stars = np.array([
            [-rho * cos(nu), rho * sin(nu), 0],
            [rho * cos(nu), -rho * sin(nu), 0],
            [0, 0, z]
        ]).T

        trail.append([
            [-rho * cos(nu), rho * sin(nu), 0],
            [rho * cos(nu), -rho * sin(nu), 0],
            [0, 0, z]
        ])
        v += -z / (rho ** 2 + z ** 2) ** 1.5 * dt
        z += v * dt
        self.ts.append(t - self.t_0)
        self.zs.append(z)
        self.vs.append(v)
        if len(trail) > self.trail_len:
            trail.pop(0)
        return stars, trail, z, v

    def turn(self, m_turn, angle):
        '''Modifies the rotation matrix adding rotation by the given angle'''
        a, b = angle
        m_x = np.array([
            [1, 0, 0],
            [0, cos(a), -sin(a)],
            [0, sin(a), cos(a)]
        ])

        m_z = np.array([
            [cos(b), -sin(b), 0],
            [sin(b), cos(b), 0],
            [0, 0, 1]
        ])
        return m_z @ m_x @ m_turn

    def show_plots(self, STATE):
        '''Plot relevant graphs and show them in a separate Tk window'''
        STATE.pause = True

        import matplotlib
        matplotlib.use('TkAgg')

        plt.subplot(2, 1, 1)
        plt.plot(self.zs, self.vs, linewidth=1, label=str('$z_0={:.2f}$\n$v_0={:.2f}$'.format(self.z_0, self.v_0)))
        plt.xlabel('$z$')
        plt.ylabel('$v_z$')
        plt.legend(loc='best')

        plt.subplot(2, 1, 2)
        plt.plot(self.ts, self.zs, linewidth=1)
        plt.xlabel('$t$')
        plt.ylabel('$z$')

        plt.show()

    def display_stats(self):
        '''
        Render the current values of the system parameters to the screen
        '''
        text_z = self.font.render('z: ' + str('{:.3f}'.format(self.z)), True, [255, 255, 255])
        text_v = self.font.render('v: ' + str('{:.3f}'.format(self.v)), True, [255, 255, 255])
        text_t = self.font.render('t: ' + str('{:.1f}'.format(self.time - self.t_0)), True, [255, 255, 255])
        self.surface.blit(text_z, (self.width - 100, 10))
        self.surface.blit(text_v, (self.width - 100, 30))
        self.surface.blit(text_t, (self.width - 100, 50))

    def open_documentation(self):
        # Must be platform-specific!!!
        if platform.system() == 'Windows':
            os.startfile("resources\\docs.pdf")  # Maybe actually cross-platform tho
        elif platform.system() == 'MacOS':
            os.system("open -a [app name] [file name]")

    def frame_rendering(self):
        self.surface.fill('black')

        # Отрисовка треков
        for point in self.trail:
            cor = self.m_turn.dot(np.array(point).transpose()).transpose()
            for i in range(3):
                pygame.draw.line(self.surface, (30, 255, 0),
                                 [self.scale * cor[i][0] + self.width / 2, -self.scale * cor[i][2] + self.height / 2],
                                 [self.scale * cor[i][0] + self.width / 2, -self.scale * cor[i][2] + self.height / 2], 1)

        self.dt = self.scale_time * (t.time() - self.last_time)
        if self.touched:
            vector = pygame.mouse.get_rel()
            self.angle = [vector[1] / 500, vector[0] / 500]
        elif self.arrows:
            keys = pygame.key.get_pressed()
            vector = [0, 0]
            for i in range(4):
                if keys[list(self.direction.keys())[i]]:
                    vector = list(map(lambda x, y: x + y, vector, self.direction[list(self.direction.keys())[i]]))
            self.angle = [vector[1] / 150, vector[0] / 150]
        else:
            if not self.STATE.pause:
                self.stars, self.trail, self.z, self.v = self.move(self.stars, self.trail, self.time, self.dt, self.z, self.v, self.e)
                self.time += self.dt
            for i in range(2):
                if abs(self.angle[i]) < 0.0001:
                    self.angle[i] = 0
                elif self.angle[i] > 0:
                    self.angle[i] -= 0.0002
                else:
                    self.angle[i] += 0.0002

        self.last_time = t.time()
        self.m_turn = self.turn(self.m_turn, self.angle)
        self.distant_stars.update_coordinates(self.m_turn)

        display = (self.m_turn @ self.stars).T

        self.distant_stars.display(self.dist)

        for n in range(2):  # выбираем первый объект
            for i in range(n + 1, 3):  # выбираем второй объект
                for k in range(1, self.points_between):
                    x = self.scale * (k * display[n][0] + (self.points_between - k) * display[i][0]) / self.points_between
                    y = self.scale * (k * display[n][2] + (self.points_between - k) * display[i][2]) / self.points_between
                    circle(self.surface, (30, 255 / 3 * (n + 1), 255 / 3 * i), (x + self.width / 2, -y + self.height / 2), 1)

        for i in range(3):
            x = self.scale * display[i][0]
            y = self.scale * display[i][2]
            pygame.draw.circle(self.surface, self.color[i], (x + self.width / 2, -y + self.height / 2), 3)

        text_fps = self.font.render('fps: ' + str(int(self.scale_time / self.dt)), True, [255, 255, 255])
        self.surface.blit(text_fps, (10, 10))

    def event_tracking(self, ev, UI):
        if ev.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # MOUSE BUTTON EVENTS
        elif ev.type == pygame.MOUSEBUTTONDOWN:
            UI.click()
            for i in range(3):
                if ev.pos[0] == self.stars[0][i] and ev.pos[1] == self.stars[1][i]:
                    pass
            if not self.touched:
                self.touched = True
                pygame.mouse.get_rel()
        elif ev.type == pygame.MOUSEBUTTONUP:
            self.touched = False
        elif ev.type == pygame.MOUSEWHEEL:
            self.scale += 10 * ev.y

        # KEY EVENTS - to be moved to UI hotkeys

        elif ev.type == pygame.KEYDOWN:
            UI.listen(ev.key)
            if self.direction.get(ev.key) is not None:
                self.arrows = True
        elif ev.type == pygame.KEYUP:
            self.arrows = False
            keys = pygame.key.get_pressed()
            for i in range(4):
                if keys[list(self.direction.keys())[i]]:
                    self.arrows = True
            if not keys[pygame.K_EQUALS] and self.STATE.zoom == 1 or not keys[pygame.K_MINUS] and self.STATE.zoom == -1:
                self.STATE.zoom = 0

        self.scale += self.STATE.zoom

        return UI