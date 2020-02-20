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
from octobot_commons.logging.logging_util import get_logger

from .abstract_evaluator import *
from .realtime_evaluator import *
from .social_evaluator import *
from .strategy_evaluator import *
from .TA_evaluator import *

try:
    from tentacles.Evaluator.RealTime import *
    from tentacles.Evaluator.Social import *
    from tentacles.Evaluator.Strategies import *
    from tentacles.Evaluator.TA import *
except ModuleNotFoundError as e:
    get_logger("Evaluator").error(f"tentacles folder not found raised a ModuleNotFoundError exception : {e}")
