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
from octobot_commons.channels_name import OctoBotTradingChannelsName
from octobot_evaluators.evaluator import AbstractEvaluator


class TAEvaluator(AbstractEvaluator):
    __metaclass__ = AbstractEvaluator

    def __init__(self):
        super().__init__()
        self.time_frame = None
        self.short_term_averages = [7, 5, 4, 3, 2, 1]  # TODO remove
        self.long_term_averages = [40, 30, 20, 15, 10]  # TODO remove

    def get_symbol_candles(self, exchange_name: str, exchange_id: str, symbol: str, time_frame):
        try:
            from octobot_trading.api.symbol_data import get_symbol_candles_manager
            return get_symbol_candles_manager(self.get_exchange_symbol_data(exchange_name, exchange_id, symbol),
                                              time_frame)
        except ImportError:
            self.logger.error(f"Can't get OHLCV: requires OctoBot-Trading package installed")

    async def start(self, bot_id: str) -> bool:
        """
        Default TA start: to be overwritten
        Subscribe to OHLCV notification from self.symbols and self.time_frames
        :return: success of the evaluator's start
        """
        await super().start(bot_id)
        try:
            from octobot_trading.channels.exchange_channel import get_chan as get_trading_chan
            from octobot_trading.api.exchange import get_exchange_id_from_matrix_id
            exchange_id = get_exchange_id_from_matrix_id(self.exchange_name, self.matrix_id)
            await get_trading_chan(OctoBotTradingChannelsName.OHLCV_CHANNEL.value, exchange_id).new_consumer(
                self.ohlcv_callback)  # TODO filter
            return True
        except ImportError:
            self.logger.error("Can't connect to OHLCV trading channel")
        return False

    async def ohlcv_callback(self, exchange: str, exchange_id: str, cryptocurrency: str, symbol: str,
                             time_frame: str, candle: dict):
        # To be used to trigger an evaluation
        pass
