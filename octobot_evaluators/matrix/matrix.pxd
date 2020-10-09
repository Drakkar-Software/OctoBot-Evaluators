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
    cdef public str matrix_id
    cdef public EventTree matrix

    cpdef void set_node_value(self, object value, object value_type, list value_path, double timestamp=*)
    cpdef list get_node_children_at_path(self, list node_path, EventTreeNode starting_node=*)
    cpdef dict get_node_children_by_names_at_path(self, list node_path, EventTreeNode starting_node=*)
    cpdef EventTreeNode get_node_at_path(self, list node_path, EventTreeNode starting_node=*)
