from monopoly import *
import matplotlib.pyplot as plt

JOUEURS = 2
PARTIES = 1000
TOURS = 250

colours = plt.rcParams["axes.prop_cycle"].by_key()["color"]
fig, ax = plt.subplots()
ax.set_title("Monopoly à {} toto".format(JOUEURS))

for p in range(PARTIES):
    joueurs = [Joueur("n°%d" % (j,)) for j in range(JOUEURS)]
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
