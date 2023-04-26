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

    # give the best path (shortest + less agent)
    def best_path(self, grid):
        paths = grid.find_shortest_paths(self.position, self.goal, []) #recupère la liste des chemins les plus courts
        #print("list des chemins", paths)
        if len(paths)<=0: #si pas de chemin trouver
            print(f"L'agent n°{self.name} ne peut pas se déplacer de {self.position} vers {self.goal}.")
            return -1
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
                print(f"{self.name} se déplasse de {self.position} à {(new_x, new_y)}")
                self.position = (new_x, new_y)
            else:
                other_agent = self.grid.get_agent(new_x, new_y)
                print(f"{self.name} bloqué par {other_agent.name}")
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
                        
                        print(f"{self.name} : L'agent {message.sender.name} est bloqué, je vais lui répondre")
                        #message.response(bool(random.getrandbits(1)))# vrai code
                        if self.is_goal():
                            print(f"{self.name} : ne peut PAS bouger")
                            print(f"{self.position} position actuelle //{self.goal} objectif")
                            self.isBlock=True # Je suis blocké 
                            message.response(True) 
                        else:
                            print(f"{self.name} : peut bouger")
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

            print(f"{self.name} : boucle update")
            
            time.sleep(1)# évite de surcharger le cpu !
            if (self.stopped):
                break

    def callback_blocked(self, sender, value):
        print(f"{self.name} : value retourné {value}")
        """
        if (value): # A revoir !!!
            print(f"{self.name} : L'agent {sender.name} m'a répondu pas cool, je vais lui dire qu'il est po gentil")
            self.send_message(Message(TypeMessage.PASGENTIL, None), sender)
        """
        #self.resolve_agent()
        self.event.set()
    
    def resolve_agent(self):
        print("resolve agent", self.name)
        best_path=self.best_path(self.grid)
        print("son meilleur chemin:", best_path)
        for case in best_path:
            dx = case[0]-self.position[0]
            dy = case[1]-self.position[1]
            ret=self.move(dx, dy)
            if ret == -1:
                self.event.wait()

