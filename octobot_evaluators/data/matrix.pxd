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
from octobot_commons.event_tree cimport EventTree
from octobot_commons.event_tree cimport EventTreeNode


cdef class Matrix:
    cdef public str id
    cdef public EventTree matrix

    cpdef void set_tentacle_value(self, object value, object value_type, list value_path)
    cpdef list get_node_children_at_path(self, list node_path, EventTreeNode starting_node=*)
    cpdef EventTreeNode get_node_at_path(self, list node_path, EventTreeNode starting_node=*)
    cpdef list get_tentacle_nodes(self, str exchange_name=*, object tentacle_type=*, str tentacle_name=*)
    cpdef list get_tentacles_value_nodes(self, list tentacle_nodes, str cryptocurrency=*, str symbol=*, str time_frame=*)

cpdef list get_tentacle_path(str exchange_name=*, object tentacle_type=*, str tentacle_name=*)
cpdef list get_tentacle_value_path(str cryptocurrency=*, str symbol=*, str time_frame=*)
