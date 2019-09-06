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
from octobot_channels.channels import get_chan
from octobot_commons.constants import CONFIG_WILDCARD
from octobot_commons.time_frame_manager import TimeFrameManager

from octobot_evaluators.channels import MATRIX_CHANNEL
from octobot_evaluators.constants import CONFIG_EVALUATOR_STRATEGIES, CONFIG_FORCED_EVALUATOR, \
    STRATEGIES_REQUIRED_TIME_FRAME, CONFIG_FORCED_TIME_FRAME, STRATEGIES_REQUIRED_EVALUATORS, TENTACLE_DEFAULT_CONFIG
from octobot_evaluators.evaluator import AbstractEvaluator


class StrategyEvaluator(AbstractEvaluator):
    def __init__(self):
        super().__init__()

    @classmethod
    def get_config_tentacle_type(cls) -> str:
        return CONFIG_EVALUATOR_STRATEGIES

    async def start(self) -> None:
        """
        Default Strategy start: to be overwritten
        Subscribe to Matrix notification from self.symbols and self.time_frames
        :return: None
        """
        await get_chan(MATRIX_CHANNEL).new_consumer(self.matrix_callback)   # TODO filter

    async def matrix_callback(self,
                              evaluator_name,
                              evaluator_type,
                              eval_note,
                              exchange_name,
                              symbol,
                              time_frame):
        # To be used to trigger an evaluation
        pass

    @classmethod
    def get_required_time_frames(cls, config):
        if CONFIG_FORCED_TIME_FRAME in config:
            return TimeFrameManager.parse_time_frames(config[CONFIG_FORCED_TIME_FRAME])
        strategy_config = cls.get_specific_config()
        if STRATEGIES_REQUIRED_TIME_FRAME in strategy_config:
            return TimeFrameManager.parse_time_frames(strategy_config[STRATEGIES_REQUIRED_TIME_FRAME])
        else:
            raise Exception(f"'{STRATEGIES_REQUIRED_TIME_FRAME}' is missing in {cls.get_config_file_name()}")

    @classmethod
    def get_required_evaluators(cls, config, strategy_config=None):
        if CONFIG_FORCED_EVALUATOR in config:
            return config[CONFIG_FORCED_EVALUATOR]
        strategy_config = strategy_config or cls.get_specific_config()
        if STRATEGIES_REQUIRED_EVALUATORS in strategy_config:
            return strategy_config[STRATEGIES_REQUIRED_EVALUATORS]
        else:
            raise Exception(f"'{STRATEGIES_REQUIRED_EVALUATORS}' is missing in {cls.get_config_file_name()}")

    @classmethod
    def get_default_evaluators(cls, config):
        strategy_config = cls.get_specific_config()
        if TENTACLE_DEFAULT_CONFIG in strategy_config:
            return strategy_config[TENTACLE_DEFAULT_CONFIG]
        else:
            required_evaluators = cls.get_required_evaluators(config, strategy_config)
            if required_evaluators == CONFIG_WILDCARD:
                return []
            else:
                return required_evaluators
