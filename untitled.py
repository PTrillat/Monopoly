def strRed(skk):
    return "\033[91m{}\033[00m".format(skk)


def strGreen(skk):
    return "\033[92m{}\033[00m".format(skk)


def strYellow(skk):
    return "\033[93m{}\033[00m".format(skk)


def strLightPurple(skk):
    return "\033[94m{}\033[00m".format(skk)


def strPurple(skk):
    return "\033[95m{}\033[00m".format(skk)


def strCyan(skk):
    return "\033[96m{}\033[00m".format(skk)


def strLightGray(skk):
    return "\033[97m{}\033[00m".format(skk)


def strBlack(skk):
    return "\033[98m{}\033[00m".format(skk)


import random


class Joueur(object):
    def __init__(self, pseudo, seuil):
        self.seuil = seuil
        self.pseudo = pseudo
        self.solvable = True  # n'a pas encore perdu
        self.argent = 1500
        self.position = Plateau.DEPART
        self.chance_sortie = False
        self.caisse_sortie = False
        self.portefeuille = []
        self.doubles_de_suite = 0

    def resumer(self, plateau=None, details=False):
        chaine = (
            strGreen(self.pseudo)
            + " débute son tour avec "
            + strYellow(str(self.argent) + "€")
            + " en "
        )
        if plateau:
            chaine += strPurple(plateau.cases[self.position].nom)
        else:
            chaine += "position " + str(self.position)
        if details:
            if len(self.portefeuille) > 0:
                chaine += " avec :\n\t{:<30} | {:>4} | {:^6} |".format(
                    "nom", "prix", "niveau"
                )
                for achetable in self.portefeuille:
                    chaine += "\n\t" + str(achetable)
        return chaine

    def compter_doubles(self, double):
        self.doubles_de_suite = self.doubles_de_suite + 1 if double else 0
        return self.doubles_de_suite

    def reposer_chance(self, plateau):
        self.chance_sortie = False
        plateau.chance.append(Chance.SORTIE_DE_PRISON)

    def reposer_caisse(self, plateau):
        self.caisse_sortie = False
        plateau.caisse.append(Caisse.SORTIE_DE_PRISON)

    def nettoyer(self, plateau):
        if self.chance_sortie:
            self.reposer_chance(plateau)
        if self.caisse_sortie:
            self.reposer_caisse(plateau)
        for achetable in self.portefeuille:
            achetable.nettoyer()

    def aller(self, position, plateau=None):
        quotient, self.position = divmod(position, Plateau.TOTAL)
        # if plateau:
            # fmt: off
            # print("\t" + strGreen(self.pseudo) + " arrive " + strPurple(plateau.cases[self.position].nom))
            # fmt: on
        if quotient != 0:
            self.argent += 200
            # if plateau:
                # fmt: off
                # print("\t" + strGreen(self.pseudo) + " touche " + strYellow("200€") + " de la case départ")
                # fmt: on

    def taxer(self, montant, plateau=None):  # le montant peut-être négatif
        self.argent -= montant
        # if plateau:
            # fmt: off
            # print("\t" + strGreen(self.pseudo) + " paye " + strYellow(str(montant) + "€")) + " et tombe à " + strYellow(str(self.argent) + "€")
            # fmt: on
        if self.argent < 0:
            # TODO : ajouter l'hypothèque, la vente à la banque, aux enchères...
            montant -= self.argent  # on ne peut payer que ce qu'on a
            self.solvable = False
            raise AssertionError("pas solvable")
        return montant  # montant réellement payé

    def aller_en_prison(self):
        # print("\t" + strGreen(self.pseudo) + " va en " + strRed("PRISON"))
        self.position = Plateau.PRISON
        self.tours_en_prison = 1
        self.doubles_de_suite = 0

    def sortir_de_prison(self):
        # print("\t" + strGreen(self.pseudo) + " sort en prison")
        self.position = Plateau.SIMPLE_VISITE
        self.tours_en_prison = 0
        self.doubles_de_suite = 0

    def payer(self, montant, joueur):
        if joueur is not self and joueur.solvable:
            joueur.argent += self.taxer(montant)

    def payer_loyer(self, achetable, doubler=False):
        if achetable.bailleur is None or achetable.bailleur is self:
            return False
        montant = achetable.loyer() * (1 + doubler)
        self.payer(montant, achetable.bailleur)
        # fmt: off
        # print("\t" + strGreen(self.pseudo) + " paye un loyer de " + str(montant) + "€ à " + strRed(achetable.bailleur.pseudo))
        # fmt: on
        return True

    def acheter(self, achetable):
        # print("\t" + strGreen(self.pseudo) + " achète " + strPurple(achetable.nom))
        self.taxer(achetable.prix)
        achetable.bailleur = self
        self.portefeuille.append(achetable)

    def taxer_constructions(self, maison, hotel):
        montant = 0
        for achetable in self.portefeuille:
            if isinstance(achetable, Terrain):
                if achetable.construction == 5:  # TODO : HOTEL
                    montant += hotel
                else:
                    montant += montant * achetable.construction
        self.taxer(montant)

    def strategie_prison(self):
        return True, True, False

    def strategie_achat(self, achetable):
        return random.random() < self.seuil


class Case(object):
    def __init__(self, nom):
        self.nom = nom


class Achetable(Case):
    def __init__(self, nom, groupe, prix):
        Case.__init__(self, nom)
        self.groupe = groupe
        self.prix = prix
        self.bailleur = None  # id est le propriétaire
        self.groupe.append(self)  # dans le groupe dont elle fait partie

    def taille(self):
        return sum([a.bailleur == self.bailleur for a in self.groupe])

    def membre_d_un_monopole(self):
        for achetable in self.groupe:
            if achetable.bailleur != self.bailleur:
                return False
        return True

    def nettoyer(self):
        self.bailleur = None

    def __str__(self):
        return "{:<30} | {:>4} |".format(self.nom, self.prix)


class Gare(Achetable):
    def __init__(self, nom, groupe):
        Achetable.__init__(self, "Gare " + nom, groupe, 200)

    def loyer(self):
        return 25 * self.taille()


class Compagnie(Achetable):
    def __init__(self, nom, groupe, des):
        Achetable.__init__(self, "Compagnie d'" + nom, groupe, 150)
        self.des = des  # fonction donnant la valeur des des (vient du plateau)

    def loyer(self):
        return self.des() * (10 if self.membre_d_un_monopole() else 4)


class Terrain(Achetable):
    def __init__(self, nom, groupe, prix, maison, *loyers):
        Achetable.__init__(self, nom, groupe, prix)
        self.loyers = loyers  # liste des loyers en fonction du niveau de construction
        self.maison = maison  # prix de construction d'une maison / hôtel
        self.construction = 0  # par convention hotel = 5 maisons

    def construire(self):
        if self.construction < 5:
            self.bailleur.taxer(self.maison)
            self.construction += 1

    def loyer(self):
        doubler = self.membre_d_un_monopole() and self.construction == 0
        return self.loyers[self.construction] * (1 + doubler)

    def nettoyer(self):
        Achetable.nettoyer(self)
        self.construction = 0

    def __str__(self):
        return "{:<30} | {:>4} | {:^6} |".format(self.nom, self.prix, self.construction)


class Groupe(object):
    MARRON = 0
    GRIS = 1
    ROSE = 2
    ORANGE = 3
    ROUGE = 4
    JAUNE = 5
    VERT = 6
    BLEU = 7
    COMPAGNIE = 8
    GARE = 9
    TOTAL = 10


class Chance(object):
    SORTIE_DE_PRISON = 0
    AVANCEZ_DEPART = 1
    ALLEZ_EN_PRISON = 2
    RUE_DE_LA_PAIX = 3
    AVANCEZ_BOULEVARD_DE_LA_VILLETTE = 4
    RENDEZ_VOUS_AVENUE_HENRI_MARTIN = 5
    ALLEZ_GARE_MONTPARNASSE = 6
    RECULEZ_DE_TROIS_CASES = 7
    DIVIDENDE = 8
    IMMEUBLE = 9
    EXCES_DE_VITESSE = 10
    PRESIDENT = 11
    REPARATION = 12
    GARE_PLUS_PROCHE = (13, 14)
    COMPAGNIE_PLUS_PROCHE = 15
    TOTAL = 16


class Caisse(object):
    SORTIE_DE_PRISON = 0
    AVANCEZ_DEPART = 1
    ALLEZ_EN_PRISON = 2
    ASSURANCE_VIE = 3
    IMPOTS = 4
    PLACEMENT = 5
    HERITAGE = 6
    BANQUE = 7
    BEAUTE = 8
    EXPERT = 9
    STOCK = 10
    HOSPITALISATION = 11
    MEDECIN = 12
    SCOLARITE = 13
    ANNIVERSAIRE = 14
    TRAVAUX = 15
    TOTAL = 16


class Plateau(object):
    DEPART = 0
    IMPOTS_SUR_LE_REVENU = 4
    GARE_MONTPARNASSE = 5
    SIMPLE_VISITE = 10
    BOULEVARD_DE_LA_VILLETTE = 11
    COMPAGNIE_D_ELECTRICITE = 12
    GARE_DE_LYON = 15
    AVENUE_HENRI_MARTIN = 24
    GARE_DU_NORD = 25
    COMPAGNIE_D_EAU = 28
    PRISON = 30
    GARE_SAINT_LAZARE = 35
    TAXE_DE_LUXE = 38
    RUE_DE_LA_PAIX = 39
    TOTAL = 40
    CHANCE = (7, 22, 36)  # cases chance
    CAISSE = (2, 17, 33)  # cases caissede communauté

    def __init__(self, *joueurs):
        self.joueurs = joueurs
        self.de_1 = 0
        self.de_2 = 0
        self.chance = list(range(Chance.TOTAL))  # Pile de cartes chance
        self.caisse = list(range(Caisse.TOTAL))  # Pile de cartes caisse de communauté
        self.groupes = [list() for _ in range(Groupe.TOTAL)]
        # fmt: off
        self.cases = [Case("Départ"),
            Terrain("Boulevard de Belleville"  , self.groupes[Groupe.MARRON],  60,  50,  2,  10,  30,   90,  160,  250), Case("Caisse de communauté"),
            Terrain("Rue Lecourbe"             , self.groupes[Groupe.MARRON],  60,  50,  4,  20,  60,  180,  320,  450), Case("Impôt sur le revenu"), Gare("Montparnasse", self.groupes[Groupe.GARE]),
            Terrain("Rue Vaugirard"            , self.groupes[Groupe.GRIS  ], 100,  50,  6,  30,  90,  270,  400,  550), Case("Chance"),
            Terrain("Rue de Courcelles"        , self.groupes[Groupe.GRIS  ], 100,  50,  6,  30,  90,  270,  400,  550),
            Terrain("Avenue de la République"  , self.groupes[Groupe.GRIS  ], 120,  50,  8,  40, 100,  300,  450,  600), Case("Simple Visite"),
            Terrain("Boulevard de la Villette" , self.groupes[Groupe.ROSE  ], 140, 100, 10,  50, 150,  450,  625,  750), Compagnie("éléctricité", self.groupes[Groupe.COMPAGNIE], self.somme),
            Terrain("Avenue de Neuilly"        , self.groupes[Groupe.ROSE  ], 140, 100, 10,  50, 150,  450,  625,  750),
            Terrain("Rue de Paradis"           , self.groupes[Groupe.ROSE  ], 160, 100, 12,  60, 180,  500,  700,  900), Gare("de Lyon", self.groupes[Groupe.GARE]),
            Terrain("Avenue Mozart"            , self.groupes[Groupe.ORANGE], 180, 100, 14,  70, 200,  550,  750,  950), Case("Caisse de communauté"),
            Terrain("Boulevard Saint-Michel"   , self.groupes[Groupe.ORANGE], 180, 100, 14,  70, 200,  550,  750,  950),
            Terrain("Place Pigalle"            , self.groupes[Groupe.ORANGE], 200, 100, 16,  80, 220,  600,  800, 1000), Case("Parc gratuit"),
            Terrain("Avenue Matignon"          , self.groupes[Groupe.ROUGE ], 220, 150, 18,  90, 250,  700,  875, 1050), Case("Chance"),
            Terrain("Boulevard Malesherbes"    , self.groupes[Groupe.ROUGE ], 220, 150, 18,  90, 250,  700,  875, 1050),
            Terrain("Avenue Henri-Martin"      , self.groupes[Groupe.ROUGE ], 240, 150, 20, 100, 300,  750,  925, 1100), Gare("du Nord", self.groupes[Groupe.GARE]),
            Terrain("Faubourg Saint-Honoré"    , self.groupes[Groupe.JAUNE ], 260, 150, 22, 110, 330,  800,  975, 1150),
            Terrain("Place de la bourse"       , self.groupes[Groupe.JAUNE ], 260, 150, 22, 110, 330,  800,  975, 1150), Compagnie("eaux", self.groupes[Groupe.COMPAGNIE], self.somme),
            Terrain("Rue la Fayette"           , self.groupes[Groupe.JAUNE ], 280, 150, 24, 120, 360,  850, 1025, 1200), Case("Allez en prison"),
            Terrain("Avenue de Breteuil"       , self.groupes[Groupe.VERT  ], 300, 200, 26, 130, 390,  900, 1100, 1275),
            Terrain("Avenue Foch"              , self.groupes[Groupe.VERT  ], 300, 200, 26, 130, 390,  900, 1100, 1275), Case("Caisse de communauté"),
            Terrain("Boulevard des Capucines"  , self.groupes[Groupe.VERT  ], 320, 200, 28, 150, 450, 1000, 1200, 1400), Gare("Saint-Lazare", self.groupes[Groupe.GARE]), Case("Chance"),
            Terrain("Avenue des Champs-Élysées", self.groupes[Groupe.BLEU  ], 350, 200, 35, 175, 500, 1100, 1300, 1500), Case("Taxe de luxe"),
            Terrain("Rue de la paix"           , self.groupes[Groupe.BLEU  ], 400, 200, 50, 200, 600, 1400, 1700, 2000),
        ]
        # fmt: on
        random.shuffle(self.chance)
        random.shuffle(self.caisse)

    def lancer(self):
        self.de_1 = random.randint(1, 6)
        self.de_2 = random.randint(1, 6)
        # print("Lancer de dés : %d %d" % (self.de_1, self.de_2))

    def somme(self):
        return self.de_1 + self.de_2

    def double(self):
        return self.de_1 == self.de_2

    def autres(self, joueur):
        for j in self.joueurs:
            if j is not joueur:
                yield j

    def gare_la_plus_proche(self, joueur):
        if Plateau.GARE_MONTPARNASSE <= joueur.position < Plateau.GARE_DE_LYON:
            joueur.aller(Plateau.GARE_DE_LYON, self)
        elif Plateau.GARE_DE_LYON <= joueur.position < Plateau.GARE_DU_NORD:
            joueur.aller(Plateau.GARE_DU_NORD, self)
        elif Plateau.GARE_DU_NORD <= joueur.position < Plateau.GARE_SAINT_LAZARE:
            joueur.aller(Plateau.GARE_SAINT_LAZARE, self)
        else:
            joueur.aller(Plateau.GARE_MONTPARNASSE, self)
        return self.cases[joueur.position]

    def compagnie_la_plus_proche(self, joueur):
        if Plateau.COMPAGNIE_D_ELECTRICITE <= joueur.position < Plateau.COMPAGNIE_D_EAU:
            joueur.aller(Plateau.COMPAGNIE_D_EAU)
        else:
            joueur.aller(Plateau.COMPAGNIE_D_ELECTRICITE)
        return self.cases[joueur.position]

    def gerer_carte_chance(self, joueur):
        carte = self.chance.pop(0)
        if carte == Chance.SORTIE_DE_PRISON:
            # print(strRed("\tsortie de prison"))
            joueur.chance_sortie = True
        else:
            self.chance.append(carte)
            if carte == Chance.AVANCEZ_DEPART:
                joueur.aller(Plateau.DEPART, self)
            elif carte == Chance.ALLEZ_EN_PRISON:
                joueur.aller_en_prison()
                return
            elif carte == Chance.RUE_DE_LA_PAIX:
                joueur.aller(Plateau.RUE_DE_LA_PAIX, self)
            elif carte == Chance.AVANCEZ_BOULEVARD_DE_LA_VILLETTE:
                joueur.aller(Plateau.BOULEVARD_DE_LA_VILLETTE, self)
            elif carte == Chance.RENDEZ_VOUS_AVENUE_HENRI_MARTIN:
                joueur.aller(Plateau.AVENUE_HENRI_MARTIN, self)
            elif carte == Chance.ALLEZ_GARE_MONTPARNASSE:
                joueur.aller(Plateau.GARE_MONTPARNASSE, self)
            elif carte == Chance.RECULEZ_DE_TROIS_CASES:
                # print(strRed("\tReculer de 3 cases"))
                joueur.aller(joueur.position - 3)
            elif carte == Chance.DIVIDENDE:
                # print(strRed("\tdividendes de 50€"))
                joueur.argent += 50
            elif carte == Chance.IMMEUBLE:
                # print(strRed("\tplacements immobiliers rapportent 150€"))
                joueur.argent += 150
            elif carte == Chance.EXCES_DE_VITESSE:
                # print(strRed("\texcès de vitesse : payer 15€"))
                joueur.taxer(15)
            elif carte == Chance.PRESIDENT:
                # print(strRed("\tprésident payer 50€ à chaque joueurs"))
                for j in self.autres(joueur):
                    joueur.payer(50, j)
            elif carte == Chance.REPARATION:
                # print(strRed("\tréparations : payer 25€ par maison et 100€ par hôtel"))
                joueur.taxer_constructions(25, 100)
            elif carte in Chance.GARE_PLUS_PROCHE:
                # print(strRed("\taller à la gare la plus proche, doubler le loyer"))
                gare = self.gare_la_plus_proche(joueur)
                joueur.payer_loyer(gare, doubler=True)
            elif carte == Chance.COMPAGNIE_PLUS_PROCHE:
                # print(strRed("\taller à la compagnie la plus proche, doubler le loyer"))
                compagnie = self.compagnie_la_plus_proche(joueur)
                joueur.payer_loyer(compagnie, doubler=True)

    def gerer_carte_caisse(self, joueur):
        carte = self.caisse.pop(0)
        if carte == Chance.SORTIE_DE_PRISON:
            # print(strCyan("\tsortie de prison"))
            joueur.caisse_sortie = True
        else:
            self.caisse.append(carte)
            if carte == Caisse.AVANCEZ_DEPART:
                joueur.aller(Plateau.DEPART, self)
            elif carte == Caisse.ALLEZ_EN_PRISON:
                return joueur.aller_en_prison()
            elif carte == Caisse.ASSURANCE_VIE:
                joueur.argent += 100
                # print(strCyan("\tassurance vie recevez 100€"))
            elif carte == Caisse.IMPOTS:
                joueur.argent += 20
                # print(strCyan("\terreur des impôts en votre faveur recevez 20€"))
            elif carte == Caisse.PLACEMENT:
                joueur.argent += 100
                # print(strCyan("\tvos placement vous rapportent 100€"))
            elif carte == Caisse.HERITAGE:
                joueur.argent += 100
                # print(strCyan("\théritez de 100€"))
            elif carte == Caisse.BANQUE:
                joueur.argent += 200
                # print(strCyan("\terreur de la banque en votre faveur recevez 200€"))
            elif carte == Caisse.BEAUTE:
                joueur.argent += 10
                # print(strCyan("\tbeauté de 10€"))
            elif carte == Caisse.EXPERT:
                joueur.argent += 25
                # print(strCyan("\texpert 25€"))
            elif carte == Caisse.STOCK:
                joueur.argent += 50
                # print(strCyan("\tactions 50€"))
            elif carte == Caisse.HOSPITALISATION:
                joueur.taxer(100)
                # print(strCyan("\thospitalisation payer 100€"))
            elif carte == Caisse.MEDECIN:
                joueur.taxer(50)
                # print(strCyan("\tmédecin payer 50€"))
            elif carte == Caisse.SCOLARITE:
                joueur.taxer(50)
                # print(strCyan("\tscolarité payer 50€"))
            elif carte == Caisse.ANNIVERSAIRE:
                # fmt: off
                # print(strCyan("\tc'est votre anniversaire recevez 10€ de chaque joueur"))
                # fmt: on
                for j in self.autres(joueur):
                    j.payer(10, joueur)
            elif carte == Caisse.TRAVAUX:
                # print(strCyan("\ttravaux : payez 40€ par maison et 115€ par hôtel"))
                joueur.taxer_constructions(40, 115)

    def gerer_la_prison(self, joueur):
        if joueur.tours_en_prison <= 3:
            veut_chance, veut_caisse, veut_taxe = joueur.strategie_prison()
            if veut_chance and joueur.chance_sortie:
                joueur.reposer_chance(plateau)
            elif veut_caisse and joueur.caisse_sortie:
                joueur.reposer_caisse(plateau)
            elif veut_taxe and joueur.argent >= 50:
                joueur.taxer(50)
            elif not self.double():
                joueur.tours_en_prison += 1
                return
        else:
            joueur.taxer(50)
        joueur.sortir_de_prison()
        return self.milieu_tour(joueur)

    def debut_tour(self, joueur):
        self.lancer()
        if joueur.position == Plateau.PRISON:
            return self.gerer_la_prison(joueur)
        elif joueur.compter_doubles(self.double()) == 3:
            return joueur.aller_en_prison()
        return self.milieu_tour(joueur)

    def milieu_tour(self, joueur):
        joueur.aller(joueur.position + self.somme(), self)
        case = self.cases[joueur.position]
        if joueur.position == Plateau.PRISON:
            return joueur.aller_en_prison()
        elif joueur.position in Plateau.CHANCE:
            return self.gerer_carte_chance(joueur)
        elif joueur.position in Plateau.CAISSE:
            return self.gerer_carte_caisse(joueur)
        elif joueur.position == Plateau.IMPOTS_SUR_LE_REVENU:
            joueur.taxer(200)
        elif joueur.position == Plateau.TAXE_DE_LUXE:
            joueur.taxer(100)
        elif isinstance(case, Achetable):
            if not joueur.payer_loyer(case):
                veut_acheter = joueur.strategie_achat(case)
                if veut_acheter and joueur.argent >= case.prix:
                    joueur.acheter(case)

    def fin_tour(self, joueur):
        pass  # TODO : ajoueter les échanges entre joueurs

    def faire_jouer(self, joueur):
        if not joueur.solvable:
            return
        try:
            # print(joueur.resumer(plateau))
            self.debut_tour(joueur)
            self.fin_tour(joueur)
        except:
            joueur.nettoyer(self)

    def tour(self):
        for joueur in self.joueurs:
            self.faire_jouer(joueur)
        return sum([joueur.solvable for joueur in self.joueurs]) > 1


JOUEURS = 3
PARTIES = 100
TOURS = 500

if False:
    joueurs = [Joueur("toto" + str(j)) for j in range(JOUEURS)]
    plateau = Plateau(*joueurs)
    for t in range(TOURS):
        poursuivre = plateau.tour()
        if not poursuivre:
            print("FIIIIIIIIIIIIIIIIIIIIN")
            break
    for joueur in joueurs:
        print(joueur.resumer(plateau, details=True))
else:
    argent = [[[] for j in range(JOUEURS)] for p in range(PARTIES)]
    for p in range(PARTIES):
        joueurs = [Joueur("toto" + str(j), (j+1)/(JOUEURS+1)) for j in range(JOUEURS)]
        plateau = Plateau(*joueurs)
        for t in range(TOURS):
            poursuivre = plateau.tour()
            for j, joueur in enumerate(plateau.joueurs):
                argent[p][j].append(joueur.argent)
            if not poursuivre:
                break

    import matplotlib.pyplot as plt

    colours = plt.rcParams["axes.prop_cycle"].by_key()["color"]

    plt.figure()
    for p in range(PARTIES):
        for j in range(JOUEURS):
            plt.plot(
                argent[p][j],
                color=colours[j],
                linewidth=4,
                alpha=0.1,
                label="θ" + str(j + 1) if p == 0 else None,
            )

    for e in plt.legend().legendHandles:
        e.set_alpha(1)
    plt.grid()
    plt.show()
