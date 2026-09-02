# Vectorbtpro_Docs - Tutorials

**Pages:** 3

---

## Stop signals

**URL:** https://vectorbt.pro/pvt_ff8edc14/tutorials/stop-signals.md

**Contents:**
- Parameters
- Time windows
- Entry signals
- Exit signals
- Simulation
- Performance
- Bonus: Dashboard
- Summary

Our goal is to use large-scale backtesting to compare the performance of trading with and without stop loss (SL), trailing stop (TS), and take profit (TP) signals. To ensure this analysis is comprehensive, we will conduct a large number of experiments across three dimensions: instruments, time, and parameters.

First, we will select 10 cryptocurrencies by market capitalization (excluding stablecoins such as USDT) and gather 3 years of their daily pricing data. Specifically, we will backtest the period from 2018 to 2021, as this range includes periods of sharp price declines (such as corrections after the all-time high in December 2017 and during the coronavirus crisis in March 2020) as well as surges (the all-time high in December 2020). This provides a balanced perspective. For each instrument, we will split this period into 400 smaller, overlapping time windows, each lasting 6 months. We will run our tests on each of these windows to account for different market conditions. For each instrument and time window, we will generate an entry signal at the very first bar and determine an exit signal according to the stop configuration. We will test 100 stop values, increasing by 1% increments, and compare the performance of each one to trading randomly and holding during that specific time window. In total, we will conduct 2,000,000 tests.

!!! important Make sure you have at least 16 GB of free RAM available, or memory swapping enabled.

The first step is to define the parameters of the analysis pipeline. As discussed above, we will backtest 3 years of pricing data, use 400 time windows, 10 cryptocurrencies, and 100 stop values. We will also set fees and slippage to 0.25% each, and the initial capital to $100. The absolute amount does not matter, but it must be consistent across all assets to allow for direct comparison. Feel free to change any parameter of interest.

Our configuration produces sample sizes with enough statistical power to analyze four variables: assets (200k tests per asset), time (5k tests per time window), exit types (400k tests per exit type), and stop values (4k tests per stop type and value). Similar to Tableau's approach to dimensions and measures, we can group our performance metrics by each of these variables. However, we will mainly focus on 5 exit types: SL exits, TS exits, TP exits, random exits, and holding exits (executed at the last bar).

[=100% "Symbol 10/10"]{: .candystripe .candystripe-animate }

The data instance `yfdata` contains a dictionary of OHLCV data, keyed by cryptocurrency name. Each DataFrame contains 1096 rows (days) and 5 columns (O, H, L, C, and V). You can plot each DataFrame as follows:

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/stop-signals/yfdata.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/stop-signals/yfdata.dark.svg#only-dark){: .iimg loading=lazy }

Since assets are one of the dimensions we want to analyze, VBT expects us to combine them as columns into a single DataFrame and label them clearly. To do this, we swap assets and features to create a dictionary of DataFrames, now with assets as columns and keyed by feature name, such as "Open".

Next, we will use a 6-month sliding window over the entire time period and take 400 "snapshots" of each price DataFrame within this window. Each snapshot is a subset of data to be backtested independently. Like assets and other variables, snapshots also need to be stacked horizontally as columns. As a result, we will obtain 180 rows (window length in days) and 4000 columns (10 assets x 400 windows). Each column will represent the price of one asset within one specific time window.

Resetting the index prevents the operation from producing many NaNs.

but instead of stacking, store the result in a Series indexed by split label.

A great feature of VBT is its use of [hierarchical indexing](https://pandas.pydata.org/pandas-docs/stable/user_guide/advanced.html) to store valuable information for each backtest. This ensures that the column hierarchy is preserved throughout the entire backtesting pipeline—from signal generation to performance modeling—and can be easily extended. Currently, our columns have the following hierarchy:

This multi-index captures three parameters: the symbol, the start date of the time window, and its end date. Later, we will extend this multi-index with exit types and stop values, so that each of the 2 million tests has its own price series.

Unlike most other backtesting libraries, VBT does not store signals as a signed integer array. Instead, it splits signals into two boolean arrays—entries and exits—which makes manipulation much easier. At the beginning of each time window, let's generate an entry signal indicating a buy order. The DataFrame will have the same shape, index, and columns as the price DataFrame, so VBT can link their elements together.

For each of the entry signals we created, we will generate an exit signal according to our five exit types: SL, TS, TP, random, and holding. We will also concatenate their DataFrames into a single (huge) DataFrame with 180 rows and 2,000,000 columns, each representing a separate backtest. Since exit signals are boolean, their memory usage remains manageable.

Let's first generate exit signals according to stop conditions. We want to test 100 different stop values with a 1% increment, starting from 1% and ending at 100% (that is, find the timestamp where the price exceeds the entry price by 100%). When OHLC data is checked against these conditions, the position closes at (or shortly after) the time the particular stop is hit.

!!! tip We use [OHLCSTX](https://vectorbt.pro/pvt*ff8edc14/api/signals/generators/ohlcstx/#vectorbtpro.signals.generators.ohlcstx.OHLCSTX) instead of the built-in stop-loss in [Portfolio.from*signals](https://vectorbt.pro/pvt*ff8edc14/api/portfolio/base/#vectorbtpro.portfolio.base.Portfolio.from*signals) because we want to analyze signals before simulation. Also, constructing parameter grids is easier this way. For a reality check, you can run the same setup using [Portfolio.from*signals](https://vectorbt.pro/pvt*ff8edc14/api/portfolio/base/#vectorbtpro.portfolio.base.Portfolio.from_signals) alone.

indicator is an exit generator, so the first input array is always an entry mask.

because we cannot execute the stop at the same bar as the entry signal anyway.

Since we only need the exits and stop price arrays, set it to `None` to save memory.

This extends our column hierarchy with a new column level to indicate the stop value. We just need to make this consistent across all DataFrames:

A major feature of VBT is its strong emphasis on data science, allowing us to apply popular analysis tools to nearly any part of the backtesting pipeline. For example, let's explore how the number of exit signals depends on the stop type and value:

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/stop-signals/avg*num*signals.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/stop-signals/avg*num*signals.dark.svg#only-dark){: .iimg loading=lazy }

We see that TS is by far the most common exit signal. The SL and TP curves track closely up to a stop value of 50% and then diverge, with TP dominating. While it may seem that bulls are mostly in charge, especially for larger price moves, remember that it is much easier to achieve a 50% profit than a 50% loss, since the latter requires a 100% profit to recover. This means that negative downward spikes tend to dominate small to medium price changes (and potentially shake out weak hands). These are well-known dynamics in cryptocurrency markets.

To simplify our analysis going forward, we want to ensure that each column has at least one exit signal to close the position. If a column has no exit signal, we should add one at the last timestamp. We do this by combining the stop exits with a last-bar exit using the *OR* rule and selecting whichever signal comes first:

Next, we will generate signals for the two remaining exit types: random and holding. These will act as benchmarks to compare SL, TS, and TP against.

"Holding" exit signals are placed at the very last bar of each time series. In most cases, we do not need to bother with these, since we can simply assess open positions. However, for consistency, we want each column to have exactly one signal. Another reason is to ensure the shape and columns match those of the stop signals, so we can concatenate all DataFrames later.

To generate random exit signals, simply shuffle any signal array. The only requirement is that each column contains exactly one signal.

The final step is to concatenate all DataFrames along the column axis and add a new column level called `exit_type`:

The `exits` array now contains 2,000,000 columns—one for each backtest. The column hierarchy is complete, with one tuple of parameters per backtest.

!!! warning One boolean array takes roughly 400 MB of RAM:

This setup allows us to group signals by one or more levels and easily analyze them together. For example, let's compare different exit types and stop values by the average distance from exit signal to entry signal (in days):

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/stop-signals/avg*distance.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/stop-signals/avg*distance.dark.svg#only-dark){: .iimg loading=lazy }

This scatterplot gives a more detailed look at the distribution of exit signals. As expected, plain holding exits occur exactly 179 days after entry (the maximum possible), while random exits are distributed evenly across the time window and are not affected by any stop value. We are most interested in the stop curves, which are flat, indicating high price volatility during our timeframe. The lower the curve, the greater the likelihood of hitting a stop. For example, a TS of 20% is hit after an average of only 30 days, while SL and TP stops would take 72 and 81 days, respectively. But is an early exit actually beneficial?

Now comes the actual backtesting part:

already used to generate the signal arrays, the closing price is sufficient here.

The simulation took about 50 seconds on my Apple M1 and produced a total of 3,995,570 orders ready for analysis (should be 4 million, but some price data appear to be missing). Keep in mind that any floating array generated by the portfolio object with the same shape as our exit signals, such as portfolio value or returns, requires 8 * 180 * 2,000,000 bytes, or almost 3 GB of RAM. We can analyze anything from trades to Sharpe ratio, but given the size of the data, we will focus on a fast-to-calculate metric: total return.

If your computer takes a long time to run the simulation, you can:

chunk matches the shape of the price and entries arrays (and remember to delete the previous portfolio before running a new one):

[=100% "Chunk 5/5"]{: .candystripe .candystripe-animate }

This approach has similar execution time but is much easier on memory.

The first step is always to look at the baseline distribution:

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/stop-signals/holding*histplot.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/stop-signals/holding*histplot.dark.svg#only-dark){: .iimg loading=lazy }

The distribution of holding performance across time windows is highly left-skewed. On one hand, this indicates prolonged sideways and bearish regimes within our timeframe. On the other hand, since the price of any asset can rise infinitely but only fall to zero, the distribution is naturally denser on the left and sparser on the right. Every second return is a loss of more than 6%, but thanks to occasional bull runs, the strategy still achieves an average profit of 9%.

Let's add other strategies to our analysis:

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/stop-signals/return*by*type.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/stop-signals/return*by*type.dark.svg#only-dark){: .iimg loading=lazy }

None of the strategies outperforms the baseline's average return. However, the TP strategy is the most consistent—while it sets an upper bound that limits extreme profits (note the missing outliers), its trade returns are less volatile and mostly positive. SL and TS are unbounded at the top because some stops are never triggered, causing those columns to fall back to plain holding. The random strategy is interesting, too: while its average return is lower, it ranks second after TP in terms of median return and volatility.

To further support this picture, let's calculate each strategy's win rate:

Almost 60% of TP trades are profitable—a stark contrast to the other strategies. However, a high win rate does not guarantee long-term trading success if your winning trades are much smaller than your losing ones. Therefore, let's group by stop type and value and calculate the [expectancy](https://www.icmarkets.com/blog/reward-to-risk-win-ratio-and-expectancy/):

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/stop-signals/expectancy*by*stop.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/stop-signals/expectancy*by*stop.dark.svg#only-dark){: .iimg loading=lazy }

Each strategy can steadily add to our account over time, with the holding strategy emerging as the clear winner—we can expect to add nearly $9 out of every $100 invested after each 6-month holding period. The only configuration that outperforms the baseline is TS, specifically with stop values ranging from 20% to 40%. The weakest performers are SL and TS with stop values around 45% and 60%, which seem to be triggered at the bottoms of major corrections, making them even worse than random exits. The TP strategy, on the other hand, outperforms the random exit strategy once the stop value crosses 30%. In general, patience seems to pay off in cryptocurrencies.

Finally, let's see how these strategies fare under different market conditions. We will use a simplified regime classification that divides holding returns into 20 bins and calculates each strategy's expectancy within those bins (the last bin is excluded for chart readability). Due to the highly skewed distribution of holding returns, we need to ensure that the bins are equal in size.

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/stop-signals/expectancy*by*bin.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/stop-signals/expectancy*by*bin.dark.svg#only-dark){: .iimg loading=lazy }

The chart above confirms the general intuition behind stop orders: SL and TS help limit losses during downtrends, TP works well for short-term trades seeking quick gains, and holding excels in high-growth markets. Interestingly, random exits perform poorly in sideways and bullish periods, but they often match or outperform stop exits in bear markets.

Dashboards can be a powerful way to interact with your data.

Let's first define the components of our dashboard. We have two types of components: controls (such as an asset dropdown) and graphs. Controls set parameters and trigger updates for the graphs.

The second step is to define the update function, which is triggered whenever any control is changed. We also call this function manually to initialize the graphs with default parameters.

In the final step, we define the dashboard layout and run it:

<div class="grid cards width-eighty" markdown>

Large-scale backtesting is useful for much more than just hyperparameter optimization. When used thoughtfully, it provides a way to explore complex trading phenomena. By leveraging multidimensional arrays, dynamic compilation, and pandas integration—as done by VBT—you can quickly gain new insights by applying popular data science tools to each part of your backtesting pipeline.

In this example, we ran 2 million tests to see how various stop values affect stop signals' performance and how stop signals compare to holding and random trading. The results confirm many of our earlier beliefs about stop signals across different market conditions, but they also reveal optimal configurations that may have worked well in recent years of trading cryptocurrencies.

[:material-language-python: Python code](https://vectorbt.pro/pvt*ff8edc14/assets/jupytext/tutorials/stop-signals.py.txt){ .md-button target="blank*" } [:material-notebook-outline: Notebook](https://github.com/polakowo/vectorbt.pro/blob/notebooks/StopSignals.ipynb){ .md-button target="blank_" }

**Examples:**

Example 1 (pycon):
```pycon
>>> from vectorbtpro import *
>>> import ipywidgets

>>> seed = 42
>>> symbols = [
...     "BTC-USD", "ETH-USD", "XRP-USD", "BCH-USD", "LTC-USD", 
...     "BNB-USD", "EOS-USD", "XLM-USD", "XMR-USD", "ADA-USD"
... ]
>>> start_date = vbt.utc_timestamp("2018-01-01")
>>> end_date = vbt.utc_timestamp("2021-01-01")
>>> time_delta = end_date - start_date
>>> window_len = vbt.timedelta("180d")
>>> window_cnt = 400
>>> exit_types = ["SL", "TS", "TP", "Random", "Holding"]
>>> step = 0.01  # (1)!
>>> stops = np.arange(step, 1 + step, step)

>>> vbt.settings.wrapping["freq"] = "d"
>>> vbt.settings.plotting["layout"]["template"] = "vbt_dark"
>>> vbt.settings.portfolio["init_cash"] = 100.  # (2)!
>>> vbt.settings.portfolio["fees"] = 0.0025  # (3)!
>>> vbt.settings.portfolio["slippage"] = 0.0025  # (4)!

>>> pd.Series({
...     "Start date": start_date,
...     "End date": end_date,
...     "Time period (days)": time_delta.days,
...     "Assets": len(symbols),
...     "Window length": window_len,
...     "Windows": window_cnt,
...     "Exit types": len(exit_types),
...     "Stop values": len(stops),
...     "Tests per asset": window_cnt * len(stops) * len(exit_types),
...     "Tests per window": len(symbols) * len(stops) * len(exit_types),
...     "Tests per exit type": len(symbols) * window_cnt * len(stops),
...     "Tests per stop type and value": len(symbols) * window_cnt,
...     "Tests total": len(symbols) * window_cnt * len(stops) * len(exit_types)
... })
Start date                       2018-01-01 00:00:00+00:00
End date                         2021-01-01 00:00:00+00:00
Time period (days)                                    1096
Assets                                                  10
Window length                            180 days 00:00:00
Windows                                                400
Exit types                                               5
Stop values                                            100
Tests per asset                                     200000
Tests per window                                      5000
Tests per exit type                                 400000
Tests per stop type and value                         4000
Tests total                                        2000000
dtype: object
```

Example 2 (pycon):
```pycon
>>> cols = ["Open", "Low", "High", "Close", "Volume"]
>>> yfdata = vbt.YFData.pull(symbols, start=start_date, end=end_date)
```

Example 3 (pycon):
```pycon
>>> yfdata.data.keys()
dict_keys(['BTC-USD', 'ETH-USD', 'XRP-USD', 'BCH-USD', 'LTC-USD', 
           'BNB-USD', 'EOS-USD', 'XLM-USD', 'XMR-USD', 'ADA-USD'])

>>> yfdata.data["BTC-USD"].shape
(1096, 7)
```

Example 4 (pycon):
```pycon
>>> yfdata.plot(symbol="BTC-USD").show()  # (1)!
```

---

## Overview

**URL:** https://vectorbt.pro/pvt_ff8edc14/tutorials/overview.md

Here you will find a comprehensive collection of guides and tutorials designed to help you master the powerful features of VBT. Whether you are a beginner looking to get started or an advanced user seeking to refine your skills, our tutorials cover everything from basic setup to complex strategy development.

<div class="grid cards" markdown>

---

## Basic RSI strategy

**URL:** https://vectorbt.pro/pvt_ff8edc14/tutorials/basic-rsi.md

**Contents:**
- Single backtest
- Multiple backtests
  - Using for-loop
  - Using columns
- Summary

One of the main strengths of VBT (PRO) is its ability to quickly create and backtest multiple strategy configurations. In this introductory example, we will explore the profitability of the following RSI strategy, which is commonly used by beginners:

As a bonus, we will gradually expand the analysis to include multiple parameter combinations. Sound interesting? Let's get started.

First, let's handle the data. With a simple one-liner, we can download all available daily data for the BTC/USDT pair from Binance:

[=100% "100%"]{: .candystripe .candystripe-animate }

The returned object is of type [BinanceData](https://vectorbt.pro/pvt*ff8edc14/api/data/custom/binance/#vectorbtpro.data.custom.binance.BinanceData), which extends [Data](https://vectorbt.pro/pvt*ff8edc14/api/data/base/#vectorbtpro.data.base.Data) to interact with the Binance API. The [Data](https://vectorbt.pro/pvt*ff8edc14/api/data/base/#vectorbtpro.data.base.Data) class is VBT's built-in container for retrieving, storing, and managing data. When a DataFrame is received, it is post-processed and stored inside the dictionary [Data.data](https://vectorbt.pro/pvt*ff8edc14/api/data/base/#vectorbtpro.data.base.Data.data), keyed by pair (also known as a "symbol" in VBT). You can access your DataFrame either from this dictionary or by using the convenient [Data.get](https://vectorbt.pro/pvt_ff8edc14/api/data/base/#vectorbtpro.data.base.Data.get) method, which lets you specify one or more columns instead of returning the entire DataFrame.

Let's plot the data using [Data.plot](https://vectorbt.pro/pvt_ff8edc14/api/data/base/#vectorbtpro.data.base.Data.plot):

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/basic-rsi/ohlcv.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/basic-rsi/ohlcv.dark.svg#only-dark){: .iimg loading=lazy }

Another way to describe the data is by using Pandas' [info](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.info.html) method. The tabular format is very helpful for counting null values (it looks like our data does not have any—great!)

In our example, we will generate signals based on the opening price and execute them using the closing price. We could also place orders as soon as the signal is generated, or at a later time, but here we will show how to separate the generation of signals from their execution.

Now it is time to run the indicator!

VBT supports five different RSI implementations: one written using Numba, and four more ported from three different technical analysis libraries. Each indicator is wrapped with the versatile [IndicatorFactory](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory). :mechanical*arm:

To list all available indicators or search for a specific one, use [IndicatorFactory.list*indicators](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.list_indicators):

You can retrieve the actual indicator class like this:

Here is a general rule for choosing an implementation:

To run any indicator, use the `run` method. To see which arguments this method accepts, pass it to [phelp](https://vectorbt.pro/pvt_ff8edc14/api/utils/formatting/#vectorbtpro.utils.formatting.phelp):

As shown above, we must at least provide `close`, which can be any numeric time series. By default, the rolling window is 14 bars and uses Wilder's smoothed moving average. Since we want to base our decisions on the opening price, we will pass `open_price` as `close`:

That's it! By calling the [RSI.run](https://vectorbt.pro/pvt_ff8edc14/api/indicators/custom/rsi/#vectorbtpro.indicators.custom.rsi.RSI.run) method, we calculated the RSI values and received an instance with various methods and properties for analysis. To retrieve the resulting Pandas object, you can access the `rsi` attribute (see "Outputs" in the result of `phelp`).

Now that we have the RSI array, we want to generate an entry signal whenever an RSI value crosses below 30, and an exit signal whenever it crosses above 70:

You can also use the methods [RSI.rsi*crossed*below](https://vectorbt.pro/pvt*ff8edc14/api/indicators/custom/rsi/#vectorbtpro.indicators.custom.rsi.RSI.rsi*crossed*below) and [RSI.rsi*crossed*above](https://vectorbt.pro/pvt*ff8edc14/api/indicators/custom/rsi/#vectorbtpro.indicators.custom.rsi.RSI.rsi*crossed*above), which were auto-generated for the `rsi` output by [IndicatorFactory](https://vectorbt.pro/pvt_ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory):

!!! tip If you are curious about what else has been generated, print `dir(rsi)` or explore the [API](https://vectorbt.pro/pvt_ff8edc14/api/indicators/custom/rsi/#vectorbtpro.indicators.custom.rsi.RSI) generated for the class.

Before proceeding with portfolio modeling, let's plot the RSI and signals to make sure we set everything up correctly:

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/basic-rsi/rsi.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/basic-rsi/rsi.dark.svg#only-dark){: .iimg loading=lazy }

The chart looks good. But notice how there are several entries between two exits, and vice versa? How does VBT handle this? When you use [Portfolio.from*signals](https://vectorbt.pro/pvt*ff8edc14/api/portfolio/base/#vectorbtpro.portfolio.base.Portfolio.from_signals), VBT will automatically ignore entry signals if a position is already open, and ignore exit signals if the position is already closed. To make our analysis clearer, let's keep only the first signal in each case:

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/basic-rsi/rsi2.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/basic-rsi/rsi2.dark.svg#only-dark){: .iimg loading=lazy }

The difference is clear. But what other methods are available to analyze the distribution of signals? How can you *quantify* this analysis? That's what VBT is all about. Let's compute various statistics for `clean*entries` and `clean*exits` using [SignalsAccessor](https://vectorbt.pro/pvt_ff8edc14/api/signals/accessors/#vectorbtpro.signals.accessors.SignalsAccessor):

between each entry and exit.

We are now ready for modeling! We will use the class method [Portfolio.from*signals](https://vectorbt.pro/pvt*ff8edc14/api/portfolio/base/#vectorbtpro.portfolio.base.Portfolio.from*signals), which takes the signal arrays, processes each signal step by step, and generates orders. It then creates an instance of [Portfolio](https://vectorbt.pro/pvt*ff8edc14/api/portfolio/base/#vectorbtpro.portfolio.base.Portfolio) that you can use to assess the strategy's performance.

Our experiment is simple: buy $100 of Bitcoin when an entry signal is generated and close the position when an exit signal is generated. We will start with infinite capital so our buying power is not limited at any time.

!!! info Running the method above for the first time may take some time because it needs to be compiled first. Compilation will happen each time a new combination of data types is encountered. But do not worry: Numba caches most compiled functions and reuses them in subsequent runs.

!!! tip If you check the API for [Portfolio.from*signals](https://vectorbt.pro/pvt*ff8edc14/api/portfolio/base/#vectorbtpro.portfolio.base.Portfolio.from*signals), you will notice that many arguments are set to None. The value `None` has a special meaning: it tells VBT to use the default value from the global settings. You can find all the default values for the `Portfolio` class [here](https://vectorbt.pro/pvt*ff8edc14/api/*settings/#vectorbtpro.*settings.portfolio).

Let's print the statistics for our portfolio:

!!! tip That's a lot of statistics, right? If you want to see how they're implemented, print `pf.metrics` and check the `calc_func` argument of the metric you're interested in. If a function is a lambda, check the source code to see its contents.

Our strategy is not too bad: the portfolio has gained over 71% in profit over the past years, but simply holding Bitcoin still outperformed it with a massive 450%. Despite Bitcoin's volatility, the minimum recorded portfolio value was $97 from $100 initially invested. The total time exposure of 38% means we were in the market 38% of the time. The maximum gross exposure of 100% means we invested 100% of our available cash on each trade. The maximum drawdown (MDD) of 46% is the largest drop from a portfolio high to a low (maybe a stop loss could help here?).

The total number of orders matches the total number of (cleaned) signals, but why are there only 8 trades instead of 15? By default, a trade in VBT is a sell order; as soon as an exit order is filled (reducing or closing the current position), the profit and loss (PnL) based on the weighted average entry and exit price is calculated. The win rate of 70% means that 70% of the trades (sell orders) generated a profit, with the best trade bringing a 54% profit and the worst bringing a 32% loss. Since the average winning trade brings more profit than the average losing trade brings loss, various metrics such as profit factor and expectancy are positive.

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/basic-rsi/pf.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/basic-rsi/pf.dark.svg#only-dark){: .iimg loading=lazy }

!!! tip One benefit of an interactive plot like this is that you can use tools from the Plotly toolbar to draw a vertical line connecting orders, their P&L, and their impact on cumulative returns. Give it a try!

So, how can we improve from here?

Even a simple strategy like ours offers many possible parameters:

To keep our analysis flexible, we will write a function that lets us specify all of this information and returns a subset of statistics:

!!! note We removed the signal cleaning step because it is not necessary when signals are passed to [Portfolio.from*signals](https://vectorbt.pro/pvt*ff8edc14/api/portfolio/base/#vectorbtpro.portfolio.base.Portfolio.from_signals) (which automatically cleans the signals for you).

By increasing the upper threshold to 80% and lowering the lower threshold to 20%, the number of trades dropped to just 2 because crossing these thresholds becomes much less likely. You can also see that the total return fell to roughly 7%—not a good sign. But how do we actually know if this negative result means our strategy is bad and not just a result of pure luck? Testing only one parameter combination from a large set is usually just guessing.

Let's generate multiple parameter combinations for the thresholds, simulate them, and concatenate their statistics for further analysis:

[Cartesian product](https://en.wikipedia.org/wiki/Cartesian_product).

[list comprehension](https://realpython.com/list-comprehension-python/). This creates a list of Series.

We just simulated 121 different combinations of upper and lower thresholds and stored their statistics in a list. To analyze this list, we need to convert it to a DataFrame first, with metrics arranged as columns:

But how do we know which row corresponds to which parameter combination? We will create a [MultiIndex](https://pandas.pydata.org/pandas-docs/stable/user*guide/advanced.html) with two levels, `lower*th` and `upper*th`, and set it as the index of `comb*stats_df`:

Much better! Now we can analyze each part of the retrieved information in different ways. Since we have the same number of lower and upper thresholds, let's create a heatmap with the X axis representing lower thresholds, the Y axis representing upper thresholds, and the color bar reflecting the expectancy:

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/basic-rsi/heatmap.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/basic-rsi/heatmap.dark.svg#only-dark){: .iimg loading=lazy }

Now we can explore entire regions of parameter combinations that yield positive or negative results.

As you may have read in the documentation, VBT is designed for processing multidimensional data. It is built around the idea that you can represent each asset, period, parameter combination, or backtest generally as a column in a two-dimensional array.

Instead of calculating everything inside a loop (which isn't wrong, but is often slower than a vectorized solution), we can update our code to accept parameters as arrays. A function that takes such an array will automatically convert multiple parameters into multiple columns. One major benefit of this approach is that we do not have to collect results, place them into a list, and convert them into a DataFrame—VBT handles it all!

First, define the parameters that we want to test:

Instead of applying `itertools.product`, we will instruct various parts of our pipeline to create a product instead, so that we can observe how each part affects the column hierarchy.

The RSI part is easy: we can pass `param*product=True` to build a product of `windows` and `wtypes` and run the calculation over each column in `open*price`:

We can see that [RSI](https://vectorbt.pro/pvt*ff8edc14/api/indicators/custom/rsi/#vectorbtpro.indicators.custom.rsi.RSI) has added two levels to the column hierarchy: `rsi*window` and `rsi*wtype`. These are similar to what we created manually for thresholds in [Using for-loop](#using-for-loop). There are now 39 columns in total, which equals `len(open*price.columns)` x `len(windows)` x `len(wtypes)`.

The next step is crossovers. Unlike indicators, crossovers are regular functions that take any array-like object, broadcast it to the shape of `rsi`, and then search for crossovers. The broadcasting step uses [broadcast](https://vectorbt.pro/pvt_ff8edc14/api/base/reshaping/#vectorbtpro.base.reshaping.broadcast), which is a powerful function for bringing multiple arrays into a single shape (learn more about broadcasting in the documentation).

In our case, we want to build a product of `lower*ths`, `upper*th*index`, and all columns in `rsi`. Since `rsi*crossed*below` and `rsi*crossed_above` are two different functions, we need to build a product of the threshold values manually, then instruct each crossover function to combine them with every column in `rsi`:

the second with the second, and so on—121 combinations in total.

that we want to build a product with the columns in `rsi`.

We have produced over 4719 columns—impressive! Did you notice, though, that `entries` and `exits` now have different columns? `entries` has `lower*th` as one of its column levels, while `exits` has `upper*th`. How can we pass differently labeled arrays (including `close*price`, which has only one column) to [Portfolio.from*signals](https://vectorbt.pro/pvt*ff8edc14/api/portfolio/base/#vectorbtpro.portfolio.base.Portfolio.from*signals)?

No worries! VBT knows how to merge this information. Let's see how it works:

takes the mean of all columns and returns a Series. Here, we want to disable the aggregation function and stack all Series into one large DataFrame.

Congratulations! We just backtested 4719 parameter combinations in less than a second :zap:

!!! important Even though we gained impressive performance, we need to be careful not to fill up all available RAM with our wide arrays. You can check the size of any [Pickleable](https://vectorbt.pro/pvt*ff8edc14/api/utils/pickling/#vectorbtpro.utils.pickling.Pickleable) instance using [Pickleable.getsize](https://vectorbt.pro/pvt*ff8edc14/api/utils/pickling/#vectorbtpro.utils.pickling.Pickleable.getsize). For example, to print the total size of our portfolio in a human-readable format:

One way to analyze the produced statistics is to use Pandas. For example, to calculate the mean expectancy for each `rsi_window`:

The longer the RSI window, the higher the mean expectancy.

Now, let's display the top 5 parameter combinations:

To analyze any specific combination with VBT, you can select it from the portfolio just like you would select a column in a regular Pandas DataFrame. Let's plot the equity of the most successful combination:

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/basic-rsi/value.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/basic-rsi/value.dark.svg#only-dark){: .iimg loading=lazy }

!!! tip Instead of selecting a column from a portfolio, which creates a new portfolio containing only that column, you can also check if the method you want to call supports the argument `column` and pass your column as this argument. For example, you could also use `pf.plot_value(column=(22, 80, 20, "wilder"))`.

Even though, in theory, the best combination doubles our money, it is still inferior to simply holding Bitcoin—our basic RSI strategy cannot beat the market :anger:

But even if it could, there is more to do than just searching for the right parameters: we need to at least (cross-)validate the strategy. You can also see how the strategy performs on other assets. Curious how? Just expand `open*price` and `close*price` to include multiple assets. Each example will work out of the box!

[=100% "100%"]{: .candystripe .candystripe-animate }

Your homework is to run the examples on this data.

The final columns will look like this:

We can see that the column hierarchy now contains another level, `symbol`, which represents the asset. Let's visualize the distribution of expectancy across both assets:

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/basic-rsi/histplot.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/basic-rsi/histplot.dark.svg#only-dark){: .iimg loading=lazy }

ETH appears to react more aggressively to our strategy on average than BTC. This could be due to the market's greater volatility, a different structure, or just pure randomness.

One of the main takeaways from this analysis is that with strategies that have simple and explainable mechanics, we can attempt to explain the mechanics of the market itself. Not only can we use this to improve ourselves and design better indicators, but we can also use this information as input to ML models, which are better at finding patterns than humans. The possibilities are endless!

VBT is a powerful tool that allows us to explore new areas more quickly and analyze them in greater detail. Rather than relying on overused and outdated charts and indicators from books and YouTube videos, we can create our own tools that align closely with the market. We can backtest thousands of strategy configurations to see how the market responds to each one—all in just milliseconds. All it takes is creativity :bulb:

[:material-language-python: Python code](https://vectorbt.pro/pvt*ff8edc14/assets/jupytext/tutorials/basic-rsi.py.txt){ .md-button target="blank*" } [:material-notebook-outline: Notebook](https://github.com/polakowo/vectorbt.pro/blob/notebooks/BasicRSI.ipynb){ .md-button target="blank_" }

**Examples:**

Example 1 (pycon):
```pycon
>>> from vectorbtpro import *  # (1)!

>>> data = vbt.BinanceData.pull('BTCUSDT')
>>> data
<vectorbtpro.data.custom.binance.BinanceData at 0x7f9c40c59550>
```

Example 2 (pycon):
```pycon
>>> data.plot().show()  # (1)!
```

Example 3 (pycon):
```pycon
>>> data.data['BTCUSDT'].info()
<class 'pandas.core.frame.DataFrame'>
DatetimeIndex: 1813 entries, 2017-08-17 00:00:00+00:00 to 2022-08-03 00:00:00+00:00
Freq: D
Data columns (total 9 columns):
 #   Column              Non-Null Count  Dtype  
---  ------              --------------  -----  
 0   Open                1813 non-null   float64
 1   High                1813 non-null   float64
 2   Low                 1813 non-null   float64
 3   Close               1813 non-null   float64
 4   Volume              1813 non-null   float64
 5   Quote volume        1813 non-null   float64
 6   Trade count         1813 non-null   int64  
 7   Taker base volume   1813 non-null   float64
 8   Taker quote volume  1813 non-null   float64
dtypes: float64(8), int64(1)
memory usage: 141.6 KB
```

Example 4 (pycon):
```pycon
>>> open_price = data.get('Open')
>>> close_price = data.get('Close')  # (1)!
```

---
