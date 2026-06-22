import numpy as np
import pyvista as pv

plotter = pv.Plotter()
for i in range(5):
    for j in range(5):
        h = np.random.randint(5,20)
        box = pv.Box(bounds=(i,i+1,j,j+1,0,h))
        plotter.add_mesh(box, color="lightgray")

plotter.show(title="3D city Massing Model")
print("hello")
