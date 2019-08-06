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

from octobot_commons.enums import TimeFrames
from octobot_commons.singleton import Singleton

from octobot_evaluators.constants import default_matrix_value, MatrixValueType, START_PENDING_EVAL_NOTE
from octobot_evaluators.enums import EvaluatorMatrixTypes
from octobot_evaluators.util import check_valid_eval_note


@Singleton
class EvaluatorMatrix:
    """
    EvaluatorMatrix dataclass store evaluation data in a matrix represented by a dictionnary
    """

    def __init__(self, config):
        self.config = config
        self.matrix = default_matrix_value()
        self.evaluator_eval_types = {}

    # setters
    def set_eval(self,
                 evaluator_name: str,
                 evaluator_type: EvaluatorMatrixTypes,
                 value: MatrixValueType,
                 exchange_name: str = None,
                 symbol: str = None,
                 time_frame: TimeFrames = None) -> None:
        """

        :param evaluator_type:
        :param evaluator_name:
        :param value:
        :param exchange_name:
        :param symbol:
        :param time_frame:
        :return: None
        """

        evaluator_matrix: dict = self.__get_evaluator_matrix(evaluator_name, evaluator_type)

        try:
            if symbol:
                if exchange_name:
                    if time_frame:
                        self.matrix[evaluator_name][symbol][exchange_name][time_frame] = value
                    else:
                        self.matrix[evaluator_name][symbol][exchange_name] = value
                else:
                    self.matrix[evaluator_name][symbol] = value
            else:
                self.matrix[evaluator_name] = value
        except KeyError:
            self.__init_matrix(evaluator_matrix, symbol, exchange_name)
            self.set_eval(evaluator_name, evaluator_type, value, exchange_name, symbol, time_frame)

    def __get_evaluator_matrix(self, evaluator_name, evaluator_type):
        """

        :param evaluator_name:
        :param evaluator_type:
        :return:
        """
        try:
            return self.matrix[evaluator_name]
        except KeyError:
            self.matrix[evaluator_name] = {}
            self.__set_evaluator_eval_type(evaluator_name, evaluator_type)
            return self.matrix[evaluator_name]

    @staticmethod
    def __init_matrix(evaluator_matrix, symbol, exchange_name) -> None:
        """

        :param evaluator_matrix:
        :param symbol:
        :param exchange_name:
        :return:
        """

        if symbol not in evaluator_matrix:
            evaluator_matrix[symbol] = {}

        if exchange_name not in evaluator_matrix[symbol]:
            evaluator_matrix[symbol][exchange_name] = {}

    def __set_evaluator_eval_type(self,
                                  evaluator_name: str,
                                  evaluator_eval_type: EvaluatorMatrixTypes) -> None:
        """

        :param evaluator_name:
        :param evaluator_eval_type:
        :return:
        """
        try:
            self.evaluator_eval_types[evaluator_name]
        except KeyError:
            self.evaluator_eval_types[evaluator_name] = evaluator_eval_type

    # getters
    def get_eval_note(self,
                      evaluator_name: str,
                      exchange_name: str = None,
                      symbol: str = None,
                      time_frame: TimeFrames = None) -> MatrixValueType:
        """

        :param evaluator_name:
        :param exchange_name:
        :param symbol:
        :param time_frame:
        :return:
        """
        try:
            if symbol:
                if exchange_name:
                    if time_frame:
                        eval_note = self.matrix[evaluator_name][symbol][exchange_name][time_frame]
                    else:
                        eval_note = self.matrix[evaluator_name][symbol][exchange_name]
                else:
                    eval_note = self.matrix[evaluator_name][symbol]
            else:
                eval_note = self.matrix[evaluator_name]

            if check_valid_eval_note(eval_note):
                return eval_note
        except KeyError:
            pass
        return START_PENDING_EVAL_NOTE

    def get_evaluator_eval_type(self, evaluator_name: str):
        """

        :param evaluator_name:
        :return:
        """
        try:
            return self.evaluator_eval_types[evaluator_name]
        except KeyError:
            return None
