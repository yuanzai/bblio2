import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt


circle1=plt.Circle((0,0),.2,color='r')
circle2=plt.Circle((.5,.5),.2,color='b')
circle3=plt.Circle((1,1),.2,color='g',clip_on=False)
fig = plt.gcf()
fig.gca().add_artist(circle1)
fig.gca().add_artist(circle2)
fig.gca().add_artist(circle3)
fig.savefig('plotcircles.png')

