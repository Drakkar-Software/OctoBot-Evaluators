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
from octobot_channels.channels.channel import get_chan
from octobot_commons.constants import CONFIG_WILDCARD
from octobot_commons.enums import TimeFrames
from octobot_commons.time_frame_manager import parse_time_frames
from octobot_evaluators.channels.evaluator_channel import get_chan
from octobot_evaluators.constants import MATRIX_CHANNEL, \
    STRATEGIES_REQUIRED_TIME_FRAME, CONFIG_FORCED_TIME_FRAME, STRATEGIES_REQUIRED_EVALUATORS, TENTACLE_DEFAULT_CONFIG, \
    EVALUATOR_CHANNEL_DATA_ACTION, RESET_EVALUATION, EVALUATOR_CHANNEL_DATA_TIME_FRAMES
from octobot_evaluators.data_manager.matrix_manager import get_tentacles_value_nodes, \
    get_tentacle_path, get_node_children_by_names_at_path, get_tentacle_value_path, get_tentacle_eval_time, \
    get_matrix_default_value_path, is_tentacle_value_valid
from octobot_evaluators.enums import EvaluatorMatrixTypes
from octobot_evaluators.errors import UnsetTentacleEvaluation
from octobot_evaluators.evaluator import AbstractEvaluator
from octobot_commons.evaluators_util import check_valid_eval_note
from octobot_tentacles_manager.api.configurator import get_tentacle_config


class StrategyEvaluator(AbstractEvaluator):
    __metaclass__ = AbstractEvaluator

    def __init__(self):
        super().__init__()
        self.consumer_instance = None
        self.strategy_time_frames = []
        self.evaluations_last_updates = {}

    async def start(self, bot_id: str) -> bool:
        """
        Default Strategy start: to be overwritten
        Subscribe to Matrix notification from self.symbols and self.time_frames
        :return: success of the evaluator's start
        """
        await super().start(bot_id)
        self.consumer_instance = await get_chan(MATRIX_CHANNEL, self.matrix_id).new_consumer(
            self.strategy_matrix_callback)
        return True

    @classmethod
    def get_is_requiring_complete_TA_updates(cls) -> bool:
        """
        :return: True if the strategy is to be waken up by technical evaluators only when every time frame update
        has been completed. This avoids partial time frame updates wakeup.
        """
        return True

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
        # TODO: find better way than this if
        # avoid self-calls
        if evaluator_name == self.get_name():
            return
        # if this callback is from a technical evaluator: ensure strategy should be notified at this moment
        if evaluator_type == EvaluatorMatrixTypes.TA.value:
            # ensure this time frame is within the strategy's time frames
            if TimeFrames(time_frame) not in self.strategy_time_frames or \
                self.get_is_requiring_complete_TA_updates() and \
                    (
                        # ensure this evaluation has not already been sent
                        self._already_sent_this_technical_evaluation(matrix_id,
                                                                     evaluator_name,
                                                                     evaluator_type,
                                                                     exchange_name,
                                                                     cryptocurrency,
                                                                     symbol,
                                                                     time_frame)
                        # ensure every technical evaluator form this time frame are valid
                        or not self._are_every_evaluation_valid(matrix_id,
                                                                evaluator_name,
                                                                evaluator_type,
                                                                exchange_name,
                                                                cryptocurrency,
                                                                symbol,
                                                                time_frame)
                    ):
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
        available_time_frames = self.get_available_time_frames(matrix_id, exchange_name, evaluator_type,
                                                               cryptocurrency, symbol)
        to_check_time_frames = [tf
                                for tf in available_time_frames
                                if TimeFrames(tf) in self.strategy_time_frames]
        available_evaluators = self._get_available_evaluators(matrix_id, exchange_name, evaluator_type)
        to_validate_node_paths = [
            get_matrix_default_value_path(tentacle_name=evaluator,
                                          tentacle_type=evaluator_type,
                                          exchange_name=exchange_name,
                                          cryptocurrency=cryptocurrency,
                                          symbol=symbol,
                                          time_frame=time_frame)
            for time_frame in to_check_time_frames
            for evaluator in available_evaluators
        ]
        current_time = self._get_exchange_current_time(exchange_name, matrix_id)
        # negative time delta to invalidate evaluations 10 secs before next timestamp
        nodes_paths_to_authorized_delta = 10
        # ensure all evaluations are valid (do not trigger on an expired evaluation)
        if all(is_tentacle_value_valid(self.matrix_id, evaluation_node_path,
                                       timestamp=current_time,
                                       delta=nodes_paths_to_authorized_delta)
               for evaluation_node_path in to_validate_node_paths):
            self._save_last_evaluation(matrix_id, exchange_name, evaluator_type, evaluator_name,
                                       cryptocurrency, symbol, time_frame)
            return True
        return False

    def _save_last_evaluation(self, matrix_id, exchange_name, evaluator_type, tentacle_name,
                              cryptocurrency, symbol, time_frame):
        update_time = get_tentacle_eval_time(matrix_id,
                                             get_matrix_default_value_path(
                                                  tentacle_name=tentacle_name,
                                                  tentacle_type=evaluator_type,
                                                  exchange_name=exchange_name,
                                                  cryptocurrency=cryptocurrency,
                                                  symbol=symbol,
                                                  time_frame=time_frame)
                                             )
        self._set_last_evaluation_time(exchange_name, evaluator_type, cryptocurrency, symbol, time_frame, update_time)

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

    def get_evaluations_by_evaluator(self,
                                     matrix_id,
                                     exchange_name=None,
                                     tentacle_type=None,
                                     cryptocurrency=None,
                                     symbol=None,
                                     time_frame=None,
                                     allow_missing=True,
                                     allowed_values=None) -> dict:
        evaluator_nodes = get_node_children_by_names_at_path(matrix_id,
                                                             get_tentacle_path(exchange_name=exchange_name,
                                                                               tentacle_type=tentacle_type))
        evaluations_by_evaluator = {}
        for evaluator_name, node in evaluator_nodes.items():
            evaluation = get_tentacles_value_nodes(matrix_id, [node], cryptocurrency=cryptocurrency,
                                                   symbol=symbol, time_frame=time_frame)
            if len(evaluation) > 1:
                self.logger.warning("More than one evaluation corresponding to the given tentacle filter, "
                                    "this means there is an issue in this methods given arguments")
            else:
                if evaluation:
                    eval_value = evaluation[0].node_value
                    if (allowed_values is not None and eval_value in allowed_values) or \
                            check_valid_eval_note(eval_value):
                        evaluations_by_evaluator[evaluator_name] = evaluation[0]
                    elif not allow_missing:
                        raise UnsetTentacleEvaluation(f"Missing {time_frame if time_frame else 'evaluation'} "
                                                      f"for {evaluator_name} on {symbol}, evaluation is "
                                                      f"{repr(eval_value)}).")
        return evaluations_by_evaluator

    @staticmethod
    def _get_available_evaluators(matrix_id, exchange_name, tentacle_type):
        return get_node_children_by_names_at_path(matrix_id,
                                                  get_tentacle_path(exchange_name=exchange_name,
                                                                    tentacle_type=tentacle_type)).keys()

    @staticmethod
    def get_available_time_frames(matrix_id,
                                  exchange_name=None,
                                  tentacle_type=None,
                                  cryptocurrency=None,
                                  symbol=None):
        try:
            evaluator_nodes = get_node_children_by_names_at_path(matrix_id,
                                                                 get_tentacle_path(exchange_name=exchange_name,
                                                                                   tentacle_type=tentacle_type))
            first_node = next(iter(evaluator_nodes.values()))
            return get_node_children_by_names_at_path(matrix_id,
                                                      get_tentacle_value_path(cryptocurrency=cryptocurrency,
                                                                              symbol=symbol),
                                                      starting_node=first_node).keys()
        except StopIteration:
            return []

    def get_available_symbols(self, matrix_id, exchange_name,
                              cryptocurrency, tentacle_type=EvaluatorMatrixTypes.TA.value):
        try:
            evaluator_nodes = get_node_children_by_names_at_path(matrix_id,
                                                                 get_tentacle_path(exchange_name=exchange_name,
                                                                                   tentacle_type=tentacle_type))
            first_node = next(iter(evaluator_nodes.values()))
            possible_symbols = get_node_children_by_names_at_path(
                matrix_id,
                get_tentacle_value_path(cryptocurrency=cryptocurrency),
                starting_node=first_node).keys()
            if possible_symbols:
                return possible_symbols
            else:
                # try with real time evaluators
                return self.get_available_symbols(matrix_id, exchange_name,
                                                  cryptocurrency, EvaluatorMatrixTypes.REAL_TIME.value)
        except StopIteration:
            return []

    def _get_tentacle_registration_topic(self, all_symbols_by_crypto_currencies, time_frames, real_time_time_frames):
        strategy_currencies, symbols, self.strategy_time_frames = super()._get_tentacle_registration_topic(
            all_symbols_by_crypto_currencies,
            time_frames,
            real_time_time_frames)
        self.all_symbols_by_crypto_currencies = all_symbols_by_crypto_currencies
        to_handle_time_frames = [self.time_frame]
        # by default no time frame registration for strategies
        return strategy_currencies, symbols, to_handle_time_frames

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
    def get_required_evaluators(cls, strategy_config: dict = None):
        strategy_config: dict = strategy_config or get_tentacle_config(cls)
        if STRATEGIES_REQUIRED_EVALUATORS in strategy_config:
            return strategy_config[STRATEGIES_REQUIRED_EVALUATORS]
        else:
            raise Exception(f"'{STRATEGIES_REQUIRED_EVALUATORS}' is missing in configuration file")

    @classmethod
    def get_default_evaluators(cls):
        strategy_config: dict = get_tentacle_config(cls)
        if TENTACLE_DEFAULT_CONFIG in strategy_config:
            return strategy_config[TENTACLE_DEFAULT_CONFIG]
        else:
            required_evaluators = cls.get_required_evaluators(strategy_config)
            if required_evaluators == CONFIG_WILDCARD:
                return []
            else:
                return required_evaluators
