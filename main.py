'''
Méthode générale de résolution

Dans l'hypothèse où la case vide se trouve en bas à droite : 
remettre le jeu dans l'ordre ligne par ligne en commençant par la ligne 
du haut ; quand il ne reste plus que deux lignes mélangées, 
les réordonner colonne par colonne en commençant par celle de gauche.
'''

from agent import Agent
from grid import Grid

grid = Grid(5, 5)

agent1 = Agent("Agent 1", 0, 0, grid)
# agent2 = Agent("Agent 2", 1, 0, grid)
# agent3 = Agent("Agent 3", 0, 4, grid)
grid.add_agent(agent1)
# grid.add_agent(agent2)
# grid.add_agent(agent3)

# agent1.move(3,2)
print("\nChemin plus court pour aller de (0,0) à (3,4) :\n", grid.shortest_path((0,0), (3,4)))
# agent1.move(1,0)



grid.stop()