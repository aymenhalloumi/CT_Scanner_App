from flask_appbuilder import Model
from sqlalchemy import Column, Integer, String, Text

class Project(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False, unique=True)
    description = Column(Text)
    status = Column(String(50), default='Planned')

    def __repr__(self):
        return self.name 
