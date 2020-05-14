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
from octobot_channels.constants import CHANNEL_WILDCARD
from octobot_channels.consumer import Consumer
from octobot_channels.producer import Producer

from octobot_commons.enums import ChannelConsumerPriorityLevels
from octobot_commons.logging.logging_util import get_logger
from octobot_evaluators.constants import EVALUATORS_CHANNEL, TA_RE_EVALUATION_TRIGGER_UPDATED_DATA, RESET_EVALUATION, \
    EVALUATOR_CHANNEL_DATA_ACTION, EVALUATOR_CHANNEL_DATA_EXCHANGE_ID, EVALUATOR_CHANNEL_DATA_TIME_FRAMES


class EvaluatorChannelConsumer(Consumer):
    """
    Consumer adapted for EvaluatorChannel
    """


class EvaluatorChannelProducer(Producer):
    """
    Producer adapted for EvaluatorChannel
    """


class EvaluatorChannel(Channel):
    PRODUCER_CLASS = EvaluatorChannelProducer
    CONSUMER_CLASS = EvaluatorChannelConsumer
    DEFAULT_PRIORITY_LEVEL = ChannelConsumerPriorityLevels.MEDIUM.value

    def __init__(self, matrix_id):
        super().__init__()
        self.matrix_id = matrix_id

    def get_consumer_from_filters(self, consumer_filters, origin_consumer=None) -> list:
        """
        Returns the instance filtered consumers list except origin_consumer if provided
        :param consumer_filters: the consumer filters dict
        :param origin_consumer: the consumer behind the call if any else None
        :return: the filtered consumer list
        """
        return [consumer
                for consumer in super(EvaluatorChannel, self).get_consumer_from_filters(consumer_filters)
                if origin_consumer is None or consumer is not origin_consumer]


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


async def trigger_technical_evaluators_re_evaluation_with_updated_data(matrix_id,
                                                                       evaluator_name,
                                                                       evaluator_type,
                                                                       exchange_name,
                                                                       cryptocurrency,
                                                                       symbol,
                                                                       exchange_id,
                                                                       time_frames
                                                                       ):
    # first reset evaluations to avoid partially updated TA cycle validation
    await get_chan(EVALUATORS_CHANNEL, matrix_id).get_internal_producer().send(
        matrix_id,
        data={
            EVALUATOR_CHANNEL_DATA_ACTION: RESET_EVALUATION,
            EVALUATOR_CHANNEL_DATA_TIME_FRAMES: time_frames
        },
        evaluator_name=evaluator_name,
        evaluator_type=evaluator_type,
        exchange_name=exchange_name,
        cryptocurrency=cryptocurrency,
        symbol=symbol,
        time_frame=CHANNEL_WILDCARD
    )
    await get_chan(EVALUATORS_CHANNEL, matrix_id).get_internal_producer().send(
        matrix_id,
        data={
            EVALUATOR_CHANNEL_DATA_ACTION: TA_RE_EVALUATION_TRIGGER_UPDATED_DATA,
            EVALUATOR_CHANNEL_DATA_EXCHANGE_ID: exchange_id,
            EVALUATOR_CHANNEL_DATA_TIME_FRAMES: time_frames
        },
        evaluator_name=evaluator_name,
        evaluator_type=evaluator_type,
        exchange_name=exchange_name,
        cryptocurrency=cryptocurrency,
        symbol=symbol,
        time_frame=CHANNEL_WILDCARD
    )
