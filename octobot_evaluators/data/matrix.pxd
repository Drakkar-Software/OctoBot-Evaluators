# cython: language_level=3
#  Drakkar-Software OctoBot-Matrixs
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


cdef class EvaluatorMatrix:
    cdef dict evaluator_eval_types

    cdef public dict matrix

    cdef void __get_evaluator_matrix(self, str evaluator_name, str evaluator_type)
    cdef void __set_evaluator_eval_type(self, str evaluator_name, str evaluator_eval_type):

    @staticmethod
    cdef void __init_matrix(dict evaluator_matrix, str symbol, str exchange_name)

    cpdef object get_eval_note(self,
                      str evaluator_name,
                      str exchange_name = *,
                      str symbol = *,
                      object time_frame = *):
    cpdef str get_evaluator_eval_type(self, str evaluator_name)
    cpdef void set_eval(self,
                  str evaluator_name,
                  str evaluator_type,
                  object value,
                  str exchange_name = *,
                  str symbol = *,
                  object time_frame = *)
