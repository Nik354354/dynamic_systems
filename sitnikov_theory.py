import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import ode
from math import sin, cos, atan2


class Theory:
    def __init__(self, z_0, v_0, t_0, e): #setting initial values
        self.z_0 = z_0
        self.v_0 = v_0
        self.t_0 = t_0
        self.e = e
        self.ts = []
        self.ys = []
        self.Y_0 = []
        self.t_max = 100
        for i in range(-1, 2, 1):
            self.Y_0.append([z_0, v_0 + i / 100])

    def bin_search(self, f, a, b):
        '''Basic binary search for the function f's root between a and b'''
        m = (a + b) / 2
        if b - a < 10 ** (-7):
            return m
        elif f(m) > 0:
            return self.bin_search(f, a, m)
        elif f(m) < 0:
            return self.bin_search(f, m, b)
        elif f(m) == 0:
            return m

    def rho(self, t, e):
        '''searching E using previous algorithm'''
        f = lambda x, t, e: x - e * sin(x) - t
        E = self.bin_search(lambda x: f(x, t, e), t - e, t + e)
        nu = 2 * atan2(((1 + e) / (1 - e)) ** 0.5 * sin(E / 2), cos(E / 2))
        return (1 - e ** 2) / (1 + e * cos(nu))

    def f_out(self, t, y):  #step handler
        self.ts.append(t)
        self.ys.append(list(y.copy()))
        y1, y2 = y
        if y1 ** 2 + y2 ** 2 < 0.005:
            return -1

    def plot_theory(self):
        f = lambda t, y, e: [y[1], -y[0] / (self.rho(t, e) ** 2 + y[0] ** 2) ** 1.5]
        ODE = ode(f)
        ODE.set_integrator('dopri5', max_step=0.01, nsteps=10000) 
        ODE.set_solout(self.f_out) #adds values for plotting
        fig, ax = plt.subplots()
        fig.set_facecolor('white')
        for y_0 in self.Y_0:  #iteration over initial parameter values
            self.ts, self.ys = [], [] #zeroing arrays
            ODE.set_initial_value(y_0, self.t_0)  #setting initial values
            ODE.set_f_params(self.e)  #passing an extra argument e to a function f(t,y,e)
            ODE.integrate(self.t_max)  #solutioning of ODE
            Y = np.array(self.ys)
            T = np.array(self.ts)

            plt.subplot(2, 1, 1) #plotting
            plt.plot(Y[:, 0], Y[:, 1], linewidth=1, label='z_0=%.2f' % y_0[0])
            plt.xlabel('z')
            plt.ylabel('v_z')
            plt.xlim(-8, 10)
            plt.ylim(-1.5, 1.5)
            plt.legend(loc='best')

            plt.subplot(2, 1, 2)
            plt.plot(T, Y[:, 0], linewidth=1, label='v_0=%.2f' % y_0[1])
            plt.xlabel('t')
            plt.ylabel('z')
            plt.ylim(-20, 20)
            plt.legend(loc='best')

        plt.show()


















