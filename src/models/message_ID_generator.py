
class MessageIDGenerator:
    def __init__(self):
        self.id_for_message_id: int = 0 

    def get_next_id(self) -> int:
        if  self.id_for_message_id == 99999999999:
             self.id_for_message_id = 0
        self.id_for_message_id += 1
        return self.id_for_message_id