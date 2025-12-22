from PIL import Image
import matplotlib.pyplot as plt

img=Image.open("image.jpg").resize((20,20))
colors=img.getcolors(400)

labels=range(len(colors[:5]))
sizes=[c[0] for c in colors[:5]]

plt.pie(sizes, labels=labels)
plt.show()