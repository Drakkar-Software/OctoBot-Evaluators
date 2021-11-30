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
import asyncio
import time

import octobot_tentacles_manager.api as api
import octobot_tentacles_manager.configuration as tm_configuration

import async_channel.constants as channel_constants
import async_channel.enums as channel_enums

import octobot_commons.constants as common_constants
import octobot_commons.tentacles_management as tentacles_management

import octobot_evaluators.evaluators.channel as evaluator_channels
import octobot_evaluators.constants as constants
import octobot_evaluators.matrix as matrix


class AbstractEvaluator(tentacles_management.AbstractTentacle):
    __metaclass__ = tentacles_management.AbstractTentacle

    def __init__(self, tentacles_setup_config: tm_configuration.TentaclesSetupConfiguration):
        super().__init__()
        # Evaluator matrix id
        self.matrix_id: str = None

        # Tentacle global setup configuration
        self.tentacles_setup_config: tm_configuration.TentaclesSetupConfiguration = tentacles_setup_config

        # Evaluator specific config (Is loaded from tentacle specific file)
        self.specific_config: dict = {}

        # If this indicator is enabled
        self.enabled: bool = self.is_enabled(self.tentacles_setup_config, False)

        # Specified Cryptocurrency for this instance (Should be None if wildcard)
        self.cryptocurrency: str = None

        # Specified Cryptocurrency name for this instance (Should be None if wildcard)
        self.cryptocurrency_name: str = None

        # Symbol is the cryptocurrency pair (Should be None if wildcard)
        self.symbol: str = None

        # Evaluation related exchange name
        self.exchange_name: str = None

        # Time_frame is the chart time frame (Should be None if wildcard)
        self.time_frame = None

        # history time represents the period of time of the indicator
        self.history_time = None

        # Evaluator category
        self.evaluator_type = None

        # Eval note will be set by the eval_impl at each call
        self.eval_note = common_constants.START_PENDING_EVAL_NOTE

        # Pertinence of indicator will be used with the eval_note to provide a relevancy
        self.pertinence = constants.START_EVAL_PERTINENCE

        # Active tells if this evaluator is currently activated (an evaluator can be paused)
        self.is_active: bool = True

        # Evaluators Channel consumer instance
        self.evaluators_consumer_instance = None

        self.eval_note_time_to_live = None
        self.eval_note_changed_time = None

        # Define evaluators default consumer priority level
        self.priority_level: int = channel_enums.ChannelConsumerPriorityLevels.MEDIUM.value

        # Local caches, to be initialized if necessary
        self.caches = {}

        # Other caches, these are managed by other tentacles,
        # they are referenced here for performances only
        self.remote_caches = {}

        self.consumers = []

    @staticmethod
    def get_eval_type():
        """
        Override this method when self.eval_note is other than : START_PENDING_EVAL_NOTE or float[-1:1]
        :return: type
        """
        return constants.EVALUATOR_EVAL_DEFAULT_TYPE

    @classmethod
    def get_is_cryptocurrencies_wildcard(cls) -> bool:
        """
        :return: True if the evaluator is not cryptocurrency dependant else False
        """
        return True

    @classmethod
    def get_is_cryptocurrency_name_wildcard(cls) -> bool:
        """
        :return: True if the evaluator is not cryptocurrency name dependant else False
        """
        return True

    @classmethod
    def get_is_symbol_wildcard(cls) -> bool:
        """
        :return: True if the evaluator is not symbol dependant else False
        """
        return True

    @classmethod
    def get_is_time_frame_wildcard(cls) -> bool:
        """
        :return: True if the evaluator is not time_frame dependant else False
        """
        return True

    @classmethod
    def get_required_candles_count(cls, tentacles_setup_config: tm_configuration.TentaclesSetupConfiguration):
        return api.get_tentacle_config(tentacles_setup_config, cls).get(
            common_constants.CONFIG_TENTACLES_REQUIRED_CANDLES_COUNT,
            -1
        )

    def get_context(self, symbol, time_frame, trigger_cache_timestamp,
                    cryptocurrency=None, exchange=None, exchange_id=None,
                    trigger_source=None, trigger_value=None):
        try:
            import octobot_trading.api as exchange_api
            import octobot_trading.modes.scripting_library as scripting_library
            exchange_manager = exchange_api.get_exchange_manager_from_exchange_name_and_id(
                exchange or self.exchange_name,
                exchange_id or exchange_api.get_exchange_id_from_matrix_id(self.exchange_name, self.matrix_id)
            )
            trading_modes = exchange_api.get_trading_modes(exchange_manager)
            trading_mode = trading_modes[0]
            for candidate_trading_mode in trading_modes:
                if exchange_api.get_trading_mode_symbol(candidate_trading_mode) == symbol:
                    trading_mode = candidate_trading_mode
            return scripting_library.Context(
                self,
                exchange_manager,
                exchange_api.get_trader(exchange_manager),
                exchange or self.exchange_name,
                symbol,
                self.matrix_id,
                cryptocurrency,
                symbol,
                time_frame,
                self.logger,
                *exchange_api.get_trading_mode_writers(trading_mode),
                trading_mode.__class__,
                trigger_cache_timestamp,
                trigger_source,
                trigger_value,
                None,
                None,
            )
        except ImportError:
            self.logger.error("Evaluator get_context requires OctoBot-Trading package installed")

    @staticmethod
    def invalidate_cache_on_code_change():
        # False is not yet supported
        return True

    @staticmethod
    def invalidate_cache_on_config_change():
        # False is not yet supported
        return True

    def use_cache(self):
        return False

    def _get_tentacle_registration_topic(self, all_symbols_by_crypto_currencies, time_frames, real_time_time_frames):
        currencies = [self.cryptocurrency]
        symbols = [self.symbol]
        available_time_frames = [self.time_frame]
        if self.get_is_cryptocurrencies_wildcard():
            currencies = all_symbols_by_crypto_currencies.keys()
        if self.get_is_symbol_wildcard():
            symbols = [currency_symbol
                       for currency_symbols in all_symbols_by_crypto_currencies.values()
                       for currency_symbol in currency_symbols]
        if self.get_is_time_frame_wildcard():
            available_time_frames = time_frames
        return currencies, symbols, available_time_frames

    def initialize(self, all_symbols_by_crypto_currencies, time_frames, real_time_time_frames):
        currencies, symbols, time_frames = self._get_tentacle_registration_topic(all_symbols_by_crypto_currencies,
                                                                                 time_frames,
                                                                                 real_time_time_frames)
        for currency in currencies:
            for symbol in symbols:
                if symbol is None or symbol in all_symbols_by_crypto_currencies[currency]:
                    for time_frame in time_frames:
                        matrix.set_tentacle_value(
                            matrix_id=self.matrix_id,
                            tentacle_type=self.get_eval_type(),
                            tentacle_value=None,
                            tentacle_path=matrix.get_matrix_default_value_path(
                                exchange_name=self.exchange_name,
                                tentacle_type=self.evaluator_type.value,
                                tentacle_name=self.get_name(),
                                cryptocurrency=currency,
                                symbol=symbol,
                                time_frame=time_frame.value if time_frame else None
                            )
                        )

    async def evaluation_completed(self,
                                   cryptocurrency: str = None,
                                   symbol: str = None,
                                   time_frame=None,
                                   eval_note=None,
                                   eval_time=0,
                                   notify=True,
                                   origin_consumer=None,
                                   context=None) -> None:
        """
        Main async method to notify matrix to update
        :param cryptocurrency: evaluated cryptocurrency
        :param symbol: evaluated symbol
        :param time_frame: evaluated time frame
        :param eval_note: if None = self.eval_note
        :param eval_time: the time of the evaluation if relevant, default is 0
        :param notify: if true, will trigger matrix consumers
        :param origin_consumer: the sender consumer if it doesn't want to be notified
        :return: None
        """
        try:
            if eval_note is None:
                eval_note = self.eval_note if self.eval_note is not None else common_constants.START_PENDING_EVAL_NOTE

            if self.use_cache():
                ctx = context or self.get_context(symbol, time_frame, eval_time)
                await ctx.set_cached_value(eval_note, flush_if_necessary=True)
            self.ensure_eval_note_is_not_expired()
            await evaluator_channels.get_chan(constants.MATRIX_CHANNEL,
                                              self.matrix_id).get_internal_producer().send_eval_note(
                matrix_id=self.matrix_id,
                evaluator_name=self.get_name(),
                evaluator_type=self.evaluator_type.value,
                eval_note=eval_note,
                eval_note_type=self.get_eval_type(),
                eval_time=eval_time,
                exchange_name=self.exchange_name,
                cryptocurrency=cryptocurrency,
                symbol=symbol,
                time_frame=time_frame,
                notify=notify,
                origin_consumer=origin_consumer)
        except Exception as e:
            # if ConfigManager.is_in_dev_mode(self.config): # TODO
            #     raise e
            # else:
            self.logger.exception(e, True, f"Exception in evaluation_completed(): {e}")
        finally:
            if self.eval_note == "nan":
                self.eval_note = common_constants.START_PENDING_EVAL_NOTE
                self.logger.warning(str(self.symbol) + " evaluator returned 'nan' as eval_note, ignoring this value.")

    async def start(self, bot_id: str) -> bool:
        """
        :return: success of the evaluator's start
        """
        self.evaluators_consumer_instance = await evaluator_channels.get_chan(constants.EVALUATORS_CHANNEL,
                                                                              self.matrix_id) \
            .new_consumer(
                self.evaluators_callback,
                cryptocurrency=self.cryptocurrency if self.cryptocurrency else channel_constants.CHANNEL_WILDCARD,
                symbol=self.symbol if self.symbol else channel_constants.CHANNEL_WILDCARD,
                time_frame=self.time_frame if self.time_frame else channel_constants.CHANNEL_WILDCARD,
                priority_level=self.priority_level,
            )

    async def stop(self) -> None:
        """
        implement if necessary
        :return: None
        """
        await self.close_caches()
        for consumer in self.consumers:
            await consumer.stop()

    async def close_caches(self):
        self.remote_caches = {}
        await asyncio.gather(
            *(
                cache.close()
                for caches_by_tf in self.caches.values()
                for cache in caches_by_tf.values()
            )
        )
        self.caches = {}

    async def prepare(self) -> None:
        """
        Called just before start(), implement if necessary
        :return: None
        """
        pass

    async def start_evaluator(self, bot_id: str) -> None:
        """
        Start a task as matrix producer
        :return: None
        """
        if await self.start(bot_id):
            self.logger.debug("Evaluator started")
        else:
            self.logger.debug("Evaluator not started")

    def set_default_config(self):
        """
        To implement in subclasses if config necessary
        :return:
        """
        self.specific_config = {}

    def reset(self) -> None:
        """
        Reset temporary parameters to enable fresh start
        :return: None
        """
        self.eval_note = common_constants.START_PENDING_EVAL_NOTE

    @classmethod
    def has_class_in_parents(cls, klass) -> bool:
        """
        Explore up to the 2nd degree parent
        :param klass: python Class to explore
        :return: Boolean
        """
        if klass in cls.__bases__:
            return True
        elif any(klass in base.__bases__ for base in cls.__bases__):
            return True
        else:
            for base in cls.__bases__:
                if any(klass in super_base.__bases__ for super_base in base.__bases__):
                    return True
        return False

    @classmethod
    def get_parent_evaluator_classes(cls, higher_parent_class_limit=None) -> list:
        """
        Return the evaluator parent classe(s)
        :param higher_parent_class_limit:
        :return: list of classes
        """
        return [
            class_type
            for class_type in cls.mro()
            if (higher_parent_class_limit if higher_parent_class_limit else AbstractEvaluator) in class_type.mro()
        ]

    def set_eval_note(self, new_eval_note) -> None:
        """
        Performs additionnal check to eval_note before changing it
        :param new_eval_note:
        :return: None
        """
        self.eval_note_changed()

        if self.eval_note == common_constants.START_PENDING_EVAL_NOTE:
            self.eval_note = common_constants.INIT_EVAL_NOTE

        if self.eval_note + new_eval_note > 1:
            self.eval_note = 1
        elif self.eval_note + new_eval_note < -1:
            self.eval_note = -1
        else:
            self.eval_note += new_eval_note

    @classmethod
    def is_enabled(cls, tentacles_setup_config, default) -> bool:
        """
        Check if the evaluator is enabled by configuration
        :param tentacles_setup_config: tentacles setup config
        :param default: default value if evaluator config is not found
        :return: evaluator config
        """
        try:
            return api.is_tentacle_activated_in_tentacles_setup_config(tentacles_setup_config,
                                                                       cls.get_name(),
                                                                       raise_errors=True)
        except KeyError:
            for parent in cls.mro():
                try:
                    return api.is_tentacle_activated_in_tentacles_setup_config(tentacles_setup_config,
                                                                               parent.__name__,
                                                                               raise_errors=True)
                except KeyError:
                    pass
        return default

    def save_evaluation_expiration_time(self, eval_note_time_to_live, eval_note_changed_time=None) -> None:
        """
        Use only if the current evaluation is to stay for a pre-defined amount of seconds
        :param eval_note_time_to_live:
        :param eval_note_changed_time:
        :return: None
        """
        self.eval_note_time_to_live = eval_note_time_to_live
        self.eval_note_changed_time = eval_note_changed_time if eval_note_changed_time else time.time()

    def eval_note_changed(self) -> None:
        """
        Eval note changed callback
        :return: None
        """
        if self.eval_note_time_to_live is not None and self.eval_note_changed_time is None:
            self.eval_note_changed_time = time.time()

    def ensure_eval_note_is_not_expired(self) -> None:
        """
        Eval note expiration check
        :return: None
        """
        if self.eval_note_time_to_live is not None:
            if self.eval_note_changed_time is None:
                self.eval_note_changed_time = time.time()

            if time.time() - self.eval_note_changed_time > self.eval_note_time_to_live:
                self.eval_note = common_constants.START_PENDING_EVAL_NOTE
                self.eval_note_time_to_live = None
                self.eval_note_changed_time = None

    def get_exchange_symbol_data(self, exchange_name: str, exchange_id: str, symbol: str):
        try:
            import octobot_trading.api as exchange_api
            exchange_manager = exchange_api.get_exchange_manager_from_exchange_name_and_id(exchange_name, exchange_id)
            return exchange_api.get_symbol_data(exchange_manager, symbol)
        except (ImportError, KeyError):
            self.logger.error(f"Can't get {exchange_name} from exchanges instances")
        return

    async def evaluators_callback(self,
                                  matrix_id,
                                  evaluator_name,
                                  evaluator_type,
                                  exchange_name,
                                  cryptocurrency,
                                  symbol,
                                  time_frame,
                                  data):
        # Used to communicate between evaluators
        pass
