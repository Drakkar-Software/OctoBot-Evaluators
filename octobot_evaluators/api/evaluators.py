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
import copy

import async_channel.channels as channel_instances

import octobot_commons.constants as common_constants
import octobot_commons.logging as logging
import octobot_commons.tentacles_management as tentacles_management
import octobot_commons.time_frame_manager as time_frame_manager

import octobot_evaluators.api as api
import octobot_evaluators.evaluators.channel as evaluator_channels
import octobot_evaluators.matrix as matrix
import octobot_evaluators.evaluators as evaluator

LOGGER_NAME = "EvaluatorsAPI"


async def create_and_start_all_type_evaluators(tentacles_setup_config: object,
                                               matrix_id: str,
                                               exchange_name: str,
                                               bot_id: str,
                                               symbols_by_crypto_currencies: dict = None,
                                               symbols: list = None,
                                               time_frames: list = None,
                                               real_time_time_frames: list = None,
                                               relevant_evaluators=common_constants.CONFIG_WILDCARD,
                                               ) -> list:
    return await evaluator.create_and_start_all_type_evaluators(tentacles_setup_config=tentacles_setup_config,
                                                                matrix_id=matrix_id,
                                                                exchange_name=exchange_name,
                                                                bot_id=bot_id,
                                                                symbols_by_crypto_currencies=symbols_by_crypto_currencies,
                                                                symbols=symbols,
                                                                time_frames=time_frames,
                                                                real_time_time_frames=real_time_time_frames,
                                                                relevant_evaluators=relevant_evaluators)


def get_evaluator_classes_from_type(evaluator_type, tentacles_setup_config, activated_only=True) -> list:
    if activated_only:
        return [cls for cls in tentacles_management.get_all_classes_from_parent(
            evaluator.EvaluatorClassTypes[evaluator_type]) if cls.is_enabled(tentacles_setup_config, False)]
    return tentacles_management.get_all_classes_from_parent(evaluator.EvaluatorClassTypes[evaluator_type])


async def initialize_evaluators(config, tentacles_setup_config) -> str:
    """
    :param config: bot config
    :param tentacles_setup_config: tentacles configuration
    :return: initialized matrix id
    """
    _init_time_frames(config, tentacles_setup_config)
    # take evaluators and strategies candles requirements into account if any
    api.init_required_candles_count_from_evaluators_and_strategies(config, tentacles_setup_config)

    return create_matrix()


def get_evaluators_time_frames(config) -> list:
    return time_frame_manager.get_config_time_frame(config)


def _init_time_frames(config, tentacles_setup_config):
    # Init time frames using enabled strategies
    api.init_time_frames_from_strategies(config, tentacles_setup_config)


def create_matrix() -> str:
    created_matrix: matrix.Matrix = matrix.Matrix()
    matrix.Matrices.instance().add_matrix(created_matrix)
    return created_matrix.matrix_id


async def stop_evaluator(evaluator) -> None:
    return await evaluator.stop()


async def stop_evaluator_channel(matrix_id, chan_name) -> None:
    try:
        await evaluator_channels.get_chan(chan_name, matrix_id).stop()
    except Exception as e:
        logging.get_logger(LOGGER_NAME).exception(e, True, f"Error when stopping evaluator channel {chan_name}: {e}")


async def stop_all_evaluator_channels(matrix_id) -> None:
    for channel in channel_instances.ChannelInstances.instance().channels[matrix_id]:
        await stop_evaluator_channel(matrix_id, channel)
