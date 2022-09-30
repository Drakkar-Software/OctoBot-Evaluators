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
cimport octobot_commons.tree as tree

cimport octobot_evaluators.matrix.matrix as matrix

cpdef matrix.Matrix get_matrix(str matrix_id)
cpdef void set_tentacle_value(str matrix_id, list tentacle_path, object tentacle_type,
                              object tentacle_value, double timestamp=*)
cpdef tree.BaseTreeNode get_tentacle_node(str matrix_id, list tentacle_path)
cpdef tree.BaseTreeNode delete_tentacle_node(str matrix_id, list tentacle_path)
cpdef object get_tentacle_value(str matrix_id, list tentacle_path)
cpdef list get_matrix_default_value_path(str tentacle_name,
                                         object tentacle_type,
                                         str exchange_name=*,
                                         str cryptocurrency=*,
                                         str symbol=*,
                                         str time_frame=*)
cpdef object get_tentacle_eval_time(str matrix_id, list tentacle_path)
cpdef list get_tentacle_nodes(str matrix_id, str exchange_name=*, object tentacle_type=*, str tentacle_name=*)
cpdef dict get_node_children_by_names_at_path(str matrix_id, list tentacle_path, object starting_node=*)

cpdef list get_tentacles_value_nodes(str matrix_id,
                                     list tentacle_nodes,
                                     str cryptocurrency=*,
                                     str symbol=*,
                                     str time_frame=*)
cpdef object get_latest_eval_time(str matrix_id,
                                  str exchange_name=*,
                                  object tentacle_type=*,
                                  str cryptocurrency=*,
                                  str symbol=*,
                                  str time_frame=*)
cpdef list get_tentacle_path(str exchange_name=*, object tentacle_type=*, str tentacle_name=*)
cpdef list get_tentacle_value_path(str cryptocurrency=*, str symbol=*, str time_frame=*)
cpdef dict get_evaluations_by_evaluator(str matrix_id,
                                        str exchange_name=*,
                                        str tentacle_type=*,
                                        str cryptocurrency=*,
                                        str symbol=*,
                                        str time_frame=*,
                                        bint allow_missing=*,
                                        list allowed_values=*)
cpdef list get_available_time_frames(str matrix_id,
                                     str exchange_name,
                                     str tentacle_type,
                                     str cryptocurrency,
                                     str symbol)
cpdef list get_available_symbols(str matrix_id,
                                 str exchange_name,
                                 str cryptocurrency,
                                 str tentacle_type=*,
                                 str second_tentacle_type=*)
cpdef object is_tentacle_value_valid(str matrix_id, list tentacle_path, double timestamp=*, int delta=*)    # object to allow raising errors
cpdef bint is_tentacles_values_valid(str matrix_id, list tentacle_path_list, double timestamp=*, int delta=*)
