from flask_app.models.base_model import BaseModel

class GameModel(BaseModel):
    def __init__(self):
        self.id = 0
        self.away_team = ''
        self.home_team = ''
        self.away_score = 0
        self.home_score = 0
        self.half_length = 0
        self.date = ''