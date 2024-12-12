
class MessageIDGenerator:
    def __init__(self):
        self.create_id_for_message_id = 0 

    def get_next_id(self):
        self.create_id_for_message_id += 1
        return self.create_id_for_message_id
    
