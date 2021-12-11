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
cimport octobot_evaluators.evaluators.channel as evaluator_channels

cdef class MatrixChannel(evaluator_channels.EvaluatorChannel):
    cdef public str exchange_name

cdef class MatrixChannelConsumer(evaluator_channels.EvaluatorChannelConsumer):
    pass

cdef class MatrixChannelSupervisedConsumer(evaluator_channels.EvaluatorChannelSupervisedConsumer):
    pass

cdef class MatrixChannelProducer(evaluator_channels.EvaluatorChannelProducer):
    pass
