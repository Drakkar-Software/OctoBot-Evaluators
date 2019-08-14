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
from octobot_commons.singleton.singleton_class import Singleton

from octobot_evaluators.constants import default_matrix_value, MatrixValueType, START_PENDING_EVAL_NOTE
from octobot_evaluators.util import check_valid_eval_note


class EvaluatorMatrix(Singleton):
    """
    EvaluatorMatrix dataclass store evaluation data in a matrix represented by a dictionary
    """

    def __init__(self):
        self.matrix = default_matrix_value()
        self.evaluator_eval_types = {}

    def set_eval(self,
                 evaluator_name,
                 evaluator_type,
                 value,
                 exchange_name=None,
                 symbol=None,
                 time_frame=None) -> None:
        """
        Set the new eval note to the matrix corresponding to evaluator note params
        :param evaluator_type: the evaluator type ("TA", "Social", ...)
        :param evaluator_name: the evaluator name
        :param value: the eval note to add to the matrix
        :param exchange_name: the evaluation exchange name
        :param symbol: the evaluation symbol
        :param time_frame: the evaluation time frame
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
            EvaluatorMatrix.__init_matrix(evaluator_matrix, symbol, exchange_name)
            self.set_eval(evaluator_name, evaluator_type, value, exchange_name, symbol, time_frame)

    def __get_evaluator_matrix(self, evaluator_name, evaluator_type) -> dict:
        """
        Returns the matrix of the evaluator from its type
        :param evaluator_name: evaluator name
        :param evaluator_type: evaluator type
        :return: evaluator matrix
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
        Creates the matrix corresponding to the params if not exists
        :param evaluator_matrix: matrix evaluator dictionary
        :param symbol: evaluator matrix symbol
        :param exchange_name: evaluator matrix exchange name
        :return: None
        """

        if symbol not in evaluator_matrix:
            evaluator_matrix[symbol] = {}

        if exchange_name not in evaluator_matrix[symbol]:
            evaluator_matrix[symbol][exchange_name] = {}

    def __set_evaluator_eval_type(self, evaluator_name, evaluator_eval_type) -> None:
        """
        Set the evaluator evaluation type in evaluator_eval_types if not exists
        :param evaluator_name: the evaluator name
        :param evaluator_eval_type: the evaluator evaluation type
        :return: None
        """
        try:
            self.evaluator_eval_types[evaluator_name]
        except KeyError:
            self.evaluator_eval_types[evaluator_name] = evaluator_eval_type

    # getters
    def get_eval_note(self,
                      evaluator_name,
                      exchange_name=None,
                      symbol=None,
                      time_frame=None) -> MatrixValueType:
        """
        Returns the evaluator eval note corresponding to params
        :param evaluator_name: the evaluator name
        :param exchange_name: the evaluator exchange name
        :param symbol: the evaluator symbol
        :param time_frame: the evaluator time frame
        :return: MatrixValueType
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

    def get_evaluator_eval_type(self, evaluator_name) -> object:
        """
        Return the evaluator eval type from evaluator_eval_types list
        :param evaluator_name: the evaluator name
        :return: the evaluator eval type
        """
        try:
            return self.evaluator_eval_types[evaluator_name]
        except KeyError:
            return None
