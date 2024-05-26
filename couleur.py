from monopoly import *
import matplotlib.pyplot as plt

def JoueurCouleur(Joueur):
    def __init__(self, indices, *args, **kargs):
        Joueur.__init__(self, *args, **kargs)
        self.indices = indices

    def strategie_achat(self, achetable):
        if isinstance(achetable, Gare):
            return True
        if isinstance(achetable, Compagnie):
            return True
        return achetable.indice in self.indices

INDICES = [
    (Groupe.MARRON, Groupe.GRIS),
    (Groupe.ROSE, Groupe.ORANGE),
    (Groupe.ROUGE, Groupe.JAUNE),
    (Groupe.VERT, Groupe.BLEU)
]
PARTIES = 1000
TOURS = 250

colours = plt.rcParams["axes.prop_cycle"].by_key()["color"]
fig, ax = plt.subplots()
ax.set_title("Monopoly à {} toto".format(JOUEURS))

for p in range(PARTIES):
    joueurs = [JoueurCouleur("groupe n°%d" % (j,)) for j in range(JOUEURS)]
    plateau = Plateau(*joueurs)
    argents = [[] for j in range(JOUEURS)]

    t = 0
    while t < TOURS and plateau.tour():
        for a, j in zip(argents, joueurs):
            a.append(j.argent) # if j.solvable else None)
        t += 1

    for a, c, j in zip(argents, colours, joueurs):
        plt.plot(a, color=c, linewidth=0.2, label=j.pseudo if p==0 else None)

plt.legend()
plt.grid()
plt.show()
