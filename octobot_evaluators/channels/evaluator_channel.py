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
from asyncio import Queue

from octobot_channels.consumer import Consumer
from octobot_channels.producer import Producer
from octobot_commons.logging.logging_util import get_logger

from octobot_channels.channels.channel import Channel, Channels

from octobot_channels import CONSUMER_CALLBACK_TYPE, CHANNEL_WILDCARD
from octobot_channels.channels.channel_instances import ChannelInstances


class EvaluatorChannel(Channel):
    FILTER_SIZE = 1
    PRODUCER_CLASS = None

    def __init__(self, exchange_name):
        super().__init__()
        self.logger = get_logger(f"{self.__class__.__name__}[{exchange_name}]")
        self.exchange_name = exchange_name

    def new_consumer(self,
                     callback: CONSUMER_CALLBACK_TYPE,
                     size=0,
                     symbol=CHANNEL_WILDCARD,
                     time_frame=None,
                     filter_size=False):
        self._add_new_consumer_and_run(EvaluatorChannelConsumer(callback, size=size, filter_size=filter_size),
                                       symbol=symbol,
                                       time_frame=time_frame)

    def get_consumers_by_timeframe(self, time_frame, symbol):
        if not symbol:
            symbol = CHANNEL_WILDCARD
        try:
            return [consumer
                    for consumer in self.consumers[symbol][time_frame]
                    if not consumer.filter_size or should_send_filter]
        except KeyError:
            self._init_consumer_if_necessary(self.consumers, symbol, is_dict=True)
            self._init_consumer_if_necessary(self.consumers[symbol], time_frame)
            return self.consumers[symbol][time_frame]

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


class EvaluatorChannelConsumer(Consumer):
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
                await self.callback(**(await self.queue.get()))
            except Exception as e:
                self.logger.exception(f"Exception when calling callback : {e}")


class EvaluatorChannelProducer(Producer):
    async def send_with_wildcard(self, **kwargs):
        await self.send(**kwargs)
        await self.send(**kwargs, is_wildcard=True)


class EvaluatorChannels(Channels):
    @staticmethod
    def set_chan(chan: EvaluatorChannel, name: str) -> None:
        chan_name = chan.get_name() if name else name

        try:
            exchange_chan = ChannelInstances.instance().channels[chan.exchange_name]
        except KeyError:
            ChannelInstances.instance().channels[chan.exchange_name] = {}
            exchange_chan = ChannelInstances.instance().channels[chan.exchange_name]

        if chan_name not in exchange_chan:
            exchange_chan[chan_name] = chan
        else:
            raise ValueError(f"Channel {chan_name} already exists.")

    @staticmethod
    def get_chan(chan_name: str, exchange_name: str) -> EvaluatorChannel:
        try:
            return ChannelInstances.instance().channels[exchange_name][chan_name]
        except KeyError:
            get_logger(__class__.__name__).error(f"Channel {chan_name} not found on {exchange_name}")
            return None
