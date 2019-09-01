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
from octobot_channels.channels import del_chan, get_chan

from octobot_evaluators.api import create_matrix_channels
from octobot_evaluators.channels import MATRIX_CHANNEL


async def matrix_callback(evaluator_name,
                          evaluator_type,
                          eval_note,
                          exchange_name,
                          symbol,
                          time_frame):
    pass


@pytest.mark.asyncio
async def test_evaluator_channel_creation():
    del_chan(MATRIX_CHANNEL)
    await create_matrix_channels()
    await get_chan(MATRIX_CHANNEL).new_consumer(matrix_callback)
    await get_chan(MATRIX_CHANNEL).stop()
