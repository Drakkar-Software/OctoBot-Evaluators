# cython: language_level=3
#  Drakkar-Software OctoBot-Matrixs
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
from asyncio import Queue

from octobot_channels.consumer import Consumer
from octobot_channels.producer import Producer
from octobot_commons.logging.logging_util import get_logger

from octobot_channels.channels.channel import Channel, Channels

from octobot_channels import CONSUMER_CALLBACK_TYPE, CHANNEL_WILDCARD
from octobot_channels.channels.channel_instances import ChannelInstances

from octobot_evaluators.data import EvaluatorMatrix

MATRIX_CHANNELS = "MatrixChannels"


class MatrixChannel(Channel):
    FILTER_SIZE = 1
    PRODUCER_CLASS = None

    def __init__(self):
        super().__init__()
        self.logger = get_logger(f"{self.__class__.__name__}")

    def new_consumer(self,
                     callback: CONSUMER_CALLBACK_TYPE,
                     size=0,
                     symbol=CHANNEL_WILDCARD,
                     time_frame=None,
                     filter_size=False):
        self._add_new_consumer_and_run(MatrixChannelConsumer(callback, size=size, filter_size=filter_size),
                                       symbol=symbol,
                                       time_frame=time_frame)

    def _add_new_consumer_and_run(self, consumer, symbol=CHANNEL_WILDCARD, time_frame=None):
        if symbol:
            # create dict and list if required
            self._init_consumer_if_necessary(self.consumers, symbol, is_dict=True)

            self._init_consumer_if_necessary(self.consumers[symbol], time_frame)
            self.consumers[symbol][time_frame].append(consumer)
        else:
            self.consumers[CHANNEL_WILDCARD] = [consumer]
        consumer.run()
        self.logger.info(f"Consumer started for symbol {symbol} on {time_frame}")

    @staticmethod
    def _init_consumer_if_necessary(consumer_list: dict, key: str, is_dict=False) -> None:
        if key not in consumer_list:
            consumer_list[key] = [] if not is_dict else {}


class MatrixChannelConsumer(Consumer):
    def __init__(self, callback: CONSUMER_CALLBACK_TYPE, size=0, filter_size=0):  # TODO to be removed
        super().__init__(callback)
        self.logger = get_logger(f"{self.__class__.__name__}")
        self.filter_size = filter_size
        self.should_stop = False
        self.queue = Queue(maxsize=size)
        self.callback = callback

    async def consume(self):
        while not self.should_stop:
            try:
                temp = (await self.queue.get())  # TODO
                get_logger(f"CONSUMED : {temp}")
                await self.callback(**temp)
            except Exception as e:
                self.logger.exception(f"Exception when calling callback : {e}")


class MatrixChannelProducer(Producer):
    async def send_eval_note(self, evaluator_name, evaluator_type, eval_note,
                             exchange_name=None, symbol=None, time_frame=None):
        EvaluatorMatrix.instance().set_eval(evaluator_name=evaluator_name,
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


class MatrixChannels(Channels):
    @staticmethod
    def set_chan(chan: MatrixChannel, name: str) -> None:
        chan_name = chan.get_name() if name else name

        try:
            matrix_chan = ChannelInstances.instance().channels[MATRIX_CHANNELS]
        except KeyError:
            ChannelInstances.instance().channels[MATRIX_CHANNELS] = {}
            matrix_chan = ChannelInstances.instance().channels[MATRIX_CHANNELS]

        if chan_name not in matrix_chan:
            matrix_chan[chan_name] = chan
        else:
            raise ValueError(f"Channel {chan_name} already exists.")

    @staticmethod
    def get_chan(chan_name: str) -> MatrixChannel:
        try:
            return ChannelInstances.instance().channels[MATRIX_CHANNELS][chan_name]
        except KeyError:
            get_logger(__class__.__name__).error(f"Channel {chan_name} not found in {MATRIX_CHANNELS}")
            return None
