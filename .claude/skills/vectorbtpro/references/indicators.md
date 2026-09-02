# Vectorbtpro_Docs - Indicators

**Pages:** 8

---

## Indicators

**URL:** https://vectorbt.pro/pvt_ff8edc14/documentation/indicators.md

**Contents:**
- Pipeline
- Factory
  - Workflow
- Factory methods
  - From custom function
  - From apply function
    - Custom iteration
    - Execution
    - Numba
    - Debugging

The [IndicatorFactory](https://vectorbt.pro/pvt_ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory) class is one of the most powerful components in the VBT ecosystem. It can wrap any indicator function, making it both parameterizable and analyzable.

An indicator is a pipeline that performs the following steps:

producing the same shape (for example, a rolling average).

Let's manually create an indicator that takes two time series, computes their normalized moving averages, and returns the difference between the two. We will test different shapes as well as parameter combinations to see how broadcasting can be leveraged:

combinations: `(2, 3)` and `(2, 4)`.

Pretty neat! We just built a flexible pipeline that can handle arbitrary input and parameter combinations. The resulting DataFrame shows each column as a specific window combination applied to each column in both `ts1` and `ts2`. But is this pipeline user-friendly? :thinking: Dealing with broadcasting, output concatenation, and column hierarchies makes this process very similar to working with regular Pandas code.

The pipeline above can be easily standardized using [IndicatorBase.run*pipeline](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorBase.run*pipeline). This method conveniently prepares inputs, parameters, and columns. However, you still need to perform the calculation and output concatenation yourself by providing a `custom*func`. Let's update the example:

With much less code, we performed the entire calculation using only NumPy and Numba—a big win! But what is this complex output?

This raw output is designed for internal use by VBT and is not intended for direct use. It contains metadata necessary for working with the indicator. Additionally, if you review the source of this function, you will see that it accepts many different arguments. This complexity provides great flexibility, as each argument corresponds to a specific step in the pipeline. But do not worry: we will not use this function directly.

Instead, we will use [IndicatorFactory](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory), which simplifies [IndicatorBase.run*pipeline](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorBase.run*pipeline) by providing a unified interface and various automations. Let's use the factory to wrap our `custom_func`:

!!! tip `vbt.IF` is a shortcut for [IndicatorFactory](https://vectorbt.pro/pvt_ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory).

As you can see, [IndicatorFactory](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory) takes the specification for our indicator and creates a Python class that knows how to communicate with [IndicatorBase.run*pipeline](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorBase.run*pipeline) and manage and format its results. Specifically, it attaches the class method `MADiff.run`, which works just like `custom*func` but prepares and forwards all arguments to [IndicatorBase.run*pipeline](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorBase.run*pipeline) under the hood. Whenever we call the `run` method, it initializes and returns an instance of `MADiff` containing all the input and output data.

You may wonder: *"Why does the factory create a class instead of a function? Wouldn't an indicator function be more intuitive?"* If you have read [Building blocks](https://vectorbt.pro/pvt*ff8edc14/documentation/building-blocks), you may already be familiar with the class [Analyzable](https://vectorbt.pro/pvt*ff8edc14/api/generic/analyzable/#vectorbtpro.generic.analyzable.Analyzable), the main class for analyzing data. The indicator class created by the factory is a subclass of [Analyzable](https://vectorbt.pro/pvt*ff8edc14/api/generic/analyzable/#vectorbtpro.generic.analyzable.Analyzable), so you not only get access to the output, but also to many methods for analyzing this output. For example, the factory automatically provides `crossed*above`, `cross_below`, `stats`, and many other methods for each input and output in the indicator:

The main goal of [IndicatorFactory](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory) is to create a stand-alone indicator class that includes a `run` method for executing the indicator. To accomplish this, it needs to know what inputs, parameters, and outputs to expect. You can provide this information using `input*names`, `param_names`, and other arguments in the constructor:

When initialized, it builds the skeleton of our indicator class, which is a type of [IndicatorBase](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorBase). This is accessible via [IndicatorFactory.Indicator](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.Indicator). Even though the factory creates the constructor for this class and attaches various properties and methods, we cannot run the indicator yet:

This is because we still need to provide the calculation function. There are several methods starting with the prefix `with*`. The fundamental method, used by all others, is [IndicatorFactory.with*custom*func](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.with*custom*func) (which we used earlier). It overrides the abstract `run` method to execute the indicator using [IndicatorBase.run*pipeline](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorBase.run_pipeline) and returns a fully functional indicator class:

The calculation function has now been successfully attached, so we can run this indicator!

Factory methods come in two forms: instance and class methods. Instance methods, with the prefix `with*`, such as [IndicatorFactory.with*custom*func](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.with*custom*func), require instantiating the indicator factory. This means you need to call `vbt.IF(...)` and manually provide the required information as we did with `MADiff`. Class methods, with the prefix `from*`, such as [IndicatorFactory.from*expr](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.from*expr), can (semi-)automatically parse the required information.

The method [IndicatorFactory.with*custom*func](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.with*custom*func) accepts a "custom function", which is the most flexible way to define an indicator. However, with this flexibility comes added responsibility: as the user, you must handle iterating through parameters, manage caching, and concatenate columns for each parameter combination (usually using [apply*and*concat](https://vectorbt.pro/pvt*ff8edc14/api/base/combining/#vectorbtpro.base.combining.apply*and*concat)). You must also ensure that each output array has the correct number of columns, equal to the number of columns in the input arrays multiplied by the number of parameter combinations. In addition, your custom function receives commands passed by the pipeline, so it is up to you to properly process those commands.

For example, if your custom function needs the index and columns alongside the NumPy arrays, you can instruct the pipeline to pass the wrapper by setting `pass*wrapper=True` in `with*custom*func`. This and all other arguments are forwarded directly to [IndicatorBase.run*pipeline](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorBase.run*pipeline), which handles communication with your custom function.

The method [IndicatorFactory.with*apply*func](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.with*apply*func) greatly simplifies indicator development. It creates a `custom*func` that handles caching, iteration over parameters with [apply*and*concat](https://vectorbt.pro/pvt*ff8edc14/api/base/combining/#vectorbtpro.base.combining.apply*and*concat), output concatenation with [column*stack](https://vectorbt.pro/pvt*ff8edc14/api/base/reshaping/#vectorbtpro.base.reshaping.column*stack), and then passes this function to [IndicatorFactory.with*custom*func](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.with*custom_func). Your only task is to write an "apply function," which accepts a single parameter combination and performs the calculation. The resulting outputs are automatically concatenated along the column axis.

!!! note An apply function has mostly the same signature as a custom function, but the parameters are individual values instead of multiple values.

Let's create our indicator using an apply function:

That's all you need! Under the hood, the code creates a custom function that iterates over all parameter combinations and calls `apply_func` on each one. If you print `ts1`, `ts2`, `w1`, and `w2`, you would see that `ts1` and `ts2` remain the same, while `w1` and `w2` are now individual values. This design allows you to simplify your code, working with one set of parameters at a time without worrying about multiple parameter combinations.

Another advantage of this method is that apply functions are a natural fit in VBT :monkey:, so you can use most regular and Numba-compiled functions that take two-dimensional NumPy arrays directly as apply functions. For example, let's build an indicator for rolling covariance:

In this example, both input arrays and the window parameter are passed directly to [rolling*cov*nb](https://vectorbt.pro/pvt*ff8edc14/api/generic/nb/rolling/#vectorbtpro.generic.nb.rolling.rolling*cov_nb).

We can easily emulate `apply*func` using `custom*func` and [apply*and*concat](https://vectorbt.pro/pvt*ff8edc14/api/base/combining/#vectorbtpro.base.combining.apply*and_concat). For example, if we need the index of the current iteration or want access to all parameter combinations:

[apply*and*concat](https://vectorbt.pro/pvt*ff8edc14/api/base/combining/#vectorbtpro.base.combining.apply*and_concat) must take the index of the iteration and select the parameters manually using this index.

requires the number of iterations, which is simply the length of any parameter array.

The same result can be achieved using [IndicatorFactory.with*apply*func](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.with*apply*func) and `select*params=False`:

Since the same apply function is called multiple times—once per parameter combination—we can use one of VBT's preset execution engines to distribute these calls sequentially (default), across multiple threads, or across multiple processes. In fact, the function [apply*and*concat](https://vectorbt.pro/pvt*ff8edc14/api/base/combining/#vectorbtpro.base.combining.apply*and*concat), which is used to iterate over all parameter combinations, handles this automatically by forwarding all calls to the executor function [execute](https://vectorbt.pro/pvt*ff8edc14/api/utils/execution/#vectorbtpro.utils.execution.execute). By passing keyword arguments in `execute_kwargs`, we can define how to distribute these calls. For example, to disable the progress bar:

[=100% "Iteration 100/100"]{: .candystripe .candystripe-animate }

When the apply function is Numba-compiled, the indicator factory also makes the parameter selection function Numba-compiled (with the GIL released), allowing for multithreading. This behavior can be disabled by setting `jit*select*params` to False. The keyword arguments used to configure the Numba-compiled function can be supplied via the `jit_kwargs` argument.

!!! note Setting `jit*select*params` will remove all keyword arguments since variable keyword arguments are not supported by Numba (yet). To pass keyword arguments to the apply function anyway, set `remove*kwargs` to False or use the `kwargs*as_args` argument, which specifies which keyword arguments should be supplied as (variable) positional arguments.

Additionally, you can explicitly set `jitted_loop` to True to loop over each parameter combination in a Numba loop. This can speed up iteration for shallow inputs with a large number of columns, but may slow it down otherwise.

!!! note In this case, the execution will be performed by Numba, so you cannot use `execute_kwargs` anymore.

Sometimes it is not clear which arguments are being passed to `apply_func`. Debugging in this case is usually simple: just replace your apply function with a generic function that accepts variable arguments and prints them.

Parsers offer the most convenient way to build indicator classes. For example, there are dedicated parser methods for third-party technical analysis packages that can automatically or semi-automatically derive the specification of each indicator. Additionally, a powerful expression parser can help you avoid writing complex Python functions for simple indicators. Let's *express* our indicator as an expression:

Notice that we did not need to call `vbt.IF(...)`? [IndicatorFactory.from*expr](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.from*expr) is a class method that parses `input*names` and other information directly from the expression and creates a factory instance using only this information. It is amazing how we reduced our first implementation with `mov*avg*crossover` to just this while still enjoying all the features, right?

Once you have built your indicator class, it is time to run it. The primary method for executing an indicator is the class method [IndicatorBase.run](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorBase.run). This method accepts positional and keyword arguments based on the specifications provided to the [IndicatorFactory](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory). These arguments include input arrays, in-place output arrays, and parameters. Any additional arguments are forwarded down to [IndicatorBase.run*pipeline](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorBase.run_pipeline), which may use them to set up the pipeline or forward them further down to the custom function and, if provided, the apply function.

To see which arguments the `run` method accepts, use [phelp](https://vectorbt.pro/pvt_ff8edc14/api/utils/formatting/#vectorbtpro.utils.formatting.phelp):

We can see that `MADiff.run` takes two input time series, `ts1` and `ts2`, two parameters, `w1` and `w2`, and produces a single output time series, `diff`. When you call the class method, it runs the indicator and returns a new instance of `MADiff` with all data ready for analysis. Specifically, you can access the output as a regular instance attribute, `MADiff.diff`.

The second method for running indicators is [IndicatorBase.run*combs](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorBase.run*combs). This method accepts the same inputs as the method above, but computes all combinations of the given parameters using a combinatorial function and returns **multiple** indicator instances that can be combined with each other. This is useful for comparing multiple indicators of the **same type** but with different parameters, such as when testing a moving average crossover, which involves two [MA](https://vectorbt.pro/pvt*ff8edc14/api/indicators/custom/ma/#vectorbtpro.indicators.custom.ma.MA) instances applied to the same time series:

In the example above, [MA.run*combs](https://vectorbt.pro/pvt*ff8edc14/api/indicators/custom/ma/#vectorbtpro.indicators.custom.MA.ma.run_combs) generated the combinations of `window` using [itertools.combinations](https://docs.python.org/3/library/itertools.html#itertools.combinations) with `r=2`. The first set of window combinations was passed to the first instance, and the second set to the second instance. The same example can be replicated using only the `run` method:

The main advantage of a single `run_combs` call over multiple `run` calls is that it does not need to re-compute each combination, thanks to smart caching.

!!! note `run_combs` should only be used for combining multiple indicators. To test multiple parameter combinations, use `run` and provide parameters as lists.

VBT provides a collection of preset, fully Numba-compiled indicators (such as [ATR](https://vectorbt.pro/pvt_ff8edc14/api/indicators/custom/atr/#vectorbtpro.indicators.custom.atr.ATR)) that benefit from manual caching, extension, and plotting. You can use them as inspiration for how to create indicators in a classic yet efficient way.

!!! note VBT uses SMA and EMA, while other technical analysis libraries and TradingView use Wilder's method. There is no right or wrong method. See [different smoothing methods](https://www.macroption.com/atr-calculation/).

[:material-language-python: Python code](https://vectorbt.pro/pvt*ff8edc14/assets/jupytext/documentation/indicators/index.py.txt){ .md-button target="blank*" }

**Examples:**

Example 1 (pycon):
```pycon
>>> from vectorbtpro import *

>>> def mov_avg_crossover(ts1, ts2, w1, w2):
...     ts1, ts2 = vbt.broadcast(ts1, ts2)  # (1)!
...
...     w1, w2 = vbt.broadcast(  # (2)!
...         vbt.to_1d_array(w1), 
...         vbt.to_1d_array(w2))
...
...     ts1_mas = []
...     for w in w1:
...         ts1_mas.append(ts1.vbt.rolling_mean(w) / ts1)  # (3)!
...     ts2_mas = []
...     for w in w2:
...         ts2_mas.append(ts2.vbt.rolling_mean(w) / ts2)
...
...     ts1_ma = pd.concat(ts1_mas, axis=1)  # (4)!
...     ts2_ma = pd.concat(ts2_mas, axis=1)
...
...     ts1_ma.columns = vbt.combine_indexes((  # (5)!
...         pd.Index(w1, name="ts1_window"), 
...         ts1.columns))
...     ts2_ma.columns = vbt.combine_indexes((
...         pd.Index(w2, name="ts2_window"), 
...         ts2.columns))
...
...     return ts1_ma.vbt - ts2_ma  # (6)!

>>> def generate_index(n):  # (7)!
...     return vbt.date_range("2020-01-01", periods=n)

>>> ts1 = pd.Series([1, 2, 3, 4, 5, 6, 7], index=generate_index(7))
>>> ts2 = pd.DataFrame({
...     'a': [5, 4, 3, 2, 3, 4, 5],
...     'b': [2, 3, 4, 5, 4, 3, 2]
... }, index=generate_index(7))
>>> w1 = 2
>>> w2 = [3, 4]

>>> mov_avg_crossover(ts1, ts2, w1, w2)
ts1_window                                       2
ts2_window                   3                   4
                   a         b         a         b
2020-01-01       NaN       NaN       NaN       NaN
2020-01-02       NaN       NaN       NaN       NaN
2020-01-03 -0.500000  0.083333       NaN       NaN
2020-01-04 -0.625000  0.075000 -0.875000  0.175000
2020-01-05  0.011111 -0.183333 -0.100000 -0.100000
2020-01-06  0.166667 -0.416667  0.166667 -0.416667
2020-01-07  0.128571 -0.571429  0.228571 -0.821429
```

Example 2 (pycon):
```pycon
>>> def custom_func(ts1, ts2, w1, w2):
...     ts1_mas = []
...     for w in w1:
...         ts1_mas.append(vbt.nb.rolling_mean_nb(ts1, w) / ts1)  # (1)!
...     ts2_mas = []
...     for w in w2:
...         ts2_mas.append(vbt.nb.rolling_mean_nb(ts2, w) / ts2)
...
...     ts1_ma = np.column_stack(ts1_mas)  # (2)!
...     ts2_ma = np.column_stack(ts2_mas)
...
...     return ts1_ma - ts2_ma  # (3)!

>>> outputs = vbt.IndicatorBase.run_pipeline(
...     num_ret_outputs=1,
...     custom_func=custom_func,
...     inputs=dict(ts1=ts1, ts2=ts2),
...     params=dict(w1=w1, w2=w2)
... )
>>> outputs
(<vectorbtpro.base.wrapping.ArrayWrapper at 0x7fb188993160>,
 [array([[1, 1],
         [2, 2],
         [3, 3],
         [4, 4],
         [5, 5],
         [6, 6],
         [7, 7]]),
  array([[5, 2],
         [4, 3],
         [3, 4],
         [2, 5],
         [3, 4],
         [4, 3],
         [5, 2]])],
 array([0, 1, 0, 1]),
 [],
 [array([[        nan,         nan,         nan,         nan],
         [        nan,         nan,         nan,         nan],
         [-0.5       ,  0.08333333,         nan,         nan],
         [-0.625     ,  0.075     , -0.875     ,  0.175     ],
         [ 0.01111111, -0.18333333, -0.1       , -0.1       ],
         [ 0.16666667, -0.41666667,  0.16666667, -0.41666667],
         [ 0.12857143, -0.57142857,  0.22857143, -0.82142857]])],
 [[2, 2], [3, 4]],
 [Int64Index([2, 2, 2, 2], dtype='int64'),
  Int64Index([3, 3, 4, 4], dtype='int64')],
 [])
```

Example 3 (pycon):
```pycon
>>> MADiff = vbt.IF(
...     class_name='MADiff',
...     input_names=['ts1', 'ts2'],
...     param_names=['w1', 'w2'],
...     output_names=['diff'],
... ).with_custom_func(custom_func)

>>> madiff = MADiff.run(ts1, ts2, w1, w2)
>>> madiff.diff
madiff_w1                                        2
madiff_w2                    3                   4
                   a         b         a         b
2020-01-01       NaN       NaN       NaN       NaN
2020-01-02       NaN       NaN       NaN       NaN
2020-01-03 -0.500000  0.083333       NaN       NaN
2020-01-04 -0.625000  0.075000 -0.875000  0.175000
2020-01-05  0.011111 -0.183333 -0.100000 -0.100000
2020-01-06  0.166667 -0.416667  0.166667 -0.416667
2020-01-07  0.128571 -0.571429  0.228571 -0.821429
```

Example 4 (pycon):
```pycon
>>> madiff.diff_stats(column=(2, 3, 'a'))
Start        2020-01-01 00:00:00
End          2020-01-07 00:00:00
Period           7 days 00:00:00
Count                          5
Mean                    -0.16373
Std                     0.371153
Min                       -0.625
Median                  0.011111
Max                     0.166667
Min Index    2020-01-04 00:00:00
Max Index    2020-01-06 00:00:00
Name: (2, 3, a), dtype: object
```

---

## Development

**URL:** https://vectorbt.pro/pvt_ff8edc14/documentation/indicators/development.md

**Contents:**
- Parameters
  - Defaults
  - Array-like
  - Lazy broadcasting
    - With Numba
  - Parameterless
- Inputs
  - One dim
  - Defaults
  - Using Pandas

VBT offers a wide range of functions and arguments to simplify indicator development. All you need is an indicator function and a way to specify how it should be handled.

[IndicatorFactory](https://vectorbt.pro/pvt_ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory) allows you to define any parameter grids you need. An indicator can have one or more parameters. Each parameter can accept one or more values, which can be scalars (such as integers), arrays, or any other objects.

If an indicator has multiple parameters, and one or more of them have several values, their values will broadcast together. For example, if the parameter `w1` has only a single value `2` and the parameter `w2` has two values `3` and `4`, then `w1` will be stretched to two values: `2` and `2`. This allows the indicator to [zip](https://realpython.com/python-zip-function/) both parameters and create two parameter combinations: `(2, 3)` and `(2, 4)`. The indicator will then iterate through these combinations and apply a function to each one. The example below illustrates broadcasting:

!!! note Do not confuse broadcasting with a product operation. The product of `[2, 3]` and `[4, 5]` would result in 4 combinations: `[2, 4]`, `[2, 5]`, `[3, 4]`, and `[3, 5]`. In broadcasting, smaller arrays are simply stretched to match the length of larger arrays for zipping.

To illustrate how parameters are used in indicators, here is a simple example. This indicator returns 1 when the rolling mean is above an upper bound, -1 when it is below a lower bound, and 0 when it is between the upper and lower bounds:

To retrieve the list of parameter names:

The broadcasted values of each parameter are accessible as attributes of the indicator instance, using the parameter name followed by `_list`:

By default, when `per_column` is set to False, each parameter combination is applied to every column in the input. For example, if your input array has 20 columns and you want to test 5 parameter combinations, you will get `20 * 5 = 100` columns in total.

A single parameter combination:

Multiple parameter combinations:

Product of parameter combinations:

You can build more complex parameter combinations using the [generate*param*combs](https://vectorbt.pro/pvt*ff8edc14/api/utils/params/#vectorbtpro.utils.params.generate*param_combs) function. For example, if the lower bound should always remain below the upper bound, you can control this relationship using [itertools.combinations](https://docs.python.org/3/library/itertools.html#itertools.combinations). After that, you can create a Cartesian product with the window using [itertools.product](https://docs.python.org/3/library/itertools.html#itertools.product).

One parameter combination per column:

Any argument passed to [IndicatorFactory.with*custom*func](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.with*custom*func) that is not listed among the arguments of [IndicatorBase.run*pipeline](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorBase.run*pipeline) is intended to be used as a default argument for the calculation function. Since most methods, including [IndicatorFactory.with*apply*func](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.with*apply_func), call this method, you can easily set parameter defaults by passing them along with the function:

The reason why the parameters `window` and `lower` do not appear in the column hierarchy above is that default values are hidden by default. To display them, set `hide_default` to False:

Some parameters are intended to be specified per row, column, or element of the input. By default, if you pass a parameter value as an array, the indicator will treat this array as a list of multiple values, one per input. To make the indicator interpret this array as a single value, set the flag `is*array*like` to True in `param*settings`. To automatically broadcast the parameter value to the input shape, set `bc*to_input` to True, 0 (index axis), or 1 (column axis).

In our example, the parameter `window` can be broadcast per column, and both parameters `lower` and `upper` can be broadcast per element. To enable this, we need to rewrite `apply_func` to apply the rolling mean on each column instead of the entire input:

Both bound parameters can now be passed as a scalar (one value for the entire input), a one-dimensional array (one value per row or column, depending on whether the input is a Series or a DataFrame), a two-dimensional array (one value per element), or a list containing any of these. This approach allows for maximum parameter flexibility.

For example, let's build a grid of two parameter combinations:

Our `apply_func` gets called twice, once for each parameter combination in `window`. If you print the shapes of the passed arguments, you will see that each window array now matches the number of columns in `ts`, while each bound array exactly matches the shape of `ts`:

Broadcasting a large number of parameters to the input shape can use a lot of memory, especially when the arrays are materialized. Fortunately, VBT can preserve the original (smaller) dimensions of each parameter array and give you full control over broadcasting. This requires setting `keep*flex` to True in `broadcast*kwargs`, which will make the factory first check whether the array can be broadcast, and then expand it to either one or two dimensions in the most memory-efficient way. There are two configs in [configs](https://vectorbt.pro/pvt_ff8edc14/api/indicators/configs) for this purpose: one for column-wise broadcasting and one for element-wise broadcasting.

Well done! This is the most flexible and memory-efficient way to implement an indicator. Instead of broadcasting all array-like parameter values immediately, we delay this operation until it is actually needed.

The implementation above is very flexible, but it is not the most optimized because it iterates over the input shape multiple times. As a bonus, let's rewrite our `apply*func` to be Numba-compiled: this version will iterate over columns and rows, select each parameter value [flexibly](https://vectorbt.pro/pvt*ff8edc14/documentation/fundamentals/#flexible-indexing) without any broadcasting, and fill the output array step by step.

!!! tip This is perfectly valid Python code. Even if you remove the `@njit` decorator, it will still work!

Remember that executing code compiled with Numba can provide performance increases many times greater than standard Python and even Pandas :snail:

Indicators can also be parameterless, such as [OBV](https://vectorbt.pro/pvt_ff8edc14/api/indicators/custom/obv/#vectorbtpro.indicators.custom.obv.OBV).

[IndicatorFactory](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory) allows you to pass none, one, or multiple inputs. If multiple inputs are provided, it will try to broadcast them into a single shape using [broadcast](https://vectorbt.pro/pvt*ff8edc14/api/base/reshaping/#vectorbtpro.base.reshaping.broadcast) (see [Broadcasting](https://vectorbt.pro/pvt_ff8edc14/documentation/fundamentals/#broadcasting)).

Remember, in VBT each column represents a separate backtest. So, to work with multiple pieces of data such as OHLCV, you should provide them as separate Pandas objects, not as a single monolithic DataFrame (see [Multidimensionality](https://vectorbt.pro/pvt_ff8edc14/documentation/fundamentals/#multidimensionality)).

Let's create a parameterless indicator that calculates the position of the closing price relative to the candle:

To see the list of input names:

You can access any (broadcasted and tiled) input array as an attribute of the indicator instance:

!!! note The input array attached to the indicator instance may look different from what you passed in: 1) it has been broadcasted with the other inputs, and 2) when you access the attribute, it is automatically tiled by the number of parameter combinations to make it easier to compare with outputs. To access the original array, prepend an underscore (`_high`).

To demonstrate broadcasting, let's pass `high` as a scalar, `low` as a Series, and `close` as a DataFrame (even if this combination does not make sense):

!!! tip By default, if all inputs are Series, they are automatically converted into two-dimensional NumPy arrays. This provides a unified array interface, as most VBT functions mainly work with two-dimensional data. To keep their original dimensions, set `to*2d` to False in [IndicatorFactory.with*apply*func](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.with*apply*func) or any other factory method.

To change broadcasting rules, you can pass a dict called `broadcast*kwargs`, which is unpacked and forwarded to [broadcast](https://vectorbt.pro/pvt*ff8edc14/api/base/reshaping/#vectorbtpro.base.reshaping.broadcast). For example, let's tell the broadcaster to cast all three arrays to `np.float16`:

!!! tip Remember that any additional keyword arguments passed to a `run` method are forwarded to [IndicatorBase.run*pipeline](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorBase.run_pipeline). This allows you to set up the pipeline during both indicator creation and execution.

Since all arrays are passed directly to [broadcast](https://vectorbt.pro/pvt*ff8edc14/api/base/reshaping/#vectorbtpro.base.reshaping.broadcast), you can also wrap any of them using the [BCO](https://vectorbt.pro/pvt*ff8edc14/api/base/reshaping/#vectorbtpro.base.reshaping.BCO) class to override broadcasting rules for that particular array only:

Sometimes, adapting your indicator function to work with two-dimensional data is not straightforward. For example, when using a TA-Lib indicator in `apply*func`, you may need to pass only one column at a time. To instruct [IndicatorFactory.with*apply*func](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.with*apply*func) to split any input and in-place output (Pandas or NumPy) array by column, use the `takes_1d` argument:

!!! note Do not confuse this with `per_column`, which also splits by column but applies one parameter combination to one column instead of all columns.

Just like with parameters, you can define defaults for your inputs:

However, unlike parameters, setting inputs to scalars is often not ideal. Instead, you may want to set them to other inputs, which is possible using [Ref](https://vectorbt.pro/pvt_ff8edc14/api/base/reshaping/#vectorbtpro.base.reshaping.Ref):

Working only with NumPy arrays is not always the best choice: sometimes you want to take advantage of Pandas metadata or VBT's Pandas extensions. To prevent conversion of Pandas objects to NumPy arrays, you can set `keep_pd` to True.

For example, let's create an indicator that takes a DataFrame and normalizes it against the mean of each group of columns. The interesting part is that the `group_by` for grouping columns will be a parameter!

Alternatively, you can have [IndicatorBase.run*pipeline](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorBase.run*pipeline) pass inputs as NumPy arrays, along with a [wrapper](https://vectorbt.pro/pvt*ff8edc14/documentation/building-blocks/#wrapping) that includes the Pandas metadata:

functions provided by VBT.

What if an indicator does not take any input arrays? For example, you may want to create an indicator that takes an input shape, creates one or more output arrays of that shape, and fills them using information provided as additional arguments. To do this, you can require the user to provide an input shape using `require*input*shape`.

Let's define a generator that emulates random returns and generates a synthetic price. This is a parameterized way of implementing [RandomData](https://vectorbt.pro/pvt_ff8edc14/api/data/custom/random/#vectorbtpro.data.custom.random.RandomData):

supports random seeds.

!!! info When `require*input*shape` is True, [IndicatorFactory](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory) prepends an `input*shape` argument to the `run` method's signature. Without this argument, the `apply_func` itself must determine the input shape.

However, having integer columns and index is not very convenient. Fortunately, VBT allows you to pass `input*index` and `input*columns`!

You can even build an indicator that decides on the output shape dynamically. Let's create a fun indicator that returns an array with a random shape:

no iteration takes place.

[IndicatorFactory](https://vectorbt.pro/pvt_ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory) supports returning one or more outputs. There are two types of outputs: regular outputs and in-place outputs (also called "in-place outputs").

Regular outputs are arrays explicitly returned by the calculation function. Each output must have the same shape and match the number of columns in the input, multiplied by the number of parameter combinations. This requirement only needs special attention when using `custom*func`, as `apply*func` handles the tiling automatically. If there is only one output, an array must be returned. If there are multiple outputs, a tuple containing multiple arrays must be returned.

Let's demonstrate multiple regular outputs by computing and returning the entries and exits from a moving average crossover:

!!! important Any output registered in `output_names` must have the same shape as the broadcasted inputs. This requirement makes it possible to index the indicator instance.

To get the list of output names:

Any (broadcasted and tiled) output array can be accessed as an attribute of the indicator instance:

In-place outputs are arrays that are not returned but modified in place. They act as regular inputs when entering the pipeline and as regular outputs when exiting. In particular:

By default, in-place outputs are created as empty arrays with uninitialized floating point values. This allows for the creation of optional outputs that, if not written to, do not consume much memory. Since not all outputs should have the `float` data type, you can pass `dtype` in the `in*output*settings`.

Let's modify the indicator above by converting both signal arrays to in-place outputs:

to initialize both signal arrays with the boolean data type.

If you print the `output_names`, you will see that `entries` and `exits` are no longer included:

To see all in-place output arrays, use the `in*output*names` attribute:

Both signal arrays can be accessed as usual:

!!! tip An interesting scenario occurs when there are no regular outputs, only in-place outputs. In this case, you should set `output_names` to an empty list, modify all arrays in place, and return `None`. See the example below.

You might be wondering: *"Why should we bother using in-place outputs when we can just return regular outputs?"* The answer is that we can provide custom data and overwrite it without using additional memory. Consider the following example, where we keep the first `n` signals in a boolean time series:

As you can see, one array fulfills the job of two, and this is done without modifying the passed `signals` array!

!!! note Unlike regular inputs, none of the in-place outputs is required when running an indicator, so they appear in the signature of the `run` method as keyword arguments with `None` as the default value. Be sure to pass each in-place output as a keyword argument after other positional arguments (such as inputs and parameters).

Any additional output returned by `custom*func` that is not registered in `output*names` is returned in a raw format along with the indicator instance. Such outputs can be objects of any type, especially arrays whose shapes differ from those of the inputs. They are not included in the indicator instance because the indicator factory does not know how to wrap, index, and analyze them; only the user does. For example, let's return the rolling mean along with its maximum in each column:

Use the `lazy_outputs` argument when constructing an indicator to define lazy outputs— outputs that are computed from "normal" outputs and are only calculated when explicitly requested. They are available as regular cacheable properties of the indicator instance and can be of any type. Continuing with the previous example, let's add a cached property that returns the maximum of the rolling mean:

!!! tip You can achieve the same result by subclassing `MAMax` and defining the property in the subclass.

Sometimes, you may need to pass arguments that are not inputs, in-place outputs, or parameters.

If you review the `apply*func` of `CrossSig`, you will notice it takes another optional argument, `minp`, which controls the minimum number of observations in a window required to have a value. Listing a keyword argument with its default in `custom*func` or `apply*func` is one way to provide a default value. Another way is to make the argument positional and provide its default to [IndicatorFactory.with*custom*func](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.with*custom*func) or another factory method. The default can also be set during execution in the `run` method.

Variable arguments, often appearing as `*args`, are used to accept a *variable* number of arguments. To enable variable arguments, you need to set `var*args` to True. The reason is as follows: when [IndicatorFactory.with*custom*func](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.with*custom*func) builds the `run` method, it must rearrange the arguments so that required arguments appear before optional arguments. Without the `var_args` flag, the `run` method does not expect any additional positional arguments to be passed, which can lead to an error or, even worse, a corrupted result.

Let's add a variable number of inputs:

!!! note The indicator above is effectively inputless: inputs that are not registered in `input_names` will not broadcast automatically and are not available as attributes of an indicator instance.

Positional arguments are handled in the same way as variable arguments.

You can set `keyword*only*args` to True to require that all arguments be used as keyword-only arguments. This can help avoid accidentally placing arguments in the wrong position.

For example, consider the `RelClose` indicator:

[IndicatorFactory](https://vectorbt.pro/pvt_ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory) reuses calculation artifacts whenever possible. Since it was originally designed for hyperparameter optimization and parameter combinations may get repeated, preventing the repeated processing of the same parameter combination is essential for good performance.

First, look at a typical raw output by passing repeated parameter combinations and setting `return_raw` to True:

The raw output consists of:

!!! info A raw output represents the context of running an indicator. If any parameter combination appears in the list of zipped parameter combinations, it means that it was actually run, not cached.

You can see that the calculation function was executed for the same parameter combination twice. This is not a problem if your calculation is fast enough that you do not mind re-running the same procedure. However, if your indicator is very complex and slow to compute, you can instruct [IndicatorBase.run*pipeline](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorBase.run*pipeline) to run the indicator on unique parameter combinations only by passing `run*unique`:

only unique parameter combinations. You can ignore this.

Let's compare the performance of running the same parameter combination repeatedly with and without `run_unique`:

!!! tip The moving average is one of the fastest indicators available. Try this example on a more complex indicator to see the impact of built-in caching.

there are duplicates among parameter combinations.

if two identical parameter combinations can lead to different results (for example, when using a `custom_func` that makes decisions based on the entire parameter grid, or when there is some randomness involved).

!!! note `run_unique` is disabled by default.

Internally, `run*unique` uses the raw output computed from unique parameter combinations to produce the output for all parameter combinations. But what if you already have your own raw output? You can pass it as `use*raw`. This does not call the calculation function, but instead stacks raw outputs in the order their parameter combinations appear in the requested grid. If some requested parameter combinations cannot be found in `use_raw`, it will raise an error:

This allows you to pre-compute indicators.

Another performance boost can be achieved by caching manually, which must be implemented inside `custom*func`. Additionally, `custom*func` must accept a `return*cache` argument to return the cache and a `use*cache` argument to reuse the cache (similar to `return*raw` and `use*raw`). Fortunately, [IndicatorFactory.with*apply*func](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.with*apply*func) accepts a `cache*func` and provides a `custom_func` that meets these requirements.

Consider this scenario: you want to calculate the relative distance between two computationally expensive rolling windows. You have already decided on the value for the first window, and want to test thousands of values for the second window. Without caching, and even with `run_unique` enabled, the first rolling window will be recalculated many times, wasting resources:

To avoid this, pre-compute all unique rolling windows in `cache*func` and use them in `apply*func`:

instead of single values.

outputs, they all must appear as separate arguments.

This method cuts processing time by half!

What happens when you pass `per*column=True` to apply each parameter combination per column? Internally, [IndicatorFactory.with*apply*func](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.with*apply*func) splits any input, in-place output, and parameter array per column, passing one element from each to `apply*func` at a time. However, the same splitting cannot be done for `cache*func`, because you would then get 1) a list of input arrays instead of a single array (which would cause an error if the caching function was Numba-compiled, since Numba does not allow the same argument with two different types), and 2) each input array in the list could be different, so maintaining a single caching dictionary with parameter combinations as keys would not be sufficient.

To handle this edge case, VBT passes input and in-place output arrays in their regular shape (not split), and also provides a `per*column` argument set to True, so `cache*func` knows that each parameter corresponds to only one column in the input. In the caching function, you can use this flag to decide how to proceed. Usually, you simply disable caching and perform all calculations directly in the apply function.

This design is even better than the previous one because caching is now optional, and any other function can call `apply_func` without needing to handle caching. This approach also works with Numba.

Similar to raw outputs, you can force [IndicatorBase.run*pipeline](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorBase.run*pipeline) and `custom*func` to return the cache, allowing you to reuse it in other calculations or even indicators. The clear advantage of this method is that you are not limited to a fixed set of parameter combinations, but can instead use the actual parameter values, providing more control over performance management.

Like regular functions, indicators can depend on each other. To build a stacked indicator, the first step is to merge their inputs and parameters. Consider the classic moving average crossover, where we want to use the TA-Lib `SMA` indicator twice: once for the fast moving average and once for the slow moving average. By checking the arguments accepted by the indicator's `run` method, we see that it takes a time series `close` and a parameter `timeperiod`. Since both moving averages use the same time series, our only input is `close`. However, the parameter `timeperiod` should be different for each moving average, so we need to define two parameters: `timeperiod1` and `timeperiod2` (feel free to use any other names).

This implementation does have one drawback: it needlessly creates two indicator instances and repeatedly converts between NumPy arrays and Pandas objects. An ideal implementation would use only NumPy and Numba. Fortunately, any indicator constructed by [IndicatorFactory](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory) supports the `return*raw` argument, which allows you to access the actual NumPy array(s) returned by the calculation function.

Looking for another approach? Any indicator class created by [IndicatorFactory.with*custom*func](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.with*custom*func) has a `custom*func` attribute to access the custom function. Similarly, any indicator class created by [IndicatorFactory.with*apply*func](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.with*apply*func) has an `apply*func` attribute to access the apply function. This lets you call an indicator's `custom*func` from your own `custom*func` and its `apply*func` from your own `apply*func`. Note that the `apply*func` of all parsed indicators is created dynamically with `pass*packed` set to True, so it accepts arguments in the packed form:

This approach is as fast as it gets!

[:material-language-python: Python code](https://vectorbt.pro/pvt*ff8edc14/assets/jupytext/documentation/indicators/development.py.txt){ .md-button target="blank*" }

**Examples:**

Example 1 (pycon):
```pycon
>>> from vectorbtpro import *

>>> def broadcast_params(*params):
...     return list(zip(*vbt.broadcast(*[vbt.to_1d_array(p) for p in params])))

>>> broadcast_params(2, 3)
[(2, 3)]

>>> broadcast_params([2, 3], 4)
[(2, 4), (3, 4)]

>>> broadcast_params(2, [3, 4])
[(2, 3), (2, 4)]

>>> broadcast_params([2, 3], [4, 5])
[(2, 4), (3, 5)]

>>> broadcast_params([2, 3], [4, 5, 6])
ValueError: Could not broadcast shapes: {0: (2,), 1: (3,)}
```

Example 2 (pycon):
```pycon
>>> def apply_func(ts, window, lower, upper):
...     out = np.full_like(ts, np.nan, dtype=float_)
...     ts_mean = vbt.nb.rolling_mean_nb(ts, window)
...     out[ts_mean >= upper] = 1
...     out[ts_mean <= lower] = -1
...     out[(ts_mean > lower) & (ts_mean < upper)] = 0
...     return out

>>> Bounded = vbt.IF(
...     class_name="Bounded",
...     input_names=['ts'],
...     param_names=['window', 'lower', 'upper'],
...     output_names=['out']
... ).with_apply_func(apply_func)

>>> def generate_index(n):
...     return vbt.date_range("2020-01-01", periods=n)

>>> ts = pd.DataFrame({
...     'a': [5, 4, 3, 2, 3, 4, 5],
...     'b': [2, 3, 4, 5, 4, 3, 2]
... }, index=generate_index(7))
>>> bounded = Bounded.run(ts, 2, 3, 5)
```

Example 3 (pycon):
```pycon
>>> bounded.param_names
('window', 'lower', 'upper')
```

Example 4 (pycon):
```pycon
>>> bounded.window_list
[2]
```

---

## Indicators

**URL:** https://vectorbt.pro/pvt_ff8edc14/cookbook/indicators.md

**Contents:**
- Listing
- Running
  - Parallelization
- Registration

!!! question Learn more in the [Indicators documentation](https://vectorbt.pro/pvt_ff8edc14/documentation/indicators/).

To list the currently supported indicators, use [IndicatorFactory.list*indicators](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.list*indicators). You can filter the returned indicator names by location, which can be listed with [IndicatorFactory.list*locations](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.list*locations), or by applying a glob or regex pattern.

!!! note If you do not specify a location, indicators from all locations will be parsed, which may take some time. To avoid repeated calls, save the results to a variable.

<div class="separator-container"> <hr class="separator"> <span class="separator-text">+</span> <hr class="separator"> </div>

To get the class of an indicator, use [IndicatorFactory.get*indicator](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.get_indicator).

Custom, TA-LIB, and Pandas-TA indicators are preferred in that order.

<div class="separator-container"> <hr class="separator"> <span class="separator-text">+</span> <hr class="separator"> </div>

To get familiar with an indicator class, call [phelp](https://vectorbt.pro/pvt_ff8edc14/api/utils/formatting/#vectorbtpro.utils.formatting.phelp) on the `run` class method, which is used to run the indicator. The specification, such as input names, is also available through various properties that can be accessed programmatically.

These are the arrays on which the indicator is computed.

These are the parameters being tested.

These are the arrays written in-place by the indicator.

These are the arrays returned by the indicator.

These arrays can be optionally calculated after the indicator has finished computing.

To run an indicator, call the [IndicatorBase.run](https://vectorbt.pro/pvt_ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorBase.run) class method of its class. Pass the input arrays (any array-like objects, such as Pandas DataFrames or NumPy arrays), parameters (which can be single values or lists for testing multiple parameter combinations), and other arguments expected by the indicator. Running the indicator returns **an indicator instance** (not the actual arrays!).

But if it expects other time series such as "open", "high", or "low", use only "close".

If the close price is a Series, its name will become a tuple.

and you want the output arrays to have the same columns or names as the input arrays.

!!! warning Testing a wide grid of parameter combinations will produce large arrays. For example, testing 10000 parameter combinations on one year of daily data would create an array that takes 30MB of RAM. If the indicator returns three arrays, RAM consumption would be at least 120MB. For one year of minute data, this would result in about 40GB. To avoid excessive memory use, test only a subset of combinations at a time, such as by using [parameterization](https://vectorbt.pro/pvt*ff8edc14/cookbook/optimization#parameterization) or [chunking](https://vectorbt.pro/pvt*ff8edc14/cookbook/optimization#chunking).

<div class="separator-container"> <hr class="separator"> <span class="separator-text">+</span> <hr class="separator"> </div>

Often, you may want an indicator to skip missing values. For this, use `skipna=True`. This argument works for any indicator, not just TA-Lib indicators, with one requirement: the jitted loop must be disabled. When passing a two-dimensional input array, make sure to also set `split_columns=True` to split its columns and process one column at a time.

<div class="separator-container"> <hr class="separator"> <span class="separator-text">+</span> <hr class="separator"> </div>

Another approach is to remove missing values entirely.

<div class="separator-container"> <hr class="separator"> <span class="separator-text">+</span> <hr class="separator"> </div>

To retrieve the output arrays from an indicator instance, you can access each one as an attribute, or use various unpacking options such as [IndicatorBase.unpack](https://vectorbt.pro/pvt_ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorBase.unpack).

<div class="separator-container"> <hr class="separator"> <span class="separator-text">+</span> <hr class="separator"> </div>

To keep outputs in NumPy format and/or skip any shape checks, use `return_raw="outputs"`.

<div class="separator-container"> <hr class="separator"> <span class="separator-text">+</span> <hr class="separator"> </div>

A simpler way to run indicators is by using [Data.run](https://vectorbt.pro/pvt_ff8edc14/api/data/base/#vectorbtpro.data.base.Data.run), which takes an indicator name or class, determines what input names the indicator expects, and runs the indicator by automatically passing all the inputs found in the data instance. This method also supports unpacking and running multiple indicators, which is very useful for feature engineering.

The function and output names will appear in the column levels "run_func" and "output" respectively.

<div class="separator-container"> <hr class="separator"> <span class="separator-text">+</span> <hr class="separator"> </div>

To quickly run and plot a TA-Lib indicator on a single parameter combination without using the indicator factory, use [talib*func](https://vectorbt.pro/pvt*ff8edc14/api/indicators/talib*/#vectorbtpro.indicators.talib.talib*func) and [talib*plot*func](https://vectorbt.pro/pvt*ff8edc14/api/indicators/talib*/#vectorbtpro.indicators.talib.talib*plot*func) respectively. Unlike the official TA-Lib implementation, these handle DataFrames, NaNs, broadcasting, and timeframes properly. The indicator factory's TA-Lib version is based on these functions.

Parameter combinations are processed using [execute](https://vectorbt.pro/pvt_ff8edc14/api/utils/execution/#vectorbtpro.utils.execution.execute) so it is straightforward to parallelize their execution.

into an optimal number of chunks, and execute all chunks in parallel with multithreading (one chunk per thread).

number of chunks and execute all chunks in parallel with multiprocessing (one chunk per process), while processing all parameter combinations within each chunk serially.

Custom indicators can be registered with the indicator factory to appear in the list of all indicators. This allows you to refer to the indicator by name when running a data instance. Upon registration, you can assign the indicator to a custom location (the default is "custom"), which serves as a tag or group. This lets you create arbitrary indicator groups. One indicator can be assigned to multiple locations. Custom indicators take priority over built-in indicators.

**Examples:**

Example 1 (text):
```text
indicator_names = vbt.IF.list_indicators()  # (1)!
indicator_names = vbt.IF.list_indicators("vbt")  # (2)!
indicator_names = vbt.IF.list_indicators("talib")  # (3)!
indicator_names = vbt.IF.list_indicators("RSI*")  # (4)!
indicator_names = vbt.IF.list_indicators("*ma")  # (5)!
indicator_names = vbt.IF.list_indicators("[a-z]+ma$", use_regex=True)  # (6)!
indicator_names = vbt.IF.list_indicators("*ma", location="pandas_ta")  # (7)!

location_names = vbt.IF.list_locations()  # (8)!
```

Example 2 (text):
```text
vbt.BBANDS  # (1)!

BBANDS = vbt.IF.get_indicator("pandas_ta:BBANDS")  # (2)!
BBANDS = vbt.indicator("pandas_ta:BBANDS")  # (3)!
BBANDS = vbt.IF.from_pandas_ta("BBANDS")  # (4)!
BBANDS = vbt.pandas_ta("BBANDS")  # (5)!

RSI = vbt.indicator("RSI")  # (6)!
```

Example 3 (text):
```text
vbt.phelp(vbt.OLS.run)  # (1)!

print(vbt.OLS.input_names)  # (2)!
print(vbt.OLS.param_names)  # (3)!
print(vbt.OLS.param_defaults)  # (4)!
print(vbt.OLS.in_output_names)  # (5)!
print(vbt.OLS.output_names)  # (6)!
print(vbt.OLS.lazy_output_names)  # (7)!
```

Example 4 (text):
```text
bbands = vbt.BBANDS.run(close)  # (1)!
bbands = vbt.BBANDS.run(open)  # (2)!
bbands = vbt.BBANDS.run(close, window=20)  # (3)!
bbands = vbt.BBANDS.run(close, window=vbt.Default(20))  # (4)!
bbands = vbt.BBANDS.run(close, window=20, hide_params=["window"])  # (5)!
bbands = vbt.BBANDS.run(close, window=20, hide_params=True)  # (6)!
bbands = vbt.BBANDS.run(close, window=[10, 20, 30])  # (7)!
bbands = vbt.BBANDS.run(close, window=[10, 20, 30], alpha=[2, 3, 4])  # (8)!
bbands = vbt.BBANDS.run(close, window=[10, 20, 30], alpha=[2, 3, 4], param_product=True)  # (9)!
```

---

## indicators

**URL:** https://vectorbt.pro/pvt_ff8edc14/api/indicators.md

**Contents:**
- Sub-packages
- Sub-modules

Package for building and running technical indicators.

[Technical indicators](https://www.investopedia.com/articles/trading/11/indicators-and-strategies-explained.asp) help analyze historical trends and anticipate future market movements.

---

## Analysis

**URL:** https://vectorbt.pro/pvt_ff8edc14/documentation/indicators/analysis.md

**Contents:**
- Helper methods
  - Numeric
  - Boolean
  - Enumerated
- Indexing
- Stats and plots
- Extending

To analyze an indicator, use the indicator instance returned by the `run` method.

Whenever you create an instance of [IndicatorFactory](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory), it builds and sets up an indicator class. During this process, the factory attaches many useful attributes to the class. For example, for each item in `input*names`, `in*output*names`, `output*names`, and `lazy*outputs`, it creates and attaches a set of comparison and combination methods. The properties of any of these attributes can be controlled using the `attr_settings` dictionary.

Let's modify the `CrossSig` class created earlier by combining entries and exits into a single signal array. We will also return an enumerated array that indicates the signal type. Additionally, we will specify the data type of each array in the `attr_settings` dictionary:

We can explore the helper methods that were attached using Python's `dir` command:

One helper method that appears for each array is `stats`, which calls [StatsBuilderMixin.stats](https://vectorbt.pro/pvt*ff8edc14/api/generic/stats*builder/#vectorbtpro.generic.stats_builder.StatsBuilderMixin.stats) on the accessor that matches the data type of the array:

You can also perform the same operation manually:

The factory generated the comparison methods `above`, `below`, and `equal` for the numeric arrays. Each of these methods is based on [combine*objs](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.combine*objs), which in turn builds on [BaseAccessor.combine](https://vectorbt.pro/pvt*ff8edc14/api/base/accessors/#vectorbtpro.base.accessors.BaseAccessor.combine). All operations are performed strictly with NumPy. Another benefit is that VBT's own broadcasting is used, allowing you to combine arrays with any array-like object as long as their shapes can be broadcast together. You can also compare with multiple objects at once by passing them as a tuple or list.

Let's return True when the fast moving average is above a range of thresholds:

Additionally, the factory attached the methods `crossed*above` and `crossed*below`. These are based on [GenericAccessor.crossed*above](https://vectorbt.pro/pvt*ff8edc14/api/generic/accessors/#vectorbtpro.generic.accessors.GenericAccessor.crossed*above) and [GenericAccessor.crossed*below](https://vectorbt.pro/pvt*ff8edc14/api/generic/accessors/#vectorbtpro.generic.accessors.GenericAccessor.crossed*below) respectively.

The factory generated the comparison methods `and`, `or`, and `xor` for the boolean arrays. Similar to those generated for numeric arrays, these are also based on [combine*objs](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.combine_objs):

Enumerated (or categorical) arrays, such as our `signal_type`, contain integer data that can be mapped to specific categories using a named tuple or another enum. Unlike numeric and boolean arrays, comparing them with other arrays is not meaningful. As a result, there is only one attached method, `readable`, which displays the array in a human-readable format:

!!! tip In VBT, if `-1` is not included in the enum, it automatically indicates a missing value and is replaced by `None`.

Each indicator class inherits from [Analyzable](https://vectorbt.pro/pvt_ff8edc14/documentation/building-blocks/#analyzing), allowing you to use Pandas indexing on the indicator instance to select rows and columns across all Pandas objects. Supported operations include `iloc`, `loc`, `xs`, and `**getitem**`.

Additionally, [IndicatorFactory](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory) uses the class factory function [build*param*indexer](https://vectorbt.pro/pvt*ff8edc14/api/base/indexing/#vectorbtpro.base.indexing.build*param*indexer) to generate an indexing class that enables Pandas-style indexing on each parameter. Since the indicator class inherits from this indexing class, you can use `*param*name**loc` to select one or more parameter values.

a separate instance of `CrossSig`.

All of this allows you to access rows and columns by labels, integer positions, and parameters, offering complete flexibility :man_cartwheeling:

As with any [Analyzable](https://vectorbt.pro/pvt_ff8edc14/api/generic/analyzable/#vectorbtpro.generic.analyzable.Analyzable) instance, you can compute and plot various properties of the input and output data stored in the instance.

Metrics can be set in two ways: by passing them through the `metrics` argument, or by subclassing the indicator class. The same applies to the `stats*defaults` argument, which can be specified as either a dictionary or a function, and defines the default settings for [StatsBuilderMixin.stats](https://vectorbt.pro/pvt*ff8edc14/api/generic/stats*builder/#vectorbtpro.generic.stats*builder.StatsBuilderMixin.stats). Subplots can be defined similarly to metrics, but are set using the `subplots` and `plots*defaults` arguments, and invoked through [PlotsBuilderMixin.plots](https://vectorbt.pro/pvt*ff8edc14/api/generic/plots*builder/#vectorbtpro.generic.plots*builder.PlotsBuilderMixin.plots).

Let's define some metrics and subplots for `CrossSig`:

with Series (per statistic) using [BaseAccessor.to*dict](https://vectorbt.pro/pvt*ff8edc14/api/base/accessors/#vectorbtpro.base.accessors.BaseAccessor.to_dict). The `dict` type tells VBT to make multiple metrics from one.

can automatically recognize the arguments your plotting function takes and pass the needed information. For example, it detects `self` and passes the indicator instance.

select the provided column from each time series using [Wrapping.select*col*from*obj](https://vectorbt.pro/pvt*ff8edc14/api/base/wrapping/#vectorbtpro.base.wrapping.Wrapping.select*col*from_obj).

Note that the function does not return anything; the figure is modified in place.

Calculate the metrics:

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/documentation/indicators/plots.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/documentation/indicators/plots.dark.svg#only-dark){: .iimg loading=lazy }

We have created a smart indicator, yay! :partying_face:

Indicator classes can be extended and modified just like regular Python classes, by subclassing. Let's turn the newly created `plot*mas` and `plot*signals` functions into methods of the indicator class, so we can plot each graph separately. We will also redefine the `subplots` configuration to reflect this change:

if it was not provided.

VBT's [attribute resolution](https://vectorbt.pro/pvt_ff8edc14/documentation/building-blocks/#attribute-resolution).

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/documentation/indicators/plot*signals.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/documentation/indicators/plot*signals.dark.svg#only-dark){: .iimg loading=lazy }

[:material-language-python: Python code](https://vectorbt.pro/pvt*ff8edc14/assets/jupytext/documentation/indicators/analysis.py.txt){ .md-button target="blank*" }

**Examples:**

Example 1 (pycon):
```pycon
>>> from vectorbtpro import *

>>> SignalType = namedtuple('SigType', ['Entry', 'Exit'])(0, 1)  # (1)!

>>> def apply_func(ts, fastw, sloww, minp=None):
...     fast_ma = vbt.nb.rolling_mean_nb(ts, fastw, minp=minp)
...     slow_ma = vbt.nb.rolling_mean_nb(ts, sloww, minp=minp)
...     entries = vbt.nb.crossed_above_nb(fast_ma, slow_ma)
...     exits = vbt.nb.crossed_above_nb(slow_ma, fast_ma)
...     signals = entries | exits
...     signal_type = np.full(ts.shape, -1, dtype=int_)  # (2)!
...     signal_type[entries] = SignalType.Entry
...     signal_type[exits] = SignalType.Exit
...     return (fast_ma, slow_ma, signals, signal_type)

>>> CrossSig = vbt.IF(
...     class_name="CrossSig",
...     input_names=['ts'],
...     param_names=['fastw', 'sloww'],
...     output_names=['fast_ma', 'slow_ma', 'signals', 'signal_type'],
...     attr_settings=dict(
...         fast_ma=dict(dtype=float_),
...         slow_ma=dict(dtype=float_),
...         signals=dict(dtype=bool_),
...         signal_type=dict(dtype=SignalType),
...     )
... ).with_apply_func(apply_func)

>>> def generate_index(n):
...     return vbt.date_range("2020-01-01", periods=n)

>>> ts = pd.DataFrame({
...     'a': [1, 2, 3, 2, 1, 2, 3],
...     'b': [3, 2, 1, 2, 3, 2, 1]
... }, index=generate_index(7))
>>> cross_sig = CrossSig.run(ts, 2, 3)
```

Example 2 (pycon):
```pycon
>>> dir(cross_sig)
...
'fast_ma',
'fast_ma_above',
'fast_ma_below',
'fast_ma_crossed_above',
'fast_ma_crossed_below',
'fast_ma_equal',
'fast_ma_stats',
...
'signal_type',
'signal_type_readable',
'signal_type_stats',
...
'signals',
'signals_and',
'signals_or',
'signals_stats',
'signals_xor',
...
'slow_ma',
'slow_ma_above',
'slow_ma_below',
'slow_ma_crossed_above',
'slow_ma_crossed_below',
'slow_ma_equal',
'slow_ma_stats',
...
'ts',
'ts_above',
'ts_below',
'ts_crossed_above',
'ts_crossed_below',
'ts_equal',
'ts_stats',
```

Example 3 (pycon):
```pycon
>>> cross_sig.fast_ma_stats(column=(2, 3, 'a'))  # (1)!
Start        2020-01-01 00:00:00
End          2020-01-07 00:00:00
Period           7 days 00:00:00
Count                          6
Mean                         2.0
Std                     0.547723
Min                          1.5
Median                       2.0
Max                          2.5
Min Index    2020-01-02 00:00:00
Max Index    2020-01-03 00:00:00
Name: (2, 3, a), dtype: object
```

Example 4 (pycon):
```pycon
>>> cross_sig.fast_ma.vbt.stats(column=(2, 3, 'a'))
```

---

## Indicators

**URL:** https://vectorbt.pro/pvt_ff8edc14/features/indicators.md

**Contents:**
- Hurst exponent
- Smart Money Concepts
- Signal unraveling
- Lightweight TA-Lib
- Indicator search
- Indicators for ML
- Signal detection
- Pivot detection
- Technical indicators
- Renko chart

![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/new-in/v2024*6_19.svg){ loading=lazy }

process or exhibits underlying trends. VBT offers five (!) different implementations.

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/hurst.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/hurst.dark.svg#only-dark){: .iimg loading=lazy }

![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/new-in/v2024*6_19.svg){ loading=lazy }

[Smart Money Concepts (SMC)](https://github.com/joshyattridge/smart-money-concepts) library.

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/smc.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/smc.dark.svg#only-dark){: .iimg loading=lazy }

![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/new-in/v2024*2_22.svg){ loading=lazy }

signals, into its own column. This creates a wide, two-dimensional mask that, when backtested, returns performance metrics for each signal rather than for the entire column.

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/signal*unraveling.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/signal*unraveling.dark.svg#only-dark){: .iimg loading=lazy }

![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/new-in/1*14_0.svg){ loading=lazy }

TA-Lib implementation, they can broadcast, handle DataFrames, skip missing values, and even resample to a different timeframe. Although TA-Lib functions are very fast, wrapping them with the indicator factory adds some overhead. To keep both the speed of TA-Lib and the power of VBT, the added features have been separated into a lightweight function that you can call just like a regular TA-Lib function.

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/native*talib.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/native*talib.dark.svg#only-dark){: .iimg loading=lazy }

![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/new-in/1*11_1.svg){ loading=lazy }

of them all. To make indicators easier to find, several new methods are available for globally searching for indicators.

![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/new-in/1*8_2.svg){ loading=lazy }

them individually: you can tell VBT to run all indicators from an indicator package on the given data instance. The data instance will recognize the input names of each indicator and supply the required data. You can also easily change the defaults for each indicator.

![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/new-in/1*8_0.svg){ loading=lazy }

This indicator can be used to identify outbreaks and outliers in any time series data.

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/signal*detection.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/signal*detection.dark.svg#only-dark){: .iimg loading=lazy }

![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/new-in/1*7_1.svg){ loading=lazy }

support and resistance areas, it helps spot significant price changes while filtering out short-term fluctuations and reducing noise. It works simply: a peak is registered when the price jumps above one threshold, and a valley is recorded when the price falls below another. Another advantage is that, unlike the [regular Zig Zag indicator](https://www.investopedia.com/ask/answers/030415/what-zig-zag-indicator-formula-and-how-it-calculated.asp), which tends to look ahead, our indicator only returns confirmed pivot points and is safe to use in backtesting.

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/pivot*detection.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/pivot*detection.dark.svg#only-dark){: .iimg loading=lazy }

![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/new-in/1*7_0.svg){ loading=lazy }

[technical](https://github.com/freqtrade/technical) library.

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/sumcon.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/sumcon.dark.svg#only-dark){: .iimg loading=lazy }

![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/new-in/1*7_0.svg){ loading=lazy }

is built using price movements. Each "brick" appears when the price changes by a specified amount. Because the output has irregular time intervals, only one column can be processed at once. As with everything, VBT's implementation can translate a huge number of data points very fast thanks to Numba.

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/renko*chart.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/renko*chart.dark.svg#only-dark){: .iimg loading=lazy }

![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/new-in/1*3_0.svg){ loading=lazy }

In VBT, this is implemented as an indicator that takes two time series and returns the slope, intercept, prediction, error, and the z-score of the error at each time step. This indicator can be used for cointegration tests, such as determining optimal rebalancing timings in pairs trading, and is also (literally) 1000x faster than the statsmodels equivalent [RollingOLS](https://www.statsmodels.org/dev/generated/statsmodels.regression.rolling.RollingOLS.html) :fire:

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/rolling*ols.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/rolling*ols.dark.svg#only-dark){: .iimg loading=lazy }

![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/new-in/1*2_0.svg){ loading=lazy }

support a parameter that resamples the input arrays to a target time frame, calculates the indicator, and then resamples the output arrays back to the original time frame. This makes parameterized MTF analysis easier than ever!

!!! example "Tutorial" Learn more in the [MTF analysis](https://vectorbt.pro/pvt_ff8edc14/tutorials/mtf-analysis) tutorial.

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/talib*time*frames.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/talib*time*frames.dark.svg#only-dark){: .iimg loading=lazy }

![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/new-in/1*0_10.svg){ loading=lazy }

forced users to adapt all functions accordingly. Now, the indicator factory can split each input array along columns and pass one column at a time, making it much easier to design indicators that are meant to be run natively on one-dimensional data (such as TA-Lib!).

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/stochrsi.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/stochrsi.dark.svg#only-dark){: .iimg loading=lazy }

![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/new-in/1*0_10.svg){ loading=lazy }

processes, or even in the cloud. This is a huge help when working with slow indicators :snail:

in a multithreaded fashion.

![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/new-in/1*0_9.svg){ loading=lazy }

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/talib.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/talib.dark.svg#only-dark){: .iimg loading=lazy }

![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/new-in/1*0_8.svg){ loading=lazy }

Python code enhanced with various extensions. The indicator factory automatically derives all required information, such as inputs, parameters, outputs, NumPy, VBT, and TA-Lib functions, and even complex indicators, thanks to a unique format and built-in matching mechanism. Designing indicators has never been easier!

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/indicator*expressions.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/indicator*expressions.dark.svg#only-dark){: .iimg loading=lazy }

![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/new-in/1*0_8.svg){ loading=lazy }

as an indicator :eyes:

![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/new-in/1*0_0.svg){ loading=lazy }

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/resilient*crossovers.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/features/resilient*crossovers.dark.svg#only-dark){: .iimg loading=lazy }

[:material-language-python: Python code](https://vectorbt.pro/pvt*ff8edc14/assets/jupytext/features/indicators.py.txt){ .md-button target="blank*" }

**Examples:**

Example 1 (text):
```text
>>> data = vbt.YFData.pull("BTC-USD", start="12 months ago")
>>> hurst = vbt.HURST.run(data.close, method=["standard", "logrs", "rs", "dma", "dsod"])
>>> fig = vbt.make_subplots(specs=[[dict(secondary_y=True)]])
>>> data.plot(plot_volume=False, ohlc_trace_kwargs=dict(opacity=0.3), fig=fig)
>>> fig = hurst.hurst.vbt.plot(fig=fig, add_trace_kwargs=dict(secondary_y=True))
>>> fig = fig.select_range(start=hurst.param_defaults["window"])
>>> fig.show()
```

Example 2 (text):
```text
>>> data = vbt.YFData.pull("BTC-USD", start="6 months ago")
>>> phl = vbt.smc("previous_high_low").run(  # (1)!
...     data.open,
...     data.high,
...     data.low,
...     data.close,
...     data.volume,
...     time_frame=vbt.Default("7D")
... )
>>> fig = data.plot()
>>> phl.previous_high.rename("previous_high").vbt.plot(fig=fig)
>>> phl.previous_low.rename("previous_low").vbt.plot(fig=fig)
>>> (phl.broken_high == 1).rename("broken_high").vbt.signals.plot_as_markers(
...     y=phl.previous_high, 
...     trace_kwargs=dict(marker=dict(color="limegreen")),
...     fig=fig
... )
>>> (phl.broken_low == 1).rename("broken_low").vbt.signals.plot_as_markers(
...     y=phl.previous_low, 
...     trace_kwargs=dict(marker=dict(color="orangered")),
...     fig=fig
... )
>>> fig.show()
```

Example 3 (text):
```text
>>> data = vbt.YFData.pull("BTC-USD")
>>> fast_sma = data.run("talib_func:sma", timeperiod=20)  # (1)!
>>> slow_sma = data.run("talib_func:sma", timeperiod=50)
>>> entries = fast_sma.vbt.crossed_above(slow_sma)
>>> exits = fast_sma.vbt.crossed_below(slow_sma)
>>> entries, exits = entries.vbt.signals.unravel_between(exits, relation="anychain")  # (2)!
>>> pf = vbt.PF.from_signals(
...     data, 
...     long_entries=entries, 
...     short_entries=exits, 
...     size=100,  # (3)!
...     size_type="value",
...     init_cash="auto",  # (4)!
...     tp_stop=0.2, 
...     sl_stop=0.1, 
...     group_by=vbt.ExceptLevel("signal"),  # (5)!
...     cash_sharing=True
... )
>>> pf.positions.returns.to_pd(ignore_index=True).vbt.barplot(
...     trace_kwargs=dict(marker=dict(colorscale="Spectral"))
... ).show()  # (6)!
```

Example 4 (text):
```text
>>> data = vbt.YFData.pull("BTC-USD")
>>> run_rsi = vbt.talib_func("rsi")
>>> rsi = run_rsi(data.close, timeperiod=12, timeframe="M")  # (1)!
>>> rsi
Date
2014-09-17 00:00:00+00:00          NaN
2014-09-18 00:00:00+00:00          NaN
2014-09-19 00:00:00+00:00          NaN
2014-09-20 00:00:00+00:00          NaN
2014-09-21 00:00:00+00:00          NaN
                                   ...
2024-01-18 00:00:00+00:00    64.210811
2024-01-19 00:00:00+00:00    64.210811
2024-01-20 00:00:00+00:00    64.210811
2024-01-21 00:00:00+00:00    64.210811
2024-01-22 00:00:00+00:00    64.210811
Freq: D, Name: Close, Length: 3415, dtype: float64

>>> plot_rsi = vbt.talib_plot_func("rsi")
>>> plot_rsi(rsi).show()
```

---

## Parsers

**URL:** https://vectorbt.pro/pvt_ff8edc14/documentation/indicators/parsers.md

**Contents:**
- TA-Lib
  - Skipping NaN
  - Resampling
  - Plotting
- Pandas TA
- TA
- Expressions
  - Instance method
  - Class method
  - TA-Lib

[IndicatorFactory](https://vectorbt.pro/pvt_ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory) uses a set of parsers to simplify the process of creating indicators. These include parsers for third-party indicators as well as an advanced expression parser.

!!! info Each parser method is a class method with the prefix `from_`, so you do not need to create or pass any information to the indicator factory using `vbt.IF(...)` - the method handles this for you!

[IndicatorFactory.from*talib](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.from_talib) can parse [TA-Lib](https://github.com/mrjbq7/ta-lib) indicators. When you provide the name of an indicator, the method retrieves the TA-Lib abstract function and then checks the `info` dictionary to determine the input, parameter, and output names. After creating a factory instance, it builds an apply function that can run the indicator function on two-dimensional inputs, instead of only the one-dimensional inputs that TA-Lib supports by default.

To view the list of all supported indicators:

To retrieve an indicator:

Or, you can use a shortcut:

TA-Lib indicators often do not handle missing data well. For example, a single NaN in a time series can cause all subsequent values to become NaN:

To address this, you can instruct the indicator factory to run the indicator only on non-NA values, then insert the output values at their original positions:

!!! tip Another method is to forward fill NaN values before running an indicator, but this can distort the results. Only use this approach when it is truly appropriate.

Another feature provided by the indicator factory is support for parameterized time frames.

Here is how it works:

This allows you to pack multiple time frames into a single two-dimensional array:

!!! note If some timestamps are missing, VBT may have trouble parsing the source index frequency. To specify the frequency directly, pass `broadcast*kwargs=dict(wrapper*kwargs=dict(freq="1h"))`, for example. Without the source frequency, VBT will upsample the downsampled arrays between each pair of timestamps in the source index, rather than relying on its frequency, which might be undesirable.

You can also plot each indicator. This is done programmatically by parsing the output flags of the indicator. For example, here is how to use `STOCH`:

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/documentation/indicators/stoch.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/documentation/indicators/stoch.dark.svg#only-dark){: .iimg loading=lazy }

To see the arguments that the `plot` function accepts, use [phelp](https://vectorbt.pro/pvt_ff8edc14/api/utils/formatting/#vectorbtpro.utils.formatting.phelp):

Now, let's create a plot with two subplots: OHLC above, and %D and %K below. We will also change the style of both output lines from dashed to solid and display a range between an oversold limit of 20 and an overbought limit of 80:

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/documentation/indicators/stoch*subplots.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/documentation/indicators/stoch*subplots.dark.svg#only-dark){: .iimg loading=lazy }

[IndicatorFactory.from*pandas*ta](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.from*pandas*ta) can parse [Pandas TA](https://pypi.org/project/pandas-ta/) indicators. Since Pandas TA indicators do not have metadata attached to each indicator, a method called [IndicatorFactory.parse*pandas*ta*config](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.parse*pandas*ta*config) is used. This method reads the signature of an indicator function to determine the input and parameter names and their default values. It also passes several dozen rows of sample data to the function to identify the number and names of the outputs.

!!! note If any indicator raises an error while parsing, try increasing the number of rows passed to the indicator function. For example, use `parse*kwargs=dict(test*index_len=150)`.

To get the list of all supported indicators:

To get an indicator:

Or, use the shortcut:

[IndicatorFactory.from*ta](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.from*ta) can parse [TA](https://github.com/bukosabino/ta) indicators. Similar to Pandas TA, TA indicators must be explicitly parsed to obtain the context of each indicator function. Since every indicator is a class, there is a method called [IndicatorFactory.parse*ta*config](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.parse*ta*config) that reads the signature, docstring, and attributes of the class to determine the input, parameter, and output names, as well as their defaults.

To get the list of all supported indicators:

To get an indicator:

Or, use the shortcut:

Expressions are a brand-new way to define indicators of any complexity using regular strings. The main advantage of expressions over custom and apply functions is that VBT can easily introspect the code of an indicator and add many useful automations.

Expressions are converted into full-featured indicators by a hybrid method, [IndicatorFactory.from*expr](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.from_expr). Why hybrid? It is both a class method and an instance method. You can call this method on an instance if you want full control over the indicator's specification, or on a class if you want the entire specification to be parsed for you. Let's try both approaches while building an ATR indicator!

Here is a semi-automated implementation using the instance method:

The expression `expr` is regular Python code without extensions that is evaluated using Python's `eval` command. All function names are resolved by the parser before evaluation.

Here is a fully-automated implementation using the class method and annotations:

In the first example, we provided all the required information manually by constructing a new instance of [IndicatorFactory](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory). The parser identified each input and parameter name in the expression and replaced them with actual arrays. In the second example, we used annotations to give the parser hints about the meaning of each variable. Whenever the parser finds a substring starting with `@`, it knows the variable has a special meaning for constructing a factory instance. The prefixes `@*in`, `@*p`, and `@*out` indicate an input, parameter, and output, respectively. The names appear in the order they appear in the expression (apart from OHLCV, where H always comes after O):

The parser can also detect information not starting with a special character. For example, inputs such as `open`, `high`, `low`, `close`, and `volume` are recognized automatically, so there is no need to annotate them. These are called magnet inputs, and you can specify them via the `magnet_inputs` argument. If no outputs use annotations and the expression is a multiline string with the last line containing a tuple of valid variable names, you do not need to annotate the outputs either. Also, as shown above, you can provide the class name on the first line, followed by a colon:

What about functions? The parser identifies functions by searching various modules and packages. In this example, `abs` and `nanmax` are from NumPy, while `wwm*mean*1d` is found among generic Numba-compiled functions in [nb](https://vectorbt.pro/pvt*ff8edc14/api/generic/nb/) (even without the `*nb` suffix). See the API for [IndicatorFactory.from*expr](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.from_expr) for full details. To avoid naming conflicts, you can explicitly access the NumPy, Pandas, and VBT modules as `np`, `pd`, and `vbt`:

Another automation covers TA-Lib indicators: VBT will replace any variable annotated with `@talib` with an actual TA-Lib indicator function that can operate on both one-dimensional and two-dimensional data!

How can you define your own functions and rules? Any additional keyword argument passed to [IndicatorFactory.from*expr](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.from*expr) acts as a context for evaluation and can replace a variable with the same name. Let's define our own function `shift*close`, which is an alias for [fshift*nb](https://vectorbt.pro/pvt*ff8edc14/api/generic/nb/base/#vectorbtpro.generic.nb.base.fshift_nb):

You can also create functions that depend on the evaluation context. In the example above, you can have `shift_close` accept the context and retrieve the number of periods to shift the closing price (just as an example):

The context will be automatically passed to the function once `context` has been recognized in its arguments. Moreover, you can also make `shift*close` retrieve the closing price itself. Notice how `shift*close` takes no arguments in the expression:

If you run this, you will receive an error indicating that `close` was not found in the context. This happens because the input `close` is not "visible" in the expression, so it was not added to the list of input names. To make any input, in-place output, or parameter visible—even if it is not included directly in the expression—you must notify VBT that a function depends on it. You do this using a dictionary called `func_mapping`, which maps functions to the magnet names they depend on:

Since `shift*close` depends only on the context, you can instruct the parser to call it before evaluation and only once, effectively caching its result. To do this, use `res*func*mapping` instead of `func*mapping`:

Notice that `shifted_close` no longer has parentheses—it is now an array.

But that's not all. What if you want to override any information passed to [IndicatorFactory.from*expr](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.from_expr) from within the expression itself? You can! Define a dictionary anywhere in the expression and annotate it with `@settings({...})`. The dictionary inside the parentheses will be evaluated with Python's `eval` function before the main evaluation and will be merged over the default settings of the factory method.

Let's rewrite the [instance method](#instance-method) example using only an expression:

Remember, you can use any Python code in your expressions—even other indicators. To make using indicators easier, there is a convenient annotation `@res`, which takes the name of an indicator and creates an automatically resolved function from it, similar to `shifted*close` above. This function becomes an entry in `res*func_mapping`, and the indicator's input, in-place output, and parameter names are added to the entry's magnet lists. This means you do not need to worry about passing the correct information to the indicator—vectorbt handles it for you!

Let's illustrate this by defining basic SuperTrend bands:

What happens if two indicators have overlapping inputs, parameters, or other arguments? Every argument except for the inputs receives a prefix with the indicator's short name ([IndicatorBase.short*name](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorBase.short_name)). Under the hood, VBT checks the signature of the indicator's `run` method to see whether there is an argument with the same name in the context (and remember the prefix).

By default, the resolved function returns raw output as one or more NumPy arrays. If the indicator has more than one output, you can use regular indexing to select a specific array, such as `@res*talib*macd[0]`. Let's disable raw outputs for ATR and access the `real` Pandas object from its indicator instance instead:

are passed as `**kwargs`, so you can specify `atr_kwargs` to target those variable arguments.

There is nothing more satisfying than defining an indicator in one line :drooling_face:

Notice how the output annotation `@out` is no longer bound to any variable and is now written similarly to the class name, with a trailing colon followed by the output expression. If there are multiple outputs, separate their output expressions with a comma. Here is a single-line expression for basic SuperTrend bands with multiple outputs:

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/documentation/indicators/supertrend.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/documentation/indicators/supertrend.dark.svg#only-dark){: .iimg loading=lazy }

Like many other factory methods, [IndicatorFactory.from*expr](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.from*expr) passes inputs and in-place outputs as two-dimensional NumPy arrays. You can enable the `keep*pd` flag to work with Pandas objects. Let's run our ATR indicator using only Pandas:

!!! note Unlike the previous NumPy-only expressions, this expression will not work for multiple columns of input data.

For simpler expressions, you can instruct the parser to use [pandas.eval](https://pandas.pydata.org/docs/reference/api/pandas.eval.html) instead of Python's `eval`. This provides multi-threading and other performance benefits for large inputs, since `pd.eval` switches to [NumExpr](https://github.com/pydata/numexpr) by default:

To view the expression after parsing all annotations, set `return*clean*expr` to True:

Additionally, just as in regular Python code, you can place `print` statements to explore the state at each step of execution:

[IndicatorFactory.from*wqa101](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.from*wqa101) uses the expression parser to parse and execute [101 Formulaic Alphas](https://arxiv.org/pdf/1601.00991.pdf). Each alpha expression is defined in [wqa101*expr*config](https://vectorbt.pro/pvt*ff8edc14/api/indicators/expr/#vectorbtpro.indicators.expr.wqa101*expr*config), while most functions and resolved functions used in the alpha expressions are defined in [expr*func*config](https://vectorbt.pro/pvt*ff8edc14/api/indicators/expr/#vectorbtpro.indicators.expr.expr*func*config) and [expr*res*func*config](https://vectorbt.pro/pvt*ff8edc14/api/indicators/expr/#vectorbtpro.indicators.expr.expr*res*func*config), respectively.

To get an indicator:

Replicating an alpha indicator is straightforward: look up its expression in the config and pass it to [IndicatorFactory.from*expr](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.from_expr):

[:material-language-python: Python code](https://vectorbt.pro/pvt*ff8edc14/assets/jupytext/documentation/indicators/parsers.py.txt){ .md-button target="blank*" }

**Examples:**

Example 1 (pycon):
```pycon
>>> from vectorbtpro import *

>>> vbt.IF.list_talib_indicators()  # (1)!
{'ACOS',
 'AD',
 'ADD',
 ...
 'WCLPRICE',
 'WILLR',
 'WMA'}
```

Example 2 (pycon):
```pycon
>>> vbt.IF.from_talib('RSI')  # (1)!
vectorbtpro.indicators.factory.talib.RSI
```

Example 3 (pycon):
```pycon
>>> vbt.talib('RSI')
vectorbtpro.indicators.factory.talib.RSI
```

Example 4 (pycon):
```pycon
>>> price = vbt.RandomData.pull(
...     start='2020-01-01', 
...     end='2020-06-01', 
...     timeframe='1H',
...     seed=42
... ).get()
>>> price_na = price.copy()
>>> price_na.iloc[2] = np.nan  # (1)!

>>> SMA = vbt.talib("SMA")
>>> sma = SMA.run(price_na, timeperiod=10)
>>> sma.real
2019-12-31 22:00:00+00:00   NaN
2019-12-31 23:00:00+00:00   NaN
2020-01-01 00:00:00+00:00   NaN
2020-01-01 01:00:00+00:00   NaN
2020-01-01 02:00:00+00:00   NaN
...                         ...
2020-05-31 18:00:00+00:00   NaN
2020-05-31 19:00:00+00:00   NaN
2020-05-31 20:00:00+00:00   NaN
2020-05-31 21:00:00+00:00   NaN
2020-05-31 22:00:00+00:00   NaN
Freq: H, Name: 10, Length: 3649, dtype: float64
```

---

## factory

**URL:** https://vectorbt.pro/pvt_ff8edc14/api/indicators/factory.md

**Contents:**
- build_columns <span class="dobjtype">function</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/indicators/factory.py#L209-L332" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.indicators.factory.build_columns data-toc-label="build\_columns" }
- combine_indicator_with_other <span class="dobjtype">function</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/indicators/factory.py#L369-L389" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.indicators.factory.combine_indicator_with_other data-toc-label="combine\_indicator\_with\_other" }
- combine_objs <span class="dobjtype">function</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/indicators/factory.py#L335-L363" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.indicators.factory.combine_objs data-toc-label="combine\_objs" }
- indicator <span class="dobjtype">function</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/indicators/factory.py#L6164-L6174" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.indicators.factory.indicator data-toc-label="indicator" }
- pandas_ta <span class="dobjtype">function</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/indicators/factory.py#L6190-L6200" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.indicators.factory.pandas_ta data-toc-label="pandas\_ta" }
- prepare_params <span class="dobjtype">function</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/indicators/factory.py#L103-L206" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.indicators.factory.prepare_params data-toc-label="prepare\_params" }
- resolve_jitted_indicator_func <span class="dobjtype">function</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/indicators/factory.py#L82-L100" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.indicators.factory.resolve_jitted_indicator_func data-toc-label="resolve\_jitted\_indicator\_func" }
- smc <span class="dobjtype">function</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/indicators/factory.py#L6255-L6265" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.indicators.factory.smc data-toc-label="smc" }
- ta <span class="dobjtype">function</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/indicators/factory.py#L6203-L6213" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.indicators.factory.ta data-toc-label="ta" }
- talib <span class="dobjtype">function</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/indicators/factory.py#L6177-L6187" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.indicators.factory.talib data-toc-label="talib" }

Module providing functionality for constructing and managing technical indicators.

Run for the examples below:

For each parameter in `params`, create a new column level with parameter values and stack it on top of `input_columns`.

**```params```** :&ensp;`Params` :   Collection of parameter values.

**```input_columns```** :&ensp;`IndexLike` :   Initial column index to which parameter levels are added.

**```level_names```** :&ensp;`Optional[Sequence[str]]` :   List of level names corresponding to each parameter.

**```hide_levels```** :&ensp;`Optional[Sequence[Union[str, int]]` :   Levels to exclude from visibility.

**```single_value```** :&ensp;`Optional[Sequence[bool]]` :   Flags indicating if each parameter is a single value.

**```param_settings```** :&ensp;`KwargsLikeSequence` :   Settings for parameters such as data type mapping and processing options.

**```per_column```** :&ensp;`bool` :   If True, processes parameters separately for each column.

**```ignore_ranges```** :&ensp;`bool` :   If True, ignores range checks during column stacking.

**```**kwargs```** :   Keyword arguments for [stack*indexes](https://vectorbt.pro/pvt*ff8edc14/api/base/indexes/#vectorbtpro.base.indexes.stack*indexes "vectorbtpro.base.indexes.stack*indexes").

`dict` :   Dictionary containing:

Combine [IndicatorBase](https://vectorbt.pro/pvt_ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorBase "vectorbtpro.indicators.factory.IndicatorBase") with another compatible object by applying a specified NumPy function.

**```other```** :&ensp;`Union[IndicatorBase, ArrayLike]` :   Other indicator or array.

**```np*func```** :&ensp;`Callable[[ArrayLike, ArrayLike], Array1d]` :   Function that combines the arrays from [IndicatorBase.main*output](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorBase.main*output "vectorbtpro.indicators.factory.IndicatorBase.main_output") and `other`.

`SeriesFrame` :   Resulting Series or DataFrame after combining [IndicatorBase.main*output](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorBase.main*output "vectorbtpro.indicators.factory.IndicatorBase.main*output") with the other object's data.

Combine or compare `obj` with `other` to generate signals by applying a custom combine function.

**```obj```** :&ensp;`SeriesFrame` :   Main Series or DataFrame to operate on.

**```other```** :&ensp;`MaybeTupleList[Union[ArrayLike, BaseAccessor]]` :   Object or objects to be combined with `obj`.

**```combine_func```** :&ensp;`Callable` :   Function used to combine or compare elements of `obj` and `other`.

**```*args```** :   Positional arguments for [BaseAccessor.combine](https://vectorbt.pro/pvt_ff8edc14/api/base/accessors/#vectorbtpro.base.accessors.BaseAccessor.combine "vectorbtpro.base.accessors.BaseAccessor.combine").

**```level_name```** :&ensp;`Optional[str]` :   Name for the new column level when multiple values of `other` are provided.

**```keys```** :&ensp;`Optional[IndexLike]` :   Keys to use when broadcasting multiple objects.

**```allow_multiple```** :&ensp;`bool` :   If True, permits `other` to be provided as a tuple or list.

**```**kwargs```** :   Keyword arguments for [BaseAccessor.combine](https://vectorbt.pro/pvt_ff8edc14/api/base/accessors/#vectorbtpro.base.accessors.BaseAccessor.combine "vectorbtpro.base.accessors.BaseAccessor.combine").

`SeriesFrame` :   Resulting Series or DataFrame after combining `obj` with `other`.

**```*args```** :   Positional arguments for [IndicatorFactory.get*indicator](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.get*indicator "vectorbtpro.indicators.factory.IndicatorFactory.get*indicator").

**```**kwargs```** :   Keyword arguments for [IndicatorFactory.get*indicator](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.get*indicator "vectorbtpro.indicators.factory.IndicatorFactory.get*indicator").

[IndicatorBase](https://vectorbt.pro/pvt_ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorBase "vectorbtpro.indicators.factory.IndicatorBase") :   Indicator class.

Get a Pandas TA indicator.

**```*args```** :   Positional arguments for [IndicatorFactory.from*pandas*ta](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.from*pandas*ta "vectorbtpro.indicators.factory.IndicatorFactory.from*pandas_ta").

**```**kwargs```** :   Keyword arguments for [IndicatorFactory.from*pandas*ta](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.from*pandas*ta "vectorbtpro.indicators.factory.IndicatorFactory.from*pandas_ta").

[IndicatorBase](https://vectorbt.pro/pvt_ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorBase "vectorbtpro.indicators.factory.IndicatorBase") :   Indicator class.

Resolve references in the input parameters and perform broadcasting to match the input shape.

**```params```** :&ensp;`MaybeParams` :   Input parameters, which may include references that need resolution.

**```param_names```** :&ensp;`Sequence[str]` :   Names of the parameters.

**```param_settings```** :&ensp;`Sequence[KwargsLike]` :   Sequence of dictionaries providing settings for each parameter.

**```input_shape```** :&ensp;`Optional[Shape]` :   Shape of the input arrays.

**```to_2d```** :&ensp;`bool` :   If True, reshapes inputs to 2D arrays.

**```context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

`Tuple[Params, bool]` :   Tuple where the first element is the list of processed parameters and the second element indicates whether a single parameter combination was provided.

Resolve a function using the indicator JIT policy.

**```func```** :&ensp;`Callable` :   Function to resolve.

**```jitted```** :&ensp;`JittedOption` :   Option to control JIT compilation.

`Callable` :   Resolved function.

Get a Smart Money Concepts indicator.

**```*args```** :   Positional arguments for [IndicatorFactory.from*smc](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.from*smc "vectorbtpro.indicators.factory.IndicatorFactory.from*smc").

**```**kwargs```** :   Keyword arguments for [IndicatorFactory.from*smc](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.from*smc "vectorbtpro.indicators.factory.IndicatorFactory.from*smc").

[IndicatorBase](https://vectorbt.pro/pvt_ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorBase "vectorbtpro.indicators.factory.IndicatorBase") :   Indicator class.

**```*args```** :   Positional arguments for [IndicatorFactory.from*ta](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.from*ta "vectorbtpro.indicators.factory.IndicatorFactory.from*ta").

**```**kwargs```** :   Keyword arguments for [IndicatorFactory.from*ta](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.from*ta "vectorbtpro.indicators.factory.IndicatorFactory.from*ta").

[IndicatorBase](https://vectorbt.pro/pvt_ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorBase "vectorbtpro.indicators.factory.IndicatorBase") :   Indicator class.

Get a TA-Lib indicator.

**```*args```** :   Positional arguments for [IndicatorFactory.from*talib](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.from*talib "vectorbtpro.indicators.factory.IndicatorFactory.from*talib").

**```**kwargs```** :   Keyword arguments for [IndicatorFactory.from*talib](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.from*talib "vectorbtpro.indicators.factory.IndicatorFactory.from*talib").

[IndicatorBase](https://vectorbt.pro/pvt_ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorBase "vectorbtpro.indicators.factory.IndicatorBase") :   Indicator class.

Get a Technical Consensus indicator.

**```*args```** :   Positional arguments for [IndicatorFactory.from*techcon](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.from*techcon "vectorbtpro.indicators.factory.IndicatorFactory.from*techcon").

**```**kwargs```** :   Keyword arguments for [IndicatorFactory.from*techcon](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.from*techcon "vectorbtpro.indicators.factory.IndicatorFactory.from*techcon").

[IndicatorBase](https://vectorbt.pro/pvt_ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorBase "vectorbtpro.indicators.factory.IndicatorBase") :   Indicator class.

Get a Technical indicator.

**```*args```** :   Positional arguments for [IndicatorFactory.from*technical](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.from*technical "vectorbtpro.indicators.factory.IndicatorFactory.from*technical").

**```**kwargs```** :   Keyword arguments for [IndicatorFactory.from*technical](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.from*technical "vectorbtpro.indicators.factory.IndicatorFactory.from*technical").

[IndicatorBase](https://vectorbt.pro/pvt_ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorBase "vectorbtpro.indicators.factory.IndicatorBase") :   Indicator class.

Get a WorldQuant's 101 alpha indicator.

**```*args```** :   Positional arguments for [IndicatorFactory.from*wqa101](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.from*wqa101 "vectorbtpro.indicators.factory.IndicatorFactory.from*wqa101").

**```**kwargs```** :   Keyword arguments for [IndicatorFactory.from*wqa101](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.from*wqa101 "vectorbtpro.indicators.factory.IndicatorFactory.from*wqa101").

[IndicatorBase](https://vectorbt.pro/pvt_ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorBase "vectorbtpro.indicators.factory.IndicatorBase") :   Indicator class.

Base class for indicators.

Set properties before instantiation.

**```wrapper```** :&ensp;`ArrayWrapper` :   Array wrapper instance.

**```input_list```** :&ensp;`IFArrayList` :   List of 2D input arrays.

**```input_mapper```** :&ensp;`IFInputMapper` :   1D input mapper array.

**```in*output*list```** :&ensp;`IFArrayList` :   List of 2D input-output arrays.

**```output_list```** :&ensp;`IFArrayList` :   List of 2D output arrays.

**```param_list```** :&ensp;`IFParamList` :   List of parameter value lists.

**```mapper_list```** :&ensp;`IFMapperList` :   List of mapper indexes.

**```short_name```** :&ensp;`str` :   Short name of the indicator.

**```jitted```** :&ensp;`JittedOption` :   Option to control JIT compilation.

**```**kwargs```** :   Keyword arguments for [Analyzable](https://vectorbt.pro/pvt_ff8edc14/api/generic/analyzable/#vectorbtpro.generic.analyzable.Analyzable "vectorbtpro.generic.analyzable.Analyzable").

**Inherited members**

Clone the docstring from another class.

**```another_cls```** :&ensp;`Type` :   Class from which to clone the docstring.

Clone a method to the class.

**```method```** :&ensp;`Callable` :   Method to clone.

**```target_name```** :&ensp;`Optional[str]` :   Target name for the cloned method.

Stack multiple [IndicatorBase](https://vectorbt.pro/pvt_ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorBase "vectorbtpro.indicators.factory.IndicatorBase") instances along columns for parameters.

This method uses [ArrayWrapper.column*stack](https://vectorbt.pro/pvt*ff8edc14/api/base/wrapping/#vectorbtpro.base.wrapping.ArrayWrapper.column*stack "vectorbtpro.base.wrapping.ArrayWrapper.column*stack") to combine the wrappers and stack input, in_output, output arrays, parameter lists, and mapper lists.

All objects to be merged must share the same index.

**```*objs```** :&ensp;`MaybeSequence[IndicatorBase]` :   (Additional) indicator instances to stack.

**```wrapper_kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for configuring the wrapper.

**```reindex_kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for `pd.DataFrame.reindex`.

**```**kwargs```** :   Keyword arguments for [IndicatorBase](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorBase "vectorbtpro.indicators.factory.IndicatorBase") through [Wrapping.resolve*column*stack*kwargs](https://vectorbt.pro/pvt*ff8edc14/api/base/wrapping/#vectorbtpro.base.wrapping.Wrapping.resolve*column*stack*kwargs "vectorbtpro.indicators.factory.IndicatorBase.resolve*column*stack*kwargs") and [Wrapping.resolve*stack*kwargs](https://vectorbt.pro/pvt*ff8edc14/api/base/wrapping/#vectorbtpro.base.wrapping.Wrapping.resolve*stack*kwargs "vectorbtpro.indicators.factory.IndicatorBase.resolve*stack*kwargs").

[IndicatorBase](https://vectorbt.pro/pvt_ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorBase "vectorbtpro.indicators.factory.IndicatorBase") :   New instance with combined data from the provided indicators.

Drop missing values from the indicator outputs.

**```include_all```** :&ensp;`bool` :   Flag to determine whether to include all outputs (regular, in-place, and lazy).

**```**kwargs```** :   Keyword arguments for `pd.Series.dropna` or `pd.DataFrame.dropna`.

[IndicatorBase](https://vectorbt.pro/pvt_ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorBase "vectorbtpro.indicators.factory.IndicatorBase") :   New indicator instance with missing values dropped.

Return a time series output based on a key.

**```key```** :&ensp;`Optional[Hashable]` :   Key corresponding to a specific output.

`Optional[SeriesFrame]` :   Requested time series or the main output if no key is provided.

Names of the in-place output arrays.

`Tuple[str, ...]` :   Tuple of in-place output names.

Perform indexing on an [IndicatorBase](https://vectorbt.pro/pvt_ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorBase "vectorbtpro.indicators.factory.IndicatorBase") instance.

**```*args```** :   Positional arguments for [ArrayWrapper.indexing*func](https://vectorbt.pro/pvt*ff8edc14/api/base/wrapping/#vectorbtpro.base.wrapping.ArrayWrapper.indexing*func "vectorbtpro.base.wrapping.ArrayWrapper.indexing*func").

**```wrapper_meta```** :&ensp;`DictLike` :   Metadata from the indexing operation on the wrapper.

**```**kwargs```** :   Keyword arguments for [ArrayWrapper.indexing*func](https://vectorbt.pro/pvt*ff8edc14/api/base/wrapping/#vectorbtpro.base.wrapping.ArrayWrapper.indexing*func "vectorbtpro.base.wrapping.ArrayWrapper.indexing*func").

[IndicatorBase](https://vectorbt.pro/pvt_ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorBase "vectorbtpro.indicators.factory.IndicatorBase") :   New indicator instance with updated indexing.

**Overridden methods**

Names of the input arrays.

`Tuple[str, ...]` :   Tuple of input names.

Iterate over columns or groups.

Iterates over columns or groups based on the specified grouping criteria. When grouping is enabled via [Wrapping.group*select](https://vectorbt.pro/pvt*ff8edc14/api/base/wrapping/#vectorbtpro.base.wrapping.HasWrapper.group*select "vectorbtpro.base.wrapping.Wrapping.group*select"), groups are returned instead of individual columns. The `group*by` parameter can be provided as a column name present in the wrapper, the string "all*params" for full parameter mapping, "params" for only visible parameters, or as a specific parameter name.

**```group_by```** :&ensp;`GroupByLike` :   Grouping specification.

**```apply*group*by```** :&ensp;`bool` :   If True, applies the grouping to both iteration and the final output.

**```keep_2d```** :&ensp;`bool` :   Whether to maintain the output data in a 2D format.

**```key*as*index```** :&ensp;`bool` :   Whether to return the yielded key as an index.

`Items` :   Iterator over key-value pairs representing each column or group.

**Overridden methods**

JIT option used to build this indicator.

Names of the lazy output arrays.

`Tuple[str, ...]` :   Tuple of lazy output names.

List of level names corresponding to each parameter.

`Tuple[str, ...]` :   Tuple of level names corresponding to each parameter.

If the indicator has only one output, return that output. Otherwise, return the output matching the indicator's short name (case sensitive or lower case).

`SeriesFrame` :   Main output of the indicator.

`ValueError` :   If the indicator has no main output.

Dictionary of output flags.

`Kwargs` :   Dictionary of output flags.

Names of the regular output arrays.

`Tuple[str, ...]` :   Tuple of output names.

Parameter defaults extracted from the signature of [IndicatorBase.run](https://vectorbt.pro/pvt_ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorBase.run "vectorbtpro.indicators.factory.IndicatorBase.run").

`Dict[str, Any]` :   Dictionary of parameter defaults.

Names of the parameters.

`Tuple[str, ...]` :   Tuple of parameter names.

Replace the short name of the indicator.

**```short_name```** :&ensp;`str` :   New short name for the indicator.

[IndicatorBase](https://vectorbt.pro/pvt_ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorBase "vectorbtpro.indicators.factory.IndicatorBase") :   New indicator instance with the updated short name.

Resolve a function using this indicator's JIT option.

**```func```** :&ensp;`Callable` :   Function to resolve.

**```jitted```** :&ensp;`JittedOption` :   Option to control JIT compilation.

`Callable` :   Resolved function.

Stack multiple [IndicatorBase](https://vectorbt.pro/pvt_ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorBase "vectorbtpro.indicators.factory.IndicatorBase") instances along rows.

This method uses [ArrayWrapper.row*stack](https://vectorbt.pro/pvt*ff8edc14/api/base/wrapping/#vectorbtpro.base.wrapping.ArrayWrapper.row*stack "vectorbtpro.base.wrapping.ArrayWrapper.row*stack") to combine the wrappers and stack input, in_output, and output arrays from each indicator.

All objects to be merged must have the same columns for parameters.

**```*objs```** :&ensp;`MaybeSequence[IndicatorBase]` :   (Additional) indicator instances to stack.

**```wrapper_kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for configuring the wrapper.

**```**kwargs```** :   Keyword arguments for [IndicatorBase](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorBase "vectorbtpro.indicators.factory.IndicatorBase") through [Wrapping.resolve*row*stack*kwargs](https://vectorbt.pro/pvt*ff8edc14/api/base/wrapping/#vectorbtpro.base.wrapping.Wrapping.resolve*row*stack*kwargs "vectorbtpro.indicators.factory.IndicatorBase.resolve*row*stack*kwargs") and [Wrapping.resolve*stack*kwargs](https://vectorbt.pro/pvt*ff8edc14/api/base/wrapping/#vectorbtpro.base.wrapping.Wrapping.resolve*stack*kwargs "vectorbtpro.indicators.factory.IndicatorBase.resolve*stack*kwargs").

[IndicatorBase](https://vectorbt.pro/pvt_ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorBase "vectorbtpro.indicators.factory.IndicatorBase") :   New instance with combined data from the provided indicators.

Execute the indicator run operation.

This method delegates to the internal `_run` method.

**```*args```** :   Additional positional arguments.

**```**kwargs```** :   Additional keyword arguments.

`IFRunOutput` :   Result of running the indicator.

Execute the indicator run combinations operation.

This method delegates to the internal `*run*combs` method.

**```*args```** :   Additional positional arguments.

**```**kwargs```** :   Additional keyword arguments.

`IFRunCombsOutput` :   Result of running the indicator combinations.

Run a pipeline to compute an indicator using a custom function.

This method prepares input arrays, parameters, and necessary broadcasting, and then applies the custom function to perform indicator calculations. It supports parameter combination, per-column processing, and various configurations to adjust input shapes and outputs. This method is used internally by [IndicatorFactory](https://vectorbt.pro/pvt_ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory "vectorbtpro.indicators.factory.IndicatorFactory").

**```num*ret*outputs```** :&ensp;`int` :   Number of output arrays returned by `custom_func`.

**```custom_func```** :&ensp;`Callable` :   Custom function for indicator computation.

**```*args```** :   Positional arguments for `custom_func`.

**```require*input*shape```** :&ensp;`bool` :   Flag indicating whether the input shape is required.

**```input_shape```** :&ensp;`Optional[ShapeLike]` :   Shape to which each input is broadcast.

**```input_index```** :&ensp;`Optional[IndexLike]` :   Index to assign to each input array.

**```input_columns```** :&ensp;`Optional[IndexLike]` :   Column labels for each input array.

**```inputs```** :&ensp;`Optional[MappingSequence[ArrayLike]]` :   Input arrays provided as a mapping or sequence.

**```in_outputs```** :&ensp;`Optional[MappingSequence[ArrayLike]]` :   In-place output arrays provided as a mapping or sequence.

**```in*output*settings```** :&ensp;`Optional[MappingSequence[KwargsLike]]` :   Settings for each in-place output.

**```broadcast*named*args```** :&ensp;`KwargsLike` :   Additional named arguments for broadcasting.

**```broadcast_kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for broadcasting.

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```params```** :&ensp;`Optional[MaybeParams]` :   Parameters provided as a mapping or sequence.

**```param_product```** :&ensp;`bool` :   Flag to build a Cartesian product from all parameters.

**```combine*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for [combine*params](https://vectorbt.pro/pvt*ff8edc14/api/utils/params/#vectorbtpro.utils.params.combine*params "vectorbtpro.utils.params.combine_params").

**```random_subset```** :&ensp;`Optional[int]` :   Select a random subset of parameter combinations.

**```param_settings```** :&ensp;`Optional[MappingSequence[KwargsLike]]` :   Settings for each parameter.

**```run_unique```** :&ensp;`bool` :   Flag to run only on unique parameter combinations.

**```silence_warnings```** :&ensp;`bool` :   Flag to suppress warning messages.

**```per_column```** :&ensp;`Optional[bool]` :   Flag indicating whether parameter values should be applied per column.

**```keep_pd```** :&ensp;`bool` :   If True, retain inputs as Pandas objects; otherwise, convert them to NumPy arrays.

**```to_2d```** :&ensp;`bool` :   If True, reshapes inputs to 2D arrays.

**```pass_packed```** :&ensp;`bool` :   Whether to pass inputs, in-place outputs, and parameters as packed tuples.

**```pass*input*shape```** :&ensp;`Optional[bool]` :   If True, passes `input*shape` as a keyword argument to `custom*func`.

**```pass*wrapper```** :&ensp;`bool` :   If True, passes the input wrapper to `custom*func` as a keyword argument.

**```pass*param*index```** :&ensp;`bool` :   If True, passes the parameter index to `custom_func`.

**```pass*final*index```** :&ensp;`bool` :   If True, passes the final index to `custom_func`.

**```pass*single*comb```** :&ensp;`bool` :   If True, indicates that there is only one parameter combination, and passes this information to `custom_func`.

**```pass*seed```** :&ensp;`bool` :   If True, passes `seed` as a keyword argument to `custom*func`.

**```pass*jitted```** :&ensp;`bool` :   If True, passes `jitted` as a keyword argument to `custom*func`.

**```jitted```** :&ensp;`JittedOption` :   Option to control JIT compilation.

**```level_names```** :&ensp;`Optional[Sequence[str]]` :   List of level names corresponding to each parameter.

**```hide_levels```** :&ensp;`Optional[Sequence[Union[str, int]]]` :   List of level names or indices to hide from the output.

**```build*col*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for [build*columns](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.build*columns "vectorbtpro.indicators.factory.build*columns").

**```return_raw```** :&ensp;`Union[bool, str]` :   If set, returns raw outputs and hashed parameter tuples without further post-processing.

**```use*raw```** :&ensp;`Optional[IFRawOutput]` :   If True, uses the raw results obtained previously instead of executing `custom*func`.

**```wrapper_kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for configuring the wrapper.

**```seed```** :&ensp;`Optional[int]` :   Random seed for deterministic output.

**```**kwargs```** :   Keyword arguments for `custom_func`.

`Union[tp.IFCacheOutput, tp.IFRawOutput, tp.IFPipelineOutput]` :       Tuple containing the following elements:

Short name of the indicator.

`str` :   Short name of the indicator.

Return the indicator outputs as a dictionary.

**```include_all```** :&ensp;`bool` :   Flag to determine whether to include all outputs (regular, in-place, and lazy).

`Dict[str, SeriesFrame]` :   Mapping of output names to their corresponding data.

Return the indicator outputs as a DataFrame.

**```include_all```** :&ensp;`bool` :   Flag to determine whether to include all outputs (regular, in-place, and lazy).

`Frame` :   DataFrame combining the outputs with output names as column keys.

Return indicator outputs.

If there is only one output, return it directly; otherwise, return a tuple of outputs.

`MaybeTuple[SeriesFrame]` :   Output or outputs of the indicator.

Factory for creating new indicators.

Initialize [IndicatorFactory](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory "vectorbtpro.indicators.factory.IndicatorFactory") to create a skeleton. Then, use a class method such as [IndicatorFactory.with*custom*func](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.with*custom*func "vectorbtpro.indicators.factory.IndicatorFactory.with*custom*func") to bind a calculation function to the skeleton.

!!! note The `**init**` method is not used for running the indicator; use `run` instead. Indexing requires a clean `**init**` method to create a new indicator object with re-indexed attributes.

**```class_name```** :&ensp;`Optional[str]` :   Name for the created indicator class.

**```class_docstring```** :&ensp;`Optional[str]` :   Docstring for the created indicator class.

**```module_name```** :&ensp;`Optional[str]` :   Module name to bind the generated class.

**```short_name```** :&ensp;`Optional[str]` :   Concise name for the indicator.

**```prepend*name```** :&ensp;`bool` :   Whether to prepend `short*name` to each parameter level.

**```input_names```** :&ensp;`Optional[Sequence[str]]` :   List of input names.

**```param_names```** :&ensp;`Optional[Sequence[str]]` :   List of parameter names.

**```in*output*names```** :&ensp;`Optional[Sequence[str]]` :   List of in-place output names.

**```output_names```** :&ensp;`Optional[Sequence[str]]` :   List of output names.

**```output_flags```** :&ensp;`KwargsLike` :   Dictionary of flags for in-place and regular outputs.

**```lazy_outputs```** :&ensp;`KwargsLike` :   Dictionary of user-defined functions bound to the indicator class and wrapped with `property` if not already wrapped.

**```attr_settings```** :&ensp;`KwargsLike` :   Settings for attributes, where each key maps to a dictionary of options.

**```metrics```** :&ensp;`KwargsLike` :   Metrics supported by [StatsBuilderMixin.stats](https://vectorbt.pro/pvt*ff8edc14/api/generic/stats*builder/#vectorbtpro.generic.stats*builder.StatsBuilderMixin.stats "vectorbtpro.generic.stats*builder.StatsBuilderMixin.stats").

**```stats*defaults```** :&ensp;`Union[None, Callable, Kwargs]` :   Defaults for [StatsBuilderMixin.stats](https://vectorbt.pro/pvt*ff8edc14/api/generic/stats*builder/#vectorbtpro.generic.stats*builder.StatsBuilderMixin.stats "vectorbtpro.generic.stats_builder.StatsBuilderMixin.stats").

**```subplots```** :&ensp;`KwargsLike` :   Subplots supported by [PlotsBuilderMixin.plots](https://vectorbt.pro/pvt*ff8edc14/api/generic/plots*builder/#vectorbtpro.generic.plots*builder.PlotsBuilderMixin.plots "vectorbtpro.generic.plots*builder.PlotsBuilderMixin.plots").

**```plots*defaults```** :&ensp;`Union[None, Callable, Kwargs]` :   Defaults for [PlotsBuilderMixin.plots](https://vectorbt.pro/pvt*ff8edc14/api/generic/plots*builder/#vectorbtpro.generic.plots*builder.PlotsBuilderMixin.plots "vectorbtpro.generic.plots_builder.PlotsBuilderMixin.plots").

**```**kwargs```** :   Keyword arguments for [Configured](https://vectorbt.pro/pvt_ff8edc14/api/utils/config/#vectorbtpro.utils.config.Configured "vectorbtpro.utils.config.Configured").

**Inherited members**

Built indicator class.

`Type[IndicatorBase]` :   Built indicator class.

Dictionary specifying attribute settings.

`Kwargs` :   Dictionary specifying attribute settings.

Docstring for the created indicator class.

`str` :   Docstring for the created indicator class.

Name of the created indicator class.

`str` :   Name of the created indicator class.

Custom indicators keyed by their custom locations.

`Config` :   Dictionary-like object containing custom indicators.

Deregister a custom indicator based on its name and location.

**```name```** :&ensp;`Optional[str]` :   Name of the indicator to remove.

**```location```** :&ensp;`Optional[str]` :   Location from which to remove the indicator.

**```remove_location```** :&ensp;`bool` :   Whether to remove a location if it becomes empty after the indicator is removed.

Get the Smart Money Concepts indicator class by its name.

**```func_name```** :&ensp;`str` :   Name of the smart money concepts indicator.

**```raise_error```** :&ensp;`bool` :   Flag indicating whether to raise an error if the indicator is not found.

`Optional[Callable]` :   Indicator class if found; otherwise, None.

Return a TA indicator class by its name.

Searches through modules in the TA package for an indicator class whose name matches the provided value (case-insensitive).

**```cls_name```** :&ensp;`str` :   Name of the indicator class to find.

`IndicatorMixin` :   Corresponding TA indicator class.

Get the technical indicator function corresponding to the given name.

**```func_name```** :&ensp;`str` :   Name of the technical indicator function.

`IndicatorMixin` :   Technical indicator function matching the given name.

Create an indicator based on a technical consensus class that subclasses `technical.consensus.consensus.Consensus`.

Requires the Technical library: <https://github.com/freqtrade/technical>

**```consensus_cls```** :&ensp;`Type` :   Consensus class that subclasses `technical.consensus.consensus.Consensus`.

**```factory*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for [IndicatorFactory](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory "vectorbtpro.indicators.factory.IndicatorFactory").

**```**kwargs```** :   Keyword arguments for [IndicatorFactory.with*apply*func](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.with*apply*func "vectorbtpro.indicators.factory.IndicatorFactory.with*apply_func").

`Type` :   Dynamically created indicator class.

Build an indicator class from an indicator expression.

Builds a new indicator class based on a Python expression string.

Searches each variable name parsed from `expr` in:

The configurations in [expr*func*config](https://vectorbt.pro/pvt*ff8edc14/api/indicators/expr/#vectorbtpro.indicators.expr.expr*func*config "vectorbtpro.indicators.expr.expr*func*config") and [expr*res*func*config](https://vectorbt.pro/pvt*ff8edc14/api/indicators/expr/#vectorbtpro.indicators.expr.expr*res*func*config "vectorbtpro.indicators.expr.expr*res*func*config") can be overridden via `func*mapping` and `res*func*mapping`, respectively.

!!! note Each variable name is case-sensitive.

When invoked as a class method, variable names are parsed directly from the expression. If any of `open`, `high`, `low`, `close`, or `volume` appear in the expression or are listed in `magnet*inputs` (within either `expr*func*config` or `expr*res*func*config`), they are automatically added to `input*names`. Set `magnet*inputs` to an empty list to disable this behavior.

If the expression starts with a valid variable name followed by a colon (`:`), that name is used as the generated class name. Provide an additional variable name enclosed in square brackets immediately before the colon to specify the indicator's short name.

If `parse_annotations` is True, annotations beginning with `@` define variable roles:

!!! note Variable names are parsed in the order they appear in the expression, except for magnet input names which follow the order in `magnet_inputs`.

The number of outputs is determined by counting commas outside any bracket pair. If there is only one output, it is named `out`; for multiple outputs, they are named `out1`, `out2`, etc.

Any of these settings can be overridden using `factory_kwargs`.

The code context includes all variables from [imported*star](https://vectorbt.pro/pvt*ff8edc14/api/#vectorbtpro.imported*star "vectorbtpro.imported*star").

**```expr```** :&ensp;`str` :   Expression string.

**```parse_annotations```** :&ensp;`bool` :   Flag to parse annotations starting with `@`.

**```factory*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for [IndicatorFactory](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory "vectorbtpro.indicators.factory.IndicatorFactory").

**```magnet_inputs```** :&ensp;`Iterable[str]` :   Names to be recognized as input variables.

**```magnet*in*outputs```** :&ensp;`Iterable[str]` :   Names to be recognized as in-place output variables.

**```magnet_params```** :&ensp;`Iterable[str]` :   Names to be recognized as parameter variables.

**```func*mapping```** :&ensp;`KwargsLike` :   Mapping to merge with [expr*func*config](https://vectorbt.pro/pvt*ff8edc14/api/indicators/expr/#vectorbtpro.indicators.expr.expr*func*config "vectorbtpro.indicators.expr.expr*func*config").

**```res*func*mapping```** :&ensp;`KwargsLike` :   Mapping to merge with [expr*res*func*config](https://vectorbt.pro/pvt*ff8edc14/api/indicators/expr/#vectorbtpro.indicators.expr.expr*res*func*config "vectorbtpro.indicators.expr.expr*res*func*config").

**```use*pd*eval```** :&ensp;`Optional[bool]` :   Whether to use `pd.eval` for evaluation.

**```pd*eval*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for `pd.eval`.

**```return*clean*expr```** :&ensp;`bool` :   Flag indicating whether to return the cleaned expression.

**```**kwargs```** :   Keyword arguments for [IndicatorFactory.with*apply*func](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.with*apply*func "vectorbtpro.indicators.factory.IndicatorFactory.with*apply_func").

`Union[str, Type[IndicatorBase]]` :   If `return*clean*expr` is True, returns the cleaned expression string; otherwise, returns the generated indicator class.

The same can be achieved by calling the class method and providing prefixes to the variable names to indicate their type:

Magnet names are recognized automatically:

Most settings of this method can be overridden within the expression:

Build an indicator class around a Pandas TA function.

Requires Pandas TA installed. See <https://pypi.org/project/pandas-ta/> for details.

**```func_name```** :&ensp;`str` :   Name of the Pandas TA function to wrap.

**```parse*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for [IndicatorFactory.parse*pandas*ta*config](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.parse*pandas*ta*config "vectorbtpro.indicators.factory.IndicatorFactory.parse*pandas*ta_config").

**```factory*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for [IndicatorFactory](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory "vectorbtpro.indicators.factory.IndicatorFactory").

**```**kwargs```** :   Keyword arguments for [IndicatorFactory.with*apply*func](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.with*apply*func "vectorbtpro.indicators.factory.IndicatorFactory.with*apply_func").

`Type[IndicatorBase]` :   New indicator class wrapping the specified Pandas TA function.

Build an indicator class using a Smart Money Concepts function.

Requires [smart-money-concepts](https://github.com/joshyattridge/smart-money-concepts) to be installed.

**```func_name```** :&ensp;`str` :   Name of the smartmoneyconcepts function to wrap.

**```collapse```** :&ensp;`bool` :   Flag to collapse nested indicators' configurations into a single set.

**```parse*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for [IndicatorFactory.parse*smc*config](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.parse*smc*config "vectorbtpro.indicators.factory.IndicatorFactory.parse*smc*config").

**```factory*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for [IndicatorFactory](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory "vectorbtpro.indicators.factory.IndicatorFactory").

**```**kwargs```** :   Keyword arguments for [IndicatorFactory.with*apply*func](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.with*apply*func "vectorbtpro.indicators.factory.IndicatorFactory.with*apply_func").

`Type[IndicatorBase]` :   Indicator class built around the specified smartmoneyconcepts function.

Build an indicator class around a TA technical analysis indicator.

Requires [ta](https://github.com/bukosabino/ta) to be installed.

**```cls_name```** :&ensp;`str` :   Name of the target TA class.

**```factory*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for [IndicatorFactory](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory "vectorbtpro.indicators.factory.IndicatorFactory").

**```**kwargs```** :   Keyword arguments for [IndicatorFactory.with*apply*func](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.with*apply*func "vectorbtpro.indicators.factory.IndicatorFactory.with*apply_func").

`Type[IndicatorBase]` :   Built indicator class.

Build an indicator class using a TA-Lib function.

Requires [TA-Lib](https://github.com/mrjbq7/ta-lib) to be installed.

For input, parameter, and output names, see the [TA-Lib documentation](https://github.com/mrjbq7/ta-lib/blob/master/docs/index.md).

**```func_name```** :&ensp;`str` :   Name of the TA-Lib function to wrap.

**```factory*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for [IndicatorFactory](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory "vectorbtpro.indicators.factory.IndicatorFactory").

**```**kwargs```** :   Keyword arguments for [IndicatorFactory.with*apply*func](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.with*apply*func "vectorbtpro.indicators.factory.IndicatorFactory.with*apply_func").

[IndicatorBase](https://vectorbt.pro/pvt_ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorBase "vectorbtpro.indicators.factory.IndicatorBase") :   New indicator class based on the TA-Lib function.

To plot an indicator:

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/api/talib*plot.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/api/talib*plot.dark.svg#only-dark){: .iimg loading=lazy }

Create an indicator from a preset technical consensus.

**```cls_name```** :&ensp;`str` :   Name of the technical consensus indicator.

**```**kwargs```** :   Keyword arguments for [IndicatorFactory.from*custom*techcon](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.from*custom*techcon "vectorbtpro.indicators.factory.IndicatorFactory.from*custom_techcon").

`Type[IndicatorBase]` :   Created indicator class.

Build an indicator class using the specified technical function.

This method requires the [technical](https://github.com/freqtrade/technical) package to be installed.

**```func_name```** :&ensp;`str` :   Name of the technical indicator function to wrap.

**```parse*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for [IndicatorFactory.parse*technical*config](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.parse*technical*config "vectorbtpro.indicators.factory.IndicatorFactory.parse*technical*config").

**```factory*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for [IndicatorFactory](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory "vectorbtpro.indicators.factory.IndicatorFactory").

**```**kwargs```** :   Keyword arguments for [IndicatorFactory.with*apply*func](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.with*apply*func "vectorbtpro.indicators.factory.IndicatorFactory.with*apply_func").

`Indicator` :   Indicator class constructed around the given technical function.

Build an indicator class from one of the WorldQuant's 101 alpha expressions.

Uses a specified WorldQuant alpha expression index to build an indicator class based on the expression configuration in [wqa101*expr*config](https://vectorbt.pro/pvt*ff8edc14/api/indicators/expr/#vectorbtpro.indicators.expr.wqa101*expr*config "vectorbtpro.indicators.expr.wqa101*expr_config").

!!! note Some expressions that utilize cross-sectional operations require columns to be a multi-index with a level `sector`, `subindustry`, or `industry`.

**```alpha_idx```** :&ensp;`Union[str, int]` :   WorldQuant 101 alpha expression index.

**```**kwargs```** :   Keyword arguments for [IndicatorFactory.from*expr](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.from*expr "vectorbtpro.indicators.factory.IndicatorFactory.from*expr").

`Type[IndicatorBase]` :   Constructed indicator class.

Return a custom indicator based on its name and optional location.

**```name```** :&ensp;`str` :   Name of the custom indicator.

**```location```** :&ensp;`Optional[str]` :   Location in which to search for the indicator.

**```return_first```** :&ensp;`bool` :   If multiple indicators match, return the first one when True.

[IndicatorBase](https://vectorbt.pro/pvt_ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorBase "vectorbtpro.indicators.factory.IndicatorBase") :   Custom indicator class.

Return the indicator class corresponding to the given name and location.

The indicator name can include a location prefix separated by a colon. For example, `"talib:sma"` or `"talib_sma"` returns the TA-Lib SMA indicator. If no location is specified, the indicator is searched across all available sources, including vectorbtpro indicators.

**```name```** :&ensp;`str` :   Name of the indicator, optionally including a location prefix.

**```location```** :&ensp;`Optional[str]` :   Location to filter the search for the indicator.

**```**kwargs```** :   Keyword arguments for the respective indicator constructor.

`Type[IndicatorBase]` :   Indicator class matching the provided name.

List of in-place output names.

`List[str]` :   List of in-place output names.

List of input names.

`List[str]` :   List of input names.

Dictionary of user-defined functions converted into properties.

`Kwargs` :   Dictionary of user-defined functions converted into properties.

List of built-in indicator locations in the order defined by the author.

`List[str]` :   List of built-in indicator locations.

Return a list of custom indicator names.

**```uppercase```** :&ensp;`bool` :   Whether to convert indicator names to uppercase.

**```location```** :&ensp;`Optional[str]` :   Filter indicators by a specific location.

**```prepend_location```** :&ensp;`Optional[bool]` :   When True, indicator names are prefixed with their location.

`List[str]` :   List of custom indicator names.

List of custom indicator locations in the order they were registered.

`List[str]` :   List of custom indicator locations.

Return a list of indicator names optionally filtered by a pattern or location.

A pattern may also represent a location, in which case all indicators from that location are returned. For supported locations, see [IndicatorFactory.list*locations](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.list*locations "vectorbtpro.indicators.factory.IndicatorFactory.list*locations").

**```pattern```** :&ensp;`Optional[str]` :   Pattern to filter indicator names.

**```case_sensitive```** :&ensp;`bool` :   Whether to treat the pattern as case-sensitive.

**```use_regex```** :&ensp;`bool` :   Flag indicating whether the pattern is a regular expression.

**```location```** :&ensp;`Optional[str]` :   Specific location from which to list indicators.

**```prepend_location```** :&ensp;`Optional[bool]` :   When True, indicator names are prefixed with their location.

`List[str]` :   List of matching indicator names.

List of all supported indicator locations, with custom locations listed before built-in locations.

`List[str]` :   List of all indicator locations.

List all parseable indicators in Pandas TA.

This class method iterates over the indicator functions available in Pandas TA and attempts to parse each one's configuration using [IndicatorFactory.parse*pandas*ta*config](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.parse*pandas*ta*config "vectorbtpro.indicators.factory.IndicatorFactory.parse*pandas*ta*config"). Only indicator functions that are successfully parsed are included in the final list.

!!! note Returns only the indicators that have been successfully parsed.

**```silence_warnings```** :&ensp;`bool` :   Flag to suppress warning messages.

**```**kwargs```** :   Keyword arguments for [IndicatorFactory.parse*pandas*ta*config](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.parse*pandas*ta*config "vectorbtpro.indicators.factory.IndicatorFactory.parse*pandas*ta*config").

`List[str]` :   Sorted list of indicator names in uppercase that were successfully parsed.

List all parseable indicators from the Smart Money Concepts package.

Inspects each public function in the `smartmoneyconcepts.smc` module and returns those that can be successfully parsed into a configuration.

**```silence_warnings```** :&ensp;`bool` :   Flag to suppress warning messages.

**```**kwargs```** :   Keyword arguments for [IndicatorFactory.parse*smc*config](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.parse*smc*config "vectorbtpro.indicators.factory.IndicatorFactory.parse*smc_config").

`List[str]` :   Sorted list of indicator names in uppercase.

Return a sorted list of parseable indicator class names from the TA module.

**```uppercase```** :&ensp;`bool` :   Whether to convert indicator names to uppercase.

`List[str]` :   Sorted list of indicator class names.

Return a sorted list of all parseable indicator names from TA-Lib.

`List[str]` :   Sorted list of indicator names from the TA-Lib module.

List all consensus indicators available in technical.

`List[str]` :   Sorted list of consensus indicator names.

List all parseable technical indicator functions from the technical module.

Scans the technical package for functions and attempts to parse each using [IndicatorFactory.parse*technical*config](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.parse*technical*config "vectorbtpro.indicators.factory.IndicatorFactory.parse*technical_config"). Returns a sorted list of indicator names in uppercase.

**```silence_warnings```** :&ensp;`bool` :   Flag to suppress warning messages.

**```**kwargs```** :   Keyword arguments for [IndicatorFactory.parse*technical*config](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.parse*technical*config "vectorbtpro.indicators.factory.IndicatorFactory.parse*technical_config").

`List[str]` :   Sorted list of technical indicator names in uppercase.

Return a sorted list of all vectorbtpro indicators.

`List[str]` :   Sorted list of all vectorbtpro indicator names.

List all WorldQuant's 101 alpha indicators.

`List[str]` :   List of all WorldQuant alpha expression indices as strings.

Return the matching location name for the provided input.

**```location```** :&ensp;`str` :   Location name to match (case-insensitive).

`Optional[str]` :   Matching location if found; otherwise, None.

Metrics supported by [StatsBuilderMixin.stats](https://vectorbt.pro/pvt*ff8edc14/api/generic/stats*builder/#vectorbtpro.generic.stats*builder.StatsBuilderMixin.stats "vectorbtpro.generic.stats*builder.StatsBuilderMixin.stats").

`Config` :   Metrics supported by the stats builder.

Module name from which the class originates.

`str` :   Module name from which the class originates.

Dictionary of flags for in-place and regular outputs.

`Kwargs` :   Dictionary of flags for in-place and regular outputs.

List of output names.

`List[str]` :   List of output names.

List of parameter names.

`List[str]` :   List of parameter names.

Parse the class name and short name from the expression.

**```expr```** :&ensp;`str` :   Expression string.

`Tuple[str, Optional[str], Optional[str]]` :   Modified expression, class name, and short name.

Parse the configuration of a Pandas TA indicator.

This class method inspects the signature of the provided indicator function to determine its inputs, parameters, and outputs. It creates a test DataFrame using random data, passes it to the function, and parses the output to extract column names. The resulting configuration dictionary encapsulates details required for further processing.

**```func```** :&ensp;`Callable` :   Pandas TA indicator function to parse.

**```test*input*names```** :&ensp;`Optional[Sequence[str]]` :   Collection of potential input parameter names.

**```test*index*len```** :&ensp;`int` :   Number of rows in the generated test DataFrame.

**```silence_warnings```** :&ensp;`bool` :   Flag to suppress warning messages.

**```**kwargs```** :   Keyword arguments for the indicator function.

`Kwargs` :   Dictionary containing the following keys:

Parse the configuration of a Smart Money Concepts indicator function.

Inspects the signature and source code of the given function to extract input names, parameter names, output names, default values, and nested indicator configurations.

**```func```** :&ensp;`Callable` :   Smartmoneyconcepts indicator function to parse.

**```collapse```** :&ensp;`bool` :   Flag to collapse nested indicators' configurations into a single set.

**```snake_case```** :&ensp;`bool` :   Flag to convert names to snake case.

`dict` :   Dictionary containing the parsed configuration with the following keys:

Parse the configuration of a TA indicator class.

Inspects the signature and docstring of the given indicator class to extract input names, parameter names, default values, and output names.

**```ind_cls```** :&ensp;`IndicatorMixin` :   TA indicator class to parse.

`dict` :   Dictionary containing:

Parse the configuration for a technical indicator function.

Generates a test DataFrame and inspects the provided function's signature and output to extract configuration details, including input names, parameter names, output names, and default parameter values.

**```func```** :&ensp;`Callable` :   Technical indicator function to parse.

**```test*index*len```** :&ensp;`int` :   Number of rows in the generated test DataFrame.

`dict` :   Configuration dictionary containing:

Default configuration for [PlotsBuilderMixin.plots](https://vectorbt.pro/pvt*ff8edc14/api/generic/plots*builder/#vectorbtpro.generic.plots*builder.PlotsBuilderMixin.plots "vectorbtpro.generic.plots*builder.PlotsBuilderMixin.plots").

`Kwargs` :   Dictionary containing the default configuration for the plots builder.

Whether [IndicatorFactory.short*name](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.short*name "vectorbtpro.indicators.factory.IndicatorFactory.short*name") should be prepended to each parameter level.

`bool` :   True if `short_name` should be prepended to each parameter level, False otherwise.

Register a custom indicator under a custom location.

**```indicator```** :&ensp;`Union[str, IndicatorBase]` :   Custom indicator to register, specified as a string reference or a type.

**```name```** :&ensp;`Optional[str]` :   Name under which to register the indicator.

**```location```** :&ensp;`Optional[str]` :   Custom location where the indicator should be registered.

**```if_exists```** :&ensp;`str` :   Behavior if an indicator with the same name already exists; must be "raise", "skip", or "override".

**```**kwargs```** :   Keyword arguments for [IndicatorFactory.get*indicator](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.get*indicator "vectorbtpro.indicators.factory.IndicatorFactory.get*indicator").

Concise name for the indicator.

`str` :   Concise name for the indicator.

Split an indicator name into its constituent location and indicator name.

**```name```** :&ensp;`str` :   Indicator name, which may include location information separated by a colon or underscore.

`Tuple[Optional[str], Optional[str]]` :   Tuple where the first element is the location (if detected) and the second element is the indicator name.

Default configuration for [StatsBuilderMixin.stats](https://vectorbt.pro/pvt*ff8edc14/api/generic/stats*builder/#vectorbtpro.generic.stats*builder.StatsBuilderMixin.stats "vectorbtpro.generic.stats*builder.StatsBuilderMixin.stats").

`Kwargs` :   Dictionary containing the default configuration for the stats builder.

Subplots configuration supported by [PlotsBuilderMixin.plots](https://vectorbt.pro/pvt*ff8edc14/api/generic/plots*builder/#vectorbtpro.generic.plots*builder.PlotsBuilderMixin.plots "vectorbtpro.generic.plots*builder.PlotsBuilderMixin.plots").

`Config` :   Subplots configuration supported by the plots builder.

Build indicator class around a custom apply function.

Construct and return an indicator class that wraps a custom apply function for calculations. This method simplifies indicator creation by handling caching, parameter selection, and concatenation of outputs automatically. In contrast to [IndicatorFactory.with*custom*func](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.with*custom*func "vectorbtpro.indicators.factory.IndicatorFactory.with*custom_func"), it works with one parameter selection at a time, limiting the ability to view all combinations.

The computation and concatenation are executed using [apply*and*concat*each](https://vectorbt.pro/pvt*ff8edc14/api/base/combining/#vectorbtpro.base.combining.apply*and*concat*each "vectorbtpro.base.combining.apply*and*concat*each").

!!! note If `apply_func` is a Numba-compiled function:

!!! note Reserved arguments such as `per*column` are passed as positional arguments when `jitted*loop` is True, and as keyword arguments otherwise.

**```apply_func```** :&ensp;`Callable` :   Function that receives inputs, a selection of parameters, and additional arguments, and performs calculations.

**```cache*func```** :&ensp;`Optional[Callable]` :   Function to preprocess inputs via caching before invoking `apply*func`.

**```takes_1d```** :&ensp;`bool` :   Whether to split 2D arrays into multiple 1D arrays along the column axis.

**```select_params```** :&ensp;`bool` :   Whether to automatically select in-place outputs and parameters.

**```pass_packed```** :&ensp;`bool` :   Whether to pass inputs, in-place outputs, and parameters as packed tuples.

**```cache*pass*packed```** :&ensp;`Optional[bool]` :   Overrides `pass_packed` for the caching function.

**```pass*per*column```** :&ensp;`bool` :   Whether to pass the `per_column` flag to the apply function.

**```cache*pass*per*column```** :&ensp;`Optional[bool]` :   Overrides `pass*per_column` for the caching function.

**```forward_skipna```** :&ensp;`bool` :   Whether to forward the `skipna` argument to the apply function.

**```kwargs*as*args```** :&ensp;`Optional[Iterable[str]]` :   Names of keyword arguments from `**kwargs` to pass as positional arguments to the apply function.

**```kwargs*to*ndim```** :&ensp;`KwargsLike` :   Mapping from `kwargs*as*args` names to the target number of dimensions.

**```kwargs*preprocessor```** :&ensp;`Optional[Callable]` :   Function that takes and returns keyword arguments before positional arguments from `kwargs*as_args` are resolved.

**```pass_seed```** :&ensp;`bool` :   Whether to pass `seed` to the apply and cache functions.

**```jit_kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for the `@njit` decorator of the parameter selection function.

**```**kwargs```** :   Keyword arguments for [IndicatorFactory.with*custom*func](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.with*custom*func "vectorbtpro.indicators.factory.IndicatorFactory.with*custom*func") and ultimately to [apply*and*concat*each](https://vectorbt.pro/pvt*ff8edc14/api/base/combining/#vectorbtpro.base.combining.apply*and*concat*each "vectorbtpro.base.combining.apply*and*concat_each").

`Indicator` :   Indicator class constructed around the provided apply function.

Following example produces the same indicator as the [IndicatorFactory.with*custom*func](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.with*custom*func "vectorbtpro.indicators.factory.IndicatorFactory.with*custom_func") example.

To change the execution engine or specify other engine-related arguments, use `execute_kwargs`:

Build an indicator class based on a custom calculation function.

This method offers full flexibility compared to [IndicatorFactory.with*apply*func](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.with*apply*func "vectorbtpro.indicators.factory.IndicatorFactory.with*apply*func"). The caller is responsible for handling caching and concatenation of columns for each parameter (e.g., via [apply*and*concat](https://vectorbt.pro/pvt*ff8edc14/api/base/combining/#vectorbtpro.base.combining.apply*and*concat "vectorbtpro.base.combining.apply*and*concat")). Additionally, ensure that each output array has the correct number of columns, which should equal the number of input array columns multiplied by the number of parameter combinations.

**```custom*func```** :&ensp;`Callable` :   Function that processes broadcast arrays corresponding to `input*names`, in-place output arrays corresponding to `in*output*names`, and broadcast parameter arrays corresponding to `param_names`, along with additional positional and keyword arguments.

**```require*input*shape```** :&ensp;`bool` :   Flag indicating whether the input shape is required.

**```param_settings```** :&ensp;`KwargsLike` :   Dictionary of parameter settings keyed by name.

**```in*output*settings```** :&ensp;`KwargsLike` :   Dictionary of in-place output settings keyed by name.

**```hide_params```** :&ensp;`Union[None, bool, Sequence[str]]` :   Either a boolean to hide all parameter column levels or a list of parameter names for which the column levels should be hidden.

**```hide_default```** :&ensp;`bool` :   If True, hides column levels for parameters that have default values.

**```var_args```** :&ensp;`bool` :   Specifies whether run methods should accept variable positional arguments (`*args`).

**```keyword*only*args```** :&ensp;`bool` :   Specifies whether run methods should enforce keyword-only arguments.

**```**pipeline*kwargs```** :   Keyword arguments for [IndicatorBase.run*pipeline](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorBase.run*pipeline "vectorbtpro.indicators.factory.IndicatorBase.run_pipeline").

`Indicator` :   Instance of the indicator.

Following example produces the same indicator as the [IndicatorFactory.with*apply*func](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.with*apply*func "vectorbtpro.indicators.factory.IndicatorFactory.with*apply_func") example.

The primary difference between `apply*func*nb` in this example and in [IndicatorFactory.with*apply*func](https://vectorbt.pro/pvt*ff8edc14/api/indicators/factory/#vectorbtpro.indicators.factory.IndicatorFactory.with*apply*func "vectorbtpro.indicators.factory.IndicatorFactory.with*apply_func") is that here the function receives an index for the current parameter combination, which can be used for parameter selection.

Alternatively, you can omit the separate `apply*func*nb` function and implement your logic directly in `custom_func` (which need not be Numba-compiled):

**Examples:**

Example 1 (pycon):
```pycon
>>> from vectorbtpro import *

>>> price = pd.DataFrame({
...     'a': [1, 2, 3, 4, 5],
...     'b': [5, 4, 3, 2, 1]
... }, index=pd.date_range("2020", periods=5)).astype(float)
>>> price
            a    b
2020-01-01  1.0  5.0
2020-01-02  2.0  4.0
2020-01-03  3.0  3.0
2020-01-04  4.0  2.0
2020-01-05  5.0  1.0
```

Example 2 (python):
```python
build_columns(
    params,
    input_columns,
    level_names=None,
    hide_levels=None,
    single_value=None,
    param_settings=None,
    per_column=False,
    ignore_ranges=False,
    **kwargs
)
```

Example 3 (text):
```text
* `param_indexes`: List of initial parameter indexes.
* `rep_param_indexes`: List of repeated parameter indexes corresponding to `input_columns`.
* `vis_param_indexes`: List of visible parameter indexes not hidden.
* `vis_rep_param_indexes`: List of visible repeated parameter indexes.
* `param_index`: Combined parameter index, or None if `per_column` is True.
* `final_index`: Final stacked index combining visible parameter indexes and `input_columns`.
```

Example 4 (python):
```python
combine_indicator_with_other(
    other,
    np_func
)
```

---
