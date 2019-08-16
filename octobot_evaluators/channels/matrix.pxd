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
from octobot_channels.channels.channel cimport Channel
from octobot_channels.consumer cimport Consumer
from octobot_channels.producer cimport Producer

cdef class MatrixChannel(Channel):
    cdef public str exchange_name

cdef class MatrixChannelConsumer(Consumer):
    pass

cdef class MatrixChannelProducer(Producer):
    pass

cpdef MatrixChannel get_chan(str chan_name)
cpdef void set_chan(MatrixChannel chan, str name)
cpdef void del_chan(str name)
