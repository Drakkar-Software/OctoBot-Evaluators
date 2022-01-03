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
import importlib

import async_channel.constants as channel_constants
import async_channel.channels as channels

import octobot_commons.channels_name as channels_name
import octobot_commons.enums as commons_enums
import octobot_commons.constants as commons_constants
import octobot_commons.errors as commons_errors

import octobot_evaluators.constants as constants
import octobot_evaluators.enums as enums
import octobot_evaluators.evaluators as evaluator
import octobot_evaluators.util as evaluators_util
import octobot_tentacles_manager.api as tentacles_manager_api


class ScriptedEvaluator(evaluator.AbstractEvaluator):
    __metaclass__ = evaluator.AbstractEvaluator
    EVALUATOR_SCRIPT_MODULE = None

    def __init__(self, tentacles_setup_config, post_init=True):
        super().__init__(tentacles_setup_config, post_init=post_init)
        self._script = None
        self._are_candles_initialized = False
        self._has_script_been_called_once = False

    def post_init(self, tentacles_setup_config):
        self.load_config()
        # add config folder to importable files to import the user script
        tentacles_manager_api.import_user_tentacles_config_folder(tentacles_setup_config)

    def load_config(self):
        self.specific_config = tentacles_manager_api.get_tentacle_config(self.tentacles_setup_config, self.__class__)

    async def start(self, bot_id: str) -> bool:
        """
        Default TA start: to be overwritten
        Subscribe to OHLCV notification from self.symbols and self.time_frames
        :return: success of the evaluator's start
        """
        await super().start(bot_id)
        try:
            import octobot_trading.api as exchange_api
            exchange_id = exchange_api.get_exchange_id_from_matrix_id(self.exchange_name, self.matrix_id)
            time_frame_filter = [tf.value
                                 for tf in exchange_api.get_exchange_available_required_time_frames(
                                    self.exchange_name, exchange_id)]
            if len(time_frame_filter) == 1:
                time_frame_filter = time_frame_filter[0]
            cryptocurrency = self.cryptocurrency if self.cryptocurrency else channel_constants.CHANNEL_WILDCARD
            symbol = self.symbol if self.symbol else channel_constants.CHANNEL_WILDCARD
            time_frame = self.time_frame.value if self.time_frame else time_frame_filter
            self.consumers += await self._register_on_channels(exchange_id, cryptocurrency, symbol, time_frame, bot_id)
            return True
        except ImportError:
            self.logger.error("Can't connect to trading channels")
        return False

    async def evaluator_ohlcv_callback(self, exchange: str, exchange_id: str, cryptocurrency: str, symbol: str,
                                       time_frame: str, candle: dict):
        await self._call_script(exchange, exchange_id, cryptocurrency, symbol,
                                candle[commons_enums.PriceIndexes.IND_PRICE_TIME.value],
                                commons_enums.ActivationTopics.FULL_CANDLES.value,
                                time_frame=time_frame, candle=candle)

    async def evaluator_kline_callback(self, exchange: str, exchange_id: str, cryptocurrency: str, symbol: str,
                                       time_frame, kline: dict):
        await self._call_script(exchange, exchange_id, cryptocurrency, symbol,
                                kline[commons_enums.PriceIndexes.IND_PRICE_TIME.value],
                                commons_enums.ActivationTopics.IN_CONSTRUCTION_CANDLES.value,
                                time_frame=time_frame, kline=kline)

    async def evaluator_manual_callback(self, context=None, ignore_cache=False, **kwargs):
        """
        Called when this evaluator is triggered from a manual call
        :param context: the calling script's context
        :param kwargs: unused parameters
        :return: the evaluation value
        """
        local_context = context.copy(tentacle=self)
        try:
            # Cache is initialized at the 1st call: since a new instance of the evaluator is
            # potentially created each time, use cache to figure out if it has been called already.
            # Since self._has_script_been_called_once is only used in the context of cached evaluators,
            # it' fine to have it False all the time when no cache is used.
            self._has_script_been_called_once = self.use_cache() and local_context.has_cache(
                local_context.symbol,
                local_context.time_frame,
                config_name=local_context.config_name
            )
            return_value, from_cache = await self._get_cached_or_computed_value(local_context,
                                                                    ignore_cache=ignore_cache)
            if not ignore_cache and not from_cache and \
                    self.use_cache() and return_value != commons_constants.DO_NOT_CACHE:
                await local_context.set_cached_value(return_value, flush_if_necessary=True)
            return return_value
        except commons_errors.MissingDataError as e:
            self.logger.debug(f"Can't compute evaluator value: {e}")
            return commons_constants.DO_NOT_CACHE

    async def _get_cached_or_computed_value(self, context, ignore_cache=False):
        computed_value = None
        is_value_missing = True
        if not ignore_cache and self.use_cache():
            computed_value, is_value_missing = await context.get_cached_value()
        if is_value_missing or not self._has_script_been_called_once:
            # always call the script at least once to save plotting statements
            await self._pre_script_call(context)
            computed_value = await self.get_script()(context)
            self._has_script_been_called_once = True
        return computed_value, not is_value_missing

    async def _call_script(self, exchange: str, exchange_id: str, cryptocurrency: str, symbol: str,
                           trigger_cache_timestamp: float, trigger_source: str,
                           time_frame: str = None, candle: dict = None, kline: dict = None):
        self.last_call = (exchange, exchange_id, cryptocurrency, symbol, trigger_cache_timestamp,
                          trigger_source, time_frame, candle, kline)
        context = self.get_context(symbol, time_frame, trigger_cache_timestamp, cryptocurrency=cryptocurrency,
                                   exchange=exchange, exchange_id=exchange_id, trigger_source=trigger_source,
                                   trigger_value=candle or kline)
        try:
            import octobot_trading.api as trading_api
            if not self._are_candles_initialized:
                self._are_candles_initialized = trading_api.are_symbol_candles_initialized(context.exchange_manager,
                                                                                           symbol, time_frame)
                if not self._are_candles_initialized:
                    self.logger.debug(f"Waiting for candles to be initialized before calling script "
                                      f"for {symbol} {time_frame}")
                    return
            self.eval_note, from_cache = await self._get_cached_or_computed_value(context)
            eval_time = None
            if trigger_source == commons_enums.ActivationTopics.FULL_CANDLES.value:
                eval_time = evaluators_util.get_eval_time(full_candle=candle, time_frame=time_frame)
            elif trigger_source == commons_enums.ActivationTopics.IN_CONSTRUCTION_CANDLES.value:
                eval_time = evaluators_util.get_eval_time(partial_candle=kline)
            if eval_time is None:
                self.logger.error("Can't compute evaluation time, using exchange time")
                eval_time = trading_api.get_exchange_current_time(context.exchange_manager)
            await self.evaluation_completed(cryptocurrency, symbol, time_frame,
                                            eval_time=eval_time, context=context, cache_if_available=not from_cache)
        except commons_errors.MissingDataError:
            self.eval_note = commons_constants.DO_NOT_CACHE
        except ImportError:
            self.logger.exception(f"Error when importing octobot-trading")
        except Exception as e:
            self.logger.exception(f"Error when calling evaluation script: {e}", True, e)

    async def _pre_script_call(self, context):
        try:
            import octobot_trading.modes.basic_keywords as basic_keywords
            # Always register activation_topics use input to enable changing it from run metadata
            # (where user inputs are registered)
            activation_topic_values = [
                commons_enums.ActivationTopics.FULL_CANDLES.value,
                commons_enums.ActivationTopics.IN_CONSTRUCTION_CANDLES.value
            ]
            await basic_keywords.user_input(context, commons_constants.CONFIG_ACTIVATION_TOPICS, "multiple-options",
                                               [commons_enums.ActivationTopics.FULL_CANDLES.value],
                                               options=activation_topic_values, show_in_optimizer=False)
        except ImportError:
            self.logger.error("Can't read octobot_trading scripting_library")

    @classmethod
    def get_is_symbol_wildcard(cls) -> bool:
        """
        :return: True if the evaluator is not symbol dependant else False
        """
        return False

    @classmethod
    def get_is_time_frame_wildcard(cls) -> bool:
        """
        :return: True if the evaluator is not time_frame dependant else False
        """
        return False

    def register_script_module(self, script_module):
        self.__class__.EVALUATOR_SCRIPT_MODULE = script_module
        self._script = self.get_script_from_module(script_module)

    @staticmethod
    def get_script_from_module(module):
        return module.script

    def get_script(self):
        return self._script

    async def _user_commands_callback(self, bot_id, subject, action, data) -> None:
        self.logger.debug(f"Received {action} command.")
        if action == commons_enums.UserCommands.RELOAD_SCRIPT.value:
            # live_script = data[AbstractScriptedTradingMode.USER_COMMAND_RELOAD_SCRIPT_IS_LIVE]
            await self._reload_script()
        if action == commons_enums.UserCommands.CLEAR_ALL_CACHE.value:
            await self.clear_all_cache()

    async def _reload_script(self):
        importlib.reload(self.__class__.EVALUATOR_SCRIPT_MODULE)
        self.register_script_module(self.__class__.EVALUATOR_SCRIPT_MODULE)
        # reload config
        self.load_config()
        # todo cancel and restart live tasks
        # recall script with for are_data_initialized to false to re-write initial data
        await self.close_caches(reset_cache_db_ids=True)
        run_data_writer, _, _, symbol_writer = self._get_trading_mode_writers()
        time_frames = None if self.get_is_time_frame_wildcard() else (self.time_frame.value, )
        run_data_writer.set_initialized_flags(False)
        symbol_writer.set_initialized_flags(False, time_frames)
        self._has_script_been_called_once = False
        try:
            await self._call_script(*self.last_call)
        finally:
            await run_data_writer.flush()
            run_data_writer.set_initialized_flags(True)
            symbol_writer.set_initialized_flags(True, time_frames)

    def _get_trading_mode_writers(self):
        try:
            import octobot_trading.api as exchange_api
            exchange_manager = exchange_api.get_exchange_manager_from_exchange_name_and_id(
                self.exchange_name,
                exchange_api.get_exchange_id_from_matrix_id(self.exchange_name, self.matrix_id)
            )
            trading_modes = exchange_api.get_trading_modes(exchange_manager)
            return exchange_api.get_trading_mode_writers(trading_modes[0])
        except ImportError:
            self.logger.error("required OctoBot-trading to get a trading mode writer")
            raise

    async def _register_on_channels(self, exchange_id, cryptocurrency, symbol, time_frame, bot_id):
        consumers = []
        try:
            import octobot_trading.exchange_channel as exchanges_channel
            registration_topics = self._get_channel_registration()
            if channels_name.OctoBotTradingChannelsName.OHLCV_CHANNEL.value in registration_topics:
                consumers.append(
                    await exchanges_channel.get_chan(channels_name.OctoBotTradingChannelsName.OHLCV_CHANNEL.value,
                                                     exchange_id).
                        new_consumer(self.evaluator_ohlcv_callback, cryptocurrency=cryptocurrency,
                                     symbol=symbol, time_frame=time_frame, priority_level=self.priority_level)
                )
            if channels_name.OctoBotTradingChannelsName.KLINE_CHANNEL.value in registration_topics:
                consumers.append(
                    await exchanges_channel.get_chan(channels_name.OctoBotTradingChannelsName.KLINE_CHANNEL.value,
                                                     exchange_id). \
                        new_consumer(self.evaluator_kline_callback, cryptocurrency=cryptocurrency,
                                     symbol=symbol, time_frame=time_frame, priority_level=self.priority_level)
                )
            import octobot_services.channel as services_channels
            try:
                consumers.append(
                    await channels.get_chan(services_channels.UserCommandsChannel.get_name()).new_consumer(
                        self._user_commands_callback,
                        {"bot_id": bot_id, "subject": self.get_name()}
                    )
                )
            except KeyError:
                # UserCommandsChannel might not be available
                pass
        except ImportError:
            self.logger.warning("Can't connect to trading / services channels")
        return consumers

    def _get_channel_registration(self):
        TOPIC_TO_CHANNEL_NAME = {
            commons_enums.ActivationTopics.FULL_CANDLES.value:
                channels_name.OctoBotTradingChannelsName.OHLCV_CHANNEL.value,
            commons_enums.ActivationTopics.IN_CONSTRUCTION_CANDLES.value:
                channels_name.OctoBotTradingChannelsName.KLINE_CHANNEL.value,
        }
        registration_channels = []
        # Activate on full candles only by default (same as technical evaluators)
        for topic in self.specific_config.get(commons_constants.CONFIG_ACTIVATION_TOPICS.replace(" ", "_"),
                                              [commons_enums.ActivationTopics.FULL_CANDLES.value]):
            try:
                registration_channels.append(TOPIC_TO_CHANNEL_NAME[topic])
            except KeyError:
                self.logger.error(f"Unknown registration topic: {topic}")
        return registration_channels
