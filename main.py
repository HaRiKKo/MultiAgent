from agent import Agent
from grid import Grid
import time
import random
NB_AGENTS = 10

grid = Grid(5, 5)

grid.init_grid(NB_AGENTS)

grid.resolve_grid()

grid.stop()