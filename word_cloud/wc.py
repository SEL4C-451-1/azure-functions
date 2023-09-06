import numpy as np
from PIL import Image
from os import path
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os

d = path.dirname(__file__) if "__file__" in locals() else os.getcwd()
mask = np.array(Image.open(path.join(d, "sel4c_logo_nbg.png")))
text = open(path.join(d, 'text.txt')).read()

wc = WordCloud(mask=mask, margin=10, random_state=1).generate(text)
plt.imshow(wc)
wc.to_file("result.png")
plt.axis("off")
plt.figure()
plt.show()
