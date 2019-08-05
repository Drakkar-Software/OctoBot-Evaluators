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
from typing import NewType, Dict, Union

from octobot_evaluators.enums import EvaluatorMatrixTypes

MatrixValueType = NewType('MatrixValueType', Union[str, int, float])
MatrixType = NewType('MatrixType', Dict[str, Dict[str, Union[MatrixValueType, Dict[str, MatrixValueType]]]])

CONFIG_EVALUATOR = "evaluator"
CONFIG_FORCED_EVALUATOR = "forced_evaluator"
CONFIG_EVALUATOR_SOCIAL = "Social"
CONFIG_EVALUATOR_REALTIME = "RealTime"
CONFIG_EVALUATOR_TA = "TA"
CONFIG_EVALUATOR_STRATEGIES = "Strategies"
START_PENDING_EVAL_NOTE = "0"  # force exception
INIT_EVAL_NOTE = 0
START_EVAL_PERTINENCE = 1
MAX_TA_EVAL_TIME_SECONDS = 0.1
EVALUATOR_EVAL_DEFAULT_TYPE = float


def default_matrix_value():
    return {
        EvaluatorMatrixTypes.TA: {},
        EvaluatorMatrixTypes.SOCIAL: {},
        EvaluatorMatrixTypes.REAL_TIME: {},
        EvaluatorMatrixTypes.STRATEGIES: {}
    }
