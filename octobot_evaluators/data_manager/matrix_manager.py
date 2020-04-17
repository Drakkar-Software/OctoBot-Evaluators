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
import asyncio
import time

from octobot_commons.constants import MINUTE_TO_SECONDS, MIN_EVAL_TIME_FRAME

from octobot_commons.enums import TimeFrames, TimeFramesMinutes

from octobot_evaluators.matrices.matrices import Matrices


def get_matrix(matrix_id):
    """
    Get the matrix from its id
    :param matrix_id: the matrix id
    :return: the matrix instance
    """
    return Matrices.instance().get_matrix(matrix_id)


def set_tentacle_value(matrix_id, tentacle_path, tentacle_type, tentacle_value, timestamp=0):
    """
    Set the node value at tentacle path
    :param matrix_id: the matrix id
    :param tentacle_path: the tentacle path
    :param tentacle_type: the tentacle type
    :param tentacle_value: the tentacle value
    :param timestamp: the value modification timestamp.
    """
    get_matrix(matrix_id).set_node_value(value=tentacle_value, value_type=tentacle_type,
                                         value_path=tentacle_path, timestamp=timestamp)


def get_tentacle_node(matrix_id, tentacle_path):
    """
    Return the node at tentacle path
    :param matrix_id: the matrix id
    :param tentacle_path: the tentacle path
    :return: the tentacle node
    """
    return get_matrix(matrix_id).get_node_at_path(node_path=tentacle_path)


def get_tentacle_value(matrix_id, tentacle_path):
    """
    Set the node value at tentacle path
    :param matrix_id: the matrix id
    :param tentacle_path: the tentacle path
    :return: the tentacle value
    """
    tentacle_node = get_tentacle_node(matrix_id, tentacle_path)
    if tentacle_node:
        return tentacle_node.node_value
    return None


def get_matrix_default_value_path(tentacle_name,
                                  tentacle_type,
                                  exchange_name=None,
                                  cryptocurrency=None,
                                  symbol=None,
                                  time_frame=None):
    """
    Create matrix value path with default path
    :param tentacle_name:
    :param tentacle_type:
    :param exchange_name:
    :param cryptocurrency:
    :param symbol:
    :param time_frame:
    :return: the default matrix
    """
    return get_tentacle_path(exchange_name=exchange_name,
                             tentacle_type=tentacle_type,
                             tentacle_name=tentacle_name) + get_tentacle_value_path(
        cryptocurrency=cryptocurrency,
        symbol=symbol,
        time_frame=time_frame)


def get_tentacle_nodes(matrix_id, exchange_name=None, tentacle_type=None, tentacle_name=None):
    """
    Returns the list of nodes related to the exchange_name, tentacle_type and tentacle_name, ignored if None
    :param matrix_id: the matrix id
    :param exchange_name: the exchange name to search for in the matrix
    :param tentacle_type: the tentacle type to search for in the matrix
    :param tentacle_name: the tentacle name to search for in the matrix
    :return: nodes linked to the given params
    """
    return get_matrix(matrix_id).get_node_children_at_path(get_tentacle_path(exchange_name=exchange_name,
                                                                             tentacle_type=tentacle_type,
                                                                             tentacle_name=tentacle_name))


def get_tentacles_value_nodes(matrix_id, tentacle_nodes, cryptocurrency=None, symbol=None, time_frame=None):
    """
    Returns the list of nodes related to the symbol and / or time_frame from the given tentacle_nodes list
    :param matrix_id: the matrix id
    :param tentacle_nodes: the exchange name to search for in the matrix
    :param cryptocurrency: the cryptocurrency to search for in the given node list
    :param symbol: the symbol to search for in the given node list
    :param time_frame: the time frame to search for in the given nodes list
    :return: nodes linked to the given params
    """
    return [node_at_path for node_at_path in [
        get_matrix(matrix_id).get_node_at_path(get_tentacle_value_path(cryptocurrency=cryptocurrency,
                                                                       symbol=symbol,
                                                                       time_frame=time_frame),
                                               starting_node=n)
        for n in tentacle_nodes]
            if node_at_path is not None]


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


def get_tentacle_value_path(cryptocurrency=None, symbol=None, time_frame=None) -> list:
    """
    Returns the path related to symbol and / or time_frame values
    :param cryptocurrency: the cryptocurrency to add in the path, ignored if None
    :param symbol: the symbol to add in the path, ignored if None
    :param time_frame: the time frame to add in the path, ignored if None
    :return: a list of string that represents the path of the given params
    """
    node_path: list = []
    if cryptocurrency is not None:
        node_path.append(cryptocurrency)
    if symbol is not None:
        node_path.append(symbol)
    if time_frame is not None:
        node_path.append(time_frame)
    return node_path


async def get_nodes_event(matrix_id, nodes_path, timeout=None):
    """
    Return the asyncio.wait of nodes event
    :param matrix_id: the matrix id
    :param nodes_path: the tentacle node path
    :param timeout: the event waiting timeout (when None no timeout)
    :return: the
    """
    return asyncio.gather(*[asyncio.wait_for(get_tentacle_node(matrix_id, node_path).node_event.wait(), timeout=timeout)
                            for node_path in nodes_path])


async def get_nodes_clear_event(matrix_id, nodes_path, timeout=None):
    """
    Return the asyncio.wait of nodes clear event
    :param matrix_id: the matrix id
    :param nodes_path: the tentacle node path
    :param timeout: the event waiting timeout (when None no timeout)
    :return: the
    """
    return asyncio.gather(*[asyncio.wait_for(get_tentacle_node(matrix_id, node_path).node_clear_event.wait(),
                                             timeout=timeout) for node_path in nodes_path])


async def subscribe_nodes_event(matrix_id, nodes_path, callback, timeout=None):
    """

    :param matrix_id: the matrix id
    :param nodes_path: the tentacle node path
    :param callback:
    :param timeout: the event waiting timeout (when None no timeout)
    :return:
    """
    await get_nodes_event(matrix_id, nodes_path, timeout=timeout)
    callback()


def is_tentacle_value_valid(matrix_id, tentacle_path, timestamp=0, delta=10) -> bool:
    """
    Check if the node is ready to be used
    WARNING: This method only works with complete default tentacle path
    :param matrix_id: the matrix id
    :param tentacle_path: the tentacle node path
    :param timestamp: the timestamp to use
    :param delta: the authorized delta to be valid (in seconds)
    :return: True if the node is valid else False
    """
    if timestamp == 0:
        timestamp = time.time()
    try:
        return timestamp - (get_tentacle_node(matrix_id, tentacle_path).node_value_time +
                            TimeFramesMinutes[TimeFrames(tentacle_path[-1])] * MINUTE_TO_SECONDS + delta) < 0
    except (IndexError, ValueError):
        return False


def is_tentacles_values_valid(matrix_id, tentacle_path_list, timestamp=0, delta=10) -> bool:
    """
    Check if each of the tentacle path value is valid
    :param matrix_id: the matrix id
    :param tentacle_path_list: the tentacle node path list
    :param timestamp: the timestamp to use
    :param delta: the authorized delta to be valid (in seconds)
    :return: True if all the node values are valid else False
    """
    return all([is_tentacle_value_valid(matrix_id=matrix_id,
                                        tentacle_path=tentacle_path,
                                        timestamp=timestamp,
                                        delta=delta)
                for tentacle_path in tentacle_path_list])
