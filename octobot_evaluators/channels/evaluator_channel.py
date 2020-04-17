# pylint: disable=E0203
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

from octobot_channels.channels.channel import Channel
from octobot_channels.channels.channel_instances import ChannelInstances
from octobot_channels.consumer import Consumer
from octobot_channels.producer import Producer
from octobot_commons.logging.logging_util import get_logger


class EvaluatorChannelConsumer(Consumer):
    pass


class EvaluatorChannelProducer(Producer):
    pass


class EvaluatorChannel(Channel):
    PRODUCER_CLASS = EvaluatorChannelProducer
    CONSUMER_CLASS = EvaluatorChannelConsumer

    def __init__(self, matrix_id):
        super().__init__()
        self.matrix_id = matrix_id


def set_chan(chan, name) -> None:
    chan_name = chan.get_name() if name else name

    try:
        evaluator_chan = ChannelInstances.instance().channels[chan.matrix_id]
    except KeyError:
        ChannelInstances.instance().channels[chan.matrix_id] = {}
        evaluator_chan = ChannelInstances.instance().channels[chan.matrix_id]

    if chan_name not in evaluator_chan:
        evaluator_chan[chan_name] = chan
    else:
        raise ValueError(f"Channel {chan_name} already exists.")


def get_evaluator_channels(matrix_id) -> dict:
    try:
        return ChannelInstances.instance().channels[matrix_id]
    except KeyError:
        raise KeyError(f"Channels not found with matrix_id: {matrix_id}")


def del_evaluator_channel_container(matrix_id):
    try:
        ChannelInstances.instance().channels.pop(matrix_id, None)
    except KeyError:
        raise KeyError(f"Channels not found with matrix_id: {matrix_id}")


def get_chan(chan_name, matrix_id) -> EvaluatorChannel:
    try:
        return ChannelInstances.instance().channels[matrix_id][chan_name]
    except KeyError:
        raise KeyError(f"Channel {chan_name} not found with matrix_id: {matrix_id}")


def del_chan(chan_name, matrix_id) -> None:
    try:
        ChannelInstances.instance().channels[matrix_id].pop(chan_name, None)
    except KeyError:
        get_logger(EvaluatorChannel.__name__).warning(f"Can't del chan {chan_name} with matrix_id: {matrix_id}")
