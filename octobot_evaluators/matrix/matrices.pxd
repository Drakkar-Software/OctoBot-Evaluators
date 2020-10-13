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
cimport octobot_commons.singleton as singleton

cimport octobot_evaluators.matrix as matrix

cdef class Matrices(singleton.Singleton):
    cdef public dict matrices

    cpdef void add_matrix(self, matrix.Matrix matrix)
    cpdef matrix.Matrix get_matrix(self, str matrix_id)
    cpdef void del_matrix(self, str matrix_id)
