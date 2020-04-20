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

from octobot_channels.channels.channel import get_chan
from octobot_commons.constants import CONFIG_WILDCARD, MINUTE_TO_SECONDS
from octobot_commons.enums import TimeFrames, TimeFramesMinutes
from octobot_commons.time_frame_manager import parse_time_frames
from octobot_evaluators.channels.evaluator_channel import get_chan
from octobot_evaluators.constants import MATRIX_CHANNEL, \
    STRATEGIES_REQUIRED_TIME_FRAME, CONFIG_FORCED_TIME_FRAME, STRATEGIES_REQUIRED_EVALUATORS, TENTACLE_DEFAULT_CONFIG, \
    TA_LOOP_CALLBACK
from octobot_evaluators.data_manager.evaluation import Evaluation
from octobot_evaluators.data_manager.matrix_manager import get_tentacles_value_nodes, \
    get_tentacle_path, get_node_children_by_names_at_path, get_tentacle_value_path, get_nodes_event, \
    get_matrix_default_value_path, is_tentacle_value_valid, get_nodes_clear_event
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
        self.should_stop = False
        self.update_loop_tasks = []
        self.strategy_time_frames = []
        self.strategy_currencies = []
        self.all_symbols_by_crypto_currencies = {}

    async def start(self, bot_id: str) -> bool:
        """
        Default Strategy start: to be overwritten
        Subscribe to Matrix notification from self.symbols and self.time_frames
        :return: success of the evaluator's start
        """
        await super().start(bot_id)
        self.consumer_instance = await get_chan(MATRIX_CHANNEL, self.matrix_id).new_consumer(self.matrix_callback)
        # start technical evaluator auto-update loop
        await self._init_TA_update_loops()
        return True

    async def stop(self) -> None:
        self.should_stop = True
        if self.consumer_instance:
            await get_chan(MATRIX_CHANNEL, self.matrix_id).remove_consumer(self.consumer_instance)
        for task in self.update_loop_tasks:
            task.cancel()
        self.update_loop_tasks = []

    async def matrix_callback(self,
                              matrix_id,
                              evaluator_name,
                              evaluator_type,
                              eval_note,
                              eval_note_type,
                              eval_time,
                              exchange_name,
                              cryptocurrency,
                              symbol,
                              time_frame):
        # To be used to trigger an evaluation
        # Do not forget to check if evaluator_name is self.name
        pass

    async def technical_evaluators_update_loop_callback(self,
                                                        matrix_id,
                                                        update_source,
                                                        evaluator_type,
                                                        current_time,
                                                        exchange_name,
                                                        cryptocurrency,
                                                        symbol,
                                                        time_frame):
        # Automatically called every time all technical evaluators have a relevant evaluation
        # Mostly called after a time-frame updates
        # To be used to trigger an evaluation
        # Do not forget to check if evaluator_name is self.name
        pass

    async def _init_TA_update_loops(self):
        try:
            from octobot_trading.api.exchange import get_exchange_manager_from_exchange_name_and_id, \
                get_exchange_id_from_matrix_id
            for exchange_name in get_node_children_by_names_at_path(self.matrix_id, []).keys():
                exchange_manager = get_exchange_manager_from_exchange_name_and_id(
                    exchange_name,
                    get_exchange_id_from_matrix_id(exchange_name, self.matrix_id)
                )
                for cryptocurrency in self.strategy_currencies:
                    for symbol in self.all_symbols_by_crypto_currencies[cryptocurrency]:
                        await self._strategy_TA_update_loop_by_time_frame(exchange_name, exchange_manager,
                                                                          cryptocurrency, symbol)
        except ImportError:
            self.logger.error(f"Can't start technical evaluators update loop: "
                              f"requires OctoBot-Trading package installed")

    async def _strategy_TA_update_loop_by_time_frame(self, exchange_name, exchange_manager,
                                                     cryptocurrency, symbol):
        available_time_frames = self.get_available_time_frames(self.matrix_id, exchange_name,
                                                               EvaluatorMatrixTypes.TA.value, cryptocurrency, symbol)
        # if this exchange support this symbol
        if available_time_frames:
            available_time_frames = [tf
                                     for tf in available_time_frames
                                     if TimeFrames(tf) in self.strategy_time_frames]
            available_evaluators = self._get_available_evaluators(self.matrix_id, exchange_name,
                                                                  EvaluatorMatrixTypes.TA.value)
            to_validate_node_paths = [
                get_matrix_default_value_path(tentacle_name=evaluator,
                                              tentacle_type=EvaluatorMatrixTypes.TA.value,
                                              exchange_name=exchange_name,
                                              cryptocurrency=cryptocurrency,
                                              symbol=symbol,
                                              time_frame=time_frame)
                for time_frame in available_time_frames
                for evaluator in available_evaluators
            ]
            self.update_loop_tasks.extend(
                asyncio.create_task(self._strategy_TA_update_loop(exchange_name, exchange_manager,
                                                                  available_evaluators, cryptocurrency,
                                                                  symbol, time_frame, to_validate_node_paths))
                for time_frame in available_time_frames
            )

    async def _strategy_TA_update_loop(self, exchange_name, exchange_manager, available_evaluators, cryptocurrency,
                                       symbol, time_frame, to_validate_node_paths):
        TA_update_timeout = TimeFramesMinutes[TimeFrames(time_frame)] * MINUTE_TO_SECONDS * 1.5
        try:
            while not self.should_stop:
                try:
                    await self._wait_for_evaluation_and_update(exchange_name, exchange_manager, available_evaluators,
                                                               cryptocurrency, symbol, time_frame, to_validate_node_paths,
                                                               TA_update_timeout)
                except TimeoutError:
                    self.logger.error(f"Technical evaluation of pair {symbol} took too long.")
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.logger.exception(e, True, f"Error when handling strategy technical evaluators update loop: "
                                           f"{e.__class__.__name__} {e}")

    async def _wait_for_evaluation_and_update(self, exchange_name, exchange_manager, available_evaluators,
                                              cryptocurrency, symbol, time_frame, to_validate_node_paths,
                                              update_timeout):
        from octobot_trading.api.exchange import get_exchange_current_time
        nodes_paths = [
            get_matrix_default_value_path(tentacle_name=evaluator,
                                          tentacle_type=EvaluatorMatrixTypes.TA.value,
                                          exchange_name=exchange_name,
                                          cryptocurrency=cryptocurrency,
                                          symbol=symbol,
                                          time_frame=time_frame)
            for evaluator in available_evaluators
        ]
        # negative time delta to invalidate evaluations 10 secs before next timestamp
        nodes_paths_to_authorized_delta = 10
        # wait for all evaluations for all time frames to be set
        await self._wait_for_evaluation(nodes_paths, update_timeout, clear_event=False)
        current_time = get_exchange_current_time(exchange_manager)
        # ensure all evaluations are valid (do not trigger on an expired evaluation)
        if all(is_tentacle_value_valid(self.matrix_id, evaluation_node_path,
                                       timestamp=current_time,
                                       delta=nodes_paths_to_authorized_delta)
               for evaluation_node_path in to_validate_node_paths):
            self.logger.info(f"is_tentacle_value_valid {nodes_paths}")
            try:
                self.logger.debug(f"Entering technical_evaluators_update_loop_callback for {symbol}")
                await self.technical_evaluators_update_loop_callback(self.matrix_id,
                                                                     TA_LOOP_CALLBACK,
                                                                     EvaluatorMatrixTypes.TA,
                                                                     current_time,
                                                                     exchange_name,
                                                                     cryptocurrency,
                                                                     symbol,
                                                                     time_frame)
            finally:
                self.logger.debug(f"Exiting technical_evaluators_update_loop_callback for {symbol}")
        else:
            self.logger.info(f"not is_tentacle_value_valid {nodes_paths}")
        # wait for evaluation clear
        await self._wait_for_evaluation(nodes_paths, update_timeout, clear_event=True)

    async def _wait_for_evaluation(self, nodes_paths, timeout, clear_event):
        if clear_event:
            await asyncio.wait_for(await get_nodes_clear_event(self.matrix_id, nodes_paths, timeout=timeout),
                                   timeout=timeout)
            self.logger.info(f"clear event received on {nodes_paths[-1]}")
        else:
            await asyncio.wait_for(await get_nodes_event(self.matrix_id, nodes_paths, timeout=timeout), timeout=timeout)
            self.logger.info(f"set event received {nodes_paths[-1]}")

    def _get_evaluator_nodes_time_frame_path(self,
                                             matrix_id,
                                             exchange_name,
                                             tentacle_type,
                                             cryptocurrency,
                                             symbol,
                                             time_frame):
        evaluator_nodes = get_node_children_by_names_at_path(matrix_id,
                                                             get_tentacle_path(exchange_name=exchange_name,
                                                                               tentacle_type=tentacle_type))
        return [
            get_matrix_default_value_path(tentacle_name=evaluator_name,
                                          tentacle_type=tentacle_type,
                                          exchange_name=exchange_name,
                                          cryptocurrency=cryptocurrency,
                                          symbol=symbol,
                                          time_frame=time_frame
                                          )
            for evaluator_name in evaluator_nodes.keys()
        ]

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
                        evaluations_by_evaluator[evaluator_name] = Evaluation(evaluator_name,
                                                                              eval_value,
                                                                              evaluation[0].node_type,
                                                                              evaluation[0].node_value_time)
                    elif not allow_missing:
                        raise UnsetTentacleEvaluation(f"Missing {time_frame if time_frame else 'evaluation'} "
                                                      f"for {evaluator_name} on {symbol}, evaluation is "
                                                      f"{repr(eval_value)}).")
        return evaluations_by_evaluator

    def _get_available_evaluators(self, matrix_id, exchange_name, tentacle_type):
        return get_node_children_by_names_at_path(matrix_id,
                                                  get_tentacle_path(exchange_name=exchange_name,
                                                                    tentacle_type=tentacle_type)).keys()

    def get_available_time_frames(self,
                                  matrix_id,
                                  exchange_name=None,
                                  tentacle_type=None,
                                  cryptocurrency=None,
                                  symbol=None):
        evaluator_nodes = get_node_children_by_names_at_path(matrix_id,
                                                             get_tentacle_path(exchange_name=exchange_name,
                                                                               tentacle_type=tentacle_type))
        first_node = next(iter(evaluator_nodes.values()))
        return get_node_children_by_names_at_path(matrix_id,
                                                  get_tentacle_value_path(cryptocurrency=cryptocurrency,
                                                                          symbol=symbol),
                                                  starting_node=first_node).keys()

    def get_available_symbols(self, matrix_id, exchange_name,
                              cryptocurrency, tentacle_type=EvaluatorMatrixTypes.TA.value):
        evaluator_nodes = get_node_children_by_names_at_path(matrix_id,
                                                             get_tentacle_path(exchange_name=exchange_name,
                                                                               tentacle_type=tentacle_type))
        first_node = next(iter(evaluator_nodes.values()))
        possible_symbols = get_node_children_by_names_at_path(matrix_id,
                                                              get_tentacle_value_path(cryptocurrency=cryptocurrency),
                                                              starting_node=first_node).keys()
        if possible_symbols:
            return possible_symbols
        else:
            # try with real time evaluators
            return self.get_available_symbols(matrix_id, exchange_name,
                                              cryptocurrency, EvaluatorMatrixTypes.REAL_TIME.value)

    def _get_tentacle_registration_topic(self, all_symbols_by_crypto_currencies, time_frames, real_time_time_frames):
        self.strategy_currencies, symbols, self.strategy_time_frames = super()._get_tentacle_registration_topic(
            all_symbols_by_crypto_currencies,
            time_frames,
            real_time_time_frames)
        self.all_symbols_by_crypto_currencies = all_symbols_by_crypto_currencies
        to_handle_time_frames = [self.time_frame]
        # by default no time frame registration for strategies
        return self.strategy_currencies, symbols, to_handle_time_frames

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
