import os
import chess
import numpy as np


def _project_dir():
    d = os.path.dirname
    return d(d(d(os.path.abspath(__file__))))


def _data_dir():
    return os.path.join(_project_dir(), "data")


def _tablebase_dir():
    return os.path.join(_project_dir(), "tablebases")


def create_uci_labels():
    labels = {}
    for f in range(8):
        for r in range(8):
            for v in range(0, 7):
                f_new = f + (v + 1)
                _add_move(labels, v, f, r, f_new, r)
            for v in range(7, 14):
                f_new = f - (v - 6)
                _add_move(labels, v, f, r, f_new, r)
            for v in range(14, 21):
                r_new = r + (v - 13)
                _add_move(labels, v, f, r, f, r_new)
            for v in range(21, 28):
                r_new = r - (v - 20)
                _add_move(labels, v, f, r, f, r_new)
            for v in range(28, 35):
                f_new = f + (v - 27)
                r_new = r + (v - 27)
                _add_move(labels, v, f, r, f_new, r_new)
            for v in range(35, 42):
                f_new = f - (v - 34)
                r_new = r - (v - 34)
                _add_move(labels, v, f, r, f_new, r_new)
            for v in range(42, 49):
                f_new = f + (v - 41)
                r_new = r - (v - 41)
                _add_move(labels, v, f, r, f_new, r_new)
            for v in range(49, 56):
                f_new = f - (v - 48)
                r_new = r + (v - 48)
                _add_move(labels, v, f, r, f_new, r_new)
            _add_move(labels, 56, f, r, f + 2, r + 1)
            _add_move(labels, 57, f, r, f - 2, r - 1)
            _add_move(labels, 58, f, r, f + 1, r + 2)
            _add_move(labels, 59, f, r, f - 1, r - 2)
            _add_move(labels, 60, f, r, f + 2, r - 1)
            _add_move(labels, 61, f, r, f - 2, r + 1)
            _add_move(labels, 62, f, r, f + 1, r - 2)
            _add_move(labels, 63, f, r, f - 1, r + 2)
            if r == 6:
                _add_move(labels, 64, f, r, f, r + 1, 4)
                _add_move(labels, 65, f, r, f, r + 1, 3)
                _add_move(labels, 66, f, r, f, r + 1, 2)
                _add_move(labels, 67, f, r, f + 1, r + 1, 4)
                _add_move(labels, 68, f, r, f + 1, r + 1, 3)
                _add_move(labels, 69, f, r, f + 1, r + 1, 2)
                _add_move(labels, 70, f, r, f - 1, r + 1, 4)
                _add_move(labels, 71, f, r, f - 1, r + 1, 3)
                _add_move(labels, 72, f, r, f - 1, r + 1, 2)
            elif r == 1:
                _add_move(labels, 64, f, r, f, r - 1, 4)
                _add_move(labels, 65, f, r, f, r - 1, 3)
                _add_move(labels, 66, f, r, f, r - 1, 2)
                _add_move(labels, 67, f, r, f - 1, r - 1, 4)
                _add_move(labels, 68, f, r, f - 1, r - 1, 3)
                _add_move(labels, 69, f, r, f - 1, r - 1, 2)
                _add_move(labels, 70, f, r, f + 1, r - 1, 4)
                _add_move(labels, 71, f, r, f + 1, r - 1, 3)
                _add_move(labels, 72, f, r, f + 1, r - 1, 2)
    return labels


def _add_move(labels, v, f, r, f_new, r_new, promotion=None):
    if f_new in range(0, 8) and r_new in range(0, 8):
        labels[chess.Move(r * 8 + f, r_new * 8 + f_new, promotion)] = v * 64 + r * 8 + f
        if promotion is None and (r == 6 and r_new == 7 and abs(f_new - f) <= 1 or r == 1 and r_new == 0 and abs(f_new - f) <= 1):
            labels[chess.Move(r * 8 + f, r_new * 8 + f_new, 5)] = v * 64 + r * 8 + f  # add a default queen promotion.


class Config:
    def __init__(self, config_type="normal"):
        self.opts = Options()
        self.resource = ResourceConfig()

        if config_type == "mini":
            import chess_zero.configs.mini as c
        elif config_type == "small":
            import chess_zero.configs.small as c
        elif config_type == "normal":
            import chess_zero.configs.normal as c
        else:
            raise RuntimeError(f"unknown config_type: {config_type}")
        self.play_data = c.PlayDataConfig()
        self.play = c.PlayConfig()
        self.eval = c.EvaluateConfig()
        self.human = c.PlayWithHumanConfig()
        self.trainer = c.TrainerConfig()
        self.model = c.ModelConfig()

        self.labels = create_uci_labels()
        self.n_labels = 4672  # 73x8x8. note: this is NOT (i.e. it's more than) the length of self.labels! only actually possible moves are entered as keys in self.labels.

    @staticmethod
    def flip_policy(leaf_p):
        new_p = np.zeros(4672)
        for f in range(8):
            for r in range(8):
                for v in range(73):
                    if v in range(56):
                        block, position = v // 14, v % 14
                        new_position = position - 7 if position >= 7 else position + 7
                        new_v = block * 14 + new_position
                    elif v in range(56, 64):
                        new_v = v + 1 if v % 2 == 0 else v - 1
                    else:
                        new_v = v
                    new_p[v * 64 + r * 8 + f] = leaf_p[new_v * 64 + (7 - r) * 8 + (7 - f)]
        return list(new_p)

class Options:
    new = False


class ResourceConfig:
    def __init__(self):
        self.project_dir = os.environ.get("PROJECT_DIR", _project_dir())
        self.data_dir = os.environ.get("DATA_DIR", _data_dir())
        self.model_dir = os.environ.get("MODEL_DIR", os.path.join(self.data_dir, "model"))
        self.tablebase_dir = os.environ.get("TABLEBASE_DIR", _tablebase_dir())

        self.model_dirname_tmpl = "model_%s"
        self.model_config_filename = "model_config.json"
        self.model_weight_filename = "model_weight.h5"
        self.old_model_dir = os.path.join(self.model_dir, "old_models")
        self.keep_old_models = True

        self.play_data_dir = os.path.join(self.data_dir, "play_data")
        self.play_data_filename_tmpl = "play_%s.json"

        self.log_dir = os.path.join(self.project_dir, "logs")
        self.main_log_path = os.path.join(self.log_dir, "main.log")

    def create_directories(self):
        dirs = [self.project_dir, self.data_dir, self.model_dir, self.play_data_dir, self.log_dir, self.old_model_dir, self.tablebase_dir]
        for d in dirs:
            if not os.path.exists(d):
                os.makedirs(d)
