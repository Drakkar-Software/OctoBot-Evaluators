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
from typing import NewType, Union

from octobot_evaluators.enums import EvaluatorMatrixTypes

MatrixValueType = NewType('MatrixValueType', Union[str, int, float])

CONFIG_FORCED_EVALUATOR = "forced_evaluator"
START_EVAL_PERTINENCE = 1
MAX_TA_EVAL_TIME_SECONDS = 0.1
EVALUATOR_EVAL_DEFAULT_TYPE = float
STRATEGIES_REQUIRED_TIME_FRAME = "required_time_frames"
TRADING_MODE_REQUIRED_STRATEGIES = "required_strategies"
TRADING_MODE_REQUIRED_STRATEGIES_MIN_COUNT = "required_strategies_min_count"
STRATEGIES_REQUIRED_EVALUATORS = "required_evaluators"
CONFIG_FORCED_TIME_FRAME = "forced_time_frame"
TENTACLE_DEFAULT_CONFIG = "default_config"

EVALUATOR_CLASS_TYPE_MRO_INDEX = -4

MATRIX_CHANNEL = "Matrix"
MATRIX_CHANNELS = "MatrixChannels"

evaluator_class_str_to_matrix_type_dict = {
    "TAEvaluator": EvaluatorMatrixTypes.TA,
    "SocialEvaluator": EvaluatorMatrixTypes.SOCIAL,
    "RealTimeEvaluator": EvaluatorMatrixTypes.REAL_TIME,
    "StrategyEvaluator": EvaluatorMatrixTypes.STRATEGIES
}
