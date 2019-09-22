# cython: language_level=3
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
from octobot_commons.singleton.singleton_class cimport Singleton

cdef class EvaluatorMatrix(Singleton):
    cdef dict evaluator_eval_types

    cdef public dict matrix

    cdef dict __get_evaluator_matrix(self, str evaluator_name, str evaluator_type)
    cdef void __set_evaluator_eval_type(self, str evaluator_name, object evaluator_eval_type)

    @staticmethod
    cdef void __init_matrix(dict evaluator_matrix, str symbol, str exchange_name)

    cpdef void set_eval(self,
                      str evaluator_name,
                      object evaluator_type,    # EvaluatorMatrixTypes object
                      object value,             # MatrixValueType object
                      str exchange_name = *,
                      str symbol = *,
                      object time_frame = *)    # TimeFrames object

    cpdef object get_eval_note(self,
                      str evaluator_name,
                      str exchange_name = *,
                      str symbol = *,
                      object time_frame = *)

    cpdef object get_evaluator_eval_type(self, str evaluator_name)
    cpdef list get_evaluators_name_from_symbol(self, str symbol)
    cpdef list get_evaluators_name_from_exchange(self, str exchange_name)
    cpdef list get_evaluators_name_from_symbol_and_exchange(self, str symbol, str exchange_name)
    cpdef list get_evaluators_name_from_symbol_exchange_and_time_frame(self, str symbol, str exchange_name, object time_frame)
