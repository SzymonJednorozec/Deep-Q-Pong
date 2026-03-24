from dataclasses import dataclass
from enum import Enum, auto
import json


@dataclass
class GameResult:
    reward_l: float
    reward_r: float
    done: bool
    score_l: int
    score_r: int
    points_l: int
    points_r: int


class PlayerType(Enum):
    HUMAN = auto()
    AI = auto()
    NONE = auto()

class AppConfig:
    def __init__(self):
        self.instances = 1
        self.mode = "TRAIN" # TRAIN / PLAY
        self.save_path = "model/model.pth"
        self.load_path = "model/model.pth"
        self.left_player = PlayerType.NONE
        self.right_player = PlayerType.AI

    def load_from_json(self, file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
            self.instances = data.get("instances", self.instances)
            self.mode = data.get("mode", self.mode)
            self.save_path = data.get("model_save_path", self.save_path)
            self.load_path = data.get("model_load_path", self.load_path)
            
            type_map = {
                "HUMAN": PlayerType.HUMAN,
                "AI": PlayerType.AI,
                "NONE": PlayerType.NONE
            }
            self.left_player = type_map.get(data.get("left_player"), self.left_player)
            self.right_player = type_map.get(data.get("right_player"), self.right_player)