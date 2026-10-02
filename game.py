# ======================== game.py ========================

import pygame
import random
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, GRAVITY, JUMP_VELOCITY, SPRING_JUMP_VELOCITY,
    DOODLE_SPEED, DOODLE_WIDTH, DOODLE_HEIGHT, PLATFORM_WIDTH,
    MIN_PLATFORM_GAP, MAX_PLATFORM_GAP, CAMERA_SCROLL_THRESHOLD,
    PLATFORMS, doodle_dict, DOODLE_START_X, DOODLE_START_Y, LIVES
)
from platforms import create_platform, choose_platform_type
from doodle import doodle_left_img, doodle_right_img
from window import generate_initial_platforms


# ======================== PARTIE 3.1 ========================
def apply_gravity():
    """
    Applique la gravité au Doodle en augmentant progressivement sa vitesse verticale (vel_y).
    Met à jour la position verticale (y) du Doodle.
    """
    # TODO : Mettez à jour la vitesse verticale puis la position verticale
    # du Doodle à partir de GRAVITY.
    for cle in doodle_dict:
        if cle == "vel_y":
            doodle_dict["vel_y"]+= GRAVITY
            doodle_dict["y"] += doodle_dict["vel_y"]

    return

# ===========================================================


# ======================== PARTIE 1.2 ========================
def move_doodle():
    """
    Gère le déplacement horizontal du Doodle selon les touches pressées (Flèches ou A/D).
    Implémente le passage fluide d'un côté de l'écran à l'autre (Screen Wrap).
    """
    keys = pygame.key.get_pressed()

    # TODO : Gérez les déplacements gauche/droite et mettez à jour
    # simultanément la direction et l'image du Doodle.

    if keys[pygame.K_LEFT] or keys[pygame.K_a] :
        doodle_dict["x"] -= DOODLE_SPEED
        doodle_dict.update({
            "direction": "left",
            "image": doodle_left_img
        })
    if keys[pygame.K_RIGHT] or keys[pygame.K_d] :
        doodle_dict["x"] += DOODLE_SPEED
        doodle_dict.update({
            "direction": "right",
            "image" : doodle_right_img
        })


    # TODO : Implémentez le Screen Wrap pour qu'une partie du Doodle puisse
    # sortir d'un côté avant de réapparaître de l'autre.
    # N'utilisez pas de dimensions numériques écrites directement.
    # SCREEN_WIDTH = 576
    # SCREEN_HEIGHT = 800  --> info sur la taille de la fenêtre
    
    if doodle_dict["x"]+ DOODLE_WIDTH < 0 :   # doodle_dict["x"] < -DOODLE_WIDTH: J'ai remplacé ca juste pour une meilleure lecture perso du code, à discuter avec Clo
        doodle_dict["x"] = SCREEN_WIDTH  #on le teleporte a droite
    elif doodle_dict["x"] > SCREEN_WIDTH:  #on compare la largeur de l'éecran avec la position du bord gauche du doodle si somme >0 on teleporte on affivhant la largeur du doodle à partir de x=0
        doodle_dict ["x"] = -DOODLE_WIDTH #on le teleporte a gauche

    return

# ===========================================================


# ======================== PARTIE 2.3 ========================
def move_platforms():
    """
    Déplace horizontalement les plateformes mobiles ("blue").
    Fait rebondir les plateformes lorsqu'elles atteignent les bords de la fenêtre.
    """
    # TODO : Parcourez les plateformes et gérez le déplacement des plateformes
    # bleues encore actives. Elles doivent rester dans la fenêtre en inversant
    # leur vitesse lorsqu'elles atteignent un bord.
    for platefrom in PLATFORMS:
        if platefrom["type"]== "blue" and platefrom["active"]:
            platefrom["x"]+= platefrom["vx"]
            if platefrom["x"] >= SCREEN_WIDTH- PLATFORM_WIDTH or platefrom["x"] <= 0:
                platefrom["vx"] = -platefrom["vx"]
    return

# ===========================================================


# ======================== PARTIE 3.2 ========================
def check_platform_collisions():
    """
    Détecte si le Doodle atterrit sur une plateforme.
    Le rebond ne se produit QUE lorsque le Doodle descend (vel_y > 0)
    et qu'il arrive sur le dessus d'une plateforme.
    """
    # TODO : Implémentez la détection d'un atterrissage.
    #
    # Contraintes :
    # - aucun rebond pendant la montée ;
    # - ignorer les plateformes inactives ;
    # - utiliser rects_collide(...) pour le chevauchement des rectangles ;
    # - un simple chevauchement ne suffit pas : le Doodle doit arriver par
    #   le dessus de la plateforme. Pour le vérifier, comparez la position
    #   actuelle de ses pieds à leur position approximative à l'image
    #   précédente à l'aide de vel_y. Une tolérance de 14 pixels est permise ;
    # - spring : SPRING_JUMP_VELOCITY ;
    # - brown : JUMP_VELOCITY puis désactivation de la plateforme ;
    # - green/blue : JUMP_VELOCITY.
    rect_doodle= (doodle_dict["x"], doodle_dict["y"], DOODLE_WIDTH, DOODLE_HEIGHT)

    for plateform in PLATFORMS:
        if not plateform["active"]:
            continue 
    
        rect_platform=(plateform["x"], plateform["y"],plateform["width"], plateform["height"])
        pieds_actuelle= doodle_dict["y"]+ DOODLE_HEIGHT
        pieds_avant= doodle_dict["y"]+ DOODLE_HEIGHT - doodle_dict["vel_y"]

        arriver_par_le_haut= pieds_avant <= plateform["y"]+ 14
        a_atteri_sur_la_plateforme= pieds_actuelle >= plateform["y"]

        if (doodle_dict["vel_y"]>0 
            and rects_collide(rect_doodle, rect_platform)
            and arriver_par_le_haut
             and a_atteri_sur_la_plateforme ):
            
            if plateform["type"]== "spring":
                doodle_dict["vel_y"] = SPRING_JUMP_VELOCITY
            elif plateform["type"]== "brown":
                doodle_dict["vel_y"] = JUMP_VELOCITY
                plateform["active"] = False
            else:
                doodle_dict["vel_y"] = JUMP_VELOCITY

        

    
# ===========================================================


# ======================== PARTIE 3.3 ========================
def scroll_camera():
    """
    Fait défiler le monde lorsque le Doodle dépasse CAMERA_SCROLL_THRESHOLD.
    Met à jour le score et maintient les plateformes visibles.
    """
    # TODO : Lorsque le Doodle dépasse le seuil de caméra, il doit rester
    # visuellement au seuil pendant que les plateformes sont déplacées vers
    # le bas de la même distance.
    #
    # Le score doit représenter la distance verticale ainsi parcourue et le
    # meilleur score doit être mis à jour. Les plateformes sorties sous
    # l'écran doivent être retirées, puis de nouvelles plateformes générées.
    """Lorsque le Doodle monte au-dessus de `CAMERA_SCROLL_THRESHOLD`, il doit rester visuellement à cette hauteur. 
    Pour donner l'impression qu'il continue son ascension, c'est alors l'ensemble des plateformes qui se déplace vers le bas.
    Vous devez déterminer la distance de défilement nécessaire et l'utiliser pour :

    - repositionner le Doodle au seuil de caméra ;
    - déplacer toutes les plateformes de la même distance ;
    - augmenter le score selon la distance verticale parcourue ;
    - mettre à jour `high_score` lorsque nécessaire ;
    - retirer les plateformes ayant entièrement quitté la zone utile sous l'écran ;
    - demander la génération de nouvelles plateformes au-dessus de l'écran."""

    if doodle_dict["y"] < CAMERA_SCROLL_THRESHOLD :
        scroll_camera = CAMERA_SCROLL_THRESHOLD - doodle_dict["y"]
        doodle_dict["y"] = CAMERA_SCROLL_THRESHOLD

        # on déplace les plaformes de la meme distance
        for platform in PLATFORMS :
            platform["y"] += scroll_camera

        #le score
        doodle_dict["score"] += int(scroll_camera)
        if doodle_dict["score"] > doodle_dict["high_score"] :
            doodle_dict["high_score"] = doodle_dict["score"]

        #retirer les plateformes ayant entièrement quitté la zone
        """plateformes_gardees = []
        for platform in PLATFORMS:
            if platform["y"] < SCREEN_HEIGHT:
                plateformes_gardees.append(platform)"""

        PLATFORMS[:] = [platform for platform in PLATFORMS if platform["y"] < SCREEN_HEIGHT]

        generate_new_platforms()

    return

# ===========================================================


# ======================== PARTIE 3.4 ========================
def generate_new_platforms():
    """
    Génère de nouvelles plateformes au-dessus du haut de l'écran pour maintenir
    un flux continu lorsque la caméra défile.
    """
    # TODO : Complétez cette fonction en vous inspirant de la logique de
    # génération initiale, sans la recopier inutilement.
    #
    # Vous devrez partir de la plateforme actuellement la plus haute et
    # continuer à ajouter des plateformes tant que nécessaire. Utilisez
    # choose_platform_type(...) avec les probabilités indiquées dans le README.
    
    #cas où `PLATFORMS` est vide
    if not PLATFORMS :
        highest_plat = 0.0
    else :
        highest_plat = min(plat["y"] for plat in PLATFORMS) #min car repere pygame inversé

    while highest_plat > -50 :
        espacement = random.randint(MIN_PLATFORM_GAP, MAX_PLATFORM_GAP)
        highest_plat -= espacement

    #position horizontale valide
        pos_x = random.randint(0, SCREEN_WIDTH - PLATFORM_WIDTH) #-PLATFORM_WIDTH pour que la platforme soit dans l'écran
        platform_type = choose_platform_type(0.55, 0.20, 0.13)

        new_platform = create_platform(pos_x, highest_plat, platform_type)
        PLATFORMS.append(new_platform)
    return 

# ===========================================================


def check_game_over():
    """
    Vérifie si le Doodle tombe sous le bas de l'écran.
    Si oui, réduit les vies.
    Retourne True si la partie est terminée.
    """
    if doodle_dict["y"] > SCREEN_HEIGHT:
        doodle_dict["lives"] -= 1
        return True
    return False


def restart_game():
    """
    Réinitialise la partie : position du Doodle, vitesse, score et plateformes.
    """
    doodle_dict["x"] = DOODLE_START_X
    doodle_dict["y"] = DOODLE_START_Y
    doodle_dict["vel_y"] = 0.0
    doodle_dict["direction"] = "right"
    doodle_dict["image"] = doodle_right_img
    doodle_dict["score"] = 0
    doodle_dict["lives"] = LIVES

    generate_initial_platforms()


def rects_collide(r1, r2):
    """
    Vérifie si deux rectangles (x, y, largeur, hauteur) se chevauchent.
    Cette fonction est fournie et ne doit pas être modifiée.
    """
    return not (
        r1[0] + r1[2] <= r2[0] or r1[0] >= r2[0] + r2[2] or
        r1[1] + r1[3] <= r2[1] or r1[1] >= r2[1] + r2[3]
    )
