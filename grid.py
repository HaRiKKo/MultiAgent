from collections import deque
class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.agents = {}
        self.name = "Grid"
        
    def add_agent(self, agent):
        if self.is_valid(agent.position[0], agent.position[1]) and self.is_free(agent.position[0], agent.position[1]):
            self.agents[agent.position] = agent
            agent.grid = self
            agent.start = {}
            print(f"Agent {agent.name} a été rajouter à la grille {self.name}")
        else:
            raise ValueError(f"Position invalide pour {agent.name}")
    
    def remove_agent(self, agent):
        agent.grid = None
        del self.agents[agent.position]
    
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
            if (next_x, next_y) not in path and self.is_free(next_x, next_y):
                new_path = self.find_available_paths((next_x, next_y), end, path+[start])
                paths.extend(new_path)

        completed_paths = []
        for element in paths:
            if type(element) == list:
                completed_paths.append(element)

        return completed_paths
    
    def compute_agent_in_path(self, path):
        cpt=-1
        for case in path:
            if not self.is_free(case[0], case[1]):
                cpt+=1
        return cpt
                
    
    def find_shortest_paths(self, start, end, path=[]):
        """
        Trouves tout les chemin possible pour arriver au goal SANS contourner les agents
        et trie les chemins en fonction de leur longueur (les plus cours au début)
        """

        x, y = start
        if (x < 0 or x >= self.width or y < 0 or y >= self.height):
            return path
       
        if (start == end):
            return [path + [end]]
       
        paths = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            next_x, next_y = x + dx, y + dy
            if (next_x, next_y) not in path:
                new_path = self.find_shortest_paths((next_x, next_y), end, path+[start])
                paths.extend(new_path)
                
        completed_paths = []
        for element in paths:
            if type(element) == list:
                completed_paths.append(element)
        
        completed_paths.sort(key=len) 

        shortest_payhs = []
        for way in completed_paths:
            if len(way)==len(completed_paths[0]):
                shortest_payhs.append(way) 
            else:
                break

        return shortest_payhs
    
    def get_neighbors(self, current):
        """
        Retourne les voisins de la case actuelle.
        """

        neighbors = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            x = current[0] + dx
            y = current[1] + dy
            if 0 <= x < self.height and 0 <= y < self.width:
                neighbors.append((x, y))
        return neighbors
    
    def shortest_path(self, start, goal):
        """
        Retourne le plus court chemin entre start et goal sur la grille.
        """

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
