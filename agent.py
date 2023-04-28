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
        self.steppedAway = False
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
    def best_path(self, grid):
        # determination du chemin a prendre !
        if len(grid.find_available_paths(self.position,self.goal)) == 0:
            print("Best path\n")
            paths = grid.find_shortest_paths(self.position,self.goal)
            #print("list des chemins", paths)
            if len(paths)<=0: #si pas de chemin trouver
                print(f"{self.name} ne peut pas se déplacer de {self.position} vers {self.goal}.")
                return -1 
            else: #sinon on calcule le nombre d'agent par chemin et on trie les chemins pour récupérer le chemin le moins d'agent
                dict_paths = {}
                for i in range(len(paths)): #calcule du nombre d'agent
                    dict_paths[i] = grid.compute_agent_in_goal(paths[i])
                sorted_dict = sorted(dict_paths.items(), key=lambda item: item[1])
                shortest_path = paths[sorted_dict[0][0]]
                shortest_path.pop(0) #On enlève le première element du chemin car c'est la position actuelle
                path = shortest_path     
        else:
            print("Available path\n")
            path = grid.find_available_paths(self.position,self.goal)[0]
            path.pop(0)
        return path

        
                    
    def move(self, dx, dy):
        new_x = self.position[0] + dx
        new_y = self.position[1] + dy
        
        if self.grid.is_valid(new_x, new_y):
            if self.grid.is_free(new_x, new_y):
                print(f"{self.name} se déplace de {self.position} à {(new_x, new_y)}")
                self.position = (new_x, new_y)
                if self.is_goal():
                    print(f"{self.name} arrivé à la case objectif")
                    self.steppedAway = False
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
        print("Un message a été mis dans la queue de l'agent ", self.name)
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
                        if self.steppedAway:
                            print(f"Le stepped away est activé pour {self.name}")
                            if self.grid.is_free(self.goal[0], self.goal[1]):
                                dx=self.goal[0]-self.position[0]
                                dy=self.goal[1]-self.position[1]
                                self.move(dx, dy)
                                print(f"{self.name} : A de nouveau atteint la position objectif en {self.position}")
                                self.steppedAway=False
                                self.isBlock=False
                                message.response(False)
                            else :
                                print(f"{self.name} : Ne peut pas se déplacer, s'est déjà éloigné de son objectif")
                                self.isBlock=True
                                message.response(True) 
                        # Vérifier s'il est possible de se décaler d'une case
                        # Si une case est libre -> se déplace
                        # Si non -> demande à un voisin de se déplacer
                        else:
                            print(f"Le stepped away est désactivé pour {self.name}")
                            # on récupère les voisins et on supprime le sender et son objectif si il fait partie des voisins 
                            neighbors = self.get_neighbors()
                            if message.sender.position in neighbors:
                                neighbors.remove(message.sender.position)
                            if message.sender.goal in neighbors:
                                neighbors.remove(message.sender.goal)

                            print(f"{self.name} : mes voisins : {neighbors} ")
                            libre = False # aucune case voisin libre de trouvée
                            for neighbor in neighbors:
                                if self.grid.is_free(neighbor[0], neighbor[1]):
                                    libre = True # trouvée une case voisin libre
                                    print(f"{self.name} a trouvé une case voisine libre en ", neighbor)
                                    if self.is_goal():
                                        print(f"{self.name} est à sa position objectif mais bouge d'une case.")
                                        self.steppedAway=True
                                    dx=neighbor[0]-self.position[0]
                                    dy=neighbor[1]-self.position[1]
                                    self.move(dx, dy)
                                    break
                            if not libre:
                                arret = True
                                print(f"Toutes les cases voisines de l'{self.name} sont occupées...")
                                # Envoie un message à un voisin pour qu'il se déplace
                                agents_neighbors = [] # Liste des agents voisins à partir des cases voisines
                                for position_agent in neighbors:
                                    agents_neighbors.append(self.grid.get_agent(position_agent[0], position_agent[1]))
                                neighbors_is_goal = [] # Liste avec True et False correspondant aux voisins qui sont à leur place finale ou non
                                for agent in agents_neighbors:
                                    neighbors_is_goal.append(agent.is_goal())
                                    
                                for i in range(len(neighbors_is_goal)):
                                    if not neighbors_is_goal[i]: # Il y a un voisin qui n'est pas à sa position finale
                                        # On demande à ce voisin de se pousser 
                                        neighbor_to_move = agents_neighbors[i] # UN Agent qui n'est pas encore à sa position finale
                                        position_desiree = neighbor_to_move.position
                                        print(f"{self.name} : Demande à {neighbor_to_move.name} de se déplacer car il n'est pas à son objectif")
                                        self.send_message(Message(TypeMessage.BLOCKED, self.set_event), neighbor_to_move)
                                        self.event.wait()
                                        if self.grid.is_free(position_desiree[0], position_desiree[1]): # On entre ici si l'agent à qui on a fait une demande s'est déplacé
                                            print(f"L'{neighbor_to_move.name} a bien voulu se déplacer, je peux bouger vers la case {position_desiree}")
                                            arret = False
                                            dx=position_desiree[0]-self.position[0]
                                            dy=position_desiree[1]-self.position[1]
                                            self.move(dx, dy)
                                            break
                                if not False in neighbors_is_goal : # Tous les voisins sont à leur position finale
                                    # On en choisi celui qui a un numéro plus grand = GOAL le + en bas à droite)
                                    positions_agents = [agent.position[1] for agent in agents_neighbors]
                                    index = positions_agents.index(max(positions_agents))
                                    neighbor_to_move = agents_neighbors[index]
                                    position_desiree = neighbor_to_move.position
                                    print(f"{self.name} : Demande à {neighbor_to_move.name} de se déplacer même s'il est à son objectif")
                                    self.send_message(Message(TypeMessage.BLOCKED, self.set_event), neighbor_to_move)
                                    self.event.wait()
                                    if self.grid.is_free(position_desiree[0], position_desiree[1]): # On entre ici si l'agent à qui on a fait une demande s'est déplacé
                                        print(f"L'{neighbor_to_move.name} a bien voulu se déplacer, je peux bouger vers la case {position_desiree}")
                                        arret = False
                                        dx=position_desiree[0]-self.position[0]
                                        dy=position_desiree[1]-self.position[1]
                                        self.move(dx, dy)
                                    # break
                                    # projet de marde
                                # for neighbor in neighbors: # Etudie tous les voisins
                                #     agent_voisin = self.grid.get_agent(neighbor[0], neighbor[1])
                                #     if neighbor != message.sender.position: # On vérifie que l'on essaye pas de se déplacer là où l'agent bloqué est
                                #         print(f"On essaie la case voisine à la position : {neighbor}")
                                #         self.send_message(Message(TypeMessage.BLOCKED, self.set_event), agent_voisin)
                                #         self.event.wait() # Attend la réponse de l'agent qui nous bloque
                                #         if self.grid.is_free(neighbor[0], neighbor[1]): # On entre ici si l'agent à qui on a fait une demande s'est déplacé
                                #             print(f"L'{agent_voisin.name} a bien voulu se déplacer, je peux bouger vers la case {neighbor}")
                                #             arret = False
                                #             if self.is_goal():
                                #                 print(f"{self.name} est à sa position objectif mais bouge d'une case.")
                                #                 self.steppedAway=True
                                #             dx=neighbor[0]-self.position[0]
                                #             dy=neighbor[1]-self.position[1]
                                #             self.move(dx, dy)
                                #             break
                                if arret:
                                    # Aucune des cases voisines n'est exploitable, on ne peut pas se déplacer...        
                                    print("Aucune des cases voisines n'est exploitable, on ne peut pas se déplacer...")
                                    
                                    #print("Jeux infinissable !\n Arret du jeux imminent !")
                                    #self.grid.stop()
                                    self.isBlock=True
                                    message.response(True)
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

    # def run_1(self):#ancienne fonction run
    #     while True:
    #         while True: 
    #             try:
    #                 message = self.ma_queue.get(False)  # La thread attend de recevoir un message
                    
    #                 if (message.message_type == TypeMessage.BLOCKED): # si tu es un agent qui block 
                        
    #                     print(f"{self.name} : {message.sender.name} est bloqué, je vais lui répondre")
    #                     #message.response(bool(random.getrandbits(1)))# vrai code
    #                     if self.is_goal():
    #                         print(f"{self.name} : Position finale atteinte, j'essaye de me décaler d'une case") #TODO : Faire en sorte de s'éloigner d'une case de la position finale
    #                         # Vérifier s'il est possible de se décaler d'une case
    #                         # Si une case est libre -> se déplace
    #                         # Si non -> demande à un voisin de se déplacer
    #                         # Ajout de l'agent à la liste de ceux qui se sont déplacer et devront refaire le chemin vers leur objectif
    #                         self.steppedAway=True # Je suis blocké 
    #                         message.response(True) 
    #                     else:
    #                         print(f"{self.name} : peut bouger")
    #                         neighbors = self.get_neighbors()
    #                         print(f"{self.name} : mes voisins : {neighbors} ")
    #                         libre = False # aucune case voisin libre de trouvée
    #                         for neighbor in neighbors:
    #                             if self.grid.is_free(neighbor[0], neighbor[1]):
    #                                 libre = True # trouvée une case voisin libre
    #                                 print(f"{self.name} : case voisine libre en ", neighbor)
    #                                 dx=neighbor[0]-self.position[0]
    #                                 dy=neighbor[1]-self.position[1]
    #                                 self.move(dx, dy)
    #                                 break
    #                         if not libre:
    #                             arret = True
    #                             print(f"Toutes les cases voisines de l'{self.name} sont occupées...")
    #                             # Envoie un message à un voisin pour qu'il se déplace
    #                             for neighbor in neighbors: # Etudie tous les voisins
    #                                 if neighbor != message.sender.position: # On vérifie que l'on essaye pas de se déplacer là où l'agent bloqué est
    #                                     print(f"On essaie la case voisine à la position : {neighbor}")
    #                                     agent_voisin = self.grid.get_agent(neighbor[0], neighbor[1])
    #                                     self.send_message(Message(TypeMessage.BLOCKED, self.set_event), agent_voisin)
    #                                     self.event.wait() # Attend la réponse de l'agent qui nous bloque
    #                                     if self.grid.is_free(neighbor[0], neighbor[1]): # On entre ici si l'agent à qui on a fait une demande s'est déplacé
    #                                         print(f"L'{agent_voisin} a bien voulu se déplacer, je peux bouger vers la case {neighbor}")
    #                                         arret = False
    #                                         dx=neighbor[0]-self.position[0]
    #                                         dy=neighbor[1]-self.position[1]
    #                                         self.move(dx, dy)
    #                                         break
    #                             if arret:
    #                                 # Aucune des cases voisines n'est exploitable, on ne peut pas se déplacer...        
    #                                 print("Aucune des cases voisines n'est exploitable, on ne peut pas se déplacer...")
    #                                 print("Jeux infinissable !\n Arret du jeux imminent !")
    #                                 self.grid.stop()
    #                             else :
    #                                 message.response(False) 
    #                         else:
    #                             message.response(False)
    #                     # si l'agent est déjà à son goal => ne pas bouger // sinon bouger 
                    
    #                 # réponse si tu es blocké
    #                 """
    #                 if (message.message_type == TypeMessage.PASGENTIL): # recalcule du chemin
    #                     print(self.name + ": Sorry :)")

    #                 if (message.message_type == TypeMessage.GENTIL): # relance resolve_agent
    #                     print(self.name + ": ")
    #                 """
    #             except queue.Empty:
    #                 break

    #         # print(f"{self.name} : boucle update")
            
    #         time.sleep(1)# évite de surcharger le cpu !
    #         if (self.stopped):
    #             break
    
    def set_event(self, neighbor, value):
        print(f"{self.name} : value retourné {value}")
        self.event.set()


    def callback_blocked(self, sender, value):
        print(f"{self.name} : value retourné {value}")
        self.resolve_agent()
        if self.is_goal():
            # On remet les agents déplacés dans leurs objectifs :windowjump:
            for agent in self.grid.agents:
                if agent.isBlock:
                    agent.isBlock = False
                if agent.steppedAway:
                    print(f"{agent.name} est remis sur le droit chemin après avoir été déplacé")
                    agent.resolve_agent()
            time.sleep(1)
            self.event.set()
    
    def resolve_agent(self):
        print("\nResolve agent", self.name)
        best_path=self.best_path(self.grid)
        print("-> Son meilleur chemin :", best_path)
        if best_path == -1:
            print("La position finale n'est pas accessible, arrêt prématuré du jeu")
            self.grid.stop()
        else:
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
            
            
                

