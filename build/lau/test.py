import vector
import math
import random
from matfunc import Mat,Vec,eye
from tolerance import *
from diagnostic import *



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

p1 = vector.vector()
p1.append(5)
p1.append(5)

p2 = vector.vector()
p2.append(10)
p2.append(10)

r1 = 7
r2 = 10

print cc_int(p1, r1, p2, r2)



