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
import abc 

import async_channel.channels as channels

import octobot_tentacles_manager.api as api

import octobot_evaluators.evaluators as evaluator


class SocialEvaluator(evaluator.AbstractEvaluator):
    __metaclass__ = evaluator.AbstractEvaluator
    SERVICE_FEED_CLASS = None

    def __init__(self, tentacles_setup_config):
        super().__init__(tentacles_setup_config)
        self.load_config()
        self.exchange_id = None

    def load_config(self):
        try:
            # try with this class name
            self.specific_config = api.get_tentacle_config(self.tentacles_setup_config, self.__class__)
        except KeyError:
            self.specific_config = None  # tentacle config not found
        if not self.specific_config:
            # if nothing in config, try with any super-class' config file
            for super_class in self.get_parent_evaluator_classes(SocialEvaluator):
                try:
                    self.specific_config = api.get_tentacle_config(self.tentacles_setup_config, super_class)
                    if self.specific_config:
                        return
                except KeyError:
                    pass  # super_class tentacle config not found
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
                import octobot_services.api as service_api
                service_feed = service_api.get_service_feed(self.SERVICE_FEED_CLASS, bot_id)
                if service_feed is not None:
                    service_feed.update_feed_config(self.specific_config)
                    await channels.get_chan(service_feed.FEED_CHANNEL.get_name()).new_consumer(self._feed_callback)
                    # store exchange_id to use it later for evaluation timestamps
                    import octobot_trading.api as exchange_api
                    self.exchange_id = exchange_api.get_exchange_id_from_matrix_id(self.exchange_name, self.matrix_id)
                    return True
            except ImportError as e:
                self.logger.exception(e, True, "Can't start: requires OctoBot-Services and OctoBot-Trading "
                                               "package installed")
        return False

    def get_current_exchange_time(self):
        try:
            import octobot_trading.api as exchange_api
            if self.exchange_id is not None:
                return exchange_api.get_exchange_current_time(
                    exchange_api.get_exchange_manager_from_exchange_name_and_id(
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
        # by default no time frame re+gistration for social evaluators
        return currencies, symbols, to_handle_time_frames

    @abc.abstractmethod
    async def _feed_callback(self, *args):
        raise NotImplementedError("_feed_callback is not implemented")
