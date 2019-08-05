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
#  Lesser General License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library.
import logging

from octobot_commons.constants import CONFIG_TIME_FRAME
from octobot_commons.enums import TimeFrames

from octobot_commons.logging.logging_util import get_logger
from octobot_evaluators.api import create_all_type_evaluators

config = {
    "crypto-currencies": {
        "Bitcoin": {
            "pairs": [
                "BTC/USDT"
            ]
        },
        "Ethereum": {
            "pairs": [
                "ETH/USDT"
            ]
        }
    },
    "exchanges": {},
    CONFIG_TIME_FRAME: {
        TimeFrames.ONE_MINUTE,
        TimeFrames.ONE_HOUR
    }
}

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    get_logger().info("starting...")

    create_all_type_evaluators(config, "test", "BTC/USDT", TimeFrames.ONE_HOUR)
