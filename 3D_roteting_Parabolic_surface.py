import numpy as np
import matplotlib.pyplot as plt 
from mpl_toolkits.mplot3d import Axes3D
x=np.linspace(-3,3,50)
y=np.linspace(-3,3,50)
x,y=np.meshgrid(x,y)
z=x**2+y**2
fig=plt.figure()
ax=fig.add_subplot(111,projection='3d')
for angle in range(0, 360, 3):
    ax.clear()
    ax.plot_surface(x, y, z, cmap='viridis')
    ax.view_init(30, angle)
    ax.set_title("3D Parabolic Surface")
    plt.pause(0.05)
plt.show()