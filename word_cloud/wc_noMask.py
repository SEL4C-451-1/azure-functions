import numpy as np
from PIL import Image
from os import path
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os

d = path.dirname(__file__) if "__file__" in locals() else os.getcwd()
text = open(path.join(d, 'text.txt')).read()

# There are multiple color palettes for generating the words to chose, you can find them at https://matplotlib.org/2.0.2/examples/color/colormaps_reference.html
    # I would recommed using the winter or cool colormaps due to the SEL4C identity; we can also create one, but right now I didn't do that
wc = WordCloud(background_color='white', colormap='winter', width=300, height=200).generate(text)
plt.imshow(wc)
wc.to_file("result.png")
plt.axis("off")
plt.figure()
plt.show()
