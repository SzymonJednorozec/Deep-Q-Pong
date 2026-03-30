from dataclasses import dataclass, field
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

@dataclass
class PlotInfo:
    scores: list = field(default_factory=list)
    mean_scores: list = field(default_factory=list)
    total_score: int = 0




class GameState(Enum):
    PLAY = auto()
    TRAIN = auto()
    MENU = auto()
    PAUSE = auto()

class PlayerType(Enum):
    HUMAN = auto()
    AI = auto()
    NONE = auto()

class AppConfig:
    def __init__(self):
        self.instances = 1
        self.mode = GameState.TRAIN # TRAIN / PLAY
        self.save_path = "model/model.pth"
        self.load_path = "model/model.pth"
        self.save_onnx_path = "model/model.onnx"
        self.left_player = PlayerType.NONE
        self.right_player = PlayerType.AI
        self.e_threshold = 200
        self.e_increase = 0.2
        self.e_decay = 0.995
        self.e_min = 0.1
        self.e = 1

    def load_from_json(self, file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
            self.instances = data.get("instances", self.instances)
            self.save_path = data.get("model_save_path", self.save_path)
            self.load_path = data.get("model_load_path", self.load_path)
            self.save_onnx_path = data.get("model_save_onnx_path", self.save_onnx_path)
            self.e_threshold = data.get("epsilon_increase_threshold", self.e_threshold)
            self.e_increase = data.get("epsilon_increase", self.e_increase)
            self.e_decay = data.get("epsilon_decay", self.e_decay)
            self.e_min = data.get("minimum_epsilon", self.e_min)
            self.e = data.get("epsilon", self.e)


            type_map = {
                "HUMAN": PlayerType.HUMAN,
                "AI": PlayerType.AI,
                "NONE": PlayerType.NONE,
                
                "PLAY": GameState.PLAY,
                "TRAIN": GameState.TRAIN,
                "MENU": GameState.MENU,
                "PAUSE": GameState.PAUSE,
            }
            self.mode = type_map.get(data.get("mode"),self.mode)
            self.left_player = type_map.get(data.get("left_player"), self.left_player)
            self.right_player = type_map.get(data.get("right_player"), self.right_player)