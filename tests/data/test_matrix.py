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
import pytest

from octobot_evaluators.data.matrix import Matrix, get_tentacle_path, get_tentacle_value_path


def test_default_matrix():
    matrix = Matrix()
    assert matrix.matrix.root.children == {}


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
async def test_get_node_at_path():
    matrix = Matrix()
    test_node_path = ["test-path", "test-path-2", "test-path3", 4]
    created_node = matrix.matrix.get_or_create_node(test_node_path)
    assert matrix.get_node_at_path(test_node_path) is created_node


@pytest.mark.asyncio
async def test_set_tentacle_value():
    matrix = Matrix()
    test_node_path = ["test-path", "test-path-2"]
    matrix.set_tentacle_value("test-value", str, test_node_path)
    assert matrix.matrix.get_or_create_node(test_node_path).node_type == str
    assert matrix.matrix.get_or_create_node(test_node_path).node_value == "test-value"


@pytest.mark.asyncio
async def test_get_node_children_at_path():
    matrix = Matrix()
    test_node_1_path = ["test-path-parent", "test-path-child", "test-path-1"]
    test_node_2_path = ["test-path-parent", "test-path-child", "test-path-2"]
    test_node_3_path = ["test-path-parent", "test-path-child", "test-path-3"]
    created_node_1 = matrix.matrix.get_or_create_node(test_node_1_path)
    created_node_2 = matrix.matrix.get_or_create_node(test_node_2_path)
    created_node_3 = matrix.matrix.get_or_create_node(test_node_3_path)
    assert matrix.get_node_children_at_path(["test-path-parent", "test-path-child"]) == [created_node_1,
                                                                                         created_node_2,
                                                                                         created_node_3]


@pytest.mark.asyncio
async def test_get_tentacle_nodes_on_root():
    matrix = Matrix()
    created_node_1 = matrix.matrix.get_or_create_node(
        get_tentacle_path(tentacle_type="NO_TYPE", tentacle_name="Test-TA"))
    created_node_2 = matrix.matrix.get_or_create_node(
        get_tentacle_path(exchange_name="binance", tentacle_name="Test-TA-2"))
    created_node_3 = matrix.matrix.get_or_create_node(get_tentacle_path(tentacle_name="Test-TA-3"))
    assert matrix.get_tentacle_nodes() == [matrix.get_node_at_path(get_tentacle_path(tentacle_type="NO_TYPE")),
                                           matrix.get_node_at_path(get_tentacle_path(exchange_name="binance")),
                                           created_node_3]

    with pytest.raises(AttributeError):
        assert matrix.get_tentacle_nodes(tentacle_type="TA")
        assert matrix.get_tentacle_nodes(exchange_name="bitfinex")
    assert matrix.get_tentacle_nodes(tentacle_type="NO_TYPE") == [created_node_1]
    assert matrix.get_tentacle_nodes(exchange_name="binance") == [created_node_2]


@pytest.mark.asyncio
async def test_get_tentacle_nodes_on_tentacle_type():
    matrix = Matrix()
    created_node_1 = matrix.matrix.get_or_create_node(
        get_tentacle_path(tentacle_type="NO_TYPE", tentacle_name="Test-TA"))
    created_node_2 = matrix.matrix.get_or_create_node(
        get_tentacle_path(tentacle_type="TEST_TYPE", tentacle_name="Test-TA-2"))

    with pytest.raises(AttributeError):
        assert matrix.get_tentacle_nodes(tentacle_type="TA") == []
    assert matrix.get_tentacle_nodes(tentacle_type="NO_TYPE") == [created_node_1]
    assert matrix.get_tentacle_nodes(tentacle_type="TEST_TYPE") == [created_node_2]


@pytest.mark.asyncio
async def test_get_tentacle_nodes_on_exchange_name_and_tentacle_type():
    matrix = Matrix()
    created_node_1 = matrix.matrix.get_or_create_node(get_tentacle_path(tentacle_type="NO_TYPE",
                                                                        tentacle_name="Test-TA",
                                                                        exchange_name="binance"))
    created_node_2 = matrix.matrix.get_or_create_node(get_tentacle_path(tentacle_type="TEST_TYPE",
                                                                        tentacle_name="Test-TA-2",
                                                                        exchange_name="binance"))
    assert matrix.get_tentacle_nodes(exchange_name="binance") == [
        matrix.get_node_at_path(get_tentacle_path(exchange_name="binance",
                                                  tentacle_type="NO_TYPE")),
        matrix.get_node_at_path(get_tentacle_path(exchange_name="binance",
                                                  tentacle_type="TEST_TYPE"))]
    assert matrix.get_tentacle_nodes(exchange_name="binance", tentacle_type="NO_TYPE") == [created_node_1]
    assert matrix.get_tentacle_nodes(exchange_name="binance", tentacle_type="TEST_TYPE") == [created_node_2]

    with pytest.raises(AttributeError):
        assert matrix.get_tentacle_nodes(exchange_name="bitfinex") == []


@pytest.mark.asyncio
async def test_get_tentacle_nodes_on_exchange_name():
    matrix = Matrix()
    created_node_1 = matrix.matrix.get_or_create_node(get_tentacle_path(tentacle_name="Test-TA",
                                                                        exchange_name="binance"))
    created_node_2 = matrix.matrix.get_or_create_node(get_tentacle_path(tentacle_name="Test-TA-2",
                                                                        exchange_name="binance"))

    with pytest.raises(AttributeError):
        assert matrix.get_tentacle_nodes(exchange_name="bitfinex") == []
        assert matrix.get_tentacle_nodes(tentacle_type="NO_TYPE") == []
    assert matrix.get_tentacle_nodes(exchange_name="binance") == [created_node_1, created_node_2]


@pytest.mark.asyncio
async def test_get_tentacle_nodes_on_multiple_tentacle_type():
    matrix = Matrix()
    created_node_1 = matrix.matrix.get_or_create_node(get_tentacle_path(tentacle_type="TA", tentacle_name="Test-TA"))
    created_node_2 = matrix.matrix.get_or_create_node(get_tentacle_path(tentacle_type="TA", tentacle_name="Test-TA-2"))
    created_node_3 = matrix.matrix.get_or_create_node(get_tentacle_path(tentacle_type="TA", tentacle_name="Test-TA-3"))
    assert matrix.get_tentacle_nodes(tentacle_type="TA") == [created_node_1, created_node_2, created_node_3]


@pytest.mark.asyncio
async def test_get_tentacle_nodes_on_multiple_tentacle_type_and_exchange_name():
    matrix = Matrix()
    created_node_1 = matrix.matrix.get_or_create_node(get_tentacle_path(tentacle_type="TA",
                                                                        tentacle_name="Test-TA",
                                                                        exchange_name="binance"))
    created_node_2 = matrix.matrix.get_or_create_node(get_tentacle_path(tentacle_type="TA",
                                                                        tentacle_name="Test-TA-2",
                                                                        exchange_name="binance"))
    created_node_3 = matrix.matrix.get_or_create_node(get_tentacle_path(tentacle_type="TA",
                                                                        tentacle_name="Test-TA-3",
                                                                        exchange_name="binance"))
    assert matrix.get_tentacle_nodes(exchange_name="binance", tentacle_type="TA") == [created_node_1,
                                                                                      created_node_2,
                                                                                      created_node_3]


@pytest.mark.asyncio
async def test_get_tentacle_nodes_mixed():
    matrix = Matrix()
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
    assert matrix.get_tentacle_nodes(exchange_name="binance", tentacle_type="TA") == [created_node_1, created_node_3]
    assert matrix.get_tentacle_nodes(exchange_name="binance", tentacle_type="TEST-TYPE") == [created_node_4]

    assert matrix.get_tentacle_nodes(exchange_name="bitfinex", tentacle_type="TEST-TYPE") == [created_node_5]

    assert matrix.get_tentacle_nodes(exchange_name="bitfinex") == [
        matrix.get_node_at_path(get_tentacle_path(exchange_name="bitfinex", tentacle_type="TA")),
        matrix.get_node_at_path(get_tentacle_path(exchange_name="bitfinex", tentacle_type="TEST-TYPE")),
        created_node_7]

    assert matrix.get_tentacle_nodes(tentacle_type="TEST-TYPE") == [created_node_6]

    assert matrix.get_tentacle_nodes(exchange_name="binance") == [
        matrix.get_node_at_path(get_tentacle_path(exchange_name="binance", tentacle_type="TA")),
        matrix.get_node_at_path(get_tentacle_path(exchange_name="binance", tentacle_type="TEST-TYPE")),
        created_node_9]


@pytest.mark.asyncio
async def test_get_tentacles_value_nodes_with_symbol():
    matrix = Matrix()
    created_node = matrix.matrix.get_or_create_node(get_tentacle_path(tentacle_type="TA", tentacle_name="Test-TA"))
    created_node_2 = matrix.matrix.get_or_create_node(get_tentacle_path(tentacle_type="TA", tentacle_name="Test-TA-2"))
    btc_node = matrix.matrix.get_or_create_node(get_tentacle_value_path(symbol="BTC"), starting_node=created_node)
    eth_node = matrix.matrix.get_or_create_node(get_tentacle_value_path(symbol="ETH"), starting_node=created_node)
    btc_node_2 = matrix.matrix.get_or_create_node(get_tentacle_value_path(symbol="BTC"), starting_node=created_node_2)
    assert matrix.get_tentacles_value_nodes(tentacle_nodes=[created_node, created_node_2],
                                            symbol="BTC") == [btc_node, btc_node_2]
    assert matrix.get_tentacles_value_nodes(tentacle_nodes=[created_node, created_node_2],
                                            symbol="ETH") == [eth_node]

# @pytest.mark.asyncio
# async def test_get_tentacles_value_nodes_with_time_frame():
#     matrix = Matrix()
#     assert get_tentacle_value_path(time_frame="1m") == ["1m"]
#     created_node_1 = matrix.get_node_at_path(get_tentacle_path(tentacle_type="TA", tentacle_name="Test-TA"))
#     created_node_2 = matrix.get_node_at_path(get_tentacle_path(tentacle_type="TA", tentacle_name="Test-TA-2"))
#     created_node_3 = matrix.get_node_at_path(get_tentacle_path(tentacle_type="TA", tentacle_name="Test-TA-3"))
#     assert matrix.get_tentacle_nodes(tentacle_type="TA") == [created_node_1, created_node_2, created_node_3]
#
#
# @pytest.mark.asyncio
# async def test_get_tentacles_value_nodes_with_symbol_and_time_frame():
#     matrix = Matrix()
#     assert get_tentacle_value_path(symbol="ETH", time_frame="1h") == ["ETH", "1h"]
#
#     created_node_1 = matrix.get_node_at_path(get_tentacle_path(tentacle_type="TA", tentacle_name="Test-TA"))
#     created_node_2 = matrix.get_node_at_path(get_tentacle_path(tentacle_type="TA", tentacle_name="Test-TA-2"))
#     created_node_3 = matrix.get_node_at_path(get_tentacle_path(tentacle_type="TA", tentacle_name="Test-TA-3"))
#     assert matrix.get_tentacle_nodes(tentacle_type="TA") == [created_node_1, created_node_2, created_node_3]
