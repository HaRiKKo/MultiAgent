from collections import deque
import random

from agent import Agent

class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.agents = []
        self.name = "Grid"

    def init_grid(self, nb_agents):
        init=True
        num_agent=0
        while init:
            position_desiree = (random.randint(0,self.height-1), random.randint(0, self.width-1)) # recherche d'une position
            if self.is_free(position_desiree[0], position_desiree[1]):
                agent = Agent("Agent "+str(num_agent+1), position_desiree, self.position_finale(num_agent), self)
                self.add_agent(agent)
                num_agent += 1
            if num_agent >= nb_agents or num_agent >= self.height*self.width-1:
                init=False

    def position_finale(self, num_agent):
        x = num_agent % self.width
        y = num_agent // self.height
        return (x,y)
    
    def add_agent(self, agent):
        if self.is_valid(agent.position[0], agent.position[1]) and self.is_free(agent.position[0], agent.position[1]):
            self.agents.append(agent)
            agent.grid = self
            agent.start = {}
            print(f"Agent {agent.name} a été ajouté à la grille {self.name}\n  Position de départ : {agent.position}\n  Position d'arrivée : {agent.goal}")
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
    
    def broadcast_message(self, sender, message, receiver):
        print(f"-- Broadcast d'un message de {sender.name} vers {receiver.name}")
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

        completed_paths.sort(key=len)

        return completed_paths
    
    def compute_agent_in_goal(self, path):
        cpt=0
        for case in path:
            potential_agent = self.get_agent(case[0], case[1])
            if potential_agent != None:
                cpt+=1
                if potential_agent.is_goal():
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
                # si il y a un agent qui est blocké => on le contourne pas comme la fenetre, là on plonge !
                if (self.is_free(next_x, next_y)) : # get_agent marche seulement s'il y a un agent !!!
                    new_path = self.find_shortest_paths((next_x, next_y), end, path+[start])
                    paths.extend(new_path)
                elif self.get_agent(next_x, next_y) != None and not self.get_agent(next_x, next_y).isBlock:
                    #if not self.get_agent(next_x, next_y).steppedAway:
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
        # résolution ligne par ligne
        for i in range(self.height-2):
            for agent in self.agents:
                if agent.goal[1]==i and not agent.is_goal():
                    agent.resolve_agent()
                    if (not agent.is_goal()):
                        agent.event.wait()

        # résolution colonne par colonne 
        for i in range(self.width):
            for agent in self.agents:
                if agent.goal[0]==i and not agent.is_goal():
                    agent.resolve_agent()
                    if (not agent.is_goal()):
                        agent.event.wait()
                    
        print("\nFin du taquin ! Tous les agents sont placés !\n")


                
