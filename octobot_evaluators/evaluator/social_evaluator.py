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
from abc import abstractmethod

from octobot_channels.channels.channel import get_chan
from octobot_evaluators.evaluator import AbstractEvaluator
from octobot_tentacles_manager.api.configurator import get_tentacle_config


class SocialEvaluator(AbstractEvaluator):
    __metaclass__ = AbstractEvaluator
    SERVICE_FEED_CLASS = None

    def __init__(self):
        super().__init__()
        self.load_config()

    @classmethod
    def get_is_symbol_widlcard(cls) -> bool:
        return False

    def load_config(self):
        # try with this class name
        self.specific_config = get_tentacle_config(self.__class__)
        if not self.specific_config:
            # if nothing in config, try with any super-class' config file
            for super_class in self.get_parent_evaluator_classes(SocialEvaluator):
                self.specific_config = get_tentacle_config(super_class)
                if self.specific_config:
                    return
        # set default config if nothing found
        if not self.specific_config:
            self.set_default_config()

    # Override if no service feed is required for a social evaluator
    async def start(self, bot_id: str) -> bool:
        """
        :return: success of the evaluator's start
        """
        if self.SERVICE_FEED_CLASS is None:
            self.logger.error("SERVICE_FEED_CLASS is required to use a service feed. Consumer can't start.")
        else:
            await super().start(bot_id)
            try:
                from octobot_services.api.service_feeds import get_service_feed
                service_feed = get_service_feed(self.SERVICE_FEED_CLASS, bot_id)
                if service_feed is not None:
                    service_feed.update_feed_config(self.specific_config)
                    await get_chan(service_feed.FEED_CHANNEL.get_name()).new_consumer(self._feed_callback)
                    return True
            except ImportError as e:
                self.logger.exception(e, True, "Can't start: requires OctoBot-Services package installed")
        return False

    @abstractmethod
    async def _feed_callback(self, *args):
        raise NotImplemented("_feed_callback is not implemented")
