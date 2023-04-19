import threading
import time
import queue
from message import Message, TypeMessage
import random


class Agent(threading.Thread):
    def __init__(self, name, x, y, goal, grid):
        super().__init__()
        self.name = name
        self.x = x
        self.y = y
        self.goal = goal
        self.grid = grid
        self.ma_queue = queue.Queue()
        self.stopped = False
        self.start()

    # give the best path (shortest + less agent)
    def best_path(self, grid):
        paths = grid.find_shortest_paths((self.x, self.y), self.goal, [])
        if len(paths)<=0:
            print(f"L'agent n°{self.name} ne peut pas se déplacer de {(self.x, self.y)} vers {self.goal}.")
        else:
            shortest_path = paths[0]
            shortest_path.pop(0)
        return shortest_path[0]
                
            
    #def move_to_goal(self, position, goal):
    
    def move(self, dx, dy):
        new_x = self.x + dx
        new_y = self.y + dy
        if self.grid.is_valid(new_x, new_y):
            if self.grid.is_free(new_x, new_y):
                self.x = new_x
                self.y = new_y
            else:
                other_agent = self.grid.get_agent(new_x, new_y)
                print(f"{self.name} : Agent bloqué par {other_agent.name}")
                self.send_message(Message(TypeMessage.BLOCKED, self.callback_blocked), other_agent)
        else:
            print(f"{self.name} : Mouvement impossible en ({new_x}, {new_y})")
    
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
                    
                    if (message.message_type == TypeMessage.BLOCKED):
                        
                        print(f"{self.name} : L'agent {message.sender.name} est bloqué, je vais lui répondre")
                        message.response(bool(random.getrandbits(1)))# vrai code
                        
                    if (message.message_type == TypeMessage.PASGENTIL):
                        print(self.name + ": Sorry :)")
                except queue.Empty:
                    break

            print(f"{self.name} : boucle update")
            
            time.sleep(1)# évite de surcharger le cpu !
            if (self.stopped):
                break

    def callback_blocked(self, sender, value):
        print(f"{self.name} : value retourné {value}")
        if (value): # A revoir !!!

            
            print(f"{self.name} : L'agent {sender.name} m'a répondu pas cool, je vais lui dire qu'il est po gentil")
            self.send_message(Message(TypeMessage.PASGENTIL, None), sender)
