from agent import Agent
from grid import Grid
import time
import random
import threading
import tkinter as tk

NB_AGENTS = 5
n = 3
grid = Grid(n, n)

grid.init_grid(NB_AGENTS)

def interface():
        # Création de la fenêtre
    fenetre = tk.Tk()
    fenetre.geometry("1000x1000")

    # Taille des cercles
    rayon = 70

    # Distance entre les cercles
    distance = 100

    # Dessin de la grille
    def print_cercle(agent):
        i = agent.position[0]
        j = agent.position[1]
        x = distance * (i )
        y = distance * (j)
        cercle = tk.Canvas(fenetre, width=rayon, height=rayon)
        cercle.create_oval(0, 0, rayon, rayon, fill="blue")
        cercle.create_text(rayon//2, rayon//2, text=agent.name)
        
        cercle.place(x=x + 15, y=y + 15)

    def update_grille():
        fond_bleu = tk.Canvas(fenetre, width=(n)*distance, height=(n)*distance, bg="red")
        fond_bleu.place(x=0, y=0)
        for i in range(n):
            fond_bleu.create_line(0, i*distance, (n+1)*distance, i*distance, width=3)
        for i in range(n):
            fond_bleu.create_line(i*distance, (n+1)*distance, i*distance, 0, width=3)
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



