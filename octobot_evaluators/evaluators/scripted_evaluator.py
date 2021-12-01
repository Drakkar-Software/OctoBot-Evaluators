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

import octobot_evaluators.constants as constants
import octobot_evaluators.enums as enums
import octobot_evaluators.evaluators as evaluator
import octobot_evaluators.util as evaluators_util
import octobot_tentacles_manager.api as tentacles_manager_api


class ScriptedEvaluator(evaluator.AbstractEvaluator):
    __metaclass__ = evaluator.AbstractEvaluator
    EVALUATOR_SCRIPT_MODULE = None

    def __init__(self, tentacles_setup_config):
        super().__init__(tentacles_setup_config)
        self._script = None
        self._are_candles_initialized = False
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
                                enums.ActivationTopics.FULL_CANDLES.value,
                                time_frame=time_frame, candle=candle)

    async def evaluator_kline_callback(self, exchange: str, exchange_id: str, cryptocurrency: str, symbol: str,
                                       time_frame, kline: dict):
        await self._call_script(exchange, exchange_id, cryptocurrency, symbol,
                                kline[commons_enums.PriceIndexes.IND_PRICE_TIME.value],
                                enums.ActivationTopics.IN_CONSTRUCTION_CANDLES.value,
                                time_frame=time_frame, kline=kline)

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
            await self._pre_script_call(context)
            self.eval_note = await self.get_script()(context)
            eval_time = None
            if trigger_source == enums.ActivationTopics.FULL_CANDLES.value:
                eval_time = evaluators_util.get_eval_time(full_candle=candle, time_frame=time_frame)
            elif trigger_source == enums.ActivationTopics.IN_CONSTRUCTION_CANDLES.value:
                eval_time = evaluators_util.get_eval_time(partial_candle=kline)
            if eval_time is None:
                self.logger.error("Can't compute evaluation time, using exchange time")
                eval_time = trading_api.get_exchange_current_time(context.exchange_manager)
            await self.evaluation_completed(cryptocurrency, symbol, time_frame,
                                            eval_time=eval_time, context=context)
        except Exception as e:
            self.logger.exception(f"Error when calling evaluation script: {e}", True, e)

    async def _pre_script_call(self, context):
        try:
            import octobot_trading.modes.scripting_library as scripting_library
            # Always register activation_topics use input to enable changing it from run metadata
            # (where user inputs are registered)
            activation_topic_values = [
                enums.ActivationTopics.FULL_CANDLES.value,
                enums.ActivationTopics.IN_CONSTRUCTION_CANDLES.value
            ]
            await scripting_library.user_input(context, constants.CONFIG_ACTIVATION_TOPICS, "multiple-options",
                                               [enums.ActivationTopics.FULL_CANDLES.value],
                                               options=activation_topic_values)
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

    async def _reload_script(self):
        importlib.reload(self.__class__.EVALUATOR_SCRIPT_MODULE)
        self.register_script_module(self.__class__.EVALUATOR_SCRIPT_MODULE)
        # reload config
        self.load_config()
        # todo cancel and restart live tasks
        # recall script with for are_data_initialized to false to re-write initial data
        await self.close_caches()
        run_data_writer = self._get_trading_mode_writers()[0]
        run_data_writer.are_data_initialized = False
        try:
            await self._call_script(*self.last_call)
        finally:
            run_data_writer.are_data_initialized = True

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
        try:
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
            self.logger.warning("Can't connect to services channels")
        return consumers

    def _get_channel_registration(self):
        try:
            import octobot_trading.exchange_channel as exchanges_channel
            TOPIC_TO_CHANNEL_NAME = {
                enums.ActivationTopics.FULL_CANDLES.value:
                    channels_name.OctoBotTradingChannelsName.OHLCV_CHANNEL.value,
                enums.ActivationTopics.IN_CONSTRUCTION_CANDLES.value:
                    channels_name.OctoBotTradingChannelsName.KLINE_CHANNEL.value,
            }
            registration_channels = []
            # Activate on full candles only by default (same as technical evaluators)
            for topic in self.specific_config.get(constants.CONFIG_ACTIVATION_TOPICS,
                                                  [enums.ActivationTopics.FULL_CANDLES.value]):
                try:
                    registration_channels.append(TOPIC_TO_CHANNEL_NAME[topic])
                except KeyError:
                    self.logger.error(f"Unknown registration topic: {topic}")
            return registration_channels

        except ImportError:
            self.logger.error("Can't connect to OHLCV trading channel")
