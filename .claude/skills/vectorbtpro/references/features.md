# Vectorbtpro_Docs - Features

**Pages:** 4

---

## Intelligence

**URL:** https://vectorbt.pro/pvt_ff8edc14/features/intelligence.md

**Contents:**
- Reranking
- Function calling
- Reasoning steps
- Source refactorer
- Quick search & chat
- ChatVBT
- SearchVBT
- Self-aware classes
- Knowledge assets
- And many more...

!!! info The first time you run most of these commands, it may take a while to prepare documents. However, most of the preparation steps are cached and stored, so future calls will be much faster and will not require repeating the process.

!!! abstract "Cookbook" Don't use OpenAI? Explore more configurations in the knowledge section of the [Cookbook](https://vectorbt.pro/pvt_ff8edc14/cookbook/).

![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/new-in/v2026*4_7.svg){ loading=lazy }

to surface the most relevant documents. Five providers are supported out of the box: Cohere, Jina, Voyage, Hugging Face cross-encoders (local), and any LLM via completions-based scoring.

=== "Example 1: Search with reranking"

=== "Example 2: Chat with local reranking"

![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/new-in/v2025*10_15.svg){ loading=lazy }

and define custom functions that the model can invoke, and all of this without any additional setup! This feature is particularly useful for complex queries, agentic workflows, and interactive applications where you want the model to perform specific tasks or calculations on your behalf.

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/function*calling.light.gif#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/function*calling.dark.gif#only-dark){: .iimg loading=lazy }

![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/new-in/v2025*10_15.svg){ loading=lazy }

at its conclusion. This is particularly useful for complex queries that require multiple steps to answer.

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/reasoning*steps.light.gif#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/reasoning*steps.dark.gif#only-dark){: .iimg loading=lazy }

![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/new-in/v2025*5_11.svg){ loading=lazy }

Python object, or raw string. If the source is larger than expected, it intelligently splits it into clean AST-based chunks, refactors each using an LLM, and merges them back into polished code. You can choose to return the result, update the source in place, or copy it to your clipboard. For full transparency, you can also preview the diff directly in your browser :pencil:

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/source*refiner.light.png#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/source*refiner.dark.png#only-dark){: .iimg loading=lazy }

![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/new-in/v2025*5_11.svg){ loading=lazy }

[BM25](https://en.wikipedia.org/wiki/Okapi_BM25) for fast, fully offline lexical search. This is perfect for quickly finding something specific.

![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/new-in/v2025*3_1.svg){ loading=lazy }

them to an LLM for completion. This allows you to interact seamlessly with the entire VBT knowledge base, receiving detailed and context-aware responses.

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/chatvbt.light.gif#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/chatvbt.dark.gif#only-dark){: .iimg loading=lazy }

![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/new-in/v2025*3_1.svg){ loading=lazy }

VBT provides a powerful smart search feature called SearchVBT. Enter your query and it will generate an HTML page with well-structured search results. Behind the scenes, SearchVBT uses a [RAG](https://en.wikipedia.org/wiki/Retrieval-augmented_generation) pipeline to embed, rank, and retrieve only the most relevant documents from VBT, ensuring precise and efficient search results.

![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/new-in/v2024*12_15.svg){ loading=lazy }

documentation, Discord messages, and code examples. You can even interact with it directly via an LLM!

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/knowledge*assets.light.gif#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/knowledge*assets.dark.gif#only-dark){: .iimg loading=lazy }

![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/new-in/v2024*11_12.svg){ loading=lazy }

knowledge assets—JSON files containing private website content and the complete "vectorbt.pro" Discord history. These assets can be used with LLMs and services like Cursor. In addition, VBT offers a palette of classes for working with these assets, providing functions such as converting to Markdown and HTML files, browsing the website offline, performing targeted searches, interacting with LLMs, and much more!

[:material-language-python: Python code](https://vectorbt.pro/pvt*ff8edc14/assets/jupytext/features/intelligence.py.txt){ .md-button target="blank*" }

**Examples:**

Example 1 (text):
```text
    >>> env["COHERE_API_KEY"] = "<YOUR_COHERE_API_KEY>"

    >>> vbt.search(  # (1)!
    ...     "How to rebalance weekly?",
    ...     rerank=True,  # (2)!
    ...     reranker="cohere",  # (3)!
    ...     rerank_limit=20,  # (4)!
    ... )
```

Example 2 (text):
```text
1. Works the same way with `vbt.chat()`, `vbt.quick_chat()`, and `vbt.interact()`.
2. Enable reranking after the initial retrieval pass.
3. Choose a reranker. Available options: `"cohere"`, `"jina"`, `"voyage"`, `"hf_cross_encoder"`, `"completions"`.
4. Only the top 20 documents from the initial ranking are sent to the reranker.
```

Example 3 (text):
```text
    >>> env["OPENAI_API_KEY"] = "<YOUR_OPENAI_API_KEY>"

    >>> vbt.chat(  # (1)!
    ...     "How to use stop losses with from_signals?",
    ...     rank_kwargs=dict(
    ...         rerank=True,
    ...         reranker="hf_cross_encoder",  # (2)!
    ...     ),
    ...     formatter="html",
    ... )
```

Example 4 (text):
```text
1. Pass reranking parameters through `rank_kwargs` when calling `vbt.chat()`.
2. Use a Hugging Face cross-encoder model for fully local, offline reranking.
```

---

## Overview

**URL:** https://vectorbt.pro/pvt_ff8edc14/features/overview.md

In addition to the [features](https://vectorbt.dev/getting-started/features/) available in the open-source version, VBT introduces many significant enhancements and optimizations in the following areas:

<div class="grid cards" markdown>

!!! info To keep pages concise, only a selection of the most interesting features from each release is highlighted. Full release notes are available exclusively to subscribers. If you are on the private website, navigate to *Getting started* → *Release notes*.

**Examples:**

Example 1 (text):
```text
Tags indicate releases where features were introduced for the first time. Please note that most 
features are continuously updated, so the following examples are intended to be run with the 
__latest__ version of VBT installed :writing_hand:

```python title="Import required by code examples"
from vectorbtpro import *  # (1)!
```

1. To view what is imported, call `whats_imported()`.
```

---

## Performance

**URL:** https://vectorbt.pro/pvt_ff8edc14/features/performance.md

**Contents:**
- Chunk caching
- Accumulators
- Chunking
- Parallel Numba
- Multithreading
- Multiprocessing
- Jitting
- Caching
- Hyperfast rolling metrics
- And many more...

![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/new-in/v2024*5_15.svg){ loading=lazy }

parameterization, splitting, and optimization—can now offload intermediate results to disk and reload them if the workflow crashes and restarts. You can confidently test billions of parameter combinations on cloud instances without worrying about losing your data.

![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/new-in/1*0_10.svg){ loading=lazy }

data. For example, calculating the sum of three arrays requires at least two passes. If you want to calculate such an indicator iteratively (bar by bar), you either need to pre-calculate everything and store it in memory or re-calculate each window, which can significantly impact performance. [Accumulators](https://theboostcpplibraries.com/boost.accumulators), however, maintain an internal state that allows you to compute an indicator value as soon as a new data point arrives, resulting in the best possible performance.

![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/new-in/1*0_0.svg){ loading=lazy }

automatically splits array-like arguments, passes each chunk to the function for execution, and then merges the results. This enables you to split large arrays and run any function in a distributed manner. VBT also features a central registry and provides chunking specifications for all arguments of most Numba-compiled functions, including simulation functions. Chunking can be enabled with a single command. You no longer have to worry about out-of-memory errors! :tada:

Both arrays will have the same number of values; for example, the first combination matches the first value in `fast*windows` with the first value in `slow*windows`.

[=100% "Chunk 48/48"]{: .candystripe .candystripe-animate }

![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/new-in/1*0_0.svg){ loading=lazy }

[automatic parallelization with `@jit`](https://numba.readthedocs.io/en/stable/user/parallel.html). You can enable this with a single command. This approach is best for lightweight functions that are applied to wide arrays.

![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/new-in/1*0_0.svg){ loading=lazy }

from `concurrent.futures`, [ThreadPool](https://pathos.readthedocs.io/en/latest/pathos.html#pathos.pools.ThreadPool) from `pathos`, and [Dask](https://dask.org/) backend for running multiple chunks across multiple threads. This is best for speeding up heavyweight functions that release the GIL, such as Numba and C functions. Multithreading + Chunking + Numba = :muscle:

![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/new-in/1*0_0.svg){ loading=lazy }

from `concurrent.futures`, [ProcessPool](https://pathos.readthedocs.io/en/latest/pathos.html#pathos.pools.ProcessPool) and [ParallelPool](https://pathos.readthedocs.io/en/latest/pathos.html#pathos.pools.ParallelPool) from `pathos`, [WorkerPool](https://sybrenjansen.github.io/mpire/usage/workerpool/index.html) from `mpire`, and [Ray](https://www.ray.io/) backend for running multiple chunks across multiple processes. This is best for speeding up heavyweight functions that do not release the GIL, such as regular Python functions, as well as lightweight arguments that are easy to serialize. Ever wanted to test billions of hyperparameter combinations in just a few minutes? Now you can by scaling functions and entire applications in the cloud using [Ray clusters](https://docs.ray.io/en/latest/cluster/getting-started.html) :eyes:

![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/new-in/1*0_0.svg){ loading=lazy }

means accelerating. While Numba remains the primary jitter, VBT now allows you to implement custom jitter classes, such as those for vectorized NumPy or even [JAX](https://github.com/google/jax) with GPU support. Every jitted function is registered globally, so you can switch between different implementations or even disable jitting entirely with a single command.

![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/new-in/1*0_0.svg){ loading=lazy }

This enables tracking useful statistics for all cacheable parts of VBT, such as showing the total cached size in MB. You get full control and transparency :window:

![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/new-in/1*0_0.svg){ loading=lazy }

[:material-language-python: Python code](https://vectorbt.pro/pvt*ff8edc14/assets/jupytext/features/performance.py.txt){ .md-button target="blank*" }

**Examples:**

Example 1 (python):
```python
>>> @vbt.parameterized(cache_chunks=True, chunk_len=1)  # (1)!
... def basic_iterator(i):
...     print("i:", i)
...     rand_number = np.random.uniform()
...     if rand_number < 0.2:
...         print("failed ⛔")
...         raise ValueError
...     return i

>>> attempt = 0
>>> while True:
...     attempt += 1
...     print("attempt", attempt)
...     try:
...         basic_iterator(vbt.Param(np.arange(10)))
...         print("completed 🎉")
...         break
...     except ValueError:
...         pass
attempt 1
i: 0
i: 1
failed ⛔
attempt 2
i: 1
i: 2
i: 3
i: 4
failed ⛔
attempt 3
i: 4
i: 5
i: 6
i: 7
i: 8
i: 9
completed 🎉
```

Example 2 (python):
```python
>>> @njit
... def fastest_rolling_zscore_1d_nb(arr, window, minp=None, ddof=1):
...     if minp is None:
...         minp = window
...     out = np.full(arr.shape, np.nan)
...     cumsum = 0.0
...     cumsum_sq = 0.0
...     nancnt = 0
...     
...     for i in range(len(arr)):
...         pre_window_value = arr[i - window] if i - window >= 0 else np.nan
...         mean_in_state = vbt.nb.RollMeanAIS(
...             i, arr[i], pre_window_value, cumsum, nancnt, window, minp
...         )
...         mean_out_state = vbt.nb.rolling_mean_acc_nb(mean_in_state)
...         _, _, _, mean = mean_out_state
...         std_in_state = vbt.nb.RollStdAIS(
...             i, arr[i], pre_window_value, cumsum, cumsum_sq, nancnt, window, minp, ddof
...         )
...         std_out_state = vbt.nb.rolling_std_acc_nb(std_in_state)
...         cumsum, cumsum_sq, nancnt, _, std = std_out_state
...         out[i] = (arr[i] - mean) / std
...     return out
    
>>> data = vbt.YFData.pull("BTC-USD")
>>> rolling_zscore = fastest_rolling_zscore_1d_nb(data.returns.values, 14)
>>> data.symbol_wrapper.wrap(rolling_zscore)
Date
2014-09-17 00:00:00+00:00         NaN
2014-09-18 00:00:00+00:00         NaN
2014-09-19 00:00:00+00:00         NaN
                                  ...   
2023-02-01 00:00:00+00:00    0.582381
2023-02-02 00:00:00+00:00   -0.705441
2023-02-03 00:00:00+00:00   -0.217880
Freq: D, Name: BTC-USD, Length: 3062, dtype: float64

>>> (data.returns - data.returns.rolling(14).mean()) / data.returns.rolling(14).std()
Date
2014-09-17 00:00:00+00:00         NaN
2014-09-18 00:00:00+00:00         NaN
2014-09-19 00:00:00+00:00         NaN
                                  ...   
2023-02-01 00:00:00+00:00    0.582381
2023-02-02 00:00:00+00:00   -0.705441
2023-02-03 00:00:00+00:00   -0.217880
Freq: D, Name: Close, Length: 3062, dtype: float64
```

Example 3 (text):
```text
>>> @vbt.chunked(
...     chunk_len=100,
...     merge_func="concat",  # (1)!
...     execute_kwargs=dict(  # (2)!
...         clear_cache=True,
...         collect_garbage=True
...     )
... )
... def backtest(data, fast_windows, slow_windows):  # (3)!
...     fast_ma = vbt.MA.run(data.close, fast_windows, short_name="fast")
...     slow_ma = vbt.MA.run(data.close, slow_windows, short_name="slow")
...     entries = fast_ma.ma_crossed_above(slow_ma)
...     exits = fast_ma.ma_crossed_below(slow_ma)
...     pf = vbt.PF.from_signals(data.close, entries, exits)
...     return pf.total_return

>>> param_product = vbt.combine_params(  # (4)!
...     dict(
...         fast_window=vbt.Param(range(2, 100), condition="fast_window < slow_window"),
...         slow_window=vbt.Param(range(2, 100)),
...     ),
...     build_index=False
... )
>>> backtest(
...     vbt.YFData.pull(["BTC-USD", "ETH-USD"]),  # (5)!
...     vbt.Chunked(param_product["fast_window"]),  # (6)!
...     vbt.Chunked(param_product["slow_window"])
... )
```

Example 4 (pycon):
```pycon
fast_window  slow_window  symbol 
2            3            BTC-USD    193.124482
                          ETH-USD     12.247315
             4            BTC-USD    159.600953
                          ETH-USD     15.825041
             5            BTC-USD    124.703676
                                        ...    
97           98           ETH-USD      3.947346
             99           BTC-USD     25.551881
                          ETH-USD      3.442949
98           99           BTC-USD     27.943574
                          ETH-USD      3.540720
Name: total_return, Length: 9506, dtype: float64
```

---

## Analysis

**URL:** https://vectorbt.pro/pvt_ff8edc14/features/analysis.md

**Contents:**
- Simulation ranges
- Expanding trade metrics
- Trade signals
- Edge ratio
- Trade history
- Patterns
- Projections
- MAE and MFE
- OHLC-native classes
- Benchmark

![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/new-in/v2024*5_15.svg){ loading=lazy }

data. You can set a different simulation range beforehand, and now, you can also adjust this range during the simulation. This flexibility lets you stop the simulation when further processing is unnecessary. Additionally, the date range is saved in the portfolio object, so all metrics and subplots recognize it. Processing only the relevant dates speeds up execution and adds a new dimension to your analysis: isolated time windows :microscope:

=== "Example 1: Liquidation"

=== "Example 2: Date range analysis"

![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/new-in/1*11_0.svg){ loading=lazy }

to see how these metrics develop during the trade? You can now analyze expanding trade metrics as DataFrames!

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/expanding*mfe*returns.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/expanding*mfe*returns.dark.svg#only-dark){: .iimg loading=lazy }

![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/new-in/1*8_2.svg){ loading=lazy }

short entries, and short exits. It supports different styles for positions.

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/trade*signals.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/trade*signals.dark.svg#only-dark){: .iimg loading=lazy }

![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/new-in/1*8_1.svg){ loading=lazy }

profitability. Unlike most performance metrics, the edge ratio accounts for both open profits and losses. This can help you find better trade exits.

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/running*edge*ratio.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/running*edge*ratio.dark.svg#only-dark){: .iimg loading=lazy }

![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/new-in/1*8_1.svg){ loading=lazy }

entry trades, exit trades, and positions.

![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/new-in/1*5_0.svg){ loading=lazy }

technical analysis. There are now new dedicated functions and classes for detecting patterns of any complexity in any type of time series data. The idea is simple: fit a pattern to align with the scale and period of your selected data window, then compute the element-wise distance between them to get a single similarity score. You can adjust the threshold for this score to decide above which value a data window should be marked as "matched." Thanks to Numba, this operation can be performed hundreds of thousands of times per second! :mag_right:

!!! example "Tutorial" Learn more in the [Patterns and projections](https://vectorbt.pro/pvt_ff8edc14/tutorials/patterns-and-projections) tutorial.

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/patterns.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/patterns.dark.svg#only-dark){: .iimg loading=lazy }

![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/new-in/1*5_0.svg){ loading=lazy }

Meet projections! :wave: Not only can they help you assess event performance visually and quantitatively, but they can also project events into the future to support trading. This is done by extracting the price range after each event, collecting all these price ranges into a multidimensional array, and then deriving confidence intervals and other useful statistics from that array. When combined with patterns, these tools are a quantitative analyst's dream! :stars:

!!! example "Tutorial" Learn more in the [Patterns and projections](https://vectorbt.pro/pvt_ff8edc14/tutorials/patterns-and-projections) tutorial.

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/projections.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/projections.dark.svg#only-dark){: .iimg loading=lazy }

![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/new-in/1*3_0.svg){ loading=lazy }

helps you see the maximum loss taken during a trade, also known as the maximum drawdown of the position. [Maximum Favorable Excursion (MFE)](https://analyzingalpha.com/maximum-favorable-excursion) shows the highest profit reached during a trade. Analyzing MAE and MFE statistics can help you improve your exit strategies.

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/mae*without*sl.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/mae*without*sl.dark.svg#only-dark){: .iimg loading=lazy }

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/mae*with*sl.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/mae*with*sl.dark.svg#only-dark){: .iimg loading=lazy }

![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/new-in/1*3_0.svg){ loading=lazy }

Now, most classes let you track all OHLC data for more accurate quantitative and qualitative analysis.

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/ohlc*native*classes.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/ohlc*native*classes.dark.svg#only-dark){: .iimg loading=lazy }

![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/new-in/1*0_4.svg){ loading=lazy }

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/benchmark.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/benchmark.dark.svg#only-dark){: .iimg loading=lazy }

[:material-language-python: Python code](https://vectorbt.pro/pvt*ff8edc14/assets/jupytext/features/analysis.py.txt){ .md-button target="blank*" }

**Examples:**

Example 1 (text):
```text
    >>> @njit
    ... def post_segment_func_nb(c):
    ...     value = vbt.pf_nb.get_group_value_nb(c, c.group)
    ...     if value <= 0:
    ...         vbt.pf_nb.stop_group_sim_nb(c, c.group)  # (1)!

    >>> pf = vbt.PF.from_random_signals(
    ...     "BTC-USD", 
    ...     n=10, 
    ...     seed=42,
    ...     sim_start="auto",  # (2)!
    ...     post_segment_func_nb=post_segment_func_nb,
    ...     leverage=10,
    ... )
    >>> pf.plot_value()  # (3)!
```

Example 2 (text):
```text
1. Stop the simulation of the current group if its value turns negative.
2. Start the simulation at the first signal.
3. Make sure all metrics and subplots use only data up to the liquidation point, even if the portfolio
contains the full original data set (2014 → today).

![](https://vectorbt.pro/pvt_ff8edc14/assets/images/features/liquidation.light.svg#only-light){: .iimg loading=lazy }
![](https://vectorbt.pro/pvt_ff8edc14/assets/images/features/liquidation.dark.svg#only-dark){: .iimg loading=lazy }
```

Example 3 (text):
```text
    >>> pf = vbt.PF.from_random_signals("BTC-USD", n=10, seed=42)

    >>> pf.get_sharpe_ratio(sim_start="2023", sim_end="2024")  # (1)!
    1.7846214408154346

    >>> pf.get_sharpe_ratio(sim_start="2023", sim_end="2024", rec_sim_range=True)  # (2)!
    1.8377982089422782

    >>> pf.returns_stats(settings=dict(sim_start="2023", sim_end="2024"))  # (3)!
    Start Index                  2023-01-01 00:00:00+00:00
    End Index                    2023-12-31 00:00:00+00:00
    Total Duration                       365 days 00:00:00
    Total Return [%]                             84.715081
    Benchmark Return [%]                        155.417419
    Annualized Return [%]                        84.715081
    Annualized Volatility [%]                     38.49976
    Max Drawdown [%]                             20.057773
    Max Drawdown Duration                102 days 00:00:00
    Sharpe Ratio                                  1.784621
    Calmar Ratio                                  4.223554
    Omega Ratio                                   1.378076
    Sortino Ratio                                 3.059933
    Skew                                          -0.39136
    Kurtosis                                     13.607937
    Tail Ratio                                    1.323376
    Common Sense Ratio                            1.823713
    Value at Risk                                -0.028314
    Alpha                                        -0.103145
    Beta                                          0.770428
    dtype: object
```

Example 4 (text):
```text
1. Consider only the returns within the specified date range when calculating the Sharpe ratio.
Note that returns may still be affected by data outside the date range (such as open positions).
2. Recursively apply the date range to all metrics that the Sharpe ratio depends on, such as equity,
cash, and orders, treating data outside the range as if it does not exist.
3. Make sure the date range is used consistently for all statistics.
```

---
