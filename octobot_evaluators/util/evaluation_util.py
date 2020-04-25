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
from octobot_commons.enums import PriceIndexes, TimeFramesMinutes, TimeFrames
from octobot_commons.constants import MINUTE_TO_SECONDS


def get_eval_time(full_candle=None, time_frame=None, partial_candle=None, kline=None):
    if full_candle is not None and time_frame is not None:
        # add one full time frame seconds since a full candle is available when the next has started
        return full_candle[PriceIndexes.IND_PRICE_TIME.value] + \
               TimeFramesMinutes[TimeFrames(time_frame)] * MINUTE_TO_SECONDS
    if partial_candle is not None:
        return partial_candle[PriceIndexes.IND_PRICE_TIME.value]
    if kline is not None:
        return kline[PriceIndexes.IND_PRICE_TIME.value]
    raise ValueError("Invalid arguments")


def get_shortest_time_frame(ideal_time_frame, preferred_available_time_frames, others):
    if ideal_time_frame in preferred_available_time_frames:
        return ideal_time_frame
    if preferred_available_time_frames:
        return preferred_available_time_frames[0]
    else:
        return others[0]
