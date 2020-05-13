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
from octobot_channels.constants import CHANNEL_WILDCARD
from octobot_commons.constants import CONFIG_WILDCARD
from octobot_commons.enums import TimeFrames
from octobot_commons.time_frame_manager import parse_time_frames
from octobot_evaluators.channels.evaluator_channel import get_chan
from octobot_evaluators.constants import MATRIX_CHANNEL, \
    STRATEGIES_REQUIRED_TIME_FRAME, CONFIG_FORCED_TIME_FRAME, STRATEGIES_REQUIRED_EVALUATORS, TENTACLE_DEFAULT_CONFIG, \
    EVALUATOR_CHANNEL_DATA_ACTION, RESET_EVALUATION, EVALUATOR_CHANNEL_DATA_TIME_FRAMES, \
    STRATEGIES_COMPATIBLE_EVALUATOR_TYPES
from octobot_evaluators.data_manager.matrix_manager import get_tentacle_path, get_node_children_by_names_at_path, \
    get_tentacle_eval_time, get_matrix_default_value_path, is_tentacle_value_valid, get_available_time_frames
from octobot_evaluators.enums import EvaluatorMatrixTypes
from octobot_evaluators.evaluator import AbstractEvaluator
from octobot_tentacles_manager.api.configurator import get_tentacle_config


class StrategyEvaluator(AbstractEvaluator):
    __metaclass__ = AbstractEvaluator

    def __init__(self):
        super().__init__()
        self.consumer_instance = None
        self.strategy_time_frames = []
        self.evaluations_last_updates = {}
        self.allowed_time_delta = None

        # caches
        self.available_evaluators_cache = {}
        self.available_time_frames_cache = {}
        self.available_node_paths_cache = {}

    async def start(self, bot_id: str) -> bool:
        """
        Default Strategy start: to be overwritten
        Subscribe to Matrix notification from self.symbols and self.time_frames
        :return: success of the evaluator's start
        """
        await super().start(bot_id)
        self.consumer_instance = await get_chan(MATRIX_CHANNEL, self.matrix_id).new_consumer(
            self.strategy_matrix_callback,
            priority_level=self.priority_level,
            exchange_name=self.exchange_name if self.exchange_name else CHANNEL_WILDCARD)
        self._init_exchange_allowed_time_delta(self.exchange_name, self.matrix_id)
        return True

    async def strategy_completed(self,
                                 cryptocurrency: str = None,
                                 symbol: str = None,
                                 eval_note=None,
                                 eval_time=0,
                                 notify=True) -> None:
        """
        Main async method to notify that a strategy has updated its evaluation
        :param cryptocurrency: evaluated cryptocurrency
        :param symbol: evaluated symbol
        :param eval_note: if None = self.eval_note
        :param eval_time: the time of the evaluation if relevant, default is 0
        :param notify: if true, will trigger matrix consumers
        :return: None
        """
        return await self.evaluation_completed(cryptocurrency=cryptocurrency,
                                               symbol=symbol,
                                               time_frame=None,
                                               eval_note=eval_note,
                                               eval_time=eval_time,
                                               notify=notify,
                                               origin_consumer=self.consumer_instance)

    def is_technical_evaluator_cycle_complete(self, matrix_id, evaluator_name, evaluator_type, exchange_name,
                                              cryptocurrency, symbol, time_frame) -> bool:
        """
        :return: True if the strategy is to be waken up by technical evaluators at the moment of this call.
        This avoids partial time frame updates wakeup.
        Override if necessary
        """
        # 1. Ensure this evaluation has not already been sent
        # 2. Ensure every technical evaluator form this time frame are valid
        return not self._already_sent_this_technical_evaluation(matrix_id,
                                                                evaluator_name,
                                                                evaluator_type,
                                                                exchange_name,
                                                                cryptocurrency,
                                                                symbol,
                                                                time_frame) and \
            self._are_every_evaluation_valid(matrix_id,
                                             evaluator_name,
                                             evaluator_type,
                                             exchange_name,
                                             cryptocurrency,
                                             symbol,
                                             time_frame)

    def clear_cache(self):
        self.available_evaluators_cache = {}
        self.available_time_frames_cache = {}
        self.available_node_paths_cache = {}

    async def stop(self) -> None:
        if self.consumer_instance:
            await get_chan(MATRIX_CHANNEL, self.matrix_id).remove_consumer(self.consumer_instance)

    async def strategy_matrix_callback(self,
                                       matrix_id,
                                       evaluator_name,
                                       evaluator_type,
                                       eval_note,
                                       eval_note_type,
                                       exchange_name,
                                       cryptocurrency,
                                       symbol,
                                       time_frame):
        # if this callback is from a technical evaluator: ensure strategy should be notified at this moment
        if evaluator_type == EvaluatorMatrixTypes.TA.value:
            # ensure this time frame is within the strategy's time frames
            if TimeFrames(time_frame) not in self.strategy_time_frames or \
                not self.is_technical_evaluator_cycle_complete(matrix_id,
                                                               evaluator_name,
                                                               evaluator_type,
                                                               exchange_name,
                                                               cryptocurrency,
                                                               symbol,
                                                               time_frame):
                # do not call the strategy
                return
        await self.matrix_callback(
            matrix_id,
            evaluator_name,
            evaluator_type,
            eval_note,
            eval_note_type,
            exchange_name,
            cryptocurrency,
            symbol,
            time_frame
        )

    async def matrix_callback(self,
                              matrix_id,
                              evaluator_name,
                              evaluator_type,
                              eval_note,
                              eval_note_type,
                              exchange_name,
                              cryptocurrency,
                              symbol,
                              time_frame):
        # To be used to trigger an evaluation
        # Do not forget to check if evaluator_name is self.name
        pass

    def _are_every_evaluation_valid(self,
                                    matrix_id,
                                    evaluator_name,
                                    evaluator_type,
                                    exchange_name,
                                    cryptocurrency,
                                    symbol,
                                    time_frame
                                    ):
        to_validate_node_paths = self._get_available_node_paths(matrix_id,
                                                                evaluator_type,
                                                                exchange_name,
                                                                cryptocurrency,
                                                                symbol,
                                                                use_cache=True)
        current_time = self._get_exchange_current_time(exchange_name, matrix_id)
        # ensure all evaluations are valid (do not trigger on an expired evaluation)
        if all(is_tentacle_value_valid(self.matrix_id, evaluation_node_path,
                                       timestamp=current_time,
                                       delta=self.allowed_time_delta)
               for evaluation_node_path in to_validate_node_paths):
            self._save_last_evaluation(matrix_id, exchange_name, evaluator_type, evaluator_name,
                                       cryptocurrency, symbol, time_frame)
            return True
        return False

    def _get_available_node_paths(self,
                                  matrix_id,
                                  evaluator_type,
                                  exchange_name,
                                  cryptocurrency,
                                  symbol,
                                  use_cache=True):
        if use_cache:
            try:
                return self.available_node_paths_cache[matrix_id][exchange_name][evaluator_type][cryptocurrency][symbol]
            except KeyError:
                # No cache usage here to be use to refresh data
                node_paths = self._inner_get_available_node_paths(matrix_id, evaluator_type, exchange_name,
                                                                  cryptocurrency, symbol, use_cache=False)
                if matrix_id not in self.available_node_paths_cache:
                    self.available_node_paths_cache[matrix_id] = {}
                if exchange_name not in self.available_node_paths_cache[matrix_id]:
                    self.available_node_paths_cache[matrix_id][exchange_name] = {}
                if evaluator_type not in self.available_node_paths_cache[matrix_id][exchange_name]:
                    self.available_node_paths_cache[matrix_id][exchange_name][evaluator_type] = {}
                if cryptocurrency not in self.available_node_paths_cache[matrix_id][exchange_name][evaluator_type]:
                    self.available_node_paths_cache[matrix_id][exchange_name][evaluator_type][cryptocurrency] = {}
                self.available_node_paths_cache[matrix_id][exchange_name][evaluator_type][cryptocurrency][symbol] = \
                    node_paths
                return node_paths
        return self._inner_get_available_node_paths(matrix_id, evaluator_type, exchange_name,
                                                    cryptocurrency, symbol, use_cache=use_cache)

    def _inner_get_available_node_paths(self, matrix_id, evaluator_type, exchange_name, cryptocurrency, symbol,
                                        use_cache=True):
        return [
            get_matrix_default_value_path(tentacle_name=evaluator,
                                          tentacle_type=evaluator_type,
                                          exchange_name=exchange_name,
                                          cryptocurrency=cryptocurrency,
                                          symbol=symbol,
                                          time_frame=time_frame)
            for time_frame in self.get_available_time_frames(matrix_id, exchange_name, evaluator_type,
                                                             cryptocurrency, symbol, use_cache=use_cache)
            if TimeFrames(time_frame) in self.strategy_time_frames
            for evaluator in self._get_available_evaluators(matrix_id, exchange_name, evaluator_type,
                                                            use_cache=use_cache)
        ]

    def _save_last_evaluation(self, matrix_id, exchange_name, evaluator_type, tentacle_name,
                              cryptocurrency, symbol, time_frame):
        self._set_last_evaluation_time(exchange_name,
                                       evaluator_type,
                                       cryptocurrency,
                                       symbol,
                                       time_frame,
                                       get_tentacle_eval_time(matrix_id,
                                                              get_matrix_default_value_path(
                                                                  tentacle_name=tentacle_name,
                                                                  tentacle_type=evaluator_type,
                                                                  exchange_name=exchange_name,
                                                                  cryptocurrency=cryptocurrency,
                                                                  symbol=symbol,
                                                                  time_frame=time_frame)
                                                              )
                                       )

    def _already_sent_this_technical_evaluation(self, matrix_id, evaluator, evaluator_type, exchange_name,
                                                cryptocurrency, symbol, time_frame):
        try:
            update_time = get_tentacle_eval_time(matrix_id,
                                                 get_matrix_default_value_path(
                                                      tentacle_name=evaluator,
                                                      tentacle_type=evaluator_type,
                                                      exchange_name=exchange_name,
                                                      cryptocurrency=cryptocurrency,
                                                      symbol=symbol,
                                                      time_frame=time_frame)
                                                 )
            return self.evaluations_last_updates[exchange_name][evaluator_type][cryptocurrency][symbol][time_frame] \
                == update_time
        except KeyError:
            return False

    def _set_last_evaluation_time(self, exchange_name, evaluator_type, cryptocurrency, symbol, time_frame, value):
        try:
            self.evaluations_last_updates[exchange_name][evaluator_type][cryptocurrency][symbol][time_frame] = value
        except KeyError:
            if exchange_name not in self.evaluations_last_updates:
                self.evaluations_last_updates[exchange_name] = {}
            if evaluator_type not in self.evaluations_last_updates[exchange_name]:
                self.evaluations_last_updates[exchange_name][evaluator_type] = {}
            if cryptocurrency not in self.evaluations_last_updates[exchange_name][evaluator_type]:
                self.evaluations_last_updates[exchange_name][evaluator_type][cryptocurrency] = {}
            if symbol not in self.evaluations_last_updates[exchange_name][evaluator_type][cryptocurrency]:
                self.evaluations_last_updates[exchange_name][evaluator_type][cryptocurrency][symbol] = {}
            self.evaluations_last_updates[exchange_name][evaluator_type][cryptocurrency][symbol] = {
                time_frame: value
            }

    def _get_exchange_current_time(self, exchange_name, matrix_id):
        try:
            from octobot_trading.api.exchange import get_exchange_current_time, \
                get_exchange_manager_from_exchange_name_and_id, get_exchange_id_from_matrix_id
            exchange_manager = get_exchange_manager_from_exchange_name_and_id(
                exchange_name,
                get_exchange_id_from_matrix_id(exchange_name, matrix_id)
            )
            return get_exchange_current_time(exchange_manager)
        except ImportError:
            self.logger.error("Strategy requires OctoBot-Trading package installed")

    def _init_exchange_allowed_time_delta(self, exchange_name, matrix_id):
        try:
            from octobot_trading.api.exchange import get_exchange_allowed_time_lag, \
                get_exchange_manager_from_exchange_name_and_id, get_exchange_id_from_matrix_id
            exchange_manager = get_exchange_manager_from_exchange_name_and_id(
                exchange_name,
                get_exchange_id_from_matrix_id(exchange_name, matrix_id)
            )
            self.allowed_time_delta = get_exchange_allowed_time_lag(exchange_manager)
        except ImportError:
            self.logger.error("Strategy requires OctoBot-Trading package installed")

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
        if data[EVALUATOR_CHANNEL_DATA_ACTION] == RESET_EVALUATION:
            for time_frame in data[EVALUATOR_CHANNEL_DATA_TIME_FRAMES]:
                self._set_last_evaluation_time(exchange_name, EvaluatorMatrixTypes.TA.value, cryptocurrency, symbol,
                                               time_frame.value, None)

    def _get_available_evaluators(self, matrix_id, exchange_name, tentacle_type, use_cache=True):
        if use_cache:
            try:
                return self.available_evaluators_cache[matrix_id][exchange_name][tentacle_type]
            except KeyError:
                available_evaluators = get_node_children_by_names_at_path(
                    matrix_id, get_tentacle_path(exchange_name=exchange_name, tentacle_type=tentacle_type)
                ).keys()
                if matrix_id not in self.available_evaluators_cache:
                    self.available_evaluators_cache[matrix_id] = {}
                if exchange_name not in self.available_evaluators_cache[matrix_id]:
                    self.available_evaluators_cache[matrix_id][exchange_name] = {}
                self.available_evaluators_cache[matrix_id][exchange_name][tentacle_type] = available_evaluators
                return available_evaluators
        return get_node_children_by_names_at_path(
            matrix_id, get_tentacle_path(exchange_name=exchange_name, tentacle_type=tentacle_type)
        ).keys()

    def get_available_time_frames(self,
                                  matrix_id,
                                  exchange_name=None,
                                  tentacle_type=None,
                                  cryptocurrency=None,
                                  symbol=None,
                                  use_cache=True):
        if use_cache:
            try:
                return self.available_time_frames_cache[matrix_id][exchange_name][tentacle_type][cryptocurrency][symbol]
            except KeyError:
                available_time_frames = get_available_time_frames(
                    matrix_id, exchange_name, tentacle_type, cryptocurrency, symbol)
                if matrix_id not in self.available_time_frames_cache:
                    self.available_time_frames_cache[matrix_id] = {}
                if exchange_name not in self.available_time_frames_cache[matrix_id]:
                    self.available_time_frames_cache[matrix_id][exchange_name] = {}
                if tentacle_type not in self.available_time_frames_cache[matrix_id][exchange_name]:
                    self.available_time_frames_cache[matrix_id][exchange_name][tentacle_type] = {}
                if cryptocurrency not in self.available_time_frames_cache[matrix_id][exchange_name][tentacle_type]:
                    self.available_time_frames_cache[matrix_id][exchange_name][tentacle_type][cryptocurrency] = {}
                self.available_time_frames_cache[matrix_id][exchange_name][tentacle_type][cryptocurrency][symbol] = \
                    available_time_frames
                return available_time_frames
        return get_available_time_frames(matrix_id, exchange_name, tentacle_type, cryptocurrency, symbol)

    def _get_tentacle_registration_topic(self, all_symbols_by_crypto_currencies, time_frames, real_time_time_frames):
        strategy_currencies, symbols, self.strategy_time_frames = super()._get_tentacle_registration_topic(
            all_symbols_by_crypto_currencies,
            time_frames,
            real_time_time_frames)
        self.all_symbols_by_crypto_currencies = all_symbols_by_crypto_currencies
        # by default no time frame registration for strategies
        return strategy_currencies, symbols, [self.time_frame]

    @classmethod
    def get_required_time_frames(cls, config: dict):
        if CONFIG_FORCED_TIME_FRAME in config:
            return parse_time_frames(config[CONFIG_FORCED_TIME_FRAME])
        strategy_config: dict = get_tentacle_config(cls)
        if STRATEGIES_REQUIRED_TIME_FRAME in strategy_config:
            return parse_time_frames(strategy_config[STRATEGIES_REQUIRED_TIME_FRAME])
        else:
            raise Exception(f"'{STRATEGIES_REQUIRED_TIME_FRAME}' is missing in configuration file")

    @classmethod
    def get_required_evaluators(cls, strategy_config: dict = None) -> list:
        """
        :param strategy_config: the strategy configuration dict
        :return: the list of required evaluators, [CONFIG_WILDCARD] means any evaluator
        """
        strategy_config: dict = strategy_config or get_tentacle_config(cls)
        if STRATEGIES_REQUIRED_EVALUATORS in strategy_config:
            return strategy_config[STRATEGIES_REQUIRED_EVALUATORS]
        else:
            raise Exception(f"'{STRATEGIES_REQUIRED_EVALUATORS}' is missing in configuration file")

    @classmethod
    def get_compatible_evaluators_types(cls, strategy_config: dict = None) -> list:
        """
        :param strategy_config: the strategy configuration dict
        :return: the list of compatible evaluator type, [CONFIG_WILDCARD] means any type
        """
        strategy_config: dict = strategy_config or get_tentacle_config(cls)
        if STRATEGIES_COMPATIBLE_EVALUATOR_TYPES in strategy_config:
            return strategy_config[STRATEGIES_COMPATIBLE_EVALUATOR_TYPES]
        return [CONFIG_WILDCARD]

    @classmethod
    def get_default_evaluators(cls, strategy_config: dict = None):
        strategy_config: dict = strategy_config or get_tentacle_config(cls)
        if TENTACLE_DEFAULT_CONFIG in strategy_config:
            return strategy_config[TENTACLE_DEFAULT_CONFIG]
        else:
            required_evaluators = cls.get_required_evaluators(strategy_config)
            if required_evaluators == CONFIG_WILDCARD:
                return []
            return required_evaluators
