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
from octobot_channels.constants import CHANNEL_WILDCARD
from octobot_commons.channels_name import OctoBotTradingChannelsName
from octobot_commons.constants import START_PENDING_EVAL_NOTE
from octobot_evaluators.constants import TA_RE_EVALUATION_TRIGGER_UPDATED_DATA, RESET_EVALUATION, \
    EVALUATOR_CHANNEL_DATA_TIME_FRAMES, EVALUATOR_CHANNEL_DATA_EXCHANGE_ID, EVALUATOR_CHANNEL_DATA_ACTION
from octobot_evaluators.evaluator import AbstractEvaluator


class TAEvaluator(AbstractEvaluator):
    __metaclass__ = AbstractEvaluator

    def __init__(self):
        super().__init__()
        self.time_frame = None

    async def start(self, bot_id: str) -> bool:
        """
        Default TA start: to be overwritten
        Subscribe to OHLCV notification from self.symbols and self.time_frames
        :return: success of the evaluator's start
        """
        await super().start(bot_id)
        try:
            from octobot_trading.channels.exchange_channel import get_chan as get_trading_chan
            from octobot_trading.api.exchange import get_exchange_id_from_matrix_id, \
                get_exchange_time_frames_without_real_time
            exchange_id = get_exchange_id_from_matrix_id(self.exchange_name, self.matrix_id)
            time_frame_filter = [tf.value
                                 for tf in get_exchange_time_frames_without_real_time(self.exchange_name, exchange_id)]
            if len(time_frame_filter) == 1:
                time_frame_filter = time_frame_filter[0]
            await get_trading_chan(OctoBotTradingChannelsName.OHLCV_CHANNEL.value, exchange_id).new_consumer(
                self.evaluator_ohlcv_callback,
                cryptocurrency=self.cryptocurrency if self.cryptocurrency else CHANNEL_WILDCARD,
                symbol=self.symbol if self.symbol else CHANNEL_WILDCARD,
                time_frame=self.time_frame.value if self.time_frame else time_frame_filter,
                priority_level=self.priority_level,
            )
            return True
        except ImportError:
            self.logger.error("Can't connect to OHLCV trading channel")
        return False

    async def reset_evaluation(self, cryptocurrency, symbol, time_frame):
        self.eval_note = START_PENDING_EVAL_NOTE
        await self.evaluation_completed(cryptocurrency, symbol, time_frame, eval_time=0, notify=False)

    async def ohlcv_callback(self, exchange: str, exchange_id: str,
                             cryptocurrency: str, symbol: str, time_frame, candle, inc_in_construction_data):
        # To be used to trigger an evaluation when a new candle in closed or a re-evaluation is required
        pass

    async def evaluator_ohlcv_callback(self, exchange: str, exchange_id: str, cryptocurrency: str, symbol: str,
                                       time_frame: str, candle: dict):
        await self.ohlcv_callback(exchange, exchange_id, cryptocurrency, symbol, time_frame, candle, False)

    async def evaluators_callback(self,
                                  matrix_id,
                                  evaluator_name,
                                  evaluator_type,
                                  exchange_name,
                                  cryptocurrency,
                                  symbol,
                                  time_frame,
                                  data):
        # Used to communicate between evaluators
        if data[EVALUATOR_CHANNEL_DATA_ACTION] == TA_RE_EVALUATION_TRIGGER_UPDATED_DATA:
            try:
                from octobot_trading.api.symbol_data import get_symbol_historical_candles, get_candle_as_list
                exchange_id = data[EVALUATOR_CHANNEL_DATA_EXCHANGE_ID]
                symbol_data = self.get_exchange_symbol_data(exchange_name, exchange_id, symbol)
                for time_frame in data[EVALUATOR_CHANNEL_DATA_TIME_FRAMES]:
                    last_full_candle = get_candle_as_list(get_symbol_historical_candles(symbol_data, time_frame,
                                                                                        limit=1))
                    await self.ohlcv_callback(exchange_name, exchange_id, cryptocurrency,
                                              symbol, time_frame.value, last_full_candle, True)
            except ImportError:
                self.logger.error(f"Can't get OHLCV: requires OctoBot-Trading package installed")
        elif data[EVALUATOR_CHANNEL_DATA_ACTION] == RESET_EVALUATION:
            for time_frame in data[EVALUATOR_CHANNEL_DATA_TIME_FRAMES]:
                await self.reset_evaluation(cryptocurrency, symbol, time_frame.value)
