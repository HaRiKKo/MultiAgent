from enum import Enum


class Message:
    def __init__(self, message_type, callback):
        self.message_type = message_type
        self.callback = callback
        self.receiver = None
        self.sender = None
    
    def response(self, value):
        if (self.callback is not None):
            self.callback(self.receiver, value)

class TypeMessage(Enum):
    BLOCKED = 1