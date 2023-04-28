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
        paths = grid.find_shortest_paths(self.position, self.goal, []) # Recupère la liste des chemins les plus courts
        # print("Les chemin possible\n   ",paths)
        if len(paths)<=0: # Aucun chemin
            print(f"{self.name} ne peut pas se déplacer de {self.position} vers {self.goal}.")
            return -1 
        else: # On calcule le nombre d'agent par chemin et on trie les chemins pour récupérer le chemin avec le moins d'agent sur leur position finale
            dict_paths = {}
            for i in range(len(paths)): #calcule du nombre d'agent
                dict_paths[i] = grid.compute_agent_in_goal(paths[i])
            sorted_dict = sorted(dict_paths.items(), key=lambda item: item[1])
            shortest_path = paths[sorted_dict[0][0]]
            shortest_path.pop(0) # On enlève le premier element du chemin car c'est la position actuelle
            return shortest_path
                    
    def move(self, dx, dy):
        new_x = self.position[0] + dx
        new_y = self.position[1] + dy
        
        if self.grid.is_valid(new_x, new_y):
            if self.grid.is_free(new_x, new_y):
                print(f"{self.name} : {self.position} -> {(new_x, new_y)}")
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
        # print("Un message a été mis dans la queue de l'agent ", self.name)
        self.ma_queue.put(message)

    def stop(self):
        self.stopped = True

    def run(self):
        while True:
            while True: 
                try:
                    message = self.ma_queue.get(False)  # La thread attend de recevoir un message
                    
                    if (message.message_type == TypeMessage.BLOCKED): # si tu es un agent qui block 
                        
                        print(f"{self.name} : message reçu de {message.sender.name} qui est bloqué")
                        # Cas où on demande à un agent qui s'est éloigner de sa position finale de se déplacer à nouveau 
                        if self.steppedAway:
                            # Si on lui demande de se déplacer vers sa position finale, il le fait
                            if self.grid.is_free(self.goal[0], self.goal[1]):
                                dx=self.goal[0]-self.position[0]
                                dy=self.goal[1]-self.position[1]
                                self.move(dx, dy)
                                print(f"{self.name} : A de nouveau atteint la position objectif en {self.position}")
                                self.steppedAway=False
                                message.response(False)
                            # Sinon, il ne se déplace pas
                            else :
                                print(f"{self.name} : Ne peut pas se déplacer, s'est déjà éloigné de son objectif")
                                message.response(True)

                        # Vérifier s'il est possible de se décaler d'une case
                        # Si une case est libre -> se déplace
                        # Si non -> demande à un voisin de se déplacer
                        else:
                            print(f"{self.name} : peut se déplacer")
                            neighbors = self.get_neighbors()
                            if message.sender.goal in neighbors:
                                neighbors.remove(message.sender.goal)
                            # print(f"{self.name} : mes voisins : {neighbors} ")
                            libre = False #  Vérifie si une case est libre autour de l'agent
                            for neighbor in neighbors:
                                if self.grid.is_free(neighbor[0], neighbor[1]):
                                    libre = True # A trouvé une case voisine libre
                                    print(f"{self.name} : a trouvé une case voisine libre en ", neighbor)
                                    if self.is_goal():
                                        print(f"{self.name} est à sa position objectif mais bouge d'une case.")
                                        self.steppedAway=True
                                    dx=neighbor[0]-self.position[0]
                                    dy=neighbor[1]-self.position[1]
                                    self.move(dx, dy)
                                    break

                            # Dans le cas où les cases voisines de l'agent sont toutes occupées    
                            if not libre:
                                arret = True # Booléen qui permet de savoir si on doit arrêter le jeu car il n'a pas de solution
                                print(f"Toutes les cases voisines de {self.name} sont occupées...")
                                # Envoie un message à un voisin pour qu'il se déplace
                                agents_neighbors = [] # Liste des agents voisins à partir des cases voisines
                                for position_agent in neighbors:
                                    agent = self.grid.get_agent(position_agent[0], position_agent[1])
                                    if agent != message.sender:
                                        agents_neighbors.append(agent)
                                neighbors_is_goal = [] # Liste avec True et False correspondant aux voisins qui sont à leur place finale ou non
                                for agent in agents_neighbors:
                                    neighbors_is_goal.append(agent.is_goal())

                                if False in neighbors_is_goal: # Il y a un voisin qui n'est pas à sa position finale
                                    # On demande à ce voisin de se pousser 
                                    neighbor_to_move = agents_neighbors[neighbors_is_goal.index(False)] # UN Agent qui n'est pas encore à sa position finale
                                    position_desiree = neighbor_to_move.position
                                    print(f"{self.name} : Demande à {neighbor_to_move.name} de se déplacer car il n'est pas à son objectif")
                                    self.send_message(Message(TypeMessage.BLOCKED, self.set_event), neighbor_to_move)
                                    self.event.wait()
                                    if self.grid.is_free(position_desiree[0], position_desiree[1]): # On entre ici si l'agent à qui on a fait une demande s'est déplacé
                                        print(f"{self.name} : {neighbor_to_move.name} a bien voulu se déplacer, je peux bouger vers la case {position_desiree}")
                                        arret = False # On n'arrête pas le jeu
                                        dx=position_desiree[0]-self.position[0]
                                        dy=position_desiree[1]-self.position[1]
                                        self.move(dx, dy)
                                    #     message.response(False)
                                    # else:
                                    #     message.response(True)
                                    # break
                                else : # Tous les voisins sont à leur position finale
                                    # On choisi de déplacer celui qui a un numéro plus grand = GOAL le + en bas à droite)
                                    positions_agents = [agent.position[1] for agent in agents_neighbors]
                                    index = positions_agents.index(max(positions_agents)) # Index de l'agent ayant la position finale la plus en bas à droite
                                    neighbor_to_move = agents_neighbors[index] # Agent correspondant à cet index
                                    position_desiree = neighbor_to_move.position # Position correspondant à l'agent à déplacer
                                    print(f"{self.name} : Demande à {neighbor_to_move.name} de se déplacer même s'il est à son objectif")
                                    self.send_message(Message(TypeMessage.BLOCKED, self.set_event), neighbor_to_move)
                                    self.event.wait()
                                    if self.grid.is_free(position_desiree[0], position_desiree[1]): # On entre ici si l'agent à qui on a fait une demande s'est déplacé
                                        print(f"{self.name} : L'{neighbor_to_move.name} a bien voulu se déplacer, je peux bouger vers la case {position_desiree}")
                                        arret = False
                                        dx=position_desiree[0]-self.position[0]
                                        dy=position_desiree[1]-self.position[1]
                                        self.move(dx, dy)
                                    #     message.response(False)
                                    # else:
                                    #     message.response(True)
                                if arret:
                                    # Aucune des cases voisines n'est exploitable, on ne peut pas se déplacer...        
                                    print("Aucune des cases voisines n'est exploitable, on ne peut pas se déplacer...")
                                    print("Jeux infinissable !\n Arret du jeux imminent !")
                                    self.grid.stop()
                                else :
                                    message.response(False) 
                            else:
                                message.response(False)
                except queue.Empty:
                    break

            # print(f"{self.name} : boucle update")
            
            time.sleep(1)# évite de surcharger le cpu !
            if (self.stopped):
                break

    def set_event(self, neighbor, value):
        # print(f"{self.name} : value retourné {value}")
        print("Set event")
        self.event.set()


    def callback_blocked(self, sender, value):
        # print(f"{self.name} : value retourné {value}")
        self.resolve_agent()
        if self.is_goal():
            # On remet les agents déplacés dans leurs objectifs :windowjump:
            for agent in self.grid.agents:
                if agent.steppedAway:
                    print(f"{agent.name} est remis sur le droit chemin après avoir été déplacé")
                    agent.resolve_agent()
            self.event.set()
    
    def resolve_agent(self):
        print("\nResolve ", self.name)
        best_path=self.best_path(self.grid)
        print("Son meilleur chemin :", best_path)
        if best_path == -1:
            print("La position finale n'est pas accessible, arrêt prématuré du jeu")
            self.grid.stop()
        else:
            for case in best_path:
                dx = case[0]-self.position[0]
                dy = case[1]-self.position[1]
                ret=self.move(dx, dy)
                if ret == -1:
                    # print("Sortie de resolve agent par erreur -1")
                    break
                if ret == -2:
                    print("Erreur mouvement impossible !!!")
                    break
            
            
                

