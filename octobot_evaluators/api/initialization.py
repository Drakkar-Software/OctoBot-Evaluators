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
from octobot_channels.channels.channel import set_chan
from octobot_channels.util import create_channel_instance
from octobot_commons.constants import CONFIG_TIME_FRAME
from octobot_commons.tentacles_management import create_advanced_types_list
from octobot_commons.time_frame_manager import sort_time_frames

from octobot_evaluators.channels import MatrixChannel
from octobot_evaluators.evaluator import StrategyEvaluator


def init_time_frames_from_strategies(config) -> None:
    time_frame_list = set()
    for strategies_eval_class in create_advanced_types_list(StrategyEvaluator, config):
        if strategies_eval_class.is_enabled(config, False):
            for time_frame in strategies_eval_class.get_required_time_frames(config):
                time_frame_list.add(time_frame)
    time_frame_list = sort_time_frames(time_frame_list)
    config[CONFIG_TIME_FRAME] = time_frame_list


async def create_matrix_channels() -> None:
    await create_channel_instance(MatrixChannel, set_chan)
