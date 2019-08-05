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
from dataclasses import dataclass, field

from typing import Dict, Any

from octobot_commons.enums import TimeFrames

from octobot_evaluators.constants import MatrixType, default_matrix_value, MatrixValueType
from octobot_evaluators.enums import EvaluatorMatrixTypes
from octobot_evaluators.util import check_valid_eval_note


@dataclass
class EvaluatorMatrix:
    """
    EvaluatorMatrix dataclass store evaluation data in a matrix represented by a dictionnary
    """
    config: dict
    matrix: MatrixType = field(init=False, repr=False, default_factory=default_matrix_value)
    evaluator_eval_types: Dict[str, Any] = field(init=False, repr=False, default_factory=dict)

    # setters
    def set_eval(self,
                 matrix_type: EvaluatorMatrixTypes,
                 evaluator_name: str,
                 value: MatrixValueType,
                 time_frame: TimeFrames = None) -> None:
        """

        :param matrix_type:
        :param evaluator_name:
        :param value:
        :param time_frame:
        :return:
        """
        if evaluator_name not in self.matrix[matrix_type]:
            self.matrix[matrix_type][evaluator_name] = {}

        if time_frame:
            self.matrix[matrix_type][evaluator_name][time_frame] = value
        else:
            self.matrix[matrix_type][evaluator_name] = value

    # getters
    def get_type_evals(self,
                       matrix_type: EvaluatorMatrixTypes):
        """

        :param matrix_type:
        :return:
        """
        return self.matrix[matrix_type]

    @staticmethod
    def get_eval_note(matrix: MatrixType,
                      matrix_type: EvaluatorMatrixTypes,
                      evaluator_name: str,
                      time_frame: TimeFrames = None) -> MatrixValueType:
        """

        :param matrix:
        :param matrix_type:
        :param evaluator_name:
        :param time_frame:
        :return:
        """
        if matrix_type in matrix and evaluator_name in matrix[matrix_type]:
            if time_frame is not None:
                if isinstance(matrix[matrix_type][evaluator_name], dict) \
                        and time_frame in matrix[matrix_type][evaluator_name]:
                    eval_note = matrix[matrix_type][evaluator_name][time_frame]
                    if check_valid_eval_note(eval_note):
                        return eval_note
            else:
                eval_note = matrix[matrix_type][evaluator_name]
                if check_valid_eval_note(eval_note):
                    return eval_note
        return None

    def get_matrix(self) -> MatrixType:
        """

        :return:
        """
        return self.matrix

    def set_evaluator_eval_type(self,
                                evaluator_name: str,
                                evaluator_eval_type: Any) -> None:
        """

        :param evaluator_name:
        :param evaluator_eval_type:
        :return:
        """
        self.evaluator_eval_types[evaluator_name] = evaluator_eval_type

    def get_evaluator_eval_type(self,
                                evaluator_name: str) -> Any:
        """

        :param evaluator_name:
        :return:
        """
        if evaluator_name in self.evaluator_eval_types:
            return self.evaluator_eval_types[evaluator_name]
        return None
