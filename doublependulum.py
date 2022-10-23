from turtle import update
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time

a = 0.0 # Start time
b = 50.0 # End time
N = 5000 # Number of statepoints generated
h = (b-a)/N # Gap between subsequent points
tracelength = 500 # Length of the trace
ropealpha = 0.2 # between 0 and 1
g = 9.81 # Gravitational acceleration

#tpoints = np.arange(a,b,h)

fig, ax = plt.subplots()
ax.set_xlim([-2,2])
ax.set_ylim([-2,2])

def f(r, m1, m2, L1, L2):
    theta1, theta1dot, theta2, theta2dot = r
    # equations of motion below
    ftheta1, ftheta2 = theta1dot, theta2dot
    ftheta1dot = (-g*(2*m1+m2)*np.sin(theta1) - m2*g*np.sin(theta1 - 2*theta2) - 2*np.sin(theta1 - theta2)*m2*(theta2dot**2*L2 + theta1dot**2*L1*np.cos(theta1 - theta2)))/(L1*(2*m1 + m2 - m2*np.cos(2*theta1 - 2*theta2)))
    ftheta2dot = (2*np.sin(theta1 - theta2)*(theta1dot**2*L1*(m1 + m2) + g*(m1 + m2)*np.cos(theta1) + theta2dot**2*L2*m2*np.cos(theta1 - theta2)))/(L2*(2*m1 + m2 -m2*np.cos(2*theta1 - 2*theta2)))
    return np.array([ftheta1, ftheta1dot, ftheta2, ftheta2dot])

class pendulum:
    def __init__(self, initheta1, initheta1dot, initheta2, initheta2dot, m1, m2, L1, L2, color):
        self.initheta1 = initheta1
        self.initheta1dot = initheta1dot
        self.initheta2 = initheta2
        self.initheta2dot = initheta2dot
        self.m1 = m1
        self.m2 = m2
        self.L1 = L1
        self.L2 = L2
        self.color = color
        self.hist = []

    def solvesystem(self):
        r = np.array([self.initheta1, self.initheta1dot, self.initheta2, self.initheta2dot])
        theta = [(r[0], r[2])]
        tpoints = np.arange(a,b,h)
        for tpoint in tpoints:
            # The numeric solution is solved with runge kutta (4)
            k1 = h*f(r, self.m1, self.m2, self.L1, self.L2)
            k2 = h*f(r+(1/2)*k1, self.m1, self.m2, self.L1, self.L2)
            k3 = h*f(r + (1/2)*k2, self.m1, self.m2, self.L1, self.L2)
            k4 = h*f(r + k3, self.m1, self.m2, self.L1, self.L2)
            r = r + (1/6)*(k1+2*k2+2*k3+k4)
            theta.append((r[0], r[2]))
        self.theta = theta

    def updatehist(self, x, y):
        # function for pendulum trace update
        self.hist.append((x,y))
        if len(self.hist) > tracelength:
            self.hist = self.hist[1:]

    def plotobject(self):
        mslighter = 10
        msheavier = np.sqrt(self.m1/self.m2)*mslighter if self.m1>self.m2 else np.sqrt(self.m2/self.m1)*mslighter
        if self.m1 < self.m2:
            self.block1, = ax.plot([],[],'ro', markersize = mslighter, mfc = self.color)
            self.block2, = ax.plot([],[],'ro', markersize = msheavier, mfc = self.color)
        else:
            self.block1, = ax.plot([],[],'ro', markersize = msheavier, mfc = self.color)
            self.block2, = ax.plot([],[],'ro', markersize = mslighter, mfc = self.color)   
        self.state, = ax.plot([],[], '-', linewidth = 1)
        self.fade, = ax.plot([],[], alpha = ropealpha, color = self.color)
  

# Put 2 pendulums into swinging
pendulum1 = (pendulum(np.pi/2, 0, np.pi/4, 0, 1, 1, 0.8, 0.8, 'green')) # initial theta1, initial theta1 angular velocity, initial theta2, initial theta 2 angular velocity, mass of upper block, mass of the lower block, length of upper rod, length of lower rod, pendulum color
pendulum2 = (pendulum(np.pi/2, 0, np.pi/4, 0, 1, 1, 0.8, 0.8, 'red'))
pendulums = [pendulum1, pendulum2]

for pen in pendulums:
    pen.solvesystem()
    pen.plotobject()

def initialize():
    output = []
    for pen in pendulums:
        output.append(pen.state)
        output.append(pen.block1)
        output.append(pen.block2)
    return output 


def animate(frame):
    returnlist = []
    for pen in pendulums:
        theta1, theta2 = pen.theta[frame]
        x1, y1 = pen.L1*np.sin(theta1), -pen.L1*np.cos(theta1)
        x2, y2 = x1 + pen.L2*np.sin(theta2), y1 - pen.L2*np.cos(theta2)
        pen.updatehist(x2, y2)
        pen.state.set_data([0,x1, x2],[0,y1, y2])
        pen.block1.set_data([x1],[y1])
        pen.block2.set_data([x2],[y2])
        xdatafade= [data[0] for data in pen.hist]  
        ydatafade = [data[1] for data in pen.hist] 
        pen.fade.set_data(xdatafade, ydatafade)
        returnlist.append(pen.state)
        returnlist.append(pen.block1)
        returnlist.append(pen.block2)
        returnlist.append(pen.fade)
    return returnlist

anim = animation.FuncAnimation(fig, animate, init_func = initialize, frames = 5000, interval = 0.1, blit = True)
plt.show()