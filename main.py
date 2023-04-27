'''
Méthode générale de résolution

Dans l'hypothèse où la case vide se trouve en bas à droite : 
remettre le jeu dans l'ordre ligne par ligne en commençant par la ligne 
du haut ; quand il ne reste plus que deux lignes mélangées, 
les réordonner colonne par colonne en commençant par celle de gauche.
'''

from agent import Agent
from grid import Grid
import time

grid = Grid(5, 5)
#coordonnée : (colonne, ligne)
agent1 = Agent("Agent 1", (0,0), (0,2), grid)
agent2 = Agent("Agent 2", (0,1), (0,1), grid)
agent3 = Agent("Agent 3", (1,1), (3,3), grid)
agent4 = Agent("Agent 4", (1,0), (2,4), grid)
agent5 = Agent("Agent 5", (3,2), (1,2), grid)
agent6 = Agent("Agent 6", (2,0), (2,0), grid)
agent7 = Agent("Agent 7", (4,0), (4,4), grid)
agent8 = Agent("Agent 8", (4,4), (4,0), grid)
agent9 = Agent("Agent 9", (2,1), (1,3), grid)
agent10 = Agent("Agent 10", (1,3), (3,1), grid)


grid.add_agent(agent1)
grid.add_agent(agent2)
grid.add_agent(agent3)
grid.add_agent(agent4)
grid.add_agent(agent5)
grid.add_agent(agent6)
grid.add_agent(agent7)
grid.add_agent(agent8)
grid.add_agent(agent9)
grid.add_agent(agent10)

grid.resolve_grid()

#print("\n plus court chemin:", agent1.best_path(grid))
#print("\nListe de Chemin pour aller de (0,0) à (3,2) :\n", grid.find_available_paths((0,0), (3,2)))
#print("\nChemin plus court pour aller de (0,0) à (3,2) :\n", grid.find_shortest_paths((0,0), (3,2)))
#time.sleep(6)
print("Arrêt de la grille dans le main")
grid.stop()