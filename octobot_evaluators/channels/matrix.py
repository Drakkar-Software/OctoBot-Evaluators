# cython: language_level=3
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

from octobot_channels import CHANNEL_WILDCARD
from octobot_channels.channels.channel import Channel
from octobot_channels.channels.channel_instances import ChannelInstances
from octobot_channels.consumer import Consumer
from octobot_channels.producer import Producer
from octobot_commons.logging.logging_util import get_logger

from octobot_evaluators.data import EvaluatorMatrix

MATRIX_CHANNELS = "MatrixChannels"


class MatrixChannelConsumer(Consumer):
    async def consume(self):
        while not self.should_stop:
            try:
                await self.callback(**(await self.queue.get()))
            except Exception as e:
                self.logger.exception(f"Exception when calling callback : {e}")


class MatrixChannelProducer(Producer):
    async def send(self,
                   evaluator_name,
                   evaluator_type,
                   eval_note,
                   exchange_name=None,
                   symbol=CHANNEL_WILDCARD,
                   time_frame=None):
        for consumer in self.channel.get_filtered_consumers(symbol=symbol, evaluator_type=evaluator_type):
            await consumer.queue.put({
                "evaluator_name": evaluator_name,
                "evaluator_type": evaluator_type,
                "eval_note": eval_note,
                "exchange_name": exchange_name,
                "symbol": symbol,
                "time_frame": time_frame
            })

    async def send_eval_note(self, evaluator_name, evaluator_type, eval_note,
                             exchange_name=None, symbol=None, time_frame=None):
        EvaluatorMatrix().set_eval(evaluator_name=evaluator_name,
                                   evaluator_type=evaluator_type,
                                   value=eval_note,
                                   exchange_name=exchange_name,
                                   symbol=symbol,
                                   time_frame=time_frame)

        await self.send(evaluator_name=evaluator_name,
                        evaluator_type=evaluator_type,
                        eval_note=eval_note,
                        exchange_name=exchange_name,
                        symbol=symbol,
                        time_frame=time_frame)


class MatrixChannel(Channel):
    FILTER_SIZE = 1
    PRODUCER_CLASS = MatrixChannelProducer
    CONSUMER_CLASS = MatrixChannelConsumer

    SYMBOL_KEY = "symbol"
    EVALUATOR_TYPE_KEY = "evaluator_type"

    def __init__(self):
        super().__init__()
        self.logger = get_logger(f"{self.__class__.__name__}")

    async def new_consumer(self,
                           callback: object,
                           size=0,
                           symbol=CHANNEL_WILDCARD,
                           evaluator_name=CHANNEL_WILDCARD,
                           evaluator_type=CHANNEL_WILDCARD,
                           exchange_name=CHANNEL_WILDCARD,
                           time_frame=None,
                           filter_size=False):
        await self.__add_new_consumer_and_run(MatrixChannelConsumer(callback, size=size, filter_size=filter_size),
                                              symbol=symbol,
                                              evaluator_name=evaluator_name,
                                              evaluator_type=evaluator_type,
                                              exchange_name=exchange_name,
                                              time_frame=time_frame)

    def get_filtered_consumers(self, symbol=CHANNEL_WILDCARD, evaluator_type=CHANNEL_WILDCARD):
        return self.get_consumer_from_filters({
            self.SYMBOL_KEY: symbol,
            self.EVALUATOR_TYPE_KEY: evaluator_type
        })

    async def __add_new_consumer_and_run(self, consumer,
                                         symbol=CHANNEL_WILDCARD,
                                         evaluator_name=CHANNEL_WILDCARD,
                                         evaluator_type=CHANNEL_WILDCARD,
                                         exchange_name=CHANNEL_WILDCARD,
                                         time_frame=None):
        if symbol:
            symbol = CHANNEL_WILDCARD

        consumer_filters: dict = {
            self.SYMBOL_KEY: symbol,
            self.EVALUATOR_TYPE_KEY: evaluator_type
        }

        self.add_new_consumer(consumer, consumer_filters)
        await consumer.run()
        self.logger.debug(f"Consumer started for symbol {symbol}")
