from vedo import *
import numpy as np
t = np.linspace(0, 8*np.pi, 400)
s1 = np.c_[np.cos(t), np.sin(t), t/4]
s2 = np.c_[np.cos(t+np.pi), np.sin(t+np.pi), t/4]

dns1 = Tube(s1, r=0.08, c="red5")
dna2 = Tube(s2, r=0.08, c="cyan5")

bars = []
for i in range(0, len(t), 12):
    bars.append(Line(s1[i], s2[i], c="white", lw=2))
show(
    dns1,dna2,*bars, bg="black",axes=1,viewup="z",
    interactive=True
)
