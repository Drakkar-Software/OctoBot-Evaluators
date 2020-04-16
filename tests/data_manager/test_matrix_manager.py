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

import pytest

from octobot_evaluators.data.matrix import Matrix
from octobot_evaluators.data_manager.matrix_manager import get_tentacle_path, get_tentacle_value_path, \
    get_tentacle_nodes, get_tentacles_value_nodes, get_matrix_default_value_path, set_tentacle_value, \
    get_tentacle_value, get_nodes_event, get_nodes_clear_event, get_tentacle_node
from octobot_evaluators.matrices.matrices import Matrices


@pytest.mark.asyncio
async def test_set_tentacle_value():
    matrix = Matrix()
    Matrices.instance().add_matrix(matrix)
    set_tentacle_value(matrix.matrix_id, tentacle_type="TA", tentacle_value=0, tentacle_path=["test-path"])
    assert matrix.get_node_at_path(["test-path"]).node_value == 0

    set_tentacle_value(matrix.matrix_id, tentacle_type="TA", tentacle_value="value", tentacle_path=
    get_tentacle_path(tentacle_type="TA", tentacle_name="Test-TA", exchange_name="binance"))
    assert matrix.get_node_at_path(
        get_tentacle_path(tentacle_type="TA", tentacle_name="Test-TA", exchange_name="binance")).node_value == "value"
    Matrices.instance().del_matrix(matrix.matrix_id)


@pytest.mark.asyncio
async def test_get_tentacle_value():
    matrix = Matrix()
    Matrices.instance().add_matrix(matrix)
    assert not get_tentacle_value(matrix.matrix_id, tentacle_path=["Test-TA"])

    matrix.matrix.get_or_create_node(path=["Test-TA"])
    matrix.set_node_value(value_type="TA", value_path=["Test-TA"], value=0)
    assert get_tentacle_value(matrix.matrix_id, tentacle_path=["Test-TA"]) == 0

    matrix.matrix.get_or_create_node(get_tentacle_path(tentacle_type="TA", tentacle_name="Test-TA"))
    matrix.set_node_value(value_type="TA", value_path=get_tentacle_path(tentacle_type="TA", tentacle_name="Test-TA"),
                          value="test")
    assert get_tentacle_value(matrix.matrix_id, tentacle_path=get_tentacle_path(tentacle_type="TA",
                                                                                tentacle_name="Test-TA")) == "test"
    Matrices.instance().del_matrix(matrix.matrix_id)


def test_get_matrix_default_value_path():
    assert get_matrix_default_value_path(tentacle_type="TA", tentacle_name="Test-TA", exchange_name="binance") == \
           get_tentacle_path(tentacle_type="TA", tentacle_name="Test-TA", exchange_name="binance")
    assert get_matrix_default_value_path(tentacle_type="TA", tentacle_name="Test-TA",
                                         symbol="ETH", time_frame="1h") == \
           get_tentacle_path(tentacle_type="TA", tentacle_name="Test-TA") + \
           get_tentacle_value_path(symbol="ETH", time_frame="1h")
    assert get_matrix_default_value_path(tentacle_type="TA", tentacle_name="Test-TA",
                                         symbol="ETH", exchange_name="bitmex") == \
           get_tentacle_path(tentacle_type="TA", tentacle_name="Test-TA", exchange_name="bitmex") + \
           get_tentacle_value_path(symbol="ETH")


def test_get_tentacle_path():
    assert get_tentacle_path(tentacle_type="TA", tentacle_name="Test-TA", exchange_name="binance") == ["binance", "TA",
                                                                                                       "Test-TA"]
    assert get_tentacle_path(tentacle_type="TA", tentacle_name="Test-TA") == ["TA", "Test-TA"]
    assert get_tentacle_path(exchange_name="binance", tentacle_name="Test-TA") == ["binance", "Test-TA"]
    assert get_tentacle_path(tentacle_name="Test-TA") == ["Test-TA"]


def test_get_tentacle_value_path():
    assert get_tentacle_value_path() == []
    assert get_tentacle_value_path(symbol="BTC") == ["BTC"]
    assert get_tentacle_value_path(time_frame="1m") == ["1m"]
    assert get_tentacle_value_path(symbol="ETH", time_frame="1h") == ["ETH", "1h"]


@pytest.mark.asyncio
async def test_get_tentacle_nodes_on_root():
    matrix = Matrix()
    Matrices.instance().add_matrix(matrix)
    created_node_1 = matrix.matrix.get_or_create_node(
        get_tentacle_path(tentacle_type="NO_TYPE", tentacle_name="Test-TA"))
    created_node_2 = matrix.matrix.get_or_create_node(
        get_tentacle_path(exchange_name="binance", tentacle_name="Test-TA-2"))
    created_node_3 = matrix.matrix.get_or_create_node(get_tentacle_path(tentacle_name="Test-TA-3"))
    assert get_tentacle_nodes(matrix.matrix_id) == [matrix.get_node_at_path(get_tentacle_path(tentacle_type="NO_TYPE")),
                                                    matrix.get_node_at_path(get_tentacle_path(exchange_name="binance")),
                                                    created_node_3]

    assert get_tentacle_nodes(matrix.matrix_id, tentacle_type="TA") == []
    assert get_tentacle_nodes(matrix.matrix_id, exchange_name="bitfinex") == []
    assert get_tentacle_nodes(matrix.matrix_id, tentacle_type="NO_TYPE") == [created_node_1]
    assert get_tentacle_nodes(matrix.matrix_id, exchange_name="binance") == [created_node_2]
    Matrices.instance().del_matrix(matrix.matrix_id)


@pytest.mark.asyncio
async def test_get_tentacle_nodes_on_tentacle_type():
    matrix = Matrix()
    Matrices.instance().add_matrix(matrix)
    created_node_1 = matrix.matrix.get_or_create_node(
        get_tentacle_path(tentacle_type="NO_TYPE", tentacle_name="Test-TA"))
    created_node_2 = matrix.matrix.get_or_create_node(
        get_tentacle_path(tentacle_type="TEST_TYPE", tentacle_name="Test-TA-2"))

    assert get_tentacle_nodes(matrix.matrix_id, tentacle_type="TA") == []
    assert get_tentacle_nodes(matrix.matrix_id, tentacle_type="NO_TYPE") == [created_node_1]
    assert get_tentacle_nodes(matrix.matrix_id, tentacle_type="TEST_TYPE") == [created_node_2]
    Matrices.instance().del_matrix(matrix.matrix_id)


@pytest.mark.asyncio
async def test_get_tentacle_nodes_on_exchange_name_and_tentacle_type():
    matrix = Matrix()
    Matrices.instance().add_matrix(matrix)
    created_node_1 = matrix.matrix.get_or_create_node(get_tentacle_path(tentacle_type="NO_TYPE",
                                                                        tentacle_name="Test-TA",
                                                                        exchange_name="binance"))
    created_node_2 = matrix.matrix.get_or_create_node(get_tentacle_path(tentacle_type="TEST_TYPE",
                                                                        tentacle_name="Test-TA-2",
                                                                        exchange_name="binance"))
    assert get_tentacle_nodes(matrix.matrix_id, exchange_name="binance") == [
        matrix.get_node_at_path(get_tentacle_path(exchange_name="binance",
                                                  tentacle_type="NO_TYPE")),
        matrix.get_node_at_path(get_tentacle_path(exchange_name="binance",
                                                  tentacle_type="TEST_TYPE"))]
    assert get_tentacle_nodes(matrix.matrix_id, exchange_name="binance", tentacle_type="NO_TYPE") == [created_node_1]
    assert get_tentacle_nodes(matrix.matrix_id, exchange_name="binance", tentacle_type="TEST_TYPE") == [created_node_2]
    assert get_tentacle_nodes(matrix.matrix_id, exchange_name="bitfinex") == []
    Matrices.instance().del_matrix(matrix.matrix_id)


@pytest.mark.asyncio
async def test_get_tentacle_nodes_on_exchange_name():
    matrix = Matrix()
    Matrices.instance().add_matrix(matrix)
    created_node_1 = matrix.matrix.get_or_create_node(get_tentacle_path(tentacle_name="Test-TA",
                                                                        exchange_name="binance"))
    created_node_2 = matrix.matrix.get_or_create_node(get_tentacle_path(tentacle_name="Test-TA-2",
                                                                        exchange_name="binance"))

    assert get_tentacle_nodes(matrix.matrix_id, exchange_name="bitfinex") == []
    assert get_tentacle_nodes(matrix.matrix_id, tentacle_type="NO_TYPE") == []
    assert get_tentacle_nodes(matrix.matrix_id, exchange_name="binance") == [created_node_1, created_node_2]
    Matrices.instance().del_matrix(matrix.matrix_id)


@pytest.mark.asyncio
async def test_get_tentacle_nodes_on_multiple_tentacle_type():
    matrix = Matrix()
    Matrices.instance().add_matrix(matrix)
    created_node_1 = matrix.matrix.get_or_create_node(get_tentacle_path(tentacle_type="TA", tentacle_name="Test-TA"))
    created_node_2 = matrix.matrix.get_or_create_node(get_tentacle_path(tentacle_type="TA", tentacle_name="Test-TA-2"))
    created_node_3 = matrix.matrix.get_or_create_node(get_tentacle_path(tentacle_type="TA", tentacle_name="Test-TA-3"))
    assert get_tentacle_nodes(matrix.matrix_id, tentacle_type="TA") == [created_node_1, created_node_2, created_node_3]
    Matrices.instance().del_matrix(matrix.matrix_id)


@pytest.mark.asyncio
async def test_get_tentacle_nodes_on_multiple_tentacle_type_and_exchange_name():
    matrix = Matrix()
    Matrices.instance().add_matrix(matrix)
    created_node_1 = matrix.matrix.get_or_create_node(get_tentacle_path(tentacle_type="TA",
                                                                        tentacle_name="Test-TA",
                                                                        exchange_name="binance"))
    created_node_2 = matrix.matrix.get_or_create_node(get_tentacle_path(tentacle_type="TA",
                                                                        tentacle_name="Test-TA-2",
                                                                        exchange_name="binance"))
    created_node_3 = matrix.matrix.get_or_create_node(get_tentacle_path(tentacle_type="TA",
                                                                        tentacle_name="Test-TA-3",
                                                                        exchange_name="binance"))
    assert get_tentacle_nodes(matrix.matrix_id, exchange_name="binance", tentacle_type="TA") == [created_node_1,
                                                                                                 created_node_2,
                                                                                                 created_node_3]
    Matrices.instance().del_matrix(matrix.matrix_id)


@pytest.mark.asyncio
async def test_get_tentacle_nodes_mixed():
    matrix = Matrix()
    Matrices.instance().add_matrix(matrix)
    created_node_1 = matrix.matrix.get_or_create_node(get_tentacle_path(tentacle_type="TA",
                                                                        tentacle_name="Test-TA",
                                                                        exchange_name="binance"))
    created_node_2 = matrix.matrix.get_or_create_node(get_tentacle_path(tentacle_type="TA",
                                                                        tentacle_name="Test-TA-2",
                                                                        exchange_name="bitfinex"))
    created_node_3 = matrix.matrix.get_or_create_node(get_tentacle_path(tentacle_type="TA",
                                                                        tentacle_name="Test-TA-3",
                                                                        exchange_name="binance"))
    created_node_4 = matrix.matrix.get_or_create_node(get_tentacle_path(tentacle_type="TEST-TYPE",
                                                                        tentacle_name="Test-TA-4",
                                                                        exchange_name="binance"))
    created_node_5 = matrix.matrix.get_or_create_node(get_tentacle_path(tentacle_type="TEST-TYPE",
                                                                        tentacle_name="Test-TA-5",
                                                                        exchange_name="bitfinex"))
    created_node_6 = matrix.matrix.get_or_create_node(get_tentacle_path(tentacle_type="TEST-TYPE",
                                                                        tentacle_name="Test-TA-6"))
    created_node_7 = matrix.matrix.get_or_create_node(get_tentacle_path(tentacle_name="Test-TA-7",
                                                                        exchange_name="bitfinex"))
    created_node_8 = matrix.matrix.get_or_create_node(get_tentacle_path(tentacle_name="Test-TA-8"))
    created_node_9 = matrix.matrix.get_or_create_node(get_tentacle_path(tentacle_name="Test-TA-9",
                                                                        exchange_name="binance"))
    assert get_tentacle_nodes(matrix.matrix_id, exchange_name="binance", tentacle_type="TA") == [created_node_1,
                                                                                                 created_node_3]
    assert get_tentacle_nodes(matrix.matrix_id, exchange_name="binance", tentacle_type="TEST-TYPE") == [created_node_4]

    assert get_tentacle_nodes(matrix.matrix_id, exchange_name="bitfinex", tentacle_type="TEST-TYPE") == [created_node_5]

    assert get_tentacle_nodes(matrix.matrix_id, exchange_name="bitfinex") == [
        matrix.get_node_at_path(get_tentacle_path(exchange_name="bitfinex", tentacle_type="TA")),
        matrix.get_node_at_path(get_tentacle_path(exchange_name="bitfinex", tentacle_type="TEST-TYPE")),
        created_node_7]

    assert get_tentacle_nodes(matrix.matrix_id, tentacle_type="TEST-TYPE") == [created_node_6]

    assert get_tentacle_nodes(matrix.matrix_id, exchange_name="binance") == [
        matrix.get_node_at_path(get_tentacle_path(exchange_name="binance", tentacle_type="TA")),
        matrix.get_node_at_path(get_tentacle_path(exchange_name="binance", tentacle_type="TEST-TYPE")),
        created_node_9]
    Matrices.instance().del_matrix(matrix.matrix_id)


@pytest.mark.asyncio
async def test_get_tentacles_value_nodes_with_symbol():
    matrix = Matrix()
    Matrices.instance().add_matrix(matrix)
    created_node = matrix.matrix.get_or_create_node(get_tentacle_path(tentacle_type="TA", tentacle_name="Test-TA"))
    created_node_2 = matrix.matrix.get_or_create_node(get_tentacle_path(tentacle_type="TA", tentacle_name="Test-TA-2"))
    btc_node = matrix.matrix.get_or_create_node(get_tentacle_value_path(symbol="BTC"), starting_node=created_node)
    eth_node = matrix.matrix.get_or_create_node(get_tentacle_value_path(symbol="ETH"), starting_node=created_node)
    btc_node_2 = matrix.matrix.get_or_create_node(get_tentacle_value_path(symbol="BTC"), starting_node=created_node_2)
    assert get_tentacles_value_nodes(matrix.matrix_id, tentacle_nodes=[created_node, created_node_2],
                                     symbol="BTC") == [btc_node, btc_node_2]
    assert get_tentacles_value_nodes(matrix.matrix_id, tentacle_nodes=[created_node, created_node_2],
                                     symbol="ETH") == [eth_node]
    Matrices.instance().del_matrix(matrix.matrix_id)


@pytest.mark.asyncio
async def test_get_tentacles_value_nodes_with_time_frame():
    matrix = Matrix()
    Matrices.instance().add_matrix(matrix)
    assert get_tentacle_value_path(time_frame="1m") == ["1m"]
    created_node = matrix.matrix.get_or_create_node(get_tentacle_path(tentacle_type="TA", tentacle_name="Test-TA"))
    created_node_2 = matrix.matrix.get_or_create_node(get_tentacle_path(tentacle_type="TA", tentacle_name="Test-TA-2"))
    m_node = matrix.matrix.get_or_create_node(get_tentacle_value_path(time_frame="1m"), starting_node=created_node)
    h_node = matrix.matrix.get_or_create_node(get_tentacle_value_path(time_frame="1h"), starting_node=created_node)
    h_node_2 = matrix.matrix.get_or_create_node(get_tentacle_value_path(time_frame="1h"), starting_node=created_node_2)
    assert get_tentacles_value_nodes(matrix.matrix_id, tentacle_nodes=[created_node, created_node_2],
                                     time_frame="1h") == [h_node, h_node_2]
    assert get_tentacles_value_nodes(matrix.matrix_id, tentacle_nodes=[created_node, created_node_2],
                                     symbol="1m") == [m_node]
    Matrices.instance().del_matrix(matrix.matrix_id)


@pytest.mark.asyncio
async def test_get_tentacles_value_nodes_with_symbol_and_time_frame():
    matrix = Matrix()
    Matrices.instance().add_matrix(matrix)
    assert get_tentacle_value_path(symbol="ETH", time_frame="1h") == ["ETH", "1h"]

    created_node = matrix.matrix.get_or_create_node(get_tentacle_path(tentacle_type="TA", tentacle_name="Test-TA"))
    created_node_2 = matrix.matrix.get_or_create_node(get_tentacle_path(tentacle_type="TA", tentacle_name="Test-TA-2"))
    created_node_3 = matrix.matrix.get_or_create_node(get_tentacle_path(tentacle_type="TA", tentacle_name="Test-TA-3"))
    btc_h_node = matrix.matrix.get_or_create_node(get_tentacle_value_path(symbol="BTC", time_frame="1h"),
                                                  starting_node=created_node)
    btc_m_node = matrix.matrix.get_or_create_node(get_tentacle_value_path(symbol="BTC", time_frame="1m"),
                                                  starting_node=created_node_2)
    eth_h_node = matrix.matrix.get_or_create_node(get_tentacle_value_path(symbol="ETH", time_frame="1h"),
                                                  starting_node=created_node_3)
    eth_m_node = matrix.matrix.get_or_create_node(get_tentacle_value_path(symbol="ETH", time_frame="1m"),
                                                  starting_node=created_node_2)
    eth_d_node = matrix.matrix.get_or_create_node(get_tentacle_value_path(symbol="ETH", time_frame="1d"),
                                                  starting_node=created_node)
    ltc_h_node = matrix.matrix.get_or_create_node(get_tentacle_value_path(symbol="LTC", time_frame="1h"),
                                                  starting_node=created_node_2)
    assert get_tentacles_value_nodes(matrix.matrix_id, tentacle_nodes=[created_node, created_node_2, created_node_3],
                                     symbol="BTC", time_frame="1h") == [btc_h_node]
    assert get_tentacles_value_nodes(matrix.matrix_id, tentacle_nodes=[created_node, created_node_2, created_node_3],
                                     symbol="BTC") == [
               matrix.get_node_at_path(get_tentacle_value_path(symbol="BTC"), starting_node=created_node),
               matrix.get_node_at_path(get_tentacle_value_path(symbol="BTC"), starting_node=created_node_2)]
    assert get_tentacles_value_nodes(matrix.matrix_id, tentacle_nodes=[created_node, created_node_3],
                                     symbol="BTC") == [
               matrix.get_node_at_path(get_tentacle_value_path(symbol="BTC"), starting_node=created_node)]
    assert get_tentacles_value_nodes(matrix.matrix_id, tentacle_nodes=[created_node, created_node_3],
                                     symbol="BTC", time_frame="1m") == []
    assert get_tentacles_value_nodes(matrix.matrix_id, tentacle_nodes=[created_node_3],
                                     symbol="BTC") == []
    assert get_tentacles_value_nodes(matrix.matrix_id, tentacle_nodes=[created_node, created_node_2, created_node_3],
                                     symbol="ETH") == [
               matrix.get_node_at_path(get_tentacle_value_path(symbol="ETH"), starting_node=created_node),
               matrix.get_node_at_path(get_tentacle_value_path(symbol="ETH"), starting_node=created_node_2),
               matrix.get_node_at_path(get_tentacle_value_path(symbol="ETH"), starting_node=created_node_3)]
    Matrices.instance().del_matrix(matrix.matrix_id)


@pytest.mark.asyncio
async def test_get_tentacles_value_nodes_mixed():
    matrix = Matrix()
    Matrices.instance().add_matrix(matrix)

    created_node = matrix.matrix.get_or_create_node(get_tentacle_path(tentacle_type="TA", tentacle_name="Test-TA"))
    created_node_2 = matrix.matrix.get_or_create_node(get_tentacle_path(tentacle_type="TA", tentacle_name="Test-TA-2"))
    created_node_3 = matrix.matrix.get_or_create_node(get_tentacle_path(tentacle_type="TA", tentacle_name="Test-TA-3"))
    btc_h_node = matrix.matrix.get_or_create_node(get_tentacle_value_path(symbol="BTC", time_frame="1h"),
                                                  starting_node=created_node)
    btc_node = matrix.matrix.get_or_create_node(get_tentacle_value_path(symbol="BTC"), starting_node=created_node_2)
    eth_node = matrix.matrix.get_or_create_node(get_tentacle_value_path(symbol="ETH"), starting_node=created_node_3)
    eth_m_node = matrix.matrix.get_or_create_node(get_tentacle_value_path(symbol="ETH", time_frame="1m"),
                                                  starting_node=created_node_2)
    eth_d_node = matrix.matrix.get_or_create_node(get_tentacle_value_path(symbol="ETH", time_frame="1d"),
                                                  starting_node=created_node)
    ltc_h_node = matrix.matrix.get_or_create_node(get_tentacle_value_path(symbol="LTC", time_frame="1h"),
                                                  starting_node=created_node_2)

    assert get_tentacles_value_nodes(matrix.matrix_id, tentacle_nodes=[created_node, created_node_2, created_node_3],
                                     symbol="BTC", time_frame="1h") == [btc_h_node]
    assert get_tentacles_value_nodes(matrix.matrix_id, tentacle_nodes=[created_node, created_node_2, created_node_3],
                                     symbol="BTC") == [
               matrix.get_node_at_path(get_tentacle_value_path(symbol="BTC"), starting_node=created_node),
               matrix.get_node_at_path(get_tentacle_value_path(symbol="BTC"), starting_node=created_node_2)]
    assert get_tentacles_value_nodes(matrix.matrix_id, tentacle_nodes=[created_node, created_node_3],
                                     symbol="BTC") == [
               matrix.get_node_at_path(get_tentacle_value_path(symbol="BTC"), starting_node=created_node)]
    assert get_tentacles_value_nodes(matrix.matrix_id, tentacle_nodes=[created_node, created_node_3],
                                     symbol="BTC", time_frame="1m") == []
    assert get_tentacles_value_nodes(matrix.matrix_id, tentacle_nodes=[created_node_3],
                                     symbol="BTC") == []
    assert get_tentacles_value_nodes(matrix.matrix_id, tentacle_nodes=[created_node, created_node_2, created_node_3],
                                     symbol="ETH") == [
               matrix.get_node_at_path(get_tentacle_value_path(symbol="ETH"), starting_node=created_node),
               matrix.get_node_at_path(get_tentacle_value_path(symbol="ETH"), starting_node=created_node_2),
               matrix.get_node_at_path(get_tentacle_value_path(symbol="ETH"), starting_node=created_node_3)]
    Matrices.instance().del_matrix(matrix.matrix_id)


@pytest.mark.asyncio
async def test_get_nodes_event():
    matrix = Matrix()
    Matrices.instance().add_matrix(matrix)

    evaluator_1_path = get_matrix_default_value_path(tentacle_type="TA", tentacle_name="Test-TA", cryptocurrency="BTC")
    evaluator_2_path = get_matrix_default_value_path(tentacle_type="TA", tentacle_name="Test-TA", cryptocurrency="ETH",
                                                     symbol="ETH/USD", time_frame="1m")
    evaluator_3_path = get_matrix_default_value_path(tentacle_type="TA", tentacle_name="Test-TA", cryptocurrency="ETH")
    evaluator_4_path = get_matrix_default_value_path(tentacle_type="TA", tentacle_name="Test-TA", cryptocurrency="BTC",
                                                     symbol="BTC/USD", time_frame="1m")
    evaluator_5_path = get_matrix_default_value_path(tentacle_type="TA", tentacle_name="Test-TA", cryptocurrency="BTC",
                                                     symbol="BTC/USD", time_frame="5m")

    # simulate AbstractEvaluator.initialize()
    set_tentacle_value(matrix.matrix_id, evaluator_1_path, "TA", None)
    set_tentacle_value(matrix.matrix_id, evaluator_2_path, "TA", None)
    set_tentacle_value(matrix.matrix_id, evaluator_3_path, "TA", None)
    set_tentacle_value(matrix.matrix_id, evaluator_4_path, "TA", None)
    set_tentacle_value(matrix.matrix_id, evaluator_5_path, "TA", None)

    # Asserts that a newly created event can't be successfuly awaited
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(await get_nodes_event(matrix.matrix_id, [evaluator_1_path, evaluator_3_path]), timeout=1)

    wait_should_succeed = asyncio.wait_for(await get_nodes_event(matrix.matrix_id,
                                                                 [evaluator_1_path, evaluator_4_path]), timeout=1)
    wait_should_failed = asyncio.wait_for(await get_nodes_event(matrix.matrix_id,
                                                                [evaluator_1_path, evaluator_3_path, evaluator_4_path]),
                                          timeout=1)
    set_tentacle_value(matrix.matrix_id, evaluator_1_path, "TA", None)
    set_tentacle_value(matrix.matrix_id, evaluator_4_path, "TA", None)

    await wait_should_succeed
    with pytest.raises(asyncio.TimeoutError):
        await wait_should_failed

    wait_should_succeed = asyncio.wait_for(await get_nodes_event(matrix.matrix_id,
                                                                 [get_matrix_default_value_path(tentacle_type="TA",
                                                                                                tentacle_name="Test-TA",
                                                                                                cryptocurrency="ETH")]),
                                           timeout=1)
    wait_should_failed = asyncio.wait_for(await get_nodes_event(matrix.matrix_id,
                                                                [get_matrix_default_value_path(tentacle_type="TA",
                                                                                               tentacle_name="Test-TA",
                                                                                               cryptocurrency="BTC")]),
                                          timeout=1)
    set_tentacle_value(matrix.matrix_id, evaluator_2_path, "TA", None)
    set_tentacle_value(matrix.matrix_id, evaluator_3_path, "TA", None)

    await wait_should_succeed
    with pytest.raises(asyncio.TimeoutError):
        await wait_should_failed

    wait_should_failed = asyncio.wait_for(await get_nodes_event(matrix.matrix_id,
                                                                [get_matrix_default_value_path(tentacle_type="TA",
                                                                                               tentacle_name="Test-TA",
                                                                                               cryptocurrency="BTC",
                                                                                               symbol="BTC/USD")]),
                                          timeout=1)
    wait_should_succeed = asyncio.wait_for(await get_nodes_event(matrix.matrix_id,
                                                                 [get_matrix_default_value_path(tentacle_type="TA",
                                                                                                tentacle_name="Test-TA",
                                                                                                cryptocurrency="BTC",
                                                                                                symbol="BTC/USD",
                                                                                                time_frame="1m")]),
                                           timeout=1)

    set_tentacle_value(matrix.matrix_id, evaluator_4_path, "TA", None)
    await wait_should_succeed
    with pytest.raises(asyncio.TimeoutError):
        await wait_should_failed

    Matrices.instance().del_matrix(matrix.matrix_id)


@pytest.mark.asyncio
async def test_get_nodes_clear_event():
    matrix = Matrix()
    Matrices.instance().add_matrix(matrix)

    evaluator_1_path = get_matrix_default_value_path(tentacle_type="TA", tentacle_name="Test-TA",
                                                     cryptocurrency="BTC",
                                                     symbol="BTC/USD",
                                                     time_frame="1m")
    evaluator_2_path = get_matrix_default_value_path(tentacle_type="TA", tentacle_name="Test-TA",
                                                     cryptocurrency="BTC",
                                                     symbol="BTC/USD",
                                                     time_frame="5m")
    evaluator_3_path = get_matrix_default_value_path(tentacle_type="TA", tentacle_name="Test-TA",
                                                     cryptocurrency="BTC",
                                                     symbol="BTC/USD",
                                                     time_frame="1h")
    evaluator_4_path = get_matrix_default_value_path(tentacle_type="TA", tentacle_name="Test-TA",
                                                     cryptocurrency="BTC",
                                                     symbol="BTC/USD",
                                                     time_frame="4h")
    evaluator_5_path = get_matrix_default_value_path(tentacle_type="TA", tentacle_name="Test-TA",
                                                     cryptocurrency="BTC",
                                                     symbol="BTC/USD",
                                                     time_frame="1d")

    # simulate AbstractEvaluator.initialize()
    set_tentacle_value(matrix.matrix_id, evaluator_1_path, "TA", None)
    set_tentacle_value(matrix.matrix_id, evaluator_2_path, "TA", None)
    set_tentacle_value(matrix.matrix_id, evaluator_3_path, "TA", None)
    set_tentacle_value(matrix.matrix_id, evaluator_4_path, "TA", None)
    set_tentacle_value(matrix.matrix_id, evaluator_5_path, "TA", None)

    set_tentacle_value(matrix.matrix_id, evaluator_1_path, "TA", None)
    set_tentacle_value(matrix.matrix_id, evaluator_2_path, "TA", None)
    set_tentacle_value(matrix.matrix_id, evaluator_3_path, "TA", None)
    await asyncio.wait_for(await get_nodes_clear_event(matrix.matrix_id,
                                                       [get_matrix_default_value_path(
                                                           tentacle_type="TA",
                                                           tentacle_name="Test-TA",
                                                           cryptocurrency="BTC")]),
                           timeout=1)
    assert all([not get_tentacle_node(matrix.matrix_id, node_path).node_event.is_set()
                for node_path in
                [evaluator_1_path, evaluator_2_path, evaluator_3_path, evaluator_4_path, evaluator_5_path]])
    set_tentacle_value(matrix.matrix_id, evaluator_4_path, "TA", None)
    set_tentacle_value(matrix.matrix_id, evaluator_5_path, "TA", None)
    assert not all([not get_tentacle_node(matrix.matrix_id, node_path).node_event.is_set()
                    for node_path in
                    [evaluator_1_path, evaluator_2_path, evaluator_3_path, evaluator_4_path, evaluator_5_path]])
    assert all([get_tentacle_node(matrix.matrix_id, node_path).node_event.is_set()
                for node_path in
                [evaluator_4_path, evaluator_5_path]])
    await asyncio.wait_for(await get_nodes_clear_event(matrix.matrix_id,
                                                       [get_matrix_default_value_path(
                                                           tentacle_type="TA",
                                                           tentacle_name="Test-TA",
                                                           cryptocurrency="BTC")]),
                           timeout=1)
    assert all([not get_tentacle_node(matrix.matrix_id, node_path).node_event.is_set()
                for node_path in
                [evaluator_1_path, evaluator_2_path, evaluator_3_path, evaluator_4_path, evaluator_5_path]])
    Matrices.instance().del_matrix(matrix.matrix_id)
