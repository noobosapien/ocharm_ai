from modules.component import Component

class ClassifiedMSG(Component):
    def __init__(self, user_id:str=None, content:str=None, classification:int=None):
        super().__init__()
        self.user_id = user_id
        self.content = content
        self.classification = classification
        
    def set_user_id(self, user_id: str):
        self.user_id = user_id
    
    def set_content(self, content: str):
        self.content = content
    
    def set_classification(self, classification):
        self.classification = classification
    
    def serialize(self):
        to_ret = {}
        
        to_ret['user_id'] = self.user_id
        to_ret['content'] = self.content
        to_ret['classification'] = self.classification
        
        return to_ret
