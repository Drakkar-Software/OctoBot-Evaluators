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
cimport async_channel.channels as channels
cimport async_channel.consumer as consumers
cimport async_channel.producer as producers

cdef class EvaluatorChannel(channels.Channel):
    cdef public str matrix_id

    cpdef list get_consumer_from_filters(self, dict consumer_filters, EvaluatorChannelConsumer origin_consumer=*)

cdef class EvaluatorChannelConsumer(consumers.Consumer):
    pass

cdef class EvaluatorChannelSupervisedConsumer(consumers.SupervisedConsumer):
    pass

cdef class EvaluatorChannelProducer(producers.Producer):
    pass

cpdef EvaluatorChannel get_chan(str chan_name, str matrix_id)
cpdef dict get_evaluator_channels(str matrix_id)
cpdef void set_chan(EvaluatorChannel chan, str name)
cpdef void del_evaluator_channel_container(str matrix_id)
cpdef void del_chan(str name, str matrix_id)
