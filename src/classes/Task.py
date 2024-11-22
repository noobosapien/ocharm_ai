from ..modules.component import Component

class Task(Component):
    def __init__(self, 
                 name: str = None, 
                 description:str=None, 
                 severity:int = None, 
                 minute: int=None,
                 hour: int=None,
                 day: int=None,
                 month: int=None,
                 year: int=None):
        self.name: str = name
        self.description:str = description
        self.severity:int = severity
        self.minute:int = minute
        self.hour: int = hour
        self.day: int = day
        self.month: int = month
        self.year: int = year
        self.completed:bool = False
    
    def set_completed(self, completed: bool):
        self.completed = completed
    
    
    def serialize(self):
        to_ret = {}
        
        if self.name:
            to_ret['name'] = self.name
            
        if self.description:
            to_ret['description'] = self.description
        
        if self.severity:
            to_ret['severity'] = self.severity
        
        if self.minute:
            to_ret['minute'] = self.minute
        
        if self.hour:
            to_ret['hour'] = self.hour
        
        if self.day:
            to_ret['day'] = self.day
        
        if self.month:
            to_ret['month'] = self.month
        
        if self.year:
            to_ret['year'] = self.year
        
        return to_ret
        
        