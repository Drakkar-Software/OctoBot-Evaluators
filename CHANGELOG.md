# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
 
## [1.6.21] - 2021-09-20
### Updated
- bump requirements

## [1.6.20] - 2021-09-10
### Fixed
- Error on TA re-evaluations without enough candles data

## [1.6.19] - 2021-08-11
### Fixed
- Real time time frames are now available in TA

## [1.6.18] - 2021-08-05
### Fixed
- Real time evaluators time frames fallback strategy

## [1.6.17] - 2021-07-19
### Updated
- bump requirements

## [1.6.16] - 2021-05-05
### Updated
- bump requirements

## [1.6.15] - 2021-03-03 
### Added 
- Python 3.9 support

## [1.6.14] - 2020-02-25
### Updated
- Requirements

## [1.6.13] - 2020-02-08
### Updated
- Requirements

## [1.6.12] - 2020-02-03
### Updated
- Requirements

## [1.6.11] - 2020-12-30
### Fixed
- Cython headers

## [1.6.10] - 2020-12-29
### Fixed
- Multiple unrelated traded pairs under the same cryptocurrency init process

## [1.6.9] - 2020-12-28
### Updated
- Requirements

## [1.6.8] - 2020-12-23
### Added
- Profiles handling

## [1.6.7] - 2020-11-30
### Fixed
- Evaluators channel filters for non wildcard evaluators

## [1.6.6] - 2020-11-21
### Updated
- OctoBot-Trading import

## [1.6.5] - 2020-11-07
### Updated
- Requirements

## [1.6.4] - 2020-10-29
### Updated
- Numpy requirement

## [1.6.3] - 2020-10-27
### Updated
- Evaluator factory improvements

## [1.6.2] - 2020-10-27
### Added
- Evaluator factory tests

## [1.6.1] - 2020-10-23
### Updated
- Python 3.8 support

## [1.6.0] - 2020-10-04
### Updated
- Requirements

## [1.5.23] - 2020-09-01
### Updated
- Requirements

## [1.5.22] - 2020-08-15
### Updated
- Requirements

## [1.5.21] - 2020-06-28
### Updated
- Numpy requirement

## [1.5.20] - 2020-06-28
### Updated
- Requirements

## [1.5.19] - 2020-06-19
### Updated
- Requirements

## [1.5.18] - 2020-06-07
### Updated
- Skip evaluator creation when no activated strategy

## [1.5.17] - 2020-06-04
### Fixed
- TA OHLCV channel registration

## [1.5.16] - 2020-05-27
### Updated
- Cython version

## [1.5.15] - 2020-05-21
### Updated
- Remove advanced manager from commons

## [1.5.14] - 2020-05-21
### Updated
- TA re-evaluation trading API

## [1.5.13] - 2020-05-16
### Updated
- Requirements

## [1.5.12] - 2020-05-16
### Added
- [OctoBotChannel] Add consumer

## [1.5.11] - 2020-05-14
### Fixed
- [AbstractEvaluator] Priority level

## [1.5.10] - 2020-05-14
### Changed
- [EvaluatorChannel] Default priority level to medium

## [1.5.9] - 2020-05-11
### Fixed
- [Strategies] Fix cache handling

## [1.5.8] - 2020-05-10
### Update
- [Strategies] use exchange for allowed time delta in TA evaluation validity check

## [1.5.7] - 2020-05-10
### Update
- [Requirements] requirements update

## [1.5.6] - 2020-05-08
### Update
- [Requirements] requirements update

## [1.5.5] - 2020-05-03
### Fixed
- [API] Initialization incorrect type

## [1.5.4] - 2020-05-03
### Fixed
- [EventTree] Remove event related methods in matrix_manager

## [1.5.3] - 2020-05-02
### Added
- [Channel] Synchronization support

## [1.5.2] - 2020-05-02
### Updated
- octobot-channels requirement

## [1.5.1] - 2020-04-28
### Updated
- [Strategies]: Technical evaluator cycle handling
- [Evaluators]: Evaluation time handling

## [1.5.0] - 2020-04-17
### Added
- [Channels] Evaluators channel
- Matrix event clear management
- Matrix node value expiration

### Updated
- [Channels] get_chan api with a new matrix_id param

## [1.4.8] - 2020-04-13
### Updated
- [TA] Update ohlcv callback

## [1.4.7] - 2020-04-12
### Added
- Matrix manager

## [1.4.6] - 2020-04-10
### Added
- Bot id support

## [1.4.5] - 2020-04-07
### Fixed
- Wildcard imports

## [1.4.4] - 2020-04-05
### Updated
- Integrate OctoBot-tentacles-manager 2.0.0

## [1.4.3] - 2020-04-04
### Updated
- Exception logger API from Commons

### Fixed
- Travis CI file

## [1.4.2] - 2020-02-17
### Added
- Stop method to AbstractEvaluator

### Updated
- Evaluator, initialization, matrix APIs
- Matrix channel logger

## [1.4.1] - 2020-01-18
### Updated
- Use exchange_id in exchange channels

## [1.4.0] - 2020-01-14
### Added
- Matrices class to storage matrix instances

### Updated
**Requirements**
- Commons version to 1.2.2
- Channels version to 1.3.19
- Tentacles Manager version to 1.0.13

## [1.3.3] - 2020-01-12
### Added
- get_evaluator_classes_from_type API method

### Updated
- Typing for API methods
- Social evaluator intialization

## [1.3.2] - 2020-01-07
### Added
- Cryptocurrency related evaluator

## [1.3.1] - 2019-12-21
### Updated
**Requirements**
- Commons version to 1.2.0
- Channels version to 1.3.17

## [1.3.0] - 2019-12-14
### Changed
- EvaluatorMatrix to EventTree implementation (from Commons)

### Updated
**Requirements**
- Commons version to 1.1.51
- Channels version to 1.3.16

## [1.2.6] - 2019-11-09
### Updated
**Requirements**
- Cython version to 0.29.14
- Commons version to 1.1.49
- Channels version to 1.3.15

## [1.2.5] - 2019-10-30
### Changed
- OSX support

## [1.2.4] - 2019-10-11
### Changed
- Style improvements

## [1.2.3] - 2019-10-09
### Added
- PyPi manylinux deployment

## [1.2.2] - 2019-10-08
### Changed
- Setup install

## [1.2.1] - 2019-10-07
### Changed
- Improved matrix channel cancelling management

## [1.2.0] - 2019-10-05
### Added
- Evaluator types management
- Initialization API

## Moved
- config_manager to commons

### Fixed
- Channels package compatibility
- Commons package compatibility

## [1.1.0] - 2019-09-01
### Changed
- Improved API initialization
- Improved matrix management

### Fixed
- Channel package compatibility

## [1.0.0] - 2019-08-14
### Added
- Evaluator classes migrations from OctoBot project
- Matrix class that manage global evaluation dictionary
- Matrix channel, producer and consumer
- First API methods
