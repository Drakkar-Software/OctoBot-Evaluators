# OctoBot-Evaluators [1.5.0](https://github.com/Drakkar-Software/OctoBot-Evaluators/blob/master/CHANGELOG.md)
[![PyPI](https://img.shields.io/pypi/v/OctoBot-Evaluators.svg)](https://pypi.python.org/pypi/OctoBot-Evaluators/)
[![Build Status](https://travis-ci.com/Drakkar-Software/OctoBot-Evaluators.svg?branch=master)](https://travis-ci.com/Drakkar-Software/OctoBot-Evaluators) 
[![Build status](https://ci.appveyor.com/api/projects/status/p68n2y6547xhw0t6?svg=true)](https://ci.appveyor.com/project/Herklos/octobot-evaluators)

# Where are evaluators and strategies ?

Because OctoBot is modular, a wide range of evaluators and strategies are usable.

Default evaluators and strategies are located here: [https://github.com/Drakkar-Software/OctoBot-Packages](https://github.com/Drakkar-Software/OctoBot-Packages).

To install default evaluators and strategies in your OctoBot, run the following command: 

```bash
python start.py -p install all
```


It is also possible to specify which module(s) to install by naming it(them). In this case only the modules available in the available packages can be installed.
```
python start.py -p install forum_evaluator john_smith_macd_evaluator advanced_twitter_evaluator
```

**You can find how to create your OctoBot evaluators and strategies [here](https://github.com/Drakkar-Software/OctoBot/wiki/Customize-your-OctoBot).**

