#  Drakkar-Software OctoBot-Evaluators
#  Copyright (c) Drakkar-Software, All rights reserved.
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3.0 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library.

import os

from octobot_commons.config import load_config

from octobot_evaluators.constants import CONFIG_EVALUATOR_REALTIME
from octobot_evaluators.evaluator.abstract_evaluator import AbstractEvaluator


class RealTimeEvaluator(AbstractEvaluator):
    def __init__(self):
        super().__init__()
        self.load_config()

    @classmethod
    def get_config_tentacle_type(cls) -> str:
        return CONFIG_EVALUATOR_REALTIME

    def load_config(self):
        config_file = self.get_config_file_name()
        if os.path.isfile(config_file):
            self.set_default_config()
            self.specific_config = {**self.specific_config, **load_config(config_file)}
        else:
            self.set_default_config()


