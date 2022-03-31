# cython: language_level=3
#  Drakkar-Software OctoBot-Trading
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
#  Lesser General License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library.

cdef str _get_cryptocurrency_name(object evaluator_class,
                                  dict crypto_currency_name_by_crypto_currencies,
                                  str cryptocurrency)
cdef list _get_cryptocurrencies_to_create(object evaluator_class,
                                          dict crypto_currency_name_by_crypto_currencies)
cdef list _get_symbols_to_create(object evaluator_class,
                                 dict symbols_by_crypto_currencies,
                                 str cryptocurrency,
                                 list symbols)
cdef list _get_time_frames_to_create(object evaluator_class,
                                     list time_frames)

cpdef tuple _extract_traded_pairs(dict symbols_by_crypto_currencies, str exchange_name, str matrix_id, object exchange_api)
cpdef set _filter_pairs(list pairs, str required_ticker, object exchange_api, object exchange_manager)
cpdef object create_temporary_evaluator_with_local_config(object evaluator_class, object tentacles_setup_config, object specific_config, bint should_trigger_post_init=*)
cpdef object _instantiate_evaluator(object evaluator_class, object tentacles_setup_config, bint should_trigger_post_init)
