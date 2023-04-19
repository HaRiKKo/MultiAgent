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

agent1 = Agent("Agent 1", 0, 0, (3,2), grid)
# agent2 = Agent("Agent 2", 1, 0, (1,1), grid)
# agent3 = Agent("Agent 3", 3, 2, (2,2), grid)
grid.add_agent(agent1)
# grid.add_agent(agent2)
# grid.add_agent(agent3)


# agent1.move(3,2)
#print(grid.find_shortest_paths((0,0), (3,2), []))
print(agent1.best_path(grid))
# agent1.move(1,0)



#grid.stop()