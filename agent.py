import threading
import time
import queue
from message import Message, TypeMessage
import random


class Agent(threading.Thread):
    def __init__(self, name, position, goal, grid):
        super().__init__()
        self.name = name
        self.position = position
        self.goal = goal
        self.grid = grid
        self.isBlock = False
        self.ma_queue = queue.Queue()
        self.stopped = False
        self.event = threading.Event()
        self.start()

    def is_goal(self):
        return self.position == self.goal
    
    def get_neighbors(self):
        """
        Retourne les voisins de la case actuelle.
        """

        neighbors = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            x = self.position[0] + dx
            y = self.position[1] + dy
            if 0 <= x < self.grid.height and 0 <= y < self.grid.width:
                neighbors.append((x, y))
        return neighbors

    # give the best path (shortest + less agent)

    #TODO Si pas de best path => Message d'erreur / fin du jeux / jeux impossible !
    def best_path(self, grid):
        paths = grid.find_shortest_paths(self.position, self.goal, []) #recupère la liste des chemins les plus courts
        #print("list des chemins", paths)
        if len(paths)<=0: #si pas de chemin trouver
            print(f"L'agent n°{self.name} ne peut pas se déplacer de {self.position} vers {self.goal}.")
            return -1 # HERE Message d'érreur !
        else: #sinon on calcule le nombre d'agent par chemin et on trie les chemins pour récupérer le chemin le moins d'agent
            dict_paths = {}
            for i in range(len(paths)): #calcule du nombre d'agent
                dict_paths[i] = grid.compute_agent_in_path(paths[i])
            sorted_dict = sorted(dict_paths.items(), key=lambda item: item[1])
            shortest_path = paths[sorted_dict[0][0]]
            shortest_path.pop(0) #On enlève le première element du chemin car c'est la position actuelle
            return shortest_path
                    
    def move(self, dx, dy):
        new_x = self.position[0] + dx
        new_y = self.position[1] + dy
        
        if self.grid.is_valid(new_x, new_y):
            if self.grid.is_free(new_x, new_y):
                print(f"{self.name} se déplace de {self.position} à {(new_x, new_y)}")
                self.position = (new_x, new_y)
                if self.is_goal():
                    print(f"{self.name} arrivé à la case objectif")
            else:
                other_agent = self.grid.get_agent(new_x, new_y)
                print(f"{self.name} bloqué par {other_agent.name} en position {other_agent.position}")
                self.event.clear()
                self.send_message(Message(TypeMessage.BLOCKED, self.callback_blocked), other_agent)
                return -1 #erreur blocké
        else:
            print(f"{self.name} : Mouvement impossible en ({new_x}, {new_y})")
            return -2 #erreur position
        
        return 0 # ok
    
    def send_message(self, message, receiver):
        self.grid.broadcast_message(self, message, receiver)
    
    def receive_message(self, message):
        self.ma_queue.put(message)

    def stop(self):
        self.stopped = True

    def run(self):
        while True:
            while True: 
                try:
                    message = self.ma_queue.get(False)  # La thread attend de recevoir un message
                    
                    if (message.message_type == TypeMessage.BLOCKED): # si tu es un agent qui block 
                        
                        print(f"{self.name} : {message.sender.name} est bloqué, je vais lui répondre")
                        #message.response(bool(random.getrandbits(1)))# vrai code
                        if self.is_goal():
                            print(f"{self.name} : ne peut PAS bouger")
                            print(f"{self.position} position actuelle // {self.goal} objectif")
                            self.isBlock=True # Je suis blocké 
                            message.response(True) 
                        else:
                            print(f"{self.name} : peut bouger")
                            neighbors = self.get_neighbors()
                            print(f"{self.name} : mes voisins : {neighbors} ")
                            libre = False # aucune case voisin libre de trouvée
                            for neighbor in neighbors:
                                if self.grid.is_free(neighbor[0], neighbor[1]):
                                    libre = True # trouvée une case voisin libre
                                    print("J'ai trouvé une case voisine libre en ", neighbor)
                                    dx=neighbor[0]-self.position[0]
                                    dy=neighbor[1]-self.position[1]
                                    self.move(dx, dy)
                                    break
                            if not libre:
                                arret = True
                                print(f"Toutes les cases voisines de l'{self.name} sont occupées...")
                                # Envoie un message à un voisin pour qu'il se déplace
                                for neighbor in neighbors: # Etudie tous les voisins
                                    if neighbor != message.sender.position: # On vérifie que l'on essaye pas de se déplacer là où l'agent bloqué est
                                        print(f"On essaie la case voisine à la position : {neighbor}")
                                        agent_voisin = self.grid.get_agent(neighbor[0], neighbor[1])
                                        self.send_message(Message(TypeMessage.BLOCKED, self.set_event), agent_voisin)
                                        self.event.wait() # Attend la réponse de l'agent qui nous bloque
                                        if self.grid.is_free(neighbor[0], neighbor[1]): # On entre ici si l'agent à qui on a fait une demande s'est déplacé
                                            print(f"L'{agent_voisin} a bien voulu se déplacer, je peux bouger vers la case {neighbor}")
                                            arret = False
                                            dx=neighbor[0]-self.position[0]
                                            dy=neighbor[1]-self.position[1]
                                            self.move(dx, dy)
                                            break
                                if arret:
                                    # Aucune des cases voisines n'est exploitable, on ne peut pas se déplacer...        
                                    print("Aucune des cases voisines n'est exploitable, on ne peut pas se déplacer...")
                                    print("Jeux infinissable !\n Arret du jeux imminent !")
                                    self.grid.stop()
                                else :
                                    message.response(False) 
                            else:
                                message.response(False)
                        # si l'agent est déjà à son goal => ne pas bouger // sinon bouger 
                    
                    # réponse si tu es blocké
                    """
                    if (message.message_type == TypeMessage.PASGENTIL): # recalcule du chemin
                        print(self.name + ": Sorry :)")

                    if (message.message_type == TypeMessage.GENTIL): # relance resolve_agent
                        print(self.name + ": ")
                    """
                except queue.Empty:
                    break

            # print(f"{self.name} : boucle update")
            
            time.sleep(1)# évite de surcharger le cpu !
            if (self.stopped):
                break
    
    def set_event(self, neighbor, value):
        print(f"{self.name} : value retourné {value}")
        self.event.set()


    def callback_blocked(self, sender, value):
        print(f"{self.name} : value retourné {value}")
        """
        if (value): # A revoir !!!
            print(f"{self.name} : L'agent {sender.name} m'a répondu pas cool, je vais lui dire qu'il est po gentil")
            self.send_message(Message(TypeMessage.PASGENTIL, None), sender)
        
        if value: # si l'agent ne bouge PAS
            self.resolve_agent()
            print("_________________TESTESTESTEST_____________________")
        if not value: # si l'agent bouge 
            best_path=self.best_path(self.grid)
            next=best_path[0]
            dx = next[0]-self.position[0]
            dy = next[1]-self.position[1]
            self.move(dx, dy)
            self.event.set()
        """
        self.resolve_agent()
        if self.is_goal():
            self.event.set()
    
    def resolve_agent(self):
        print("\nResolve agent", self.name)
        best_path=self.best_path(self.grid)
        print("-> Son meilleur chemin :", best_path)
        for case in best_path:
            dx = case[0]-self.position[0]
            dy = case[1]-self.position[1]
            ret=self.move(dx, dy)
            if ret == -1:
                print("Sortie de resolve agent par erreur -1")
                break
            if ret == -2:
                print("Erreur mouvement impossible !!!")
                break
            
                

