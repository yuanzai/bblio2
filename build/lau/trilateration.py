import math
import numpy
import datetime
import intersect
import vector 
import random 
from matfunc import Mat,Vec,eye 
from tolerance import * 
from diagnostic import * 
import sys 
from math import sqrt 


def trilaterate(x1, y1, d1, x2, y2, d2, x3, y3, d3):
    P1 = numpy.array([x1, y1])
    P2 = numpy.array([x2, y2])
    P3 = numpy.array([x3, y3])
#from wikipedia
#transform to get circle 1 at origin
#transform to get circle 2 on x axis
    ex = (P2 - P1)/(numpy.linalg.norm(P2 - P1))
    i = numpy.dot(ex, P3 - P1)
    ey = (P3 - P1 - i*ex)/(numpy.linalg.norm(P3 - P1 - i*ex))
    ez = numpy.cross(ex,ey)
    d = numpy.linalg.norm(P2 - P1)
    j = numpy.dot(ey, P3 - P1)

#from wikipedia
#plug and chug using above values
    #x = (pow(d1,2) - pow(d2,2) + pow(d,2))/(2*d)
    #y = ((pow(d1,2) - pow(d3,2) + pow(i,2) + pow(j,2))/(2*j)) - ((i/j)*x)
    x, y = improvisedTrilateration(x1, y1, d1, x2, y2, d2, x3, y3, d3) 
    print x
    folder = "/home/ec2-user/bblio/build/static/"
    filename = datetime.datetime.now().strftime("%y%m%d%H%M%S%z") + ".png"
    plot(x1, y1, d1, x2, y2, d2, x3, y3, d3, x, y, folder + filename)

    return filename


def plot(x1, y1, d1, x2, y2, d2, x3, y3, d3, x, y, path):
    # method to create png file
    # uses the matlibplot library to plot a graph and the 3 circles to represent the imp signal strengths
    import matplotlib as mpl
    mpl.use('Agg')

    import matplotlib.pyplot as plt
    
    #plotting overall chart
    plt.axis([0, 58, 0, 76])
    
    #defining the 3 circles
    circle1=plt.Circle((x1,y1),d1,color='r', alpha=0.5)
    circle2=plt.Circle((x2,y2),d2,color='b', alpha=0.5)
    circle3=plt.Circle((x3,y3),d3,color='g', alpha=0.5)
    
    #defining the 3 imp positions
    circle1c=plt.Circle((x1,y1),.5,color='k', alpha=0.5)
    circle2c=plt.Circle((x2,y2),.5,color='k', alpha=0.5)
    circle3c=plt.Circle((x3,y3),.5,color='k', alpha=0.5)
    
    print "xy"
    print x, y
    #defining the estimated location of the source
    point = plt.Circle((x, y), 6, color = 'k', alpha=0.7)
    
    
    # plotting on the canvas itself
    fig = plt.gcf()
    fig.set_size_inches(5.8,7.6,forward=True)
    fig.gca().add_artist(circle1)
    fig.gca().add_artist(circle2)
    fig.gca().add_artist(circle3)

    fig.gca().add_artist(circle1c)
    fig.gca().add_artist(circle2c)
    fig.gca().add_artist(circle3c)
    fig.gca().add_artist(point)
    
    fig.savefig(path)
    plt.cla()
    print x,y


def cc_int(p1, r1, p2, r2):
    """
    Intersect circle (p1,r1) circle (p2,r2)
    where p1 and p2 are 2-vectors and r1 and r2 are scalars
    Returns a list of zero, one or two solution points.
    """
    d = vector.norm(p2-p1)
    if not tol_gt(d, 0):
        return []
    u = ((r1*r1 - r2*r2)/d + d)/2
    if tol_lt(r1*r1, u*u):
        return []
    elif r1*r1 < u*u:
        v = 0.0
    else:
        v = math.sqrt(r1*r1 - u*u)
    s = (p2-p1) * u / d
    if tol_eq(vector.norm(s),0):
        p3a = p1+vector.vector([p2[1]-p1[1],p1[0]-p2[0]])*r1/d
        if tol_eq(r1/d,0):
            return [p3a]
        else:
            p3b = p1+vector.vector([p1[1]-p2[1],p2[0]-p1[0]])*r1/d
            return [p3a,p3b]
    else:
        p3a = p1 + s + vector.vector([s[1], -s[0]]) * v / vector.norm(s)
        if tol_eq(v / vector.norm(s),0):
            return [p3a]
        else:
            p3b = p1 + s + vector.vector([-s[1], s[0]]) * v / vector.norm(s)
            return [p3a,p3b]


def improvisedTrilateration(x1, y1, d1, x2,y2,d2, x3,y3,d3):
    p1 = vector.vector()
    p1.append(x1)
    p1.append(y1)

    p2 = vector.vector()
    p2.append(x2)
    p2.append(y2)

    p3 = vector.vector()
    p3.append(x3)
    p3.append(y3)
    a = cc_int(p1, d1, p2, d2)
    b = cc_int(p2, d2, p3, d3)
    c = cc_int(p3, d3, p1, d1)
    return centerFinder(a,b,c)


def centerFinder(a,b,c):
    min_a = 2
    min_b = 2
    min_c = 2
    min_lengths = sys.maxint
    for x in range(0,2):
        for y in range(0,2):
            for z in range(0,2):
                current = 0
                current += pythagoras(a[x][0], b[y][0], a[x][1], b[y][1])
                current += pythagoras(a[x][0], c[z][0], a[x][1], c[z][1])
                current += pythagoras(c[z][0], b[y][0], c[z][1], b[y][1])
                if current < min_lengths:
                    min_lengths = current
                    min_a = x
                    min_b = y
                    min_c = z
    result_x = (a[min_a][0] + b[min_b][0] + c[min_c][0]) / 3
    result_y = (a[min_a][1] + b[min_b][1] + c[min_c][1]) / 3
    return result_x, result_y

def pythagoras(x1,x2,y1,y2):
    x = abs(x1-x2)
    y = abs(y1-y2)
    return sqrt(x ** 2 + y ** 2)
