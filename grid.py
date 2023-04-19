from collections import deque
class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.agents = {}
        self.name = "Grid"
        
    def add_agent(self, agent):
        if self.is_valid(agent.x, agent.y) and self.is_free(agent.x, agent.y):
            self.agents[(agent.x, agent.y)] = agent
            agent.grid = self
            agent.start = {}
        else:
            raise ValueError(f"Position invalide pour {agent.name}")
    
    def remove_agent(self, agent):
        agent.grid = None
        del self.agents[(agent.x, agent.y)]
    
    def get_agent(self, x, y):
        return self.agents.get((x, y))
    
    def is_valid(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height
    
    def is_free(self, x, y):
        return self.get_agent(x, y) is None
    
    def broadcast_message(self, sender, message, receiver):
        message.sender = sender
        message.receiver = receiver
        receiver.receive_message(message)
    
    def stop(self):
        for agent in self.agents.values():
            agent.stop()

    def find_available_paths(self, start, end, path=[]):

        """
        Trouve la liste des chemins possible en contournant les autre agents
        """
        
        x, y = start
        if (x < 0 or x >= self.width or y < 0 or y >= self.height):
            return path
        
        if (start == end):
            return [path + [end]]
        
        paths = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            next_x, next_y = x + dx, y + dy
            if (next_x, next_y) not in path and not any((agent.x, agent.y) == (next_x, next_y) for k,agent in self.agents.items()):
                new_path = self.find_available_paths((next_x, next_y), end, path+[start])
                paths.extend(new_path)

        completed_paths = []
        for element in paths:
            if type(element) == list:
                completed_paths.append(element)

        return completed_paths
    
    # def find_shortest_paths(self, start, end, path=[]):

    #     """
    #     Trouves tout les chemin possible pour arriver au goal SANS contourner les agents
    #     et trie les chemins en fonction de leur longueur (les plus cours au début)
    #     """
        
    #     x, y = start
    #     if (x < 0 or x >= self.width or y < 0 or y >= self.height):
    #         return path
        
    #     if (start == end):
    #         return [path + [end]]
        
    #     paths = []
    #     for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
    #         next_x, next_y = x + dx, y + dy
    #         if (next_x, next_y) not in path:
    #             new_path = self.find_shortest_paths((next_x, next_y), end, path+[start])
    #             paths.extend(new_path)

    #     completed_paths = []
    #     for element in paths:
    #         if type(element) == list:
    #             completed_paths.append(element)
        
    #     completed_paths.sort(key=len) 
    #     return completed_paths
    
    def get_neighbors(self, current):
        """Retourne les voisins de la case actuelle."""
        neighbors = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            x = current[0] + dx
            y = current[1] + dy
            if 0 <= x < self.height and 0 <= y < self.width and self.is_free(x,y):
                neighbors.append((x, y))
        return neighbors
    
    def shortest_path(self, start, goal):
        """Retourne le plus court chemin entre start et goal sur la grille."""
        frontier = [(start, [])]
        visited = set([start])
        while frontier:
            current, path = frontier.pop(0)
            if current == goal:
                return path + [current]
            for neighbor in self.get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    frontier.append((neighbor, path + [current]))
        return None
