from v2 import *
import tkinter as tk
from PIL import Image, ImageTk
import itertools
import time

FENETRE_LARGEUR = 800
FENETRE_HAUTEUR = 1000

# Fenêtre principale
root = tk.Tk()
root.title("Monopoly")
root.geometry("{}x{}".format(FENETRE_LARGEUR, FENETRE_HAUTEUR))

# Pour l'instant taille du plateau (qui est carré) pas de dessin en dessous
CADRE_LARGEUR = 800
CADRE_HAUTEUR = 900
canvas = tk.Canvas(root, width=CADRE_LARGEUR, height=CADRE_HAUTEUR)
canvas.pack()

class DessinPlateau(Plateau):
    def __init__(self, CADRE_LARGEUR, CADRE_HAUTEUR, canvas, nbr=4):
        PLATEAU_DIM = int(min(CADRE_LARGEUR, CADRE_HAUTEUR))
        image = Image.open("monopoly_board.png").resize((PLATEAU_DIM, PLATEAU_DIM))
        self.image = ImageTk.PhotoImage(image)
        canvas.create_image(0, 0, anchor=tk.NW, image=self.image)

        super().__init__([DessinJoueur(j, canvas, PLATEAU_DIM) for j in range(nbr)])

class DessinJoueur(Joueur):
    def __init__(self, numéro, canvas, PLATEAU_DIM, RAYON=15):
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
        self.px = DEPART
        self.py = DEPART
        self.image = canvas.create_oval(
            self.px - RAYON, self.py - RAYON,
            self.px + RAYON, self.py + RAYON, fill=colours[numéro])

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
        if self.position != finale:
            print("boucle")
            canvas.move(self.image, *self.deplacement_pixel(self.position))
            super().aller(self.position + 1)  # on avance d'une case
            root.after(1000, lambda: None)
            time.sleep(1)
            self.aller(finale)
        

JOUEURS, TOURS = 3, 50
plateau = DessinPlateau(CADRE_LARGEUR, CADRE_HAUTEUR, canvas, JOUEURS)
joueurs = itertools.cycle(plateau.joueurs)

def toto():
    global plateau, joueurs
    joueur = next(joueurs)
    plateau.faire_jouer(joueur)

bouton = tk.Button(root, text="Déplacer Pions", command=toto)
bouton.pack()
root.mainloop()

#----------------------------*
# while t < TOURS and plateau.un_tour():
#     t += 1
# root.mainloop()


#----------------------------*
# def un_tour_avec_delai():
#     global t
#     if t < TOURS and plateau.un_tour():
#         t += 1
#         root.after(500, un_tour_avec_delai)  # Attend 500ms avant d'exécuter le prochain tour
#     else:
#         print("Partie terminée")
# root.after(500, un_tour_avec_delai)  # Démarre après 500ms
# root.mainloop()

#----------------------------*
# # Boutons pour déplacer les pions
# def faire_un_tour():
#     global t
#     if t < TOURS and plateau.un_tour():
#         t += 1
#     else:
#         print("Fin")
#         raise AssertionError
# bouton = tk.Button(root, text="Déplacer Pions", command=faire_un_tour)
# bouton.pack()

# # Lancer la boucle principale Tkinter
root.mainloop()


raise AssertionError




# Carré
PLATEAU_DIM = int(min(CADRE_LARGEUR, CADRE_HAUTEUR))
image = Image.open("monopoly_board.png").resize((PLATEAU_DIM, PLATEAU_DIM))
image = ImageTk.PhotoImage(image)
canvas.create_image(0, 0, anchor=tk.NW, image=image)

coin = 0.1273125  # pourcentage de la longeur du plateau
marge = 0.3  # pourcentage du coin

case = (1. - 2. * coin) / 9.  # taille d'une case normale car 9 case + 2 coin = 100%
coin_grand = (1. - marge) * coin + marge * case
coin_petit = 1. - (8. + marge) * case - (1. + marge) * coin

DEPART = int((1. - marge * coin) * PLATEAU_DIM)
CASE = int(case * PLATEAU_DIM)
COIN_GRAND = int(coin_grand * PLATEAU_DIM)
COIN_PETIT = int(coin_petit * PLATEAU_DIM)



def deplacer_pixel(indice: int):
    if indice == 0: return -COIN_GRAND, 0
    if indice <= 8: return -CASE, 0
    if indice == 9: return -COIN_PETIT, 0

    if indice == 10:return 0, -COIN_GRAND
    if indice <= 18:return 0, -CASE
    if indice == 19:return 0, -COIN_PETIT

    if indice == 20: return COIN_GRAND, 0
    if indice <= 28: return CASE, 0
    if indice == 29: return COIN_PETIT, 0
    
    if indice == 30: return 0, COIN_GRAND
    if indice <= 38: return 0, CASE
    if indice == 39: return 0, COIN_PETIT
    raise AssertionError

# Liste de pions (position initiale)
pions = {
    "joueur1": {"couleur": "red"  , "indice": 0, "px" : DEPART            , "py" : DEPART},
    "joueur2": {"couleur": "blue" , "indice": 0, "px" : DEPART - 2 * RAYON, "py" : DEPART},
}

class Joueur:
    pass

# Afficher les pions
for i, (joueur, pion) in enumerate(pions.items()):
    px, py = pion["px"], pion["py"]
    pion["id"] = canvas.create_oval(px - RAYON, py - RAYON, px + RAYON, py + RAYON, fill=pion["couleur"])

# Fonction pour déplacer un pion
def deplacer_pion(joueur):
    pion = pions[joueur]
    dx, dy = deplacer_pixel(pion["indice"])
    pion["px"] += dx
    pion["py"] += dy
    canvas.move(pion["id"], dx, dy)
    pion["indice"] += 1
    pion["indice"] %= 40
    print(joueur, pion["indice"], pion["px"], pion["py"])

# Boutons pour déplacer les pions
def bouton_deplacement():
    deplacer_pion("joueur1")
    # deplacer_pion("joueur2")

# Créer un bouton pour déplacer les pions
bouton = tk.Button(root, text="Déplacer Pions", command=bouton_deplacement)
bouton.pack()

# Lancer la boucle principale Tkinter
root.mainloop()
