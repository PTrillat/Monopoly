import numpy as np
import time

class colours(object):
    """Colors class:reset all colours with colours.reset
    two sub classes fg for foreground and bg for background
    use as colours.subclass.colorname i.e. colours.fg.red or colours.bg.green
    The generic bold, disable, underline, reverse, strike through, and invisible
    work with the main class i.e. colours.bold"""

    reset = "\033[0m"
    bold = "\033[01m"
    disable = "\033[02m"
    underline = "\033[04m"
    reverse = "\033[07m"
    strikethrough = "\033[09m"
    invisible = "\033[08m"

    class fg:
        black = "\033[30m"
        red = "\033[31m"
        green = "\033[32m"
        orange = "\033[33m"
        blue = "\033[34m"
        purple = "\033[35m"
        cyan = "\033[36m"
        lightgrey = "\033[37m"
        darkgrey = "\033[90m"
        lightred = "\033[91m"
        lightgreen = "\033[92m"
        yellow = "\033[93m"
        lightblue = "\033[94m"
        pink = "\033[95m"
        lightcyan = "\033[96m"

    class bg:
        black = "\033[40m"
        red = "\033[41m"
        green = "\033[42m"
        orange = "\033[43m"
        blue = "\033[44m"
        purple = "\033[45m"
        cyan = "\033[46m"
        lightgrey = "\033[47m"

class imprimer(object):
    def base(*args):
        print(*args) # pass

    def rouge(*args):
        imprimer.base(colours.fg.red, *args, colours.reset)

    def bleu(*args):
        imprimer.base(colours.fg.blue, *args, colours.reset)

    def jaune(*args):
        imprimer.base(colours.fg.yellow, *args, colours.reset)

    def vert(*args):
        imprimer.base(colours.fg.green, *args, colours.reset)

    def chance(*args):
        imprimer.base("\t", colours.bg.red, *args, colours.reset)

    def caisse(*args):
        imprimer.base("\t", colours.bg.cyan, *args, colours.reset)

####################
# Évènements
####################

class NonSolvable(Exception): pass
class AllerEnPrison(Exception): pass
class ResterEnPrison(Exception): pass
class CaseSansPropriétaire(Exception): pass
class AllerGareLaPlusProche(Exception): pass
class AllerCompagnieLaPlusProche(Exception): pass
class JoueurDéplacé(Exception): pass


####################
# Tuiles
####################

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


class Case(object):
    def __init__(self, nom: str):
        self.nom = nom

    def action(self, _, __, ___):
        pass

class CaseGratuite(Case):
    def __init__(self, nom: str):
        super().__init__(nom)

class Taxe(Case):
    def __init__(self, nom: str, montant: int):
        super().__init__(nom)
        self.montant = montant

    def action(self, joueur, _, __):
        imprimer.rouge("\t", self.nom + ". Payez " + str(self.montant) + "€")
        joueur.taxer(self.montant)

class Achetable(Case):
    def __init__(self, nom: str, groupe: Groupe, taille_groupe: int, prix: int):
        super().__init__(nom)
        self.groupe = groupe
        self.prix = prix
        self.bailleur = None
        self.taille_groupe = taille_groupe

    def nettoyer(self):
        self.bailleur = None

    # def acheté_par(self, joueur, cases):
    #     self.bailleur = joueur
    #     # Détection d'un monopolse TODO : à optimiser
    #     for c in cases:
    #         if isinstance(c, Achetable) and (c.groupe == case.groupe) and (c not in joueur.portefeuille):
    #             return # pas un monopole
    #     for c in joueur.portefeuille:
    #         if isinstance(c, Achetable) and (c.groupe == case.groupe):
    #             c.monopolisé = True

class Gare(Achetable):
    def __init__(self, nom: str):
        super().__init__("Gare " + nom, Groupe.GARE, 4, 200)

    def action(self, joueur, _, des):
        if self.bailleur is None: raise CaseSansPropriétaire
        loyer = 25 * self.bailleur.nombre_propriétés[self.groupe]
        joueur.payer(self.bailleur, loyer)

class Compagnie(Achetable):
    def __init__(self, nom):
        super().__init__("Compagnie d'" + nom, Groupe.COMPAGNIE, 2, 150)

    def action(self, joueur, _, des):
        if self.bailleur is None: raise CaseSansPropriétaire
        monopole = self.bailleur.nombre_propriétés[self.groupe] == self.taille_groupe
        loyer = sum(des) * (10 if monopole else 4)
        joueur.payer(self.bailleur, loyer)

class Terrain(Achetable):
    HOTEL = 5

    def __init__(self, nom: str, groupe: Groupe, taille_groupe: int, prix: int, construction: int, loyers: tuple[int, int, int, int, int, int]):
        super().__init__(nom, groupe, taille_groupe, prix)
        self.loyers = loyers  # liste des loyers en fonction du niveau de construction
        self.construction = construction  # prix de construction d'une maison / hôtel
        self.niveau = 0  # par convention hotel = 5 maisons

    def action(self, joueur, _, __):
        if self.bailleur is None: raise CaseSansPropriétaire
        monopole = self.bailleur.nombre_propriétés[self.groupe] == self.taille_groupe
        doubler = (not monopole) and (self.niveau == 0)
        loyer = self.loyers[self.niveau] * (2 if doubler else 1)
        joueur.payer(self.bailleur, loyer)

    def nettoyer(self):
        self.bailleur = None
        self.niveau = 0

class Chance(Case):
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

    def __init__(self):
        super().__init__("Chance")
        self.paquet = list(range(Chance.TOTAL))
        np.random.shuffle(self.paquet)

    def action(self, joueur, autres, _):
        carte = self.paquet.pop(0)  # enlève la carte du sommet du paquet
        if carte == Chance.SORTIE_DE_PRISON:
            imprimer.chance("Vous êtes libéré de prison.")
            joueur.chance_sortie = True  # ajoute à la main du joueur
            return
        self.paquet.append(carte) # repose la carte dans le paquet
        if carte == Chance.AVANCEZ_DEPART:
            imprimer.chance("Avancez jusqu'à la case départ")
            joueur.déplacer(Plateau.DEPART)
        elif carte == Chance.ALLEZ_EN_PRISON:
            imprimer.chance("Allez en prison !")
            raise AllerEnPrison
        elif carte == Chance.DIVIDENDE:
            imprimer.chance("Recevez 50€ de dividendes")
            joueur.argent += 50
        elif carte == Chance.IMMEUBLE:
            imprimer.chance("Vos placements immobiliers vous rapportent 150€")
            joueur.argent += 150
        elif carte == Chance.EXCES_DE_VITESSE:
            imprimer.chance("Excès de vitesse : payez 15€")
            joueur.taxer(15)
        elif carte == Chance.PRESIDENT:
            imprimer.chance("Vous êtes président : payez 50€ à chaque joueurs")
            for j in autres:
                joueur.payer(j, 50)
        elif carte == Chance.REPARATION:
            imprimer.chance("Frais de réparations : payez 25€ par maison et 100€ par hôtel")
            joueur.taxer_construction(25, 100)
        elif carte == Chance.RUE_DE_LA_PAIX:
            imprimer.chance("Avancez rue de la Paix")
            joueur.déplacer(Plateau.RUE_DE_LA_PAIX)
        elif carte == Chance.AVANCEZ_BOULEVARD_DE_LA_VILLETTE:
            imprimer.chance("Avancez Boulevard de la Villette")
            joueur.déplacer(Plateau.BOULEVARD_DE_LA_VILLETTE)
        elif carte == Chance.RENDEZ_VOUS_AVENUE_HENRI_MARTIN:
            imprimer.chance("Rendez vous avenue Henri-Martin")
            joueur.déplacer(Plateau.AVENUE_HENRI_MARTIN)
        elif carte == Chance.ALLEZ_GARE_MONTPARNASSE:
            imprimer.chance("Avancez jusqu'à la gare Montparnasse")
            joueur.déplacer(Plateau.GARE_MONTPARNASSE)
        elif carte == Chance.RECULEZ_DE_TROIS_CASES:
            imprimer.chance("Reculez de 3 cases")
            joueur.déplacer(joueur.position - 3)
        elif carte in Chance.GARE_PLUS_PROCHE:
            imprimer.chance("Allez à la gare la plus proche. Payer le loyer double")
            raise AllerGareLaPlusProche
        elif carte == Chance.COMPAGNIE_PLUS_PROCHE:
            imprimer.chance("Allez à la compagnie la plus proche. Payer le loyer double")
            raise AllerCompagnieLaPlusProche

class Caisse(Case):
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

    def __init__(self):
        super().__init__("Caisse")
        self.paquet = list(range(Caisse.TOTAL))
        np.random.shuffle(self.paquet)

    def action(self, joueur, autres, _):
        carte = self.paquet.pop(0)  # enlève la carte du sommet du paquet
        if carte == Caisse.SORTIE_DE_PRISON:
            imprimer.caisse("Vous êtes libéré de prison.")
            joueur.caisse_sortie = True  # ajoute à la main du joueur
            return False
        self.paquet.append(carte) # repose la carte dans le paquet
        if carte == Caisse.AVANCEZ_DEPART:
            imprimer.caisse("Avancez jusqu'à la case départ")
            joueur.déplacer(Plateau.DEPART)
        elif carte == Caisse.ALLEZ_EN_PRISON:
            imprimer.caisse("Allez en prison !")
            raise AllerEnPrison
        elif carte == Caisse.ASSURANCE_VIE:
            imprimer.caisse("Votre assurance vie vous rapporte 100€")
            joueur.argent += 100
        elif carte == Caisse.IMPOTS:
            imprimer.caisse("Erreur des impôts en votre faveur. Recevez 20€")
            joueur.argent += 20
        elif carte == Caisse.PLACEMENT:
            imprimer.caisse("Vos placement vous rapportent 100€")
            joueur.argent += 100
        elif carte == Caisse.HERITAGE:
            imprimer.caisse("Vous héritez de 100€")
            joueur.argent += 100
        elif carte == Caisse.BANQUE:
            imprimer.caisse("Erreur de la banque en votre faveur. Recevez 200€")
            joueur.argent += 200
        elif carte == Caisse.BEAUTE:
            imprimer.caisse("Vous remportez le prix de beauté. Recevez 10€")
            joueur.argent += 10
        elif carte == Caisse.EXPERT:
            imprimer.caisse("Expert ? Recevez 25€")
            joueur.argent += 25
        elif carte == Caisse.STOCK:
            imprimer.caisse("Vos actions vous rapportent 50€")
            joueur.argent += 50
        elif carte == Caisse.HOSPITALISATION:
            imprimer.caisse("Payez 100€ de fraix d'hospitalisation")
            joueur.taxer(100)
        elif carte == Caisse.MEDECIN:
            imprimer.caisse("Payez 50€ de fraix de médecin")
            joueur.taxer(50)
        elif carte == Caisse.SCOLARITE:
            imprimer.caisse("Payez 50 € de fraix de scolarité")
            joueur.taxer(50)
        elif carte == Caisse.ANNIVERSAIRE:
            imprimer.caisse("C'est votre anniversaire. Recevez 10€ de la part de chaque joueur")
            for j in autres:
                j.payer(joueur, 10)
        elif carte == Caisse.TRAVAUX:
            imprimer.caisse("Travaux : payez 40€ par maison et 115€ par hôtel")
            joueur.taxer_construction(40, 115)

class Joueur(object):
    def __init__(self, pseudo: str):
        self.pseudo = pseudo
        self.argent = 1500
        self.position = Plateau.DEPART
        self.doubles_de_suite = 0
        self.portefeuille = []  # liste de propriétés
        self.nombre_propriétés = [0] * Groupe.TOTAL
        self.solvable = True
        self.tours_en_prison = 0
        self.chance_sortie = False  # a eu l'unique carte chance libéré de prison
        self.caisse_sortie = False  # a eu l'unique carte caisse libéré de prison

    def déplacer(self, position):
        self.aller(position)
        raise JoueurDéplacé

    def avancer(self, des):
        double = des[0] == des[1]
        self.doubles_de_suite = self.doubles_de_suite + 1 if double else 0
        if self.doubles_de_suite == 3:
            raise AllerEnPrison("Trois doubles de suite")
        self.aller((self.position + sum(des)) % Plateau.TOTAL)
    
    def aller(self, finale):
        finale %= Plateau.TOTAL  # assert finale >= 0; assert finale <= Plateau.TOTAL
        if finale <= self.position:
            imprimer.jaune("\t", "Touche 200€ en passant par la case du départ")
            self.argent += 200
        self.position = finale

    def veut_acheter(self, case):
        return True

    def veut_prison(self):
        return False, False, False

    def taxer(self, montant):
        self.argent -= montant
        if self.argent < 0:
            raise NonSolvable()

    def payer(self, autre, montant):
        self.taxer(montant)
        autre.argent += montant

    def taxer_construction(self, maison, hotel):
        montant = 0
        for achetable in self.portefeuille:
            if isinstance(achetable, Terrain):
                montant += hotel if achetable.niveau == Terrain.HOTEL else maison
        self.taxer(montant)

    def resumer(self):
        imprimer.base(
            colours.fg.cyan, self.pseudo, colours.reset,
            "solvable : ", self.solvable,
            "a", colours.fg.yellow, str(self.argent) + "€", colours.reset,
            "et", len(self.portefeuille), "propriétés"
        )

    def tableau(self):
        if len(self.portefeuille) == 0:
            return ""
        chaine = "\t{:<30} | {:>4} | {:^6} |".format("nom", "prix", "niveau")
        for achetable in self.portefeuille:
            chaine += "\n\t" + str(achetable)
        return chaine

    def nettoyer(self):
        self.solvable = False
        for achetable in self.portefeuille:
            achetable.nettoyer()
        return self.reposer()

    def reposer(self, chance=False, caisse=False):
        if chance:  # reposer les cartes chance
            carte_chance, self.chance_sortie = self.chance_sortie, False
            return carte_chance
        if caisse:  # reposer les cartes caisse
            carte_caisse, self.caisse_sortie = self.caisse_sortie, False
            return carte_caisse
        # si rien n'est précisé, repose les deux : un peu crade mais pratique
        carte_chance, self.chance_sortie = self.chance_sortie, False
        carte_caisse, self.caisse_sortie = self.caisse_sortie, False
        return carte_chance, carte_caisse

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
    CAISSE = (2, 17, 33)  # cases caisse de communauté
    TOTAL = 40

    def __init__(self, joueurs):
        self.joueurs = joueurs
        self.paquet_chance = Chance()  # créé un paquet commun pour les différente cases
        self.paquet_caisse = Caisse()  # créé un paquet commun pour les différente cases
        self.cases = [
        # fmt: off
            CaseGratuite("Départ"),
            Terrain("Boulevard de Belleville"  , Groupe.MARRON, 2,  60,  50, ( 2,  10,  30,   90,  160,  250)),
            self.paquet_caisse,
            Terrain("Rue Lecourbe"             , Groupe.MARRON, 2,  60,  50, ( 4,  20,  60,  180,  320,  450)),
            Taxe("Impôt sur le revenu", 200),
            Gare("Montparnasse"),
            Terrain("Rue Vaugirard"            , Groupe.GRIS  , 3, 100,  50, ( 6,  30,  90,  270,  400,  550)),
            self.paquet_chance,
            Terrain("Rue de Courcelles"        , Groupe.GRIS  , 3, 100,  50, ( 6,  30,  90,  270,  400,  550)),
            Terrain("Avenue de la République"  , Groupe.GRIS  , 3, 120,  50, ( 8,  40, 100,  300,  450,  600)),
            Case("Simple Visite"),
            Terrain("Boulevard de la Villette" , Groupe.ROSE  , 3, 140, 100, (10,  50, 150,  450,  625,  750)),
            Compagnie("éléctricité"),
            Terrain("Avenue de Neuilly"        , Groupe.ROSE  , 3, 140, 100, (10,  50, 150,  450,  625,  750)),
            Terrain("Rue de Paradis"           , Groupe.ROSE  , 3, 160, 100, (12,  60, 180,  500,  700,  900)),
            Gare("de Lyon"),
            Terrain("Avenue Mozart"            , Groupe.ORANGE, 3, 180, 100, (14,  70, 200,  550,  750,  950)),
            self.paquet_caisse,
            Terrain("Boulevard Saint-Michel"   , Groupe.ORANGE, 3, 180, 100, (14,  70, 200,  550,  750,  950)),
            Terrain("Place Pigalle"            , Groupe.ORANGE, 3, 200, 100, (16,  80, 220,  600,  800, 1000)),
            Case("Parc gratuit"),
            Terrain("Avenue Matignon"          , Groupe.ROUGE , 3, 220, 150, (18,  90, 250,  700,  875, 1050)),
            self.paquet_chance,
            Terrain("Boulevard Malesherbes"    , Groupe.ROUGE , 3, 220, 150, (18,  90, 250,  700,  875, 1050)),
            Terrain("Avenue Henri-Martin"      , Groupe.ROUGE , 3, 240, 150, (20, 100, 300,  750,  925, 1100)),
            Gare("du Nord"),
            Terrain("Faubourg Saint-Honoré"    , Groupe.JAUNE , 3, 260, 150, (22, 110, 330,  800,  975, 1150)),
            Terrain("Place de la bourse"       , Groupe.JAUNE , 3, 260, 150, (22, 110, 330,  800,  975, 1150)),
            Compagnie("eaux"),
            Terrain("Rue la Fayette"           , Groupe.JAUNE , 3, 280, 150, (24, 120, 360,  850, 1025, 1200)),
            Case("Allez en prison"),
            Terrain("Avenue de Breteuil"       , Groupe.VERT  , 3, 300, 200, (26, 130, 390,  900, 1100, 1275)),
            Terrain("Avenue Foch"              , Groupe.VERT  , 3, 300, 200, (26, 130, 390,  900, 1100, 1275)),
            self.paquet_caisse,
            Terrain("Boulevard des Capucines"  , Groupe.VERT  , 3, 320, 200, (28, 150, 450, 1000, 1200, 1400)),
            Gare("Saint-Lazare"),
            self.paquet_chance,
            Terrain("Avenue des Champs-Élysées", Groupe.BLEU  , 2, 350, 200, (35, 175, 500, 1100, 1300, 1500)),
            Taxe("Taxe de luxe", 100),
            Terrain("Rue de la paix"           , Groupe.BLEU  , 2, 400, 200, (50, 200, 600, 1400, 1700, 2000)),
        ]
        # fmt: on

    def joueurs_actifs(self):
        for j in self.joueurs:
            if j.argent >= 0:
                yield j

    def autres_joueurs_actifs(self, joueur):
        for j in self.joueurs:
            if (j.argent >= 0) and (j is not joueur):
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

    def faire_jouer(self, joueur):
        imprimer.base("pseudo : {}, {}€, portefeuille:{}".format(joueur.pseudo, joueur.argent, joueur.nombre_propriétés))
        des = np.random.randint(1, 6, 2)

        try:
            if joueur.position == Plateau.PRISON:
                diffère = des[0] != des[1]
                if joueur.tours_en_prison > 3:
                    pass  # Fin de la peine
                elif (joueur.tours_en_prison > 1) and diffère:
                    raise AllerEnPrison
                veut_chance, veut_caisse, veut_taxe = joueur.veut_prison()
                if   veut_chance and joueur.reposer(chance=True): self.paquet_chance.append(Chance.SORTIE_DE_PRISON)
                elif veut_caisse and joueur.reposer(caisse=True): self.paquet_caisse.append(Caisse.SORTIE_DE_PRISON)
                elif veut_taxe and joueur.argent >= 50: joueur.taxer(50)
                elif diffère: raise AllerEnPrison
                # Si on tombe ici, c'est qu'on sort de prison
                joueur.tours_en_prison = 0
                joueur.position = Plateau.SIMPLE_VISITE
            joueur.avancer(des)
            print("suite de la boucle principale")
            while True:  # S'il y a plusieurs déplacements
                case = self.cases[joueur.position]
                imprimer.base("\t", case.nom, case.bailleur if isinstance(case, Achetable) else "")
                try:
                    case.action(joueur, self.autres_joueurs_actifs(joueur), des)
                    # TODO : ajouter les loyer doublé lors d'un déplacement !
                except CaseSansPropriétaire:
                    if joueur.veut_acheter(case) and joueur.argent >= case.prix:
                        joueur.taxer(case.prix)
                        joueur.portefeuille.append(case)
                        joueur.nombre_propriétés[case.groupe] += 1
                        case.bailleur = joueur
                        imprimer.vert("\tacheté !")
                except NonSolvable:
                    imprimer.rouge("NON SOLVABLE")
                    carte_chance, carte_caisse = joueur.nettoyer()
                    if carte_chance: self.paquet_chance.append(Chance.SORTIE_DE_PRISON)
                    if carte_caisse: self.paquet_caisse.append(Caisse.SORTIE_DE_PRISON)
                except AllerGareLaPlusProche:
                    imprimer.rouge("GARE")
                    joueur.aller(self.gare_la_plus_proche(joueur.position))
                    continue  # On refait un tour
                except AllerCompagnieLaPlusProche:
                    imprimer.rouge("COMPAGNIE")
                    joueur.aller(self.compagnie_la_plus_proche(joueur.position))
                    continue  # On refait un tour
                except JoueurDéplacé:
                    imprimer.rouge("DÉPLACÉ")
                    continue  # On refait un tour
                break # Fin des tours
        except AllerEnPrison:
            imprimer.rouge("PRISON")
            joueur.position = Plateau.PRISON
            joueur.tours_en_prison += 1
            joueur.doubles_de_suite = 0
        # TODO : construire
    
    def un_tour(self):
        nbr_joueurs_actifs = 0
        for joueur in self.joueurs_actifs():
            nbr_joueurs_actifs += 1
            self.faire_jouer(joueur)
        return nbr_joueurs_actifs > 1
