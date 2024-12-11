
class MessageIDGenerator:
    def __init__(self):
        self.id_for_message_id = 0 

    def get_next_id(self):
        self.id_for_message_id += 1
        return self.id_for_message_id
    
