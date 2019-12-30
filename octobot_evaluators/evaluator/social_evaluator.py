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

import os
from abc import abstractmethod

from octobot_channels.channels.channel import get_chan
from octobot_commons.config import load_config

from octobot_evaluators.constants import CONFIG_EVALUATOR_SOCIAL
from octobot_evaluators.evaluator import AbstractEvaluator
from octobot_services.api.service_feeds import get_service_feed


class SocialEvaluator(AbstractEvaluator):
    __metaclass__ = AbstractEvaluator
    SERVICE_FEED_CLASS = None

    def __init__(self):
        super().__init__()
        self.load_config()

    @classmethod
    def get_config_tentacle_type(cls) -> str:
        return CONFIG_EVALUATOR_SOCIAL

    @classmethod
    def get_is_symbol_widlcard(cls) -> bool:
        return False

    def load_config(self):
        config_file = self.get_config_file_name()
        # try with this class name
        if os.path.isfile(config_file):
            self.specific_config = load_config(config_file)
        else:
            # if it's not possible, try with any super-class' config file
            for super_class in self.get_parent_evaluator_classes(SocialEvaluator):
                super_class_config_file = super_class.get_config_file_name()
                if os.path.isfile(super_class_config_file):
                    self.specific_config = load_config(super_class_config_file)
                    return
        # set default config if nothing found
        if not self.specific_config:
            self.set_default_config()

    # Override if no service feed is required for a social evaluator
    async def start(self) -> None:
        if self.SERVICE_FEED_CLASS is None:
            self.logger.error("SERVICE_FEED_CLASS is required to use a service feed. Consumer can't start.")
        else:
            get_service_feed(self.SERVICE_FEED_CLASS).update_feed_config(self.specific_config)
            await get_chan(self.SERVICE_FEED_CLASS.FEED_CHANNEL.get_name()).new_consumer(self._feed_callback)

    @abstractmethod
    async def _feed_callback(self, *args):
        raise NotImplemented("_feed_callback is not implemented")
