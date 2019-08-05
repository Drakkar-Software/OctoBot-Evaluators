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
from octobot_commons.constants import CONFIG_TIME_FRAME
from octobot_commons.tentacles_management.advanced_manager import AdvancedManager
from octobot_commons.time_frame_manager import TimeFrameManager

from octobot_evaluators.evaluator import StrategiesEvaluator


def init_time_frames_from_strategies(config):
    time_frame_list = set()
    for strategies_eval_class in AdvancedManager.create_advanced_evaluator_types_list(StrategiesEvaluator, config):
        if strategies_eval_class.is_enabled(config, False):
            for time_frame in strategies_eval_class.get_required_time_frames(config):
                time_frame_list.add(time_frame)
    time_frame_list = TimeFrameManager.sort_time_frames(time_frame_list)
    config[CONFIG_TIME_FRAME] = time_frame_list
