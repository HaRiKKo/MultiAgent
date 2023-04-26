from collections import deque
class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.agents = []
        self.name = "Grid"
        
    def add_agent(self, agent):
        if self.is_valid(agent.position[0], agent.position[1]) and self.is_free(agent.position[0], agent.position[1]):
            self.agents.append(agent)
            agent.grid = self
            agent.start = {}
            print(f"Agent {agent.name} a été rajouter à la grille {self.name}")
        else:
            raise ValueError(f"Position invalide pour {agent.name}")
    
    def remove_agent(self, agent):
        agent.grid = None
        self.agents.remove(agent)
    
    def get_agent(self, x, y):
        list_agents = [agent for agent in self.agents if agent.position==(x, y)]
        if len(list_agents) == 0:
            return None
        else:
            return list_agents[0]
    
    def is_valid(self, x, y): 
        return 0 <= x < self.width and 0 <= y < self.height
    
    def is_free(self, x, y):
        return self.get_agent(x, y) is None
    
    # def update(self, agent, old_position):
    #     print(f"{agent.name} à été update dans la grille")
    #     del self.agents[old_position]
    #     self.agents[agent.position] = agent
    
    def broadcast_message(self, sender, message, receiver):
        print(f"Broadcast d'un message:\n sender={sender.name} \n receiver={receiver.name}")
        message.sender = sender
        message.receiver = receiver
        receiver.receive_message(message)
    
    def stop(self):
        for agent in self.agents:
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
                # si il y a un agent qui est blocké => on le contourne
                if self.is_free(next_x, next_y) or not self.get_agent(next_x, next_y).isBlock:
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
    
    def resolve_grid(self):
        # résolutionligne par ligne
        for i in range(self.height-2):
            for agent in self.agents:
                if agent.goal[1]==i and not agent.is_goal():
                    agent.resolve_agent()
        # résolution colomne par colomne 
        for i in range(self.width):
            for agent in self.agents:
                if agent.goal[0]==i and not agent.is_goal():
                    agent.resolve_agent()
