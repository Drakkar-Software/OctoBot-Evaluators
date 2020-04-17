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
from octobot_commons.constants import CONFIG_WILDCARD
from octobot_commons.time_frame_manager import parse_time_frames
from octobot_evaluators.channels.evaluator_channel import get_chan
from octobot_evaluators.constants import CONFIG_FORCED_EVALUATOR, MATRIX_CHANNEL, \
    STRATEGIES_REQUIRED_TIME_FRAME, CONFIG_FORCED_TIME_FRAME, STRATEGIES_REQUIRED_EVALUATORS, TENTACLE_DEFAULT_CONFIG
from octobot_evaluators.evaluator import AbstractEvaluator
from octobot_tentacles_manager.api.configurator import get_tentacle_config


class StrategyEvaluator(AbstractEvaluator):
    __metaclass__ = AbstractEvaluator

    def __init__(self):
        super().__init__()
        self.consumer_instance = None

    async def start(self, bot_id: str) -> bool:
        """
        Default Strategy start: to be overwritten
        Subscribe to Matrix notification from self.symbols and self.time_frames
        :return: success of the evaluator's start
        """
        await super().start(bot_id)
        self.consumer_instance = await get_chan(MATRIX_CHANNEL, self.matrix_id).new_consumer(self.matrix_callback)
        return True

    async def stop(self) -> None:
        if self.consumer_instance:
            await get_chan(MATRIX_CHANNEL, self.matrix_id).remove_consumer(self.consumer_instance)

    async def matrix_callback(self,
                              matrix_id,
                              evaluator_name,
                              evaluator_type,
                              eval_note,
                              eval_note_type,
                              exchange_name,
                              cryptocurrency,
                              symbol,
                              time_frame):
        # To be used to trigger an evaluation
        # Do not forget to check if evaluator_name is self.name
        pass

    @classmethod
    def get_required_time_frames(cls, config: dict):
        if CONFIG_FORCED_TIME_FRAME in config:
            return parse_time_frames(config[CONFIG_FORCED_TIME_FRAME])
        strategy_config: dict = get_tentacle_config(cls)
        if STRATEGIES_REQUIRED_TIME_FRAME in strategy_config:
            return parse_time_frames(strategy_config[STRATEGIES_REQUIRED_TIME_FRAME])
        else:
            raise Exception(f"'{STRATEGIES_REQUIRED_TIME_FRAME}' is missing in configuration file")

    @classmethod
    def get_required_evaluators(cls, config: dict, strategy_config: dict = None):
        if CONFIG_FORCED_EVALUATOR in config:
            return config[CONFIG_FORCED_EVALUATOR]
        strategy_config: dict = strategy_config or get_tentacle_config(cls)
        if STRATEGIES_REQUIRED_EVALUATORS in strategy_config:
            return strategy_config[STRATEGIES_REQUIRED_EVALUATORS]
        else:
            raise Exception(f"'{STRATEGIES_REQUIRED_EVALUATORS}' is missing in configuration file")

    @classmethod
    def get_default_evaluators(cls, config: dict):
        strategy_config: dict = get_tentacle_config(cls)
        if TENTACLE_DEFAULT_CONFIG in strategy_config:
            return strategy_config[TENTACLE_DEFAULT_CONFIG]
        else:
            required_evaluators = cls.get_required_evaluators(config, strategy_config)
            if required_evaluators == CONFIG_WILDCARD:
                return []
            else:
                return required_evaluators
