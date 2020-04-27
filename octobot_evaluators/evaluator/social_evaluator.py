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
        self.exchange_id = None

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
                    # store exchange_id to use it later for evaluation timestamps
                    from octobot_trading.api.exchange import get_exchange_id_from_matrix_id
                    self.exchange_id = get_exchange_id_from_matrix_id(self.exchange_name, self.matrix_id)
                    return True
            except ImportError as e:
                self.logger.exception(e, True, "Can't start: requires OctoBot-Services and OctoBot-Trading "
                                               "package installed")
        return False

    def get_current_exchange_time(self):
        try:
            from octobot_trading.api.exchange import get_exchange_current_time, \
                get_exchange_manager_from_exchange_name_and_id
            if self.exchange_id is not None:
                return get_exchange_current_time(
                    get_exchange_manager_from_exchange_name_and_id(
                        self.exchange_name,
                        self.exchange_id
                    )
                )
        except ImportError:
            self.logger.error(f"Can't get current exchange time: requires OctoBot-Trading package installed")
        return None

    def _get_tentacle_registration_topic(self, all_symbols_by_crypto_currencies, time_frames, real_time_time_frames):
        currencies, _, _ = super()._get_tentacle_registration_topic(all_symbols_by_crypto_currencies,
                                                                    time_frames,
                                                                    real_time_time_frames)
        symbols = [self.symbol]
        to_handle_time_frames = [self.time_frame]
        # by default no symbol registration for social evaluators
        # by default no time frame registration for social evaluators
        return currencies, symbols, to_handle_time_frames

    @abstractmethod
    async def _feed_callback(self, *args):
        raise NotImplementedError("_feed_callback is not implemented")
