import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.image as mpimg
from matplotlib.widgets import Button
from v2 import *
import itertools

fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.2)
plt.axis('off')

class PlateauAnimé(Plateau):
    def __init__(self, ax, nbr=4):
        img = mpimg.imread('monopoly-classique-plateau.jpg')
        ax.imshow(img)
        PLATEAU_HAUTEUR, PLATEAU_LARGEUR, _ = img.shape
        PLATEAU_DIM = int(min(PLATEAU_HAUTEUR, PLATEAU_LARGEUR))
        super().__init__([JoueurAnimé(j, ax, PLATEAU_DIM) for j in range(nbr)])

class JoueurAnimé(Joueur):
    def __init__(self, numéro, ax, PLATEAU_DIM, RAYON=10):
        colours = ["red", "green", "blue", "yellow", "black", "white"]
        super().__init__("n°{}".format(numéro))

        coin = 0.1273125  # pourcentage de la longeur du plateau
        marge = 0.3  # pourcentage du coin

        case = (1. - 2. * coin) / 9.  # taille d'une case normale car 9 case + 2 coin = 100%
        coin_grand = (1. - marge) * coin + marge * case
        coin_petit = 1. - (8. + marge) * case - (1. + marge) * coin

        self.CASE = int(case * PLATEAU_DIM)
        self.COIN_GRAND = int(coin_grand * PLATEAU_DIM)
        self.COIN_PETIT = int(coin_petit * PLATEAU_DIM)

        DEPART = int((1. - marge * coin - numéro / 100.) * PLATEAU_DIM)
        self.image, = ax.plot([DEPART], [DEPART], marker="o", markersize=10, color=colours[numéro])

    def deplacement_pixel(self, position: int):
        if position == 0: return -self.COIN_GRAND, 0
        if position <= 8: return -self.CASE, 0
        if position == 9: return -self.COIN_PETIT, 0

        if position == 10:return 0, -self.COIN_GRAND
        if position <= 18:return 0, -self.CASE
        if position == 19:return 0, -self.COIN_PETIT

        if position == 20: return self.COIN_GRAND, 0
        if position <= 28: return self.CASE, 0
        if position == 29: return self.COIN_PETIT, 0
        
        if position == 30: return 0, self.COIN_GRAND
        if position <= 38: return 0, self.CASE
        if position == 39: return 0, self.COIN_PETIT
        raise AssertionError

    def aller(self, finale):
        while self.position != finale:
            pixel = self.image.get_xydata()
            pixel += self.deplacement_pixel(self.position)
            super().aller(self.position + 1)  # on avance de un
            self.image.set_data(*pixel.T)
            plt.pause(DELTA)

JOUEURS, TOURS, DELTA = 3, 50, 0.1
plateau = PlateauAnimé(ax, JOUEURS)
joueurs = 

from matplotlib.animation import FuncAnimation

ani = FuncAnimation(fig, update, frames=range(100), interval=50)
plt.show()

def toto(event):
    global plateau, joueurs
    joueur = next(joueurs)
    plateau.faire_jouer(joueur)

ax_button = plt.axes([0.45, 0.05, 0.1, 0.075])
button = Button(ax_button, 'Avancer')
button.on_clicked(toto)
