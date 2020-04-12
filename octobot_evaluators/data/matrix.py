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
import uuid

from octobot_commons.event_tree import EventTree, NodeExistsError


class Matrix:
    """
    Matrix dataclass store tentacles data in a EventTree
    """
    __slots__ = ['matrix_id', 'matrix']

    def __init__(self):
        """
        Initialize the matrix as an EventTree instance
        """
        self.matrix_id = str(uuid.uuid4())
        self.matrix = EventTree()

    def set_node_value(self, value, value_type, value_path):
        self.matrix.set_node_at_path(value, value_type, value_path)

    def get_node_children_at_path(self, node_path, starting_node=None):
        try:
            return list(self.matrix.get_node(node_path, starting_node=starting_node).children.values())
        except NodeExistsError:
            return []

    def get_node_children_by_names_at_path(self, node_path, starting_node=None):
        try:
            return {key: val
                    for key, val in self.matrix.get_node(node_path, starting_node=starting_node).children.items()}
        except NodeExistsError:
            return {}

    def get_node_at_path(self, node_path, starting_node=None):
        try:
            return self.matrix.get_node(node_path, starting_node=starting_node)
        except NodeExistsError:
            return None
