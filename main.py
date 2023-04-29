from agent import Agent
from grid import Grid
import time
import random
import threading
import tkinter as tk

NB_AGENTS = 10

grid = Grid(5, 5)

grid.init_grid(NB_AGENTS)

def interface():
        # Création de la fenêtre
    fenetre = tk.Tk()
    fenetre.geometry("1000x1000")

    # Nombre de cercles à afficher
    n = 5

    # Taille des cercles
    rayon = 70

    # Distance entre les cercles
    distance = 100

    # Dessin de la grille
    def print_cercle(agent):
        i = agent.position[0]
        j = agent.position[1]
        x = distance * (i + 1)
        y = distance * (j + 1)
        cercle = tk.Canvas(fenetre, width=rayon, height=rayon)
        cercle.create_oval(0, 0, rayon, rayon, fill="blue")
        
        cercle.create_text(rayon//2, rayon//2, text=agent.name)
        
        cercle.place(x=x, y=y)

    def update_grille():
        fond_bleu = tk.Canvas(fenetre, width=(n+1)*distance, height=(n+1)*distance, bg="red")
        fond_bleu.place(x=0, y=0)
        for agent in grid.agents:
            print_cercle(agent)

        fenetre.after(1000, update_grille)  # appeler la fonction update_grille après 5000ms
    # Boucle principale d'affichage
    fenetre.after(1000, update_grille)
    # Boucle principale d'affichage
    fenetre.mainloop()

thread_affichage = threading.Thread(target=interface)
thread_affichage.start()

grid.resolve_grid()

grid.stop()



