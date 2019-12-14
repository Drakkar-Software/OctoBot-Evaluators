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

from octobot_commons.event_tree import EventTree, NodeExistsError
from octobot_commons.singleton.singleton_class import Singleton


class Matrix(Singleton):
    """
    Matrix dataclass store tentacles data in a EventTree
    """
    __slots__ = ['matrix']

    def __init__(self):
        """
        Initialize the matrix as an EventTree instance
        """
        self.matrix = EventTree()

    def set_tentacle_value(self, value, value_type, value_path):
        self.matrix.set_node_at_path(value, value_type, value_path)

    def get_node_children_at_path(self, node_path, starting_node=None):
        try:
            return list(self.matrix.get_node(node_path, starting_node=starting_node).children.values())
        except NodeExistsError:
            return []

    def get_node_at_path(self, node_path, starting_node=None):
        try:
            return self.matrix.get_node(node_path, starting_node=starting_node)
        except NodeExistsError:
            return None

    def get_tentacle_nodes(self, exchange_name=None, tentacle_type=None, tentacle_name=None):
        """
        Returns the list of nodes related to the exchange_name, tentacle_type and tentacle_name, ignored if None
        :param exchange_name: the exchange name to search for in the matrix
        :param tentacle_type: the tentacle type to search for in the matrix
        :param tentacle_name: the tentacle name to search for in the matrix
        :return: nodes linked to the given params
        """
        return self.get_node_children_at_path(get_tentacle_path(exchange_name=exchange_name,
                                                                tentacle_type=tentacle_type,
                                                                tentacle_name=tentacle_name))

    def get_tentacles_value_nodes(self, tentacle_nodes, symbol=None, time_frame=None):
        """
        Returns the list of nodes related to the symbol and / or time_frame from the given tentacle_nodes list
        :param tentacle_nodes: the exchange name to search for in the matrix
        :param symbol: the symbol to search for in the given node list
        :param time_frame: the time frame to search for in the given nodes list
        :return: nodes linked to the given params
        """
        return [node_at_path for node_at_path in [
            self.get_node_at_path(get_tentacle_value_path(symbol=symbol,
                                                          time_frame=time_frame),
                                  starting_node=n)
            for n in tentacle_nodes
        ] if node_at_path is not None]


def get_tentacle_path(exchange_name=None, tentacle_type=None, tentacle_name=None) -> list:
    """
    Returns the path related to the tentacle name, type and exchange name
    :param tentacle_type: the tentacle type to add in the path, ignored if None
    :param tentacle_name: the tentacle name to add in the path, ignored if None
    :param exchange_name: the exchange name to add in the path (as the first element), ignored if None
    :return: a list of string that represents the path of the given params
    """
    node_path = []
    if exchange_name is not None:
        node_path.append(exchange_name)
    if tentacle_type is not None:
        node_path.append(tentacle_type)
    if tentacle_name is not None:
        node_path.append(tentacle_name)
    return node_path


def get_tentacle_value_path(symbol=None, time_frame=None) -> list:
    """
    Returns the path related to symbol and / or time_frame values
    :param symbol: the symbol to add in the path, ignored if None
    :param time_frame: the time frame to add in the path, ignored if None
    :return: a list of string that represents the path of the given params
    """
    node_path: list = []
    if symbol is not None:
        node_path.append(symbol)
    if time_frame is not None:
        node_path.append(time_frame)
    return node_path
