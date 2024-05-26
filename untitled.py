class colours:
    '''Colors class:reset all colours with colours.reset
    two sub classes fg for foreground and bg for background
    use as colours.subclass.colorname i.e. colours.fg.red or colours.bg.green
    The generic bold, disable, underline, reverse, strike through, and invisible
    work with the main class i.e. colours.bold'''
    reset = '\033[0m'
    bold = '\033[01m'
    disable = '\033[02m'
    underline = '\033[04m'
    reverse = '\033[07m'
    strikethrough = '\033[09m'
    invisible = '\033[08m'

    class fg:
        black = '\033[30m'
        red = '\033[31m'
        green = '\033[32m'
        orange = '\033[33m'
        blue = '\033[34m'
        purple = '\033[35m'
        cyan = '\033[36m'
        lightgrey = '\033[37m'
        darkgrey = '\033[90m'
        lightred = '\033[91m'
        lightgreen = '\033[92m'
        yellow = '\033[93m'
        lightblue = '\033[94m'
        pink = '\033[95m'
        lightcyan = '\033[96m'
 
    class bg:
        black = '\033[40m'
        red = '\033[41m'
        green = '\033[42m'
        orange = '\033[43m'
        blue = '\033[44m'
        purple = '\033[45m'
        cyan = '\033[46m'
        lightgrey = '\033[47m'

class NonSolvable(Exception):
    pass

class AllerEnPrison(Exception):
    pass

class ResterEnPrison(Exception):
    pass

imprimer = lambda *args, **kargs : None # print # 

import random

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
    def __init__(self, nom, groupe, somme):
        Achetable.__init__(self, "Compagnie d'" + nom, groupe, 150)
        self.somme = somme  # fonction donnant la somme des dés (vient du plateau)

    def loyer(self):
        return self.somme() * (10 if self.membre_d_un_monopole() else 4)


class Terrain(Achetable):
    HOTEL = 5

    def __init__(self, nom, code, groupe, prix, maison, *loyers):
        Achetable.__init__(self, nom, groupe, prix)
        self.code = code  # GROUPE.MARRON par exemple
        self.loyers = loyers  # liste des loyers en fonction du niveau de construction
        self.maison = maison  # prix de construction d'une maison / hôtel
        self.niveau = 0  # par convention hotel = 5 maisons

    def construire(self):
        if self.niveau < 5:
            self.bailleur.taxer(self.maison)
            self.niveau += 1

    def loyer(self):
        doubler = self.membre_d_un_monopole() and self.niveau == 0
        return self.loyers[self.niveau] * (1 + doubler)

    def nettoyer(self):
        Achetable.nettoyer(self)
        self.niveau = 0

    def __str__(self):
        return "{:<30} | {:>4} | {:^6} |".format(self.nom, self.prix, self.niveau)

class Joueur(object):
    def __init__(self, pseudo):
        self.pseudo = pseudo
        self.solvable = True  # n'a pas encore perdu
        self.argent = 1500
        self.position = Plateau.DEPART
        self.chance_sortie = False # pourrait être une liste mais impossible d'en avoir deux
        self.caisse_sortie = False
        self.portefeuille = []
        self.doubles_de_suite = 0

    def resumer(self):
        imprimer(colours.fg.cyan, self.pseudo, colours.reset, "solvable : ", self.solvable, "a", colours.fg.yellow, str(self.argent) + "€", colours.reset)

    def tableau(self):
        if len(self.portefeuille) == 0:
            return ""
        chaine = "\t{:<30} | {:>4} | {:^6} |".format("nom", "prix", "niveau")
        for achetable in self.portefeuille:
            chaine += "\n\t" + str(achetable)
        return chaine

    def compter_doubles(self, double):
        self.doubles_de_suite = self.doubles_de_suite + 1 if double else 0
        imprimer("\tnombre de double à la suite :", self.doubles_de_suite)
        if self.doubles_de_suite == 3:
            raise AllerEnPrison("Trois doubles de suite")

    def reposer(self, chance=False, caisse=False): 
        if chance:  # reposer les cartes chance
            carte_chance, self.chance_sortie = self.chance_sortie, False
            return carte_chance
        if caisse: # reposer les cartes caisse
            carte_caisse, self.caisse_sortie = self.caisse_sortie, False
            return carte_caisse
        # si rien n'est précisé, repose les deux : un peu crade mais pratique
        carte_chance, self.chance_sortie = self.chance_sortie, False
        carte_caisse, self.caisse_sortie = self.caisse_sortie, False
        return carte_chance, carte_caisse

    def nettoyer(self):
        self.solvable = False
        for achetable in self.portefeuille:
            achetable.nettoyer()
        return self.reposer()

    def aller(self, position):
        quotient, self.position = divmod(position, Plateau.TOTAL)
        if quotient != 0:
            self.argent += 200
            imprimer("\ttouche", colours.fg.yellow, "200€", colours.reset, "en passant par la case du départ")

    def taxer(self, montant):
        imprimer("\tse fait taxer ", colours.fg.yellow, str(montant) + "€", colours.reset)
        self.argent -= montant
        # TODO : ajouter l'hypothèque, la vente à la banque, aux enchères...
        if self.argent < 0:
            raise NonSolvable

    def donner(self, joueur, montant):
        imprimer("\tdoit donner ", colours.fg.yellow, str(montant) + "€", colours.reset, "à", colours.fg.cyan, joueur.pseudo, colours.reset)
        self.taxer(montant)
        joueur.argent += montant

    def payer_loyer(self, achetable, doubler=False):
        joueur = achetable.bailleur
        montant = achetable.loyer() * (1 + doubler)
        imprimer("\tdoit payer un loyer de ", colours.fg.yellow, str(montant) + "€", colours.reset, "à", colours.fg.cyan, joueur.pseudo, colours.reset)
        self.donner(joueur, montant)

    def taxer_construction(self, maison, hotel):
        montant = 0
        for a in self.portefeuille:
            try:
                montant += hotel if a.niveau == Terrain.HOTEL else montant * a.niveau
            except:
                continue
        self.taxer(montant)

    def acheter(self, achetable):
        imprimer("\tachète", achetable.nom)
        self.taxer(achetable.prix)
        achetable.bailleur = self
        self.portefeuille.append(achetable)

    def strategie_prison(self):
        return True, True, False

    def strategie_achat(self, achetable):
        return True

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

    def afficher(carte):
        if carte == Chance.SORTIE_DE_PRISON:
            chaine = "Vous êtes libéré de prison."
        elif carte == Chance.AVANCEZ_DEPART:
            chaine = "Avancez jusqu'à la case départ"
        elif carte == Chance.ALLEZ_EN_PRISON:
            chaine = "Allez en prison !"
        elif carte == Chance.RUE_DE_LA_PAIX:
            chaine = "Avancez rue de la Paix"
        elif carte == Chance.AVANCEZ_BOULEVARD_DE_LA_VILLETTE:
            chaine = "Avancez Boulevard de la Villette"
        elif carte == Chance.RENDEZ_VOUS_AVENUE_HENRI_MARTIN:
            chaine = "Rendez vous avenue Henri-Martin"
        elif carte == Chance.ALLEZ_GARE_MONTPARNASSE:
            chaine = "Avancez jusqu'à la gare Montparnasse"
        elif carte == Chance.RECULEZ_DE_TROIS_CASES:
            chaine = "Reculez de 3 cases"
        elif carte == Chance.DIVIDENDE:
            chaine = "Recevez 50€ de dividendes"
        elif carte == Chance.IMMEUBLE:
            chaine = "Vos placements immobiliers vous rapportent 150€"
        elif carte == Chance.EXCES_DE_VITESSE:
            chaine = "Excès de vitesse : payez 15€"
        elif carte == Chance.PRESIDENT:
            chaine = "Vous êtes président : payez 50€ à chaque joueurs"
        elif carte == Chance.REPARATION:
            chaine = "Frais de réparations : payez 25€ par maison et 100€ par hôtel"
        elif carte in Chance.GARE_PLUS_PROCHE:
            chaine = "Allez à la gare la plus proche. Payer le loyer double"
        elif carte == Chance.COMPAGNIE_PLUS_PROCHE:
            chaine = "Allez à la gare la plus proche."
        imprimer(colours.fg.red, "\t" + chaine, colours.reset)
            


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

    def afficher(carte):
        if carte == Caisse.SORTIE_DE_PRISON:
            chaine = "Vous êtes libéré de prison."
        elif carte == Caisse.AVANCEZ_DEPART:
            chaine = "Avancez jusqu'à la case départ"
        elif carte == Caisse.ALLEZ_EN_PRISON:
            chaine = "Allez en prison !"
        elif carte == Caisse.ASSURANCE_VIE:
            chaine = "Votre assurance vie vous rapporte 100€"
        elif carte == Caisse.IMPOTS:
            chaine = "Erreur des impôts en votre faveur. Recevez 20€"
        elif carte == Caisse.PLACEMENT:
            chaine = "Vos placement vous rapportent 100€"
        elif carte == Caisse.HERITAGE:
            chaine = "Vous héritez de 100€"
        elif carte == Caisse.BANQUE:
            chaine = "Erreur de la banque en votre faveur. Recevez 200€"
        elif carte == Caisse.BEAUTE:
            chaine = "Vous remportez le prix de beauté. Recevez 10€"
        elif carte == Caisse.EXPERT:
            chaine = "Expert ? Recevez 25€"
        elif carte == Caisse.STOCK:
            chaine = "Vos actions vous rapportent 50€"
        elif carte == Caisse.HOSPITALISATION:
            chaine = "Payez 100€ de fraix d'hospitalisation"
        elif carte == Caisse.MEDECIN:
            chaine = "Payez 50€ de fraix de médecin"
        elif carte == Caisse.SCOLARITE:
            chaine = "Payez 50 € de fraix de scolarité"
        elif carte == Caisse.ANNIVERSAIRE:
            chaine = "C'est votre anniversaire. Recevez 10€ de la part de chaque joueur"
        elif carte == Caisse.TRAVAUX:
            chaine = "Travaux : payez 40€ par maison et 115€ par hôtel"
        imprimer(colours.fg.lightblue, "\t" + chaine, colours.reset)

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
Terrain("Boulevard de Belleville"  , Groupe.MARRON, self.groupes[Groupe.MARRON],  60,  50,  2,  10,  30,   90,  160,  250), Case("Caisse de communauté"),
Terrain("Rue Lecourbe"             , Groupe.MARRON, self.groupes[Groupe.MARRON],  60,  50,  4,  20,  60,  180,  320,  450), Case("Impôt sur le revenu"), Gare("Montparnasse", self.groupes[Groupe.GARE]),
Terrain("Rue Vaugirard"            , Groupe.GRIS  , self.groupes[Groupe.GRIS  ], 100,  50,  6,  30,  90,  270,  400,  550), Case("Chance"),
Terrain("Rue de Courcelles"        , Groupe.GRIS  , self.groupes[Groupe.GRIS  ], 100,  50,  6,  30,  90,  270,  400,  550),
Terrain("Avenue de la République"  , Groupe.GRIS  , self.groupes[Groupe.GRIS  ], 120,  50,  8,  40, 100,  300,  450,  600), Case("Simple Visite"),
Terrain("Boulevard de la Villette" , Groupe.ROSE  , self.groupes[Groupe.ROSE  ], 140, 100, 10,  50, 150,  450,  625,  750), Compagnie("éléctricité", self.groupes[Groupe.COMPAGNIE], self.somme),
Terrain("Avenue de Neuilly"        , Groupe.ROSE  , self.groupes[Groupe.ROSE  ], 140, 100, 10,  50, 150,  450,  625,  750),
Terrain("Rue de Paradis"           , Groupe.ROSE  , self.groupes[Groupe.ROSE  ], 160, 100, 12,  60, 180,  500,  700,  900), Gare("de Lyon", self.groupes[Groupe.GARE]),
Terrain("Avenue Mozart"            , Groupe.ORANGE, self.groupes[Groupe.ORANGE], 180, 100, 14,  70, 200,  550,  750,  950), Case("Caisse de communauté"),
Terrain("Boulevard Saint-Michel"   , Groupe.ORANGE, self.groupes[Groupe.ORANGE], 180, 100, 14,  70, 200,  550,  750,  950),
Terrain("Place Pigalle"            , Groupe.ORANGE, self.groupes[Groupe.ORANGE], 200, 100, 16,  80, 220,  600,  800, 1000), Case("Parc gratuit"),
Terrain("Avenue Matignon"          , Groupe.ROUGE , self.groupes[Groupe.ROUGE ], 220, 150, 18,  90, 250,  700,  875, 1050), Case("Chance"),
Terrain("Boulevard Malesherbes"    , Groupe.ROUGE , self.groupes[Groupe.ROUGE ], 220, 150, 18,  90, 250,  700,  875, 1050),
Terrain("Avenue Henri-Martin"      , Groupe.ROUGE , self.groupes[Groupe.ROUGE ], 240, 150, 20, 100, 300,  750,  925, 1100), Gare("du Nord", self.groupes[Groupe.GARE]),
Terrain("Faubourg Saint-Honoré"    , Groupe.JAUNE , self.groupes[Groupe.JAUNE ], 260, 150, 22, 110, 330,  800,  975, 1150),
Terrain("Place de la bourse"       , Groupe.JAUNE , self.groupes[Groupe.JAUNE ], 260, 150, 22, 110, 330,  800,  975, 1150), Compagnie("eaux", self.groupes[Groupe.COMPAGNIE], self.somme),
Terrain("Rue la Fayette"           , Groupe.JAUNE , self.groupes[Groupe.JAUNE ], 280, 150, 24, 120, 360,  850, 1025, 1200), Case("Allez en prison"),
Terrain("Avenue de Breteuil"       , Groupe.VERT  , self.groupes[Groupe.VERT  ], 300, 200, 26, 130, 390,  900, 1100, 1275),
Terrain("Avenue Foch"              , Groupe.VERT  , self.groupes[Groupe.VERT  ], 300, 200, 26, 130, 390,  900, 1100, 1275), Case("Caisse de communauté"),
Terrain("Boulevard des Capucines"  , Groupe.VERT  , self.groupes[Groupe.VERT  ], 320, 200, 28, 150, 450, 1000, 1200, 1400), Gare("Saint-Lazare", self.groupes[Groupe.GARE]), Case("Chance"),
Terrain("Avenue des Champs-Élysées", Groupe.BLEU  , self.groupes[Groupe.BLEU  ], 350, 200, 35, 175, 500, 1100, 1300, 1500), Case("Taxe de luxe"),
Terrain("Rue de la paix"           , Groupe.BLEU  , self.groupes[Groupe.BLEU  ], 400, 200, 50, 200, 600, 1400, 1700, 2000),
        ]
        # fmt: on
        random.shuffle(self.chance)
        random.shuffle(self.caisse)

    def lancer(self):
        self.de_1 = random.randint(1, 6)
        self.de_2 = random.randint(1, 6)
        imprimer("\tlancer de dés : %d %d" % (self.de_1, self.de_2))

    def somme(self):
        return self.de_1 + self.de_2

    def double(self):
        return self.de_1 == self.de_2

    def autres(self, joueur=None):
        for j in self.joueurs:
            if j.solvable and j is not joueur:
                yield j

    def gare_la_plus_proche(self, position):
        if Plateau.GARE_MONTPARNASSE <= position < Plateau.GARE_DE_LYON:
            return Plateau.GARE_DE_LYON
        elif Plateau.GARE_DE_LYON <= position < Plateau.GARE_DU_NORD:
            return Plateau.GARE_DU_NORD
        elif Plateau.GARE_DU_NORD <= position < Plateau.GARE_SAINT_LAZARE:
            return Plateau.GARE_SAINT_LAZARE
        return Plateau.GARE_MONTPARNASSE

    def compagnie_la_plus_proche(self, position):
        if Plateau.COMPAGNIE_D_ELECTRICITE <= position < Plateau.COMPAGNIE_D_EAU:
            return Plateau.COMPAGNIE_D_EAU
        return Plateau.COMPAGNIE_D_ELECTRICITE

    def gerer_carte_chance(self, joueur):
        carte = self.chance.pop(0)
        Chance.afficher(carte)
        if carte == Chance.SORTIE_DE_PRISON:
            joueur.chance_sortie = True  # ajoute la carte à la main du joueur
        else:
            self.chance.append(carte)  # repose la carte dans la pile
            if carte == Chance.AVANCEZ_DEPART:
                joueur.aller(Plateau.DEPART)
            elif carte == Chance.ALLEZ_EN_PRISON:
                raise AllerEnPrison
            elif carte == Chance.DIVIDENDE:
                joueur.argent += 50
            elif carte == Chance.IMMEUBLE:
                joueur.argent += 150
            elif carte == Chance.EXCES_DE_VITESSE:
                joueur.taxer(15)
            elif carte == Chance.PRESIDENT:
                for j in self.autres(joueur):
                    joueur.donner(j, 50)
            elif carte == Chance.REPARATION:
                joueur.taxer_construction(25, 100)
            elif carte == Chance.RUE_DE_LA_PAIX:
                joueur.aller(Plateau.RUE_DE_LA_PAIX)
            elif carte == Chance.AVANCEZ_BOULEVARD_DE_LA_VILLETTE:
                joueur.aller(Plateau.BOULEVARD_DE_LA_VILLETTE)
            elif carte == Chance.RENDEZ_VOUS_AVENUE_HENRI_MARTIN:
                joueur.aller(Plateau.AVENUE_HENRI_MARTIN)
            elif carte == Chance.ALLEZ_GARE_MONTPARNASSE:
                joueur.aller(Plateau.GARE_MONTPARNASSE)
            elif carte == Chance.RECULEZ_DE_TROIS_CASES:
                joueur.aller(joueur.position - 3)
            elif carte in Chance.GARE_PLUS_PROCHE:
                joueur.aller(self.gare_la_plus_proche(joueur.position))
                return True
            elif carte == Chance.COMPAGNIE_PLUS_PROCHE:
                joueur.aller(self.compagnie_la_plus_proche(joueur.position))
                return True
        return False

    def gerer_carte_caisse(self, joueur):
        carte = self.caisse.pop(0)
        Caisse.afficher(carte)
        if carte == Caisse.SORTIE_DE_PRISON:
            joueur.caisse_sortie = True  # ajoute la carte à la main du joueur
        else:
            self.caisse.append(carte)  # repose la carte dans la pile
            if carte == Caisse.AVANCEZ_DEPART:
                joueur.aller(Plateau.DEPART)
            elif carte == Caisse.ALLEZ_EN_PRISON:
                raise AllerEnPrison
            elif carte == Caisse.ASSURANCE_VIE:
                joueur.argent += 100
            elif carte == Caisse.IMPOTS:
                joueur.argent += 20
            elif carte == Caisse.PLACEMENT:
                joueur.argent += 100
            elif carte == Caisse.HERITAGE:
                joueur.argent += 100
            elif carte == Caisse.BANQUE:
                joueur.argent += 200
            elif carte == Caisse.BEAUTE:
                joueur.argent += 10
            elif carte == Caisse.EXPERT:
                joueur.argent += 25
            elif carte == Caisse.STOCK:
                joueur.argent += 50
            elif carte == Caisse.HOSPITALISATION:
                joueur.taxer(100)
            elif carte == Caisse.MEDECIN:
                joueur.taxer(50)
            elif carte == Caisse.SCOLARITE:
                joueur.taxer(50)
            elif carte == Caisse.ANNIVERSAIRE:
                for j in self.autres(joueur):
                    j.donner(joueur, 10)
            elif carte == Caisse.TRAVAUX:
                joueur.taxer_construction(40, 115)

    def gerer_prison(self, joueur):
        if joueur.compter_doubles(self.double()) == 3:
            raise AllerEnPrison
        if joueur.position != Plateau.PRISON:
            return  # hors de prison
        if joueur.tours_en_prison == 1:
            veut_chance, veut_caisse, veut_taxe = joueur.strategie_prison()
            if veut_chance and joueur.reposer(chance=True):
                self.chance.append(Chance.SORTIE_DE_PRISON)
            elif veut_caisse and joueur.reposer(caisse=True):
                self.caisse.append(Caisse.SORTIE_DE_PRISON)
            elif veut_taxe and joueur.argent >= 50:
                joueur.taxer(50)
            elif not self.double():
                raise ResterEnPrison
        elif joueur.tours_en_prison <= 3:
            if not self.double():
                raise ResterEnPrison
        else:
            joueur.taxer(50)
        # sortir de prison
        joueur.position = Plateau.SIMPLE_VISITE
        joueur.doubles_de_suite = 0 # TODO : vérifier les règles...

    def debut_tour(self, joueur):
        self.lancer()
        self.gerer_prison(joueur)
        joueur.aller(joueur.position + self.somme())
        # Cases spéciales
        doubler = False
        if joueur.position == Plateau.PRISON:
            raise AllerEnPrison
        elif joueur.position in Plateau.CHANCE:
            doubler = self.gerer_carte_chance(joueur)  # peut doubler le loyer
        elif joueur.position in Plateau.CAISSE:
            self.gerer_carte_caisse(joueur)
        elif joueur.position == Plateau.IMPOTS_SUR_LE_REVENU:
            joueur.taxer(200)
        elif joueur.position == Plateau.TAXE_DE_LUXE:
            joueur.taxer(100)
        case = self.cases[joueur.position]
        imprimer("\t-->", case.nom)
        # Cases normales
        if isinstance(case, Achetable):
            if case.bailleur is None:  # terrain achetable
                veut_acheter = joueur.strategie_achat(case)
                if veut_acheter and joueur.argent >= case.prix:
                    joueur.acheter(case)
            elif case.bailleur is not self:  # terrain possédé par un autre joueur
                joueur.payer_loyer(case)                

    def fin_tour(self, joueur):
        pass  # TODO : ajouter les échanges entre joueurs

    def faire_jouer(self, joueur):
        joueur.resumer()
        try:
            self.debut_tour(joueur)
            self.fin_tour(joueur)
        except NonSolvable:
            carte_chance, carte_caisse = joueur.nettoyer()
            if carte_chance:
                self.chance.append(Chance.SORTIE_DE_PRISON)
            if carte_caisse:
                self.caisse.append(Caisse.SORTIE_DE_PRISON)
        except AllerEnPrison:
            joueur.position = Plateau.PRISON
            joueur.tours_en_prison = 1
            joueur.doubles_de_suite = 0  # TODO : vérifier les règles
        except ResterEnPrison:
            joueur.tours_en_prison += 1
        except Exception as err:
            raise err

    def tour(self):
        nombre = 0
        for joueur in self.autres():
            self.faire_jouer(joueur)
            nombre += 1 # un joueur solvable
        return nombre > 1
