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
from octobot_evaluators.evaluator.abstract_evaluator import AbstractEvaluator
from octobot_tentacles_manager.api.configurator import get_tentacle_config


class RealTimeEvaluator(AbstractEvaluator):
    __metaclass__ = AbstractEvaluator

    def __init__(self):
        super().__init__()
        self.load_config()

    def load_config(self):
        self.set_default_config()
        self.specific_config = {**self.specific_config, **get_tentacle_config(self.__class__)}

    def get_symbol_candles(self, exchange_name: str, exchange_id: str, symbol: str, time_frame):
        try:
            from octobot_trading.api.symbol_data import get_symbol_candles_manager
            return get_symbol_candles_manager(self.get_exchange_symbol_data(exchange_name, exchange_id, symbol),
                                              time_frame)
        except ImportError:
            self.logger.error(f"Can't get candles manager: requires OctoBot-Trading package installed")

