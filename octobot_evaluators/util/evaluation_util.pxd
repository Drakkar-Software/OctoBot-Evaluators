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

cpdef double get_eval_time(list full_candle=*, object time_frame=*, list partial_candle=*, list kline=*)
cpdef object get_shortest_time_frame(object ideal_time_frame, object preferred_available_time_frames, object others)
cpdef object local_trading_context(object evaluator, str symbol, object time_frame, object trigger_cache_timestamp,
                                   str cryptocurrency=*, str exchange=*, str exchange_id=*,
                                   object trigger_source=*, object trigger_value=*)
cpdef object local_cache_client(object evaluator, str symbol, object time_frame, str exchange_name=*)
cpdef int get_required_candles_count(object trading_mode_class, object tentacles_setup_config)
