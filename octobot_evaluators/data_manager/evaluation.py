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
from octobot_commons.evaluators_util import check_valid_eval_note, UNSET_EVAL_TYPE
from octobot_evaluators.constants import EVALUATOR_EVAL_DEFAULT_TYPE


class Evaluation:
    def __init__(self, evaluator_name, evaluation_value, evaluation_type, evaluation_time):
        self.evaluator_name = evaluator_name
        self.evaluation_value = evaluation_value
        self.evaluation_type = evaluation_type
        self.evaluation_time = evaluation_time

    def is_valid_evaluation(self, eval_type=UNSET_EVAL_TYPE, expected_eval_type=EVALUATOR_EVAL_DEFAULT_TYPE,
                            current_time=None, expiry_delay=None):
        if check_valid_eval_note(self.evaluation_value,
                                 eval_type=self.evaluation_type or eval_type,
                                 expected_eval_type=expected_eval_type):
            if current_time is None and expiry_delay is None:
                return True
            else:
                if self.evaluation_time is None:
                    return True
                else:
                    return self.evaluation_time + expiry_delay - current_time > 0
        return False

    def __str__(self):
        return f"[{self.evaluator_name}] evaluation: {self.evaluation_value} ({self.evaluation_type})" \
               f" set at {self.evaluation_time}"
