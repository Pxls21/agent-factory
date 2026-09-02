# Vectorbtpro_Docs - Splitting Cv

**Pages:** 9

---

## sklearn_

**URL:** https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/sklearn_.md

**Contents:**
- SplitterCV <span class="dobjtype">class</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/generic/splitting/sklearn_.py#L26-L367" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.generic.splitting.sklearn_.SplitterCV data-toc-label="SplitterCV" }
  - get_n_splits <span class="dobjtype">method</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/generic/splitting/sklearn_.py#L332-L349" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.generic.splitting.sklearn_.SplitterCV.get_n_splits data-toc-label="get\_n\_splits" }
  - get_splitter <span class="dobjtype">method</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/generic/splitting/sklearn_.py#L171-L209" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.generic.splitting.sklearn_.SplitterCV.get_splitter data-toc-label="get\_splitter" }
  - set_group_by <span class="dobjtype">class property</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/generic/splitting/sklearn_.py#L148-L160" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.generic.splitting.sklearn_.SplitterCV.set_group_by data-toc-label="set\_group\_by" }
  - split <span class="dobjtype">method</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/generic/splitting/sklearn_.py#L351-L367" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.generic.splitting.sklearn_.SplitterCV.split data-toc-label="split" }
  - split_group_by <span class="dobjtype">class property</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/generic/splitting/sklearn_.py#L134-L146" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.generic.splitting.sklearn_.SplitterCV.split_group_by data-toc-label="split\_group\_by" }
  - splitter <span class="dobjtype">class property</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/generic/splitting/sklearn_.py#L103-L112" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.generic.splitting.sklearn_.SplitterCV.splitter data-toc-label="splitter" }
  - splitter_cls <span class="dobjtype">class property</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/generic/splitting/sklearn_.py#L114-L123" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.generic.splitting.sklearn_.SplitterCV.splitter_cls data-toc-label="splitter\_cls" }
  - splitter_kwargs <span class="dobjtype">class property</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/generic/splitting/sklearn_.py#L125-L132" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.generic.splitting.sklearn_.SplitterCV.splitter_kwargs data-toc-label="splitter\_kwargs" }
  - template_context <span class="dobjtype">class property</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/generic/splitting/sklearn_.py#L162-L169" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.generic.splitting.sklearn_.SplitterCV.template_context data-toc-label="template\_context" }

Module providing a Scikit-learn compatible cross-validator for data splitting.

Class representing a scikit-learn compatible cross-validator based on [Splitter](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter").

**```splitter```** :&ensp;`Union[None, str, Splitter, Callable]` :   Splitter instance, the name of a factory method (e.g. "from*n*rolling"), or the factory method itself.

**```splitter_cls```** :&ensp;`Optional[Type[Splitter]]` :   Splitter class to use.

**```split*group*by```** :&ensp;`AnyGroupByLike` :   Grouping specification for defining splits.

**```set*group*by```** :&ensp;`AnyGroupByLike` :   Grouping specification for defining sets.

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```**splitter_kwargs```** :   Keyword arguments for the splitter factory method.

Replicate `TimeSeriesSplit` from scikit-learn:

**Inherited members**

Return the number of splitting iterations in the cross-validator.

**```X```** :&ensp;`Any` :   Input data.

**```y```** :&ensp;`Any` :   Target values.

**```groups```** :&ensp;`Any` :   Group labels.

`int` :   Number of splits provided by the splitter.

Return a splitter instance of type [Splitter](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter").

!!! note If the splitter is provided as a string, it is resolved as an attribute of the splitter class.

**```X```** :&ensp;`Any` :   Input data for splitting.

**```y```** :&ensp;`Any` :   Target values corresponding to `X`.

**```groups```** :&ensp;`Any` :   Group labels.

`Splitter` :   Splitter object configured with the provided data and splitter parameters.

Group labels for setting.

Not passed to the factory method.

[BaseIDXAccessor.get*grouper](https://vectorbt.pro/pvt*ff8edc14/api/base/accessors/#vectorbtpro.base.accessors.BaseIDXAccessor.get*grouper "vectorbtpro.base.accessors.BaseIDXAccessor.get*grouper")

`AnyGroupByLike` :   Group labels for setting.

Generate indices to split data into training and test sets.

**```X```** :&ensp;`Any` :   Input data.

**```y```** :&ensp;`Any` :   Target values.

**```groups```** :&ensp;`Any` :   Group labels.

`Iterator[Tuple[Array1d, Array1d]]` :   Iterator yielding tuples of train and test indices.

Group labels for splitting.

Not passed to the factory method.

[BaseIDXAccessor.get*grouper](https://vectorbt.pro/pvt*ff8edc14/api/base/accessors/#vectorbtpro.base.accessors.BaseIDXAccessor.get*grouper "vectorbtpro.base.accessors.BaseIDXAccessor.get*grouper")

`AnyGroupByLike` :   Group labels for splitting.

Splitter instance, factory name, or factory function used for splitting.

If None, it is determined automatically based on [SplitterCV.splitter*kwargs](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/sklearn*/#vectorbtpro.generic.splitting.sklearn*.SplitterCV.splitter*kwargs "vectorbtpro.generic.splitting.sklearn*.SplitterCV.splitter_kwargs").

`Union[str, Splitter, Callable]` :   Splitter instance or factory.

Splitter class used as the factory for creating splitter instances.

Defaults to [Splitter](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter").

`Type[Splitter]` :   Splitter class used for creating splitter instances.

Keyword arguments for the splitter factory method.

`KwargsLike` :   Keyword arguments for the splitter factory method.

Additional context for template substitution.

`KwargsLike` :   Dictionary of context variables for template substitution.

**Examples:**

Example 1 (python):
```python
SplitterCV(
    splitter=None,
    *,
    splitter_cls=None,
    split_group_by=None,
    set_group_by=None,
    template_context=None,
    **splitter_kwargs
)
```

Example 2 (text):
```text
If None, the appropriate splitter is determined using
[Splitter.guess_method](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.guess_method "vectorbtpro.generic.splitting.base.Splitter.guess_method").
```

Example 3 (text):
```text
Defaults to [Splitter](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter").
```

Example 4 (text):
```text
See [BaseIDXAccessor.get_grouper](https://vectorbt.pro/pvt_ff8edc14/api/base/accessors/#vectorbtpro.base.accessors.BaseIDXAccessor.get_grouper "vectorbtpro.base.accessors.BaseIDXAccessor.get_grouper").
```

---

## base

**URL:** https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base.md

**Contents:**
- FixRange <span class="dobjtype">class</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/generic/splitting/base.py#L55-L60" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.generic.splitting.base.FixRange data-toc-label="FixRange" }
  - range_ <span class="dobjtype">field</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/generic/splitting/base.py#L59-L60" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.generic.splitting.base.FixRange.range_ data-toc-label="range\_" }
- RelRange <span class="dobjtype">class</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/generic/splitting/base.py#L63-L317" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.generic.splitting.base.RelRange data-toc-label="RelRange" }
  - is_gap <span class="dobjtype">field</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/generic/splitting/base.py#L132-L133" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.generic.splitting.base.RelRange.is_gap data-toc-label="is\_gap" }
  - length <span class="dobjtype">field</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/generic/splitting/base.py#L100-L106" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.generic.splitting.base.RelRange.length data-toc-label="length" }
  - length_space <span class="dobjtype">field</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/generic/splitting/base.py#L108-L119" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.generic.splitting.base.RelRange.length_space data-toc-label="length\_space" }
  - offset <span class="dobjtype">field</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/generic/splitting/base.py#L67-L73" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.generic.splitting.base.RelRange.offset data-toc-label="offset" }
  - offset_anchor <span class="dobjtype">field</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/generic/splitting/base.py#L75-L86" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.generic.splitting.base.RelRange.offset_anchor data-toc-label="offset\_anchor" }
  - offset_space <span class="dobjtype">field</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/generic/splitting/base.py#L88-L98" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.generic.splitting.base.RelRange.offset_space data-toc-label="offset\_space" }
  - out_of_bounds <span class="dobjtype">field</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/generic/splitting/base.py#L121-L130" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.generic.splitting.base.RelRange.out_of_bounds data-toc-label="out\_of\_bounds" }

Module providing base functionality for splitting.

Class representing a fixed range.

**Inherited members**

Class representing a relative range.

**Inherited members**

Indicates whether the range represents a gap.

Floating numbers between 0 and 1 are interpreted as relative.

Space used for applying the relative length.

Applied only when [RelRange.length](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.RelRange.length "vectorbtpro.generic.splitting.base.RelRange.length") is relative.

Floating numbers between 0 and 1 are interpreted as relative.

Anchor used for offset.

Space used for applying the relative offset.

Applied only when [RelRange.offset](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.RelRange.offset "vectorbtpro.generic.splitting.base.RelRange.offset") is relative.

Strategy for handling indices that are out of bounds.

Convert the relative range to a slice.

**```total_len```** :&ensp;`int` :   Total number of indices.

**```prev_start```** :&ensp;`int` :   Start index of the previous range.

**```prev_end```** :&ensp;`int` :   End index of the previous range.

**```index```** :&ensp;`Optional[IndexLike]` :   Index from which to derive datetime information.

**```freq```** :&ensp;`Optional[FrequencyLike]` :   Frequency of the index (e.g., "daily", "15 min", "index_mean").

`slice` :   Slice object computed based on the relative range parameters.

Base class for splitting.

!!! info For default settings, see [splitter](https://vectorbt.pro/pvt*ff8edc14/api/*settings/#vectorbtpro.*settings.splitter "vectorbtpro.*settings.splitter").

**```wrapper```** :&ensp;`ArrayWrapper` :   Array wrapper instance.

**```index```** :&ensp;`Index` :   Index used for splitting.

**```splits_arr```** :&ensp;`SplitsArray` :   2D array representing splits.

**```**kwargs```** :   Keyword arguments for [Analyzable](https://vectorbt.pro/pvt_ff8edc14/api/generic/analyzable/#vectorbtpro.generic.analyzable.Analyzable "vectorbtpro.generic.analyzable.Analyzable").

**Inherited members**

Apply a function over each data range.

Divides the index into ranges based on selected splits and sets, optionally grouping using `split*group*by` and `set*group*by`. For each combination of split and set, retrieves the corresponding range via [Splitter.select*range](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.select*range "vectorbtpro.generic.splitting.base.Splitter.select*range") and [Splitter.get*ready*range](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*ready*range "vectorbtpro.generic.splitting.base.Splitter.get*ready*range"). Positional and keyword arguments that are instances of [Takeable](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Takeable "vectorbtpro.generic.splitting.base.Takeable") are sliced based on these ranges using [Splitter.take*range](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.take*range "vectorbtpro.generic.splitting.base.Splitter.take*range"). Before slicing, the range into each object's index using [Splitter.get*ready*obj*range](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*ready*obj*range "vectorbtpro.generic.splitting.base.Splitter.get*ready*obj*range"). The function and its arguments are then template-substituted and scheduled for execution via [execute](https://vectorbt.pro/pvt*ff8edc14/api/utils/execution/#vectorbtpro.utils.execution.execute "vectorbtpro.utils.execution.execute"). After execution, the results are optionally merged using `merge*func` and wrapped in a Pandas object if specified.

Template substitution variables include:

Iteration over ranges is controlled by the `iteration` parameter:

**```apply_func```** :&ensp;`Callable` :   Function to apply over each range.

**```*apply*args```** :   Positional arguments for `apply*func`.

**```split```** :&ensp;`Optional[Selection]` :   Selection criteria for splits.

**```set_```** :&ensp;`Optional[Selection]` :   Selection criteria for sets.

**```split*group*by```** :&ensp;`AnyGroupByLike` :   Grouping specification for defining splits.

**```set*group*by```** :&ensp;`AnyGroupByLike` :   Grouping specification for defining sets.

**```squeeze*one*split```** :&ensp;`bool` :   Whether to squeeze the output if only one split exists.

**```squeeze*one*set```** :&ensp;`bool` :   Whether to squeeze the output if only one set exists.

**```remap*to*obj```** :&ensp;`bool` :   Whether to remap the range to the object's index.

**```obj_index```** :&ensp;`Optional[IndexLike]` :   Target index for remapping, if available.

**```obj*freq```** :&ensp;`Optional[FrequencyLike]` :   Frequency of the target index (e.g., "daily", "15 min", "index*mean").

**```range_format```** :&ensp;`str` :   Format of the returned range.

**```point_wise```** :&ensp;`bool` :   Whether to perform point-wise range extraction.

**```attach_bounds```** :&ensp;`Union[bool, str]` :   Specifies if and how to attach bounds to the result.

**```right_inclusive```** :&ensp;`bool` :   Whether the right bound is inclusive.

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```silence_warnings```** :&ensp;`bool` :   Flag to suppress warning messages.

**```index*combine*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for combining indexes.

**```freq```** :&ensp;`Optional[FrequencyLike]` :   Frequency of the index (e.g., "daily", "15 min", "index_mean").

**```iteration```** :&ensp;`str` :   Iteration mode over ranges.

**```execute_kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for the execution handler.

**```filter*results```** :&ensp;`bool` :   Whether to filter out results that are [NoResult](https://vectorbt.pro/pvt*ff8edc14/api/utils/execution/#vectorbtpro.utils.execution.NoResult "vectorbtpro.utils.execution.NoResult").

**```raise*no*results```** :&ensp;`bool` :   Flag indicating whether to raise a [NoResultsException](https://vectorbt.pro/pvt_ff8edc14/api/utils/execution/#vectorbtpro.utils.execution.NoResultsException "vectorbtpro.utils.execution.NoResultsException") exception if no results remain.

**```merge_func```** :&ensp;`MergeFuncLike` :   Function to merge the results.

**```merge*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for `merge*func`.

**```merge_all```** :&ensp;`bool` :   Whether to merge all results across iterations regardless of the iteration mode.

**```wrap_results```** :&ensp;`bool` :   Whether to wrap the final merged result in a Pandas object.

**```eval_id```** :&ensp;`Optional[Hashable]` :   Evaluation identifier.

**```**apply*kwargs```** :   Keyword arguments for `apply*func`.

`Any` :   Result of applying `apply_func` over each range, which may be a merged result, a Pandas Series, or a tuple of Pandas objects depending on the processing and output wrapping options.

Get the return of each data range:

The same but by indexing manually:

Divide into two windows, each consisting of 50% train and 50% test, compute SMA for each range, and row-stack the outputs of each set upon merging:

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/api/Splitter*apply.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/api/Splitter*apply.dark.svg#only-dark){: .iimg loading=lazy }

Bounds by calling [Splitter.get*bounds](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*bounds "vectorbtpro.generic.splitting.base.Splitter.get*bounds") with default arguments.

`Frame` :   Pandas DataFrame with the bounds.

Property returning the 3D bounds array.

This property obtains the bounds array by calling [Splitter.get*bounds*arr](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*bounds*arr "vectorbtpro.generic.splitting.base.Splitter.get*bounds_arr") with default parameters.

`BoundsArray` :   3D array of bounds.

Divide each split into multiple sub-splits using a new splitting specification.

!!! note Ensure that there is only one set before breaking up splits. Merge multiple sets into one if necessary.

**```new_split```** :&ensp;`SplitLike` :   Specification for splitting ranges.

**```sort```** :&ensp;`bool` :   Whether to sort the resulting splits by their starting boundaries.

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```wrapper_kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for configuring the wrapper.

**```init_kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for updating the splitter.

**```**split*range*kwargs```** :   Keyword arguments for [Splitter.split*range](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.split*range "vectorbtpro.generic.splitting.base.Splitter.split*range").

[Splitter](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") :   New splitter instance with updated splits.

Stack multiple [Splitter](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") instances along columns.

Stack multiple [Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") instances by stacking their wrappers along columns using [ArrayWrapper.column*stack](https://vectorbt.pro/pvt*ff8edc14/api/base/wrapping/#vectorbtpro.base.wrapping.ArrayWrapper.column*stack "vectorbtpro.base.wrapping.ArrayWrapper.column_stack").

**```*objs```** :&ensp;`MaybeSequence[Splitter]` :   (Additional) [Splitter](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") instances to stack.

**```wrapper_kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for configuring the wrapper.

**```**kwargs```** :   Keyword arguments for [Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") through [Splitter.resolve*column*stack*kwargs](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.resolve*column*stack*kwargs "vectorbtpro.generic.splitting.base.Splitter.resolve*column*stack*kwargs") and [Wrapping.resolve*stack*kwargs](https://vectorbt.pro/pvt*ff8edc14/api/base/wrapping/#vectorbtpro.base.wrapping.Wrapping.resolve*stack*kwargs "vectorbtpro.generic.splitting.base.Splitter.resolve*stack*kwargs").

[Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") :   New [Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") instance with column-stacked wrappers.

Coverage computed using default parameters from [Splitter.get*coverage](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*coverage "vectorbtpro.generic.splitting.base.Splitter.get*coverage").

`float` :   Coverage value.

Duration by calling [Splitter.get*duration](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*duration "vectorbtpro.generic.splitting.base.Splitter.get*duration") with default arguments.

`Series` :   Pandas Series of durations.

Create a [Splitter](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") instance from an expanding range.

Creates an expanding sequence of slices based on the provided index. The first slice uses a minimum length defined by min_length, and each subsequent slice begins after an offset from the previous slice's right boundary.

**```index```** :&ensp;`IndexLike` :   Index to split.

**```min_length```** :&ensp;`Union[int, float, TimedeltaLike]` :   Minimum length for the first expanding range. If specified as a float between 0 and 1, it is interpreted relative to the length of the index.

**```offset```** :&ensp;`Union[int, float, TimedeltaLike]` :   Offset after the previous range's right boundary to determine the start of the next range.

**```split```** :&ensp;`Optional[SplitLike]` :   Specification for further splitting of each range.

**```split*range*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for range splitting.

**```range*bounds*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for getting range bounds.

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```freq```** :&ensp;`Optional[FrequencyLike]` :   Frequency of the index (e.g., "daily", "15 min", "index_mean").

**```**kwargs```** :   Keyword arguments for [Splitter.from*splits](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.from*splits "vectorbtpro.generic.splitting.base.Splitter.from*splits").

[Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") :   New [Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") instance.

Roll an expanding range with a length of 10 and an offset of 10, and split it into 3/4:

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/api/from*expanding.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/api/from*expanding.dark.svg#only-dark){: .iimg loading=lazy }

Create a [Splitter](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") instance from a grouper.

Uses [BaseIDXAccessor.get*grouper](https://vectorbt.pro/pvt*ff8edc14/api/base/accessors/#vectorbtpro.base.accessors.BaseIDXAccessor.get*grouper "vectorbtpro.base.accessors.BaseIDXAccessor.get*grouper") to group the index and generate splits. Each group's indices may be adjusted using the provided `split` specification before being passed to [Splitter.from*splits](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.from*splits "vectorbtpro.generic.splitting.base.Splitter.from*splits") to build the instance.

**```index```** :&ensp;`IndexLike` :   Index to be grouped and split.

**```by```** :&ensp;`AnyGroupByLike` :   Grouper-like specification.

**```groupby_kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for `pandas.Series.groupby` and `pandas.Series.resample` methods.

**```grouper_kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for constructing the grouper.

**```split```** :&ensp;`Optional[SplitLike]` :   Specification for further splitting of each range.

**```split*range*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for range splitting.

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```split_labels```** :&ensp;`Optional[IndexLike]` :   Labels for the splits.

**```freq```** :&ensp;`Optional[FrequencyLike]` :   Frequency of the index (e.g., "daily", "15 min", "index_mean").

**```**kwargs```** :   Keyword arguments for [Splitter.from*splits](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.from*splits "vectorbtpro.generic.splitting.base.Splitter.from*splits").

[Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") :   New [Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") instance.

Map each month into a range:

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/api/from*grouper.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/api/from*grouper.dark.svg#only-dark){: .iimg loading=lazy }

Create a [Splitter](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") instance from multiple expanding ranges.

Selects n evenly spaced expanding ranges based on the given index. Each range uses a minimum length specified by min_length, which is automatically computed if not provided. An optional split configuration can be applied to transform each range.

**```index```** :&ensp;`IndexLike` :   Index to split.

**```n```** :&ensp;`int` :   Number of expanding ranges to select.

**```min_length```** :&ensp;`Union[None, int, float, TimedeltaLike]` :   Minimum length for each expanding range.

**```split```** :&ensp;`Optional[SplitLike]` :   Specification for further splitting of each range.

**```split*range*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for range splitting.

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```freq```** :&ensp;`Optional[FrequencyLike]` :   Frequency of the index (e.g., "daily", "15 min", "index_mean").

**```**kwargs```** :   Keyword arguments for [Splitter.from*splits](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.from*splits "vectorbtpro.generic.splitting.base.Splitter.from*splits").

[Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") :   New [Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") instance.

Roll 10 expanding ranges with a minimum length of 100, while reserving 50 elements for test:

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/api/from*n*expanding.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/api/from*n*expanding.dark.svg#only-dark){: .iimg loading=lazy }

Create a [Splitter](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") instance with randomly generated ranges.

Generate random ranges by selecting a range length and a start position. The range length is chosen between `min*length` and `max*length` (inclusive) using `length*choice*func`, which selects one value from the candidate lengths. Optionally, `length*p*func` returns probability weights for the length selection.

The start position is selected from positions between `min*start` and `max*end` (adjusted to accommodate the chosen range length) using `start*choice*func`. Optionally, `start*p*func` returns probability weights for the start selection.

!!! note Both choice functions must accept two arguments: the iteration index and the array of possible values.

**```index```** :&ensp;`IndexLike` :   Index from which ranges are generated.

**```n```** :&ensp;`int` :   Number of random ranges to generate.

**```min_length```** :&ensp;`Union[int, float, TimedeltaLike]` :   Minimum length for each range.

**```max*length```** :&ensp;`Union[None, int, float, TimedeltaLike]` :   Maximum length for each range. If not provided, it defaults to the same value as `min*length`.

**```min_start```** :&ensp;`Union[None, int, float, DatetimeLike]` :   Minimum allowable start position for a range.

**```max_end```** :&ensp;`Union[None, int, float, DatetimeLike]` :   Maximum allowable end position for a range.

**```length*choice*func```** :&ensp;`Optional[Callable]` :   Function to select a range length from candidate values.

**```start*choice*func```** :&ensp;`Optional[Callable]` :   Function to select a start position from candidate values.

**```length*p*func```** :&ensp;`Optional[Callable]` :   Function that returns probability weights for the length selection.

**```start*p*func```** :&ensp;`Optional[Callable]` :   Function that returns probability weights for the start selection.

**```seed```** :&ensp;`Optional[int]` :   Random seed for deterministic output.

**```split```** :&ensp;`Optional[SplitLike]` :   Specification for further splitting of each range.

**```split*range*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for range splitting.

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```freq```** :&ensp;`Optional[FrequencyLike]` :   Frequency of the index (e.g., "daily", "15 min", "index_mean").

**```**kwargs```** :   Keyword arguments for [Splitter.from*splits](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.from*splits "vectorbtpro.generic.splitting.base.Splitter.from*splits").

[Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") :   New [Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") instance.

Generate 20 random ranges with a length from [40, 100], and split each into 3/4:

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/api/from*n*random.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/api/from*n*random.dark.svg#only-dark){: .iimg loading=lazy }

Create a Splitter instance from a fixed number of rolling ranges with equal length.

**```index```** :&ensp;`IndexLike` :   Index used to generate rolling ranges.

**```n```** :&ensp;`int` :   Number of rolling ranges to generate.

**```length```** :&ensp;`Union[None, str, int, float, TimedeltaLike]` :   Length of each range.

**```optimize*anchor*set```** :&ensp;`int` :   Specifies which anchor set to optimize when using `length="optimize"`.

**```split```** :&ensp;`Optional[SplitLike]` :   Specification for further splitting of each range.

**```split*range*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for range splitting.

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```freq```** :&ensp;`Optional[FrequencyLike]` :   Frequency of the index (e.g., "daily", "15 min", "index_mean").

**```**kwargs```** :   Keyword arguments for [Splitter.from*rolling](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.from*rolling "vectorbtpro.generic.splitting.base.Splitter.from*rolling") if `length` is None or "optimize", or [Splitter.from*splits](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.from*splits "vectorbtpro.generic.splitting.base.Splitter.from*splits").

[Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") :   New [Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") instance.

Roll 10 ranges with 100 elements, and split it into 3/4:

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/api/from*n*rolling.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/api/from*n*rolling.dark.svg#only-dark){: .iimg loading=lazy }

Create a [Splitter](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") instance using a purged cross-validator.

**```index```** :&ensp;`IndexLike` :   Index representing the dataset.

**```purged*splitter```** :&ensp;`BasePurgedCV` :   Purged cross-validation splitter instance from [vectorbtpro.generic.splitting.purged](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/purged/ "vectorbtpro.generic.splitting.purged").

**```pred_times```** :&ensp;`Union[None, Index, Series]` :   Indices for prediction times.

**```eval_times```** :&ensp;`Union[None, Index, Series]` :   Indices for evaluation times.

**```split_labels```** :&ensp;`Optional[IndexLike]` :   Labels for the splits.

**```set_labels```** :&ensp;`Optional[IndexLike]` :   Labels for the training and testing sets.

**```**kwargs```** :   Keyword arguments for [Splitter.from*splits](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.from*splits "vectorbtpro.generic.splitting.base.Splitter.from*splits").

[Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") :   New [Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") instance.

Create a [Splitter](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") instance using a purged K-fold cross-validator.

**```index```** :&ensp;`IndexLike` :   Index representing the dataset.

**```n_folds```** :&ensp;`int` :   Total number of folds.

**```n*test*folds```** :&ensp;`int` :   Total number of folds allocated for testing.

**```purge_td```** :&ensp;`TimedeltaLike` :   Time delta used for purging between splits.

**```embargo_td```** :&ensp;`TimedeltaLike` :   Time interval defining the embargo period between test set evaluation times and training predictions.

**```pred_times```** :&ensp;`Union[None, Index, Series]` :   Indices for prediction times.

**```eval_times```** :&ensp;`Union[None, Index, Series]` :   Indices for evaluation times.

**```**kwargs```** :   Keyword arguments for [Splitter.from*purged](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.from*purged "vectorbtpro.generic.splitting.base.Splitter.from*purged").

[Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") :   New [Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") instance.

Create a [Splitter](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") instance using a purged walk-forward cross-validator.

**```index```** :&ensp;`IndexLike` :   Index representing the dataset.

**```n_folds```** :&ensp;`int` :   Total number of folds.

**```n*test*folds```** :&ensp;`int` :   Total number of folds allocated for testing.

**```min*train*folds```** :&ensp;`int` :   Minimum number of consecutive folds to use for training preceding the test set.

**```max*train*folds```** :&ensp;`Optional[int]` :   Maximum number of consecutive folds to use for training preceding the test set.

**```split*by*time```** :&ensp;`bool` :   Whether to partition folds based on equal time intervals using prediction times.

**```purge_td```** :&ensp;`TimedeltaLike` :   Time delta used for purging between folds.

**```pred_times```** :&ensp;`Union[None, Index, Series]` :   Indices for prediction times.

**```eval_times```** :&ensp;`Union[None, Index, Series]` :   Indices for evaluation times.

**```**kwargs```** :   Keyword arguments for [Splitter.from*purged](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.from*purged "vectorbtpro.generic.splitting.base.Splitter.from*purged").

[Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") :   New [Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") instance.

Create a [Splitter](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") instance from ranges.

Uses [get*index*ranges](https://vectorbt.pro/pvt*ff8edc14/api/base/indexing/#vectorbtpro.base.indexing.get*index*ranges "vectorbtpro.base.indexing.get*index*ranges") to generate start and end indices for splitting the index. Keyword arguments relevant to index range generation are extracted from `**kwargs`, while the remaining ones are passed to [Splitter.from*splits](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.from*splits "vectorbtpro.generic.splitting.base.Splitter.from_splits").

**```index```** :&ensp;`IndexLike` :   Index to be divided into ranges.

**```split```** :&ensp;`Optional[SplitLike]` :   Specification for further splitting of each range.

**```split*range*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for range splitting.

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```**kwargs```** :   Keyword arguments distributed between [get*index*ranges](https://vectorbt.pro/pvt*ff8edc14/api/base/indexing/#vectorbtpro.base.indexing.get*index*ranges "vectorbtpro.base.indexing.get*index*ranges") and [Splitter.from*splits](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.from*splits "vectorbtpro.generic.splitting.base.Splitter.from_splits").

[Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") :   New [Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") instance.

Translate each quarter into a range:

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/api/from*ranges*1.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/api/from*ranges*1.dark.svg#only-dark){: .iimg loading=lazy }

In addition to the above, reserve the last month for testing purposes:

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/api/from*ranges*2.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/api/from*ranges*2.dark.svg#only-dark){: .iimg loading=lazy }

Create a [Splitter](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") instance from a rolling range of fixed length.

Uses [Splitter.from*splits](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.from*splits "vectorbtpro.generic.splitting.base.Splitter.from*splits") to generate an array of splits and corresponding labels, and then construct the [Splitter](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") instance.

**```index```** :&ensp;`IndexLike` :   Index over which the rolling range is computed.

**```length```** :&ensp;`Union[int, float, TimedeltaLike]` :   Desired length of the rolling range.

**```offset```** :&ensp;`Union[int, float, TimedeltaLike]` :   Offset after the previous range's right boundary to determine the start of the next range.

**```offset_anchor```** :&ensp;`str` :   Anchor point used when applying the offset.

**```offset*anchor*set```** :&ensp;`Optional[int]` :   Index of the set from the previous range used as the offset anchor.

**```offset_space```** :&ensp;`str` :   Type of offset space.

**```backwards```** :&ensp;`Union[bool, str]` :   Determines whether rolling occurs in reverse order.

**```split```** :&ensp;`Optional[SplitLike]` :   Specification for further splitting of each range.

**```split*range*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for range splitting.

**```range*bounds*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for getting range bounds.

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```freq```** :&ensp;`Optional[FrequencyLike]` :   Frequency of the index (e.g., "daily", "15 min", "index_mean").

**```**kwargs```** :   Keyword arguments for [Splitter.from*splits](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.from*splits "vectorbtpro.generic.splitting.base.Splitter.from*splits").

[Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") :   New [Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") instance.

Divide a range into a set of non-overlapping ranges:

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/api/from*rolling*1.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/api/from*rolling*1.dark.svg#only-dark){: .iimg loading=lazy }

Divide a range into ranges, each split into 1/2:

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/api/from*rolling*2.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/api/from*rolling*2.dark.svg#only-dark){: .iimg loading=lazy }

Create non-overlapping ranges by using the right bound of the last set as an offset anchor:

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/api/from*rolling*3.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/api/from*rolling*3.dark.svg#only-dark){: .iimg loading=lazy }

Create a [Splitter](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") instance from a single split.

**```index```** :&ensp;`IndexLike` :   Index used for the split.

**```split```** :&ensp;`Optional[SplitLike]` :   Specification for further splitting of each range.

**```split*range*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for range splitting.

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```**kwargs```** :   Keyword arguments for [Splitter.from*splits](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.from*splits "vectorbtpro.generic.splitting.base.Splitter.from*splits").

[Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") :   New [Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") instance.

Create a [Splitter](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") instance using a scikit-learn cross-validator.

**```index```** :&ensp;`IndexLike` :   Index representing the dataset.

**```skl_splitter```** :&ensp;`BaseCrossValidator` :   Scikit-learn splitter instance.

**```groups```** :&ensp;`Optional[ArrayLike]` :   Group labels for the splitting process.

**```split_labels```** :&ensp;`Optional[IndexLike]` :   Labels for the splits.

**```set_labels```** :&ensp;`Optional[IndexLike]` :   Labels for the training and testing sets.

**```**kwargs```** :   Keyword arguments for [Splitter.from*splits](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.from*splits "vectorbtpro.generic.splitting.base.Splitter.from*splits").

[Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") :   New [Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") instance.

Create a [Splitter](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") instance from a custom split function.

This method repeatedly calls `split*func` with substituted templates in `split*args` and `split*kwargs`. The function should return a split or a single range (if not iterable) or None to terminate the loop. When `fix*ranges` is True or if `split` is provided, the returned split is processed using [Splitter.split*range](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.split*range "vectorbtpro.generic.splitting.base.Splitter.split*range") and its bounds are determined via [Splitter.get*range*bounds](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*range*bounds "vectorbtpro.generic.splitting.base.Splitter.get*range_bounds").

Template substitutions have access to the following:

**```index```** :&ensp;`IndexLike` :   Index used for splitting.

**```split_func```** :&ensp;`Callable` :   Function that returns a new split based on substituted arguments.

**```split*args```** :&ensp;`ArgsLike` :   Positional arguments for `split*func`.

**```split*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for `split*func`.

**```fix*ranges```** :&ensp;`bool` :   Whether to convert relative ranges ([RelRange](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.RelRange "vectorbtpro.generic.splitting.base.RelRange")) into fixed ([FixRange](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.FixRange "vectorbtpro.generic.splitting.base.FixRange")).

**```split```** :&ensp;`Optional[SplitLike]` :   Specification for further splitting of each range.

**```split*range*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for range splitting.

**```range*bounds*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for getting range bounds.

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```freq```** :&ensp;`Optional[FrequencyLike]` :   Frequency of the index (e.g., "daily", "15 min", "index_mean").

**```**kwargs```** :   Keyword arguments for [Splitter.from*splits](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.from*splits "vectorbtpro.generic.splitting.base.Splitter.from*splits").

[Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") :   New [Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") instance.

Rolling window of 30 elements, 20 for train and 10 for test:

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/api/from*split*func.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/api/from*split*func.dark.svg#only-dark){: .iimg loading=lazy }

Create a [Splitter](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") instance from an iterable of splits.

**```index```** :&ensp;`IndexLike` :   Index used to align the splits.

**```splits```** :&ensp;`Splits` :   Iterable of splits supporting both absolute and relative ranges.

**```squeeze```** :&ensp;`bool` :   Flag indicating whether to convert a single-column DataFrame to a Series.

**```fix*ranges```** :&ensp;`bool` :   Whether to convert relative ranges ([RelRange](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.RelRange "vectorbtpro.generic.splitting.base.RelRange")) into fixed ([FixRange](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.FixRange "vectorbtpro.generic.splitting.base.FixRange")).

**```wrap*with*fixrange```** :&ensp;`bool` :   Wrap fixed ranges with [FixRange](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.FixRange "vectorbtpro.generic.splitting.base.FixRange").

**```split*range*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for range splitting.

**```split*check*template```** :&ensp;`Optional[CustomTemplate]` :   Template to validate each split.

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```split_labels```** :&ensp;`Optional[IndexLike]` :   Labels for the splits.

**```set_labels```** :&ensp;`Optional[IndexLike]` :   Labels for the sets.

**```wrapper_kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for configuring the wrapper.

**```**kwargs```** :   Keyword arguments for [Splitter](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter").

[Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") :   New [Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") instance.

Return a Series or DataFrame containing the start and end bounds.

**```index_bounds```** :&ensp;`bool` :   If True, map the bounds to the provided index.

**```right_inclusive```** :&ensp;`bool` :   Whether the right bound is inclusive.

**```split*group*by```** :&ensp;`AnyGroupByLike` :   Grouping specification for defining splits.

**```set*group*by```** :&ensp;`AnyGroupByLike` :   Grouping specification for defining sets.

**```squeeze*one*split```** :&ensp;`bool` :   Whether to squeeze the output if only one split exists.

**```squeeze*one*set```** :&ensp;`bool` :   Whether to squeeze the output if only one set exists.

**```index*combine*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for combining indexes.

**```**kwargs```** :   Keyword arguments for [Splitter.get*bounds*arr](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*bounds*arr "vectorbtpro.generic.splitting.base.Splitter.get*bounds_arr").

`SeriesFrame` :   Pandas Series or DataFrame with index based on grouping and columns ['start', 'end'].

Return a 3D array of bounds.

The array dimensions are:

Each range is selected using [Splitter.select*range](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.select*range "vectorbtpro.generic.splitting.base.Splitter.select*range") and processed using [Splitter.get*range*bounds](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*range*bounds "vectorbtpro.generic.splitting.base.Splitter.get*range*bounds"). Keyword arguments are passed to [Splitter.get*range*bounds](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*range*bounds "vectorbtpro.generic.splitting.base.Splitter.get*range*bounds").

**```index_bounds```** :&ensp;`bool` :   If True, map the bounds to the provided index.

**```right_inclusive```** :&ensp;`bool` :   Whether the right bound is inclusive.

**```split*group*by```** :&ensp;`AnyGroupByLike` :   Grouping specification for defining splits.

**```set*group*by```** :&ensp;`AnyGroupByLike` :   Grouping specification for defining sets.

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```**range*bounds*kwargs```** :   Keyword arguments for [Splitter.get*range*bounds](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*range*bounds "vectorbtpro.generic.splitting.base.Splitter.get*range_bounds").

`BoundsArray` :   3D array containing the bounds.

Get the coverage of the entire mask.

**```overlapping```** :&ensp;`bool` :   Flag to compute overlapping coverage by counting overlapping True values.

**```normalize```** :&ensp;`bool` :   Flag to normalize the coverage relative to the index length.

**```split*group*by```** :&ensp;`AnyGroupByLike` :   Grouping specification for defining splits.

**```set*group*by```** :&ensp;`AnyGroupByLike` :   Grouping specification for defining sets.

**```**kwargs```** :   Keyword arguments for [Splitter.get*mask*arr](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*mask*arr "vectorbtpro.generic.splitting.base.Splitter.get*mask_arr").

`float` :   Coverage value computed based on the provided mask and parameters.

Return a Series representing the duration computed as the difference between the 'end' and 'start' bounds.

**```**kwargs```** :   Keyword arguments for [Splitter.get*bounds](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*bounds "vectorbtpro.generic.splitting.base.Splitter.get*bounds").

`Series` :   Pandas Series of durations.

Yield 2D boolean arrays for each set.

Each array has rows representing splits and columns representing index positions.

**```split*group*by```** :&ensp;`AnyGroupByLike` :   Grouping specification for defining splits.

**```set*group*by```** :&ensp;`AnyGroupByLike` :   Grouping specification for defining sets.

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```**kwargs```** :   Keyword arguments for [Splitter.get*range*mask](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*range*mask "vectorbtpro.generic.splitting.base.Splitter.get*range_mask").

`Iterator[Array2d]` :   Iterator over 2D boolean arrays.

Yield boolean DataFrames for each set.

Each DataFrame is constructed by transposing the mask array and applying appropriate index and split labels.

**```split*group*by```** :&ensp;`AnyGroupByLike` :   Grouping specification for defining splits.

**```set*group*by```** :&ensp;`AnyGroupByLike` :   Grouping specification for defining sets.

**```**kwargs```** :   Keyword arguments for [Splitter.get*iter*set*mask*arrs](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*iter*set*mask*arrs "vectorbtpro.generic.splitting.base.Splitter.get*iter*set*mask_arrs").

`Iterator[Frame]` :   Iterator over boolean DataFrames.

Yield 2D boolean arrays for each split.

Each array has rows representing sets and columns representing index positions.

**```split*group*by```** :&ensp;`AnyGroupByLike` :   Grouping specification for defining splits.

**```set*group*by```** :&ensp;`AnyGroupByLike` :   Grouping specification for defining sets.

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```**kwargs```** :   Keyword arguments for [Splitter.get*range*mask](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*range*mask "vectorbtpro.generic.splitting.base.Splitter.get*range_mask").

`Iterator[Array2d]` :   Iterator over 2D boolean arrays.

Yield boolean DataFrames for each split.

Each DataFrame is constructed by transposing the mask array and applying appropriate index and set labels.

**```split*group*by```** :&ensp;`AnyGroupByLike` :   Grouping specification for defining splits.

**```set*group*by```** :&ensp;`AnyGroupByLike` :   Grouping specification for defining sets.

**```**kwargs```** :   Keyword arguments for [Splitter.get*iter*split*mask*arrs](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*iter*split*mask*arrs "vectorbtpro.generic.splitting.base.Splitter.get*iter*split*mask_arrs").

`Iterator[Frame]` :   Iterator over boolean DataFrames.

Return a boolean Series or DataFrame representing the split mask.

The returned object uses [Splitter.index](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.index "vectorbtpro.generic.splitting.base.Splitter.index") as the index and contains the splits as columns.

!!! warning Boolean arrays for a high number of splits may consume substantial memory.

**```split*group*by```** :&ensp;`AnyGroupByLike` :   Grouping specification for defining splits.

**```set*group*by```** :&ensp;`AnyGroupByLike` :   Grouping specification for defining sets.

**```squeeze*one*split```** :&ensp;`bool` :   Whether to squeeze the output if only one split exists.

**```squeeze*one*set```** :&ensp;`bool` :   Whether to squeeze the output if only one set exists.

**```index*combine*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for combining indexes.

**```**kwargs```** :   Keyword arguments for [Splitter.get*mask*arr](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*mask*arr "vectorbtpro.generic.splitting.base.Splitter.get*mask_arr").

`SeriesFrame` :   Pandas Series or DataFrame representing the split mask.

Return a 3D boolean array representing splits.

The first dimension corresponds to splits, the second to sets, and the third to the index.

**```split*group*by```** :&ensp;`AnyGroupByLike` :   Grouping specification for defining splits.

**```set*group*by```** :&ensp;`AnyGroupByLike` :   Grouping specification for defining sets.

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```**kwargs```** :   Keyword arguments for [Splitter.get*iter*split*mask*arrs](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*iter*split*mask*arrs "vectorbtpro.generic.splitting.base.Splitter.get*iter*split*mask_arrs").

`SplitsMask` :   3D boolean array representing the split mask.

Return the number of sets, optionally considering grouping.

**```set*group*by```** :&ensp;`AnyGroupByLike` :   Grouping specification for defining sets.

`int` :   Count of sets after applying grouping.

Return the number of splits, optionally considering grouping.

**```split*group*by```** :&ensp;`AnyGroupByLike` :   Grouping specification for defining splits.

`int` :   Count of splits after applying grouping.

Get the index from an object.

Extract the index from an object that is either a Pandas Index or possesses an `index` or `wrapper.index` attribute.

**```obj```** :&ensp;`Any` :   Object with an associated index.

`Index` :   Extracted index.

Get the overlap matrix between each pair of ranges.

**```by```** :&ensp;`str` :   Specifies which overlap matrix to compute; must be one of "split", "set", or "range".

**```normalize```** :&ensp;`bool` :   Flag indicating whether to normalize overlaps relative to the total True values in both ranges.

**```split*group*by```** :&ensp;`AnyGroupByLike` :   Grouping specification for defining splits.

**```set*group*by```** :&ensp;`AnyGroupByLike` :   Grouping specification for defining sets.

**```jitted```** :&ensp;`JittedOption` :   Option to control JIT compilation.

**```squeeze*one*split```** :&ensp;`bool` :   Whether to squeeze the output if only one split exists.

**```squeeze*one*set```** :&ensp;`bool` :   Whether to squeeze the output if only one set exists.

**```index*combine*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for combining indexes.

**```**kwargs```** :   Keyword arguments for [Splitter.get*mask*arr](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*mask*arr "vectorbtpro.generic.splitting.base.Splitter.get*mask_arr").

`Frame` :   DataFrame representing the computed overlap matrix, or a scalar if the result is squeezed.

Get the inclusive left and exclusive right bounds of a range.

!!! note Even when mapped to the index, the right bound remains exclusive.

**```range_```** :&ensp;`FixRangeLike` :   Range specification to process.

**```index_bounds```** :&ensp;`bool` :   If True, map the bounds to the provided index.

**```right_inclusive```** :&ensp;`bool` :   Whether the right bound is inclusive.

**```check_constant```** :&ensp;`bool` :   If True, verify that the range is constant.

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```index```** :&ensp;`Optional[IndexLike]` :   Index used for mapping bounds.

**```freq```** :&ensp;`Optional[FrequencyLike]` :   Frequency of the index (e.g., "daily", "15 min", "index_mean").

`Tuple[Any, Any]` :   Tuple with the calculated left and right bounds.

Get the coverage of each range mask.

**```normalize```** :&ensp;`bool` :   Flag to determine if coverage should be normalized relative to the index length.

**```relative```** :&ensp;`bool` :   If True and normalization is enabled, compute coverage relative to the total True values in its split.

**```split*group*by```** :&ensp;`AnyGroupByLike` :   Grouping specification for defining splits.

**```set*group*by```** :&ensp;`AnyGroupByLike` :   Grouping specification for defining sets.

**```squeeze*one*split```** :&ensp;`bool` :   Whether to squeeze the output if only one split exists.

**```squeeze*one*set```** :&ensp;`bool` :   Whether to squeeze the output if only one set exists.

**```index*combine*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for combining indexes.

**```**kwargs```** :   Keyword arguments for [Splitter.get*mask*arr](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*mask*arr "vectorbtpro.generic.splitting.base.Splitter.get*mask_arr").

`MaybeSeries` :   Coverage values for each range mask, returned as a scalar or a Pandas Series.

Return a boolean mask array for the specified range.

**```range_```** :&ensp;`FixRangeLike` :   Range specification to generate the mask.

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```index```** :&ensp;`Optional[IndexLike]` :   Index to apply the range on.

`Array1d` :   Boolean array mask where True indicates positions within the range.

Get a ready-to-use range for indexing an array-like object.

Determine and process a range that aligns with the object index. When the object is Pandas-like or an index is provided, obtain the index using [Splitter.get*obj*index](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*obj*index "vectorbtpro.generic.splitting.base.Splitter.get*obj*index") (if needed) and remap the range using [Splitter.remap*range](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.remap*range "vectorbtpro.generic.splitting.base.Splitter.remap*range"). Finally, convert the range into a form suitable for direct indexing using [Splitter.get*ready*range](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*ready*range "vectorbtpro.generic.splitting.base.Splitter.get*ready*range").

**```obj```** :&ensp;`Any` :   Array-like object to be indexed.

**```range_```** :&ensp;`FixRangeLike` :   Input range to be processed.

**```remap*to*obj```** :&ensp;`bool` :   Whether to remap the range to the object's index.

**```obj_index```** :&ensp;`Optional[IndexLike]` :   Target index for remapping, if available.

**```obj*freq```** :&ensp;`Optional[FrequencyLike]` :   Frequency of the target index (e.g., "daily", "15 min", "index*mean").

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```jitted```** :&ensp;`JittedOption` :   Option to control JIT compilation.

**```silence_warnings```** :&ensp;`bool` :   Flag to suppress warning messages.

**```index```** :&ensp;`Optional[IndexLike]` :   Source index associated with the range.

**```freq```** :&ensp;`Optional[FrequencyLike]` :   Frequency of the source index (e.g., "daily", "15 min", "index_mean").

**```return*obj*meta```** :&ensp;`bool` :   Whether to return metadata about the object.

**```**ready*range*kwargs```** :   Keyword arguments for [Splitter.get*ready*range](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*ready*range "vectorbtpro.generic.splitting.base.Splitter.get*ready_range").

`Any` :   Processed range ready for indexing, or a tuple with object metadata and the range if requested.

Return a range directly usable for array indexing.

This function converts an input range into a format suitable for array indexing. The converted range can be one of the following: a datetime-like or integer slice with an exclusive right bound, a 1D NumPy array of indices, or a 1D boolean mask matching the length of the index.

**```range_```** :&ensp;`FixRangeLike` :   Initial range specification.

**```allow_relative```** :&ensp;`bool` :   Allow relative ranges.

**```allow*zero*len```** :&ensp;`bool` :   Permit ranges with zero length.

**```range_format```** :&ensp;`str` :   Format of the returned range.

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```index```** :&ensp;`Optional[IndexLike]` :   Index used for aligning and validating the range.

**```return_meta```** :&ensp;`bool` :   Return a metadata dictionary (which includes the converted range) if True.

`Union[RelRangeLike, ReadyRangeLike, dict]` :   Range converted to the specified format, or a metadata dictionary if `return_meta` is True.

Return the coverage of each set mask.

Coverage is calculated based on the provided parameters:

**```overlapping```** :&ensp;`bool` :   Whether to compute overlapping True values between splits.

**```normalize```** :&ensp;`bool` :   Whether to normalize the coverage by the index length.

**```relative```** :&ensp;`bool` :   When normalized, whether to compute coverage relative to the overall True count.

**```split*group*by```** :&ensp;`AnyGroupByLike` :   Grouping specification for defining splits.

**```set*group*by```** :&ensp;`AnyGroupByLike` :   Grouping specification for defining sets.

**```squeeze*one*set```** :&ensp;`bool` :   Whether to squeeze the output if only one set exists.

**```**kwargs```** :   Keyword arguments for [Splitter.get*mask*arr](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*mask*arr "vectorbtpro.generic.splitting.base.Splitter.get*mask_arr").

`MaybeSeries` :   Coverage for each set, either as a scalar or as a Series indexed by set labels.

Return a grouper for sets based on the provided grouping parameter.

**```set*group*by```** :&ensp;`AnyGroupByLike` :   Grouping specification for defining sets.

`Optional[Grouper]` :   Grouper for sets if applicable, otherwise None.

Return set labels, optionally modified by a grouper.

**```set*group*by```** :&ensp;`AnyGroupByLike` :   Grouping specification for defining sets.

`Index` :   Set labels, potentially modified by the grouper.

Return the coverage of each split mask.

Coverage is calculated based on the provided parameters:

**```overlapping```** :&ensp;`bool` :   Whether to compute overlapping True values between sets.

**```normalize```** :&ensp;`bool` :   Whether to normalize the coverage by the index length.

**```relative```** :&ensp;`bool` :   When normalized, whether to compute coverage relative to the overall True count.

**```split*group*by```** :&ensp;`AnyGroupByLike` :   Grouping specification for defining splits.

**```set*group*by```** :&ensp;`AnyGroupByLike` :   Grouping specification for defining sets.

**```squeeze*one*split```** :&ensp;`bool` :   Whether to squeeze the output if only one split exists.

**```**kwargs```** :   Keyword arguments for [Splitter.get*mask*arr](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*mask*arr "vectorbtpro.generic.splitting.base.Splitter.get*mask_arr").

`MaybeSeries` :   Coverage of each split, either as a scalar or as a Series indexed by split labels.

Return a grouper for splits based on the provided grouping parameter.

**```split*group*by```** :&ensp;`AnyGroupByLike` :   Grouping specification for defining splits.

`Optional[Grouper]` :   Grouper for splits if applicable, otherwise None.

Return split labels, optionally modified by a grouper.

**```split*group*by```** :&ensp;`AnyGroupByLike` :   Grouping specification for defining splits.

`Index` :   Split labels, potentially modified by the grouper.

Guess the appropriate factory method based on provided keyword arguments.

This method inspects the keyword arguments and compares them against the required and optional arguments of factory methods (i.e., methods starting with `from*`) defined in the class. If multiple methods match, it selects the one with the fewest combined required and optional arguments, preferring `from*n_rolling` when available. Returns None if no suitable method is found.

**```**kwargs```** :   Keyword arguments used to determine the factory method.

`Optional[str]` :   Name of the factory method if a unique match is found; otherwise, None.

Index used for splitting.

`Index` :   Index used for splitting.

Bounds computed using the index by calling [Splitter.get*bounds](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*bounds "vectorbtpro.generic.splitting.base.Splitter.get*bounds") with `index_bounds` set to True.

`Frame` :   Pandas DataFrame with the index bounds.

Duration computed using index bounds by calling [Splitter.get*duration](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*duration "vectorbtpro.generic.splitting.base.Splitter.get*duration") with `index_bounds` set to True.

`Series` :   Pandas Series of durations.

Perform indexing on a [Splitter](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") instance.

**```*args```** :   Positional arguments for [Splitter.indexing*func*meta](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.indexing*func*meta "vectorbtpro.generic.splitting.base.Splitter.indexing*func_meta").

**```splitter_meta```** :&ensp;`DictLike` :   Metadata for splitter indexing.

**```**kwargs```** :   Keyword arguments for [Splitter.indexing*func*meta](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.indexing*func*meta "vectorbtpro.generic.splitting.base.Splitter.indexing*func_meta").

[Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") :   New [Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") instance reflecting the indexing operation.

**Overridden methods**

Perform indexing on a [Splitter](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") instance and return metadata.

**```*args```** :   Positional arguments for [ArrayWrapper.indexing*func*meta](https://vectorbt.pro/pvt*ff8edc14/api/base/wrapping/#vectorbtpro.base.wrapping.ArrayWrapper.indexing*func*meta "vectorbtpro.base.wrapping.ArrayWrapper.indexing*func_meta").

**```wrapper_meta```** :&ensp;`DictLike` :   Metadata from the indexing operation on the wrapper.

**```**kwargs```** :   Keyword arguments for [ArrayWrapper.indexing*func*meta](https://vectorbt.pro/pvt*ff8edc14/api/base/wrapping/#vectorbtpro.base.wrapping.ArrayWrapper.indexing*func*meta "vectorbtpro.base.wrapping.ArrayWrapper.indexing*func_meta").

`dict` :   Dictionary with keys `wrapper*meta` and `new*splits_arr` representing the updated metadata and splits array.

Determine if the provided range is relative.

A range is considered relative if it is a number, a time delta-like object, or an instance of [RelRange](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.RelRange "vectorbtpro.generic.splitting.base.RelRange").

**```range_```** :&ensp;`RangeLike` :   Range object to evaluate.

`bool` :   True if the range is relative, otherwise False.

Iterator over 2D boolean arrays for sets by calling [Splitter.get*iter*set*mask*arrs](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*iter*set*mask*arrs "vectorbtpro.generic.splitting.base.Splitter.get*iter*set*mask_arrs") with default arguments.

`Iterator[Array2d]` :   Iterator over 2D boolean arrays.

Iterator over boolean DataFrames for sets by calling [Splitter.get*iter*set*masks](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*iter*set*masks "vectorbtpro.generic.splitting.base.Splitter.get*iter*set*masks") with default arguments.

`Iterator[Frame]` :   Iterator over boolean DataFrames.

Iterator over 2D boolean arrays for splits by calling [Splitter.get*iter*split*mask*arrs](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*iter*split*mask*arrs "vectorbtpro.generic.splitting.base.Splitter.get*iter*split*mask_arrs") with default arguments.

`Iterator[Array2d]` :   Iterator over 2D boolean arrays.

Iterator over boolean DataFrames for splits by calling [Splitter.get*iter*split*masks](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*iter*split*masks "vectorbtpro.generic.splitting.base.Splitter.get*iter*split*masks") with default arguments.

`Iterator[Frame]` :   Iterator over boolean DataFrames.

Map bounds to corresponding index values.

**```start```** :&ensp;`int` :   Starting index for the bound.

**```stop```** :&ensp;`int` :   Stopping index for the bound.

**```right_inclusive```** :&ensp;`bool` :   Whether the right bound is inclusive.

**```index```** :&ensp;`Optional[IndexLike]` :   Index to use for mapping bounds.

**```freq```** :&ensp;`Optional[FrequencyLike]` :   Frequency of the index (e.g., "daily", "15 min", "index_mean").

`Tuple[Any, Any]` :   Tuple with the mapped left and right bounds.

Boolean mask computed with default parameters from [Splitter.get*mask](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*mask "vectorbtpro.generic.splitting.base.Splitter.get*mask").

`Frame` :   Pandas DataFrame representing the split mask.

Split mask array computed with default arguments from [Splitter.get*mask*arr](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*mask*arr "vectorbtpro.generic.splitting.base.Splitter.get*mask_arr").

`SplitsMask` :   3D boolean array representing the split mask.

Merge multiple sets (columns) into a single set (column).

**```columns```** :&ensp;`Optional[Iterable[Hashable]]` :   Columns to merge.

**```new*set*label```** :&ensp;`Optional[Hashable]` :   Label for the new merged set.

**```insert*at*last```** :&ensp;`bool` :   If True, insert the merged set at the position of the last specified column.

**```wrapper_kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for configuring the wrapper.

**```init_kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for updating the splitter.

**```**merge*split*kwargs```** :   Keyword arguments for [Splitter.merge*split](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.merge*split "vectorbtpro.generic.splitting.base.Splitter.merge*split").

[Splitter](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") :   New Splitter instance with the merged sets and updated splits.

Merge multiple fixed ranges from a split into a single fixed range.

Create a single fixed range by merging individual ranges from the provided split. The function constructs a boolean mask marking True for elements within any range. If all input ranges are masks, the result is a mask; if all are slices, a slice is returned when possible; otherwise, integer indices are returned.

**```split```** :&ensp;`FixSplit` :   Collection of fixed ranges to merge.

**```range_format```** :&ensp;`Optional[str]` :   Format for the range.

**```wrap*with*template```** :&ensp;`bool` :   Whether to wrap the resulting ranges with a template of type [Rep](https://vectorbt.pro/pvt_ff8edc14/api/utils/template/#vectorbtpro.utils.template.Rep "vectorbtpro.utils.template.Rep").

**```wrap*with*fixrange```** :&ensp;`Optional[bool]` :   If True, wrap the merged range with [FixRange](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.FixRange "vectorbtpro.generic.splitting.base.FixRange").

**```wrap*with*hslice```** :&ensp;`Optional[bool]` :   If True, and applicable, wrap a slice result with an `hslice`.

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```index```** :&ensp;`Optional[IndexLike]` :   Index used for alignment.

`FixRangeLike` :   Merged fixed range, represented as a mask, slice, or integer indices depending on input types.

Metrics configuration for [Splitter](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter").

This property returns a copy of `Splitter._metrics` created during instance initialization. Modifications to the returned configuration do not affect the class-level settings.

To modify the metrics, change the configuration in-place, override this property, or assign a new value to the instance variable `Splitter._metrics`.

`Config` :   Copy of the metrics configuration for [Splitter](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter").

`int` :   Number of sets.

`int` :   Number of splits.

Parse [Takeable](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Takeable "vectorbtpro.generic.splitting.base.Takeable") instances in function annotations and inject their processed values into flattened annotated arguments.

**```flat*ann*args```** :&ensp;`FlatAnnArgs` :   Flattened annotated arguments.

**```eval_id```** :&ensp;`Optional[Hashable]` :   Evaluation identifier.

`FlatAnnArgs` :   Dictionary with updated annotated arguments after processing [Takeable](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Takeable "vectorbtpro.generic.splitting.base.Takeable") instances.

Plot splits as rows with sets represented by distinct colors.

**```split*group*by```** :&ensp;`AnyGroupByLike` :   Grouping specification for defining splits.

**```set*group*by```** :&ensp;`AnyGroupByLike` :   Grouping specification for defining sets.

**```mask*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for [Splitter.get*iter*set*masks](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*iter*set*masks "vectorbtpro.generic.splitting.base.Splitter.get*iter*set_masks").

**```trace*kwargs```** :&ensp;`KwargsLikeSequence` :   Keyword arguments for `plotly.graph*objects.Heatmap` for the mask.

**```add*trace*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for `fig.add_trace` for each trace; for example, `dict(row=1, col=1)`.

**```fig```** :&ensp;`Optional[BaseFigure]` :   Figure to update; if None, a new figure is created.

**```make*figure*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for making the figure.

**```**layout*kwargs```** :   Keyword arguments for `fig.update*layout`.

`BaseFigure` :   Figure to which traces were added.

Plot a scikit-learn splitter:

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/api/Splitter.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/api/Splitter.dark.svg#only-dark){: .iimg loading=lazy }

Plot index coverage as rows and sets as lines.

This method generates a plot where each index is represented as a row and each set is shown as a line. A stacked area plot is created if `stacked` is True; otherwise, a line plot is produced.

**```stacked```** :&ensp;`bool` :   Plot using a stacked area plot if True; otherwise, use a line plot.

**```split*group*by```** :&ensp;`AnyGroupByLike` :   Grouping specification for defining splits.

**```set*group*by```** :&ensp;`AnyGroupByLike` :   Grouping specification for defining sets.

**```mask*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for [Splitter.get*iter*set*masks](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*iter*set*masks "vectorbtpro.generic.splitting.base.Splitter.get*iter*set_masks").

**```trace*kwargs```** :&ensp;`KwargsLikeSequence` :   Keyword arguments for `plotly.graph*objects.Scatter` for the mask.

**```add*trace*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for `fig.add_trace` for each trace; for example, `dict(row=1, col=1)`.

**```fig```** :&ensp;`Optional[BaseFigure]` :   Figure to update; if None, a new figure is created.

**```make*figure*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for making the figure.

**```**layout*kwargs```** :   Keyword arguments for `fig.update*layout`.

`BaseFigure` :   Figure to which traces were added.

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/api/Splitter*coverage*area.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/api/Splitter*coverage*area.dark.svg#only-dark){: .iimg loading=lazy }

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/api/Splitter*coverage*line.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/api/Splitter*coverage*line.dark.svg#only-dark){: .iimg loading=lazy }

Default configuration for [PlotsBuilderMixin.plots](https://vectorbt.pro/pvt*ff8edc14/api/generic/plots*builder/#vectorbtpro.generic.plots_builder.PlotsBuilderMixin.plots "vectorbtpro.generic.splitting.base.Splitter.plots").

Merges the defaults from [PlotsBuilderMixin.plots*defaults](https://vectorbt.pro/pvt*ff8edc14/api/generic/plots*builder/#vectorbtpro.generic.plots*builder.PlotsBuilderMixin.plots*defaults "vectorbtpro.generic.plots*builder.PlotsBuilderMixin.plots*defaults") with the `plots` configuration from [splitter](https://vectorbt.pro/pvt*ff8edc14/api/*settings/#vectorbtpro.*settings.splitter "vectorbtpro._settings.splitter").

`Kwargs` :   Dictionary containing the default configuration for the plots builder.

Range coverage computed using default parameters from [Splitter.get*range*coverage](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*range*coverage "vectorbtpro.generic.splitting.base.Splitter.get*range_coverage").

`Series` :   Pandas Series of range coverage.

Overlap matrix computed with `get*overlap*matrix` using `by="range"`.

`Frame` :   DataFrame representing the range overlap matrix.

Remap a range to a target index.

If the source `index` matches the `target*index`, return the original range. Otherwise, resample the range to align with the target index using [Resampler.resample*source*mask](https://vectorbt.pro/pvt*ff8edc14/api/base/resampling/base/#vectorbtpro.base.resampling.base.Resampler.resample*source*mask "vectorbtpro.base.resampling.base.Resampler.resample*source*mask"). In such cases, both `freq` and `target_freq` must be provided.

**```range_```** :&ensp;`FixRangeLike` :   Input range to be remapped.

**```target_index```** :&ensp;`IndexLike` :   Target index to which the range is mapped.

**```target*freq```** :&ensp;`Optional[FrequencyLike]` :   Frequency of the target index (e.g., "daily", "15 min", "index*mean").

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```jitted```** :&ensp;`JittedOption` :   Option to control JIT compilation.

**```silence_warnings```** :&ensp;`bool` :   Flag to suppress warning messages.

**```index```** :&ensp;`Optional[IndexLike]` :   Source index associated with the range.

**```freq```** :&ensp;`Optional[FrequencyLike]` :   Frequency of the index (e.g., "daily", "15 min", "index_mean").

`FixRangeLike` :   Remapped range corresponding to the target index.

Resolve keyword arguments for initializing a [Splitter](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") after stacking splits along columns.

**```*objs```** :&ensp;`MaybeSequence[Splitter]` :   Splitter instances whose `splits` arrays are to be stacked.

**```reindex_kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for `pd.DataFrame.reindex`.

**```**kwargs```** :   Additional keyword arguments.

`Kwargs` :   Updated keyword arguments including a `splits_arr` key.

Stack multiple [Splitter](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") instances along rows.

Stack multiple [Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") instances by stacking their wrappers along rows using [ArrayWrapper.row*stack](https://vectorbt.pro/pvt*ff8edc14/api/base/wrapping/#vectorbtpro.base.wrapping.ArrayWrapper.row*stack "vectorbtpro.base.wrapping.ArrayWrapper.row_stack").

**```*objs```** :&ensp;`MaybeSequence[Splitter]` :   (Additional) [Splitter](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") instances to stack.

**```wrapper_kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for configuring the wrapper.

**```**kwargs```** :   Keyword arguments for [Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") through [Splitter.resolve*row*stack*kwargs](https://vectorbt.pro/pvt*ff8edc14/api/base/wrapping/#vectorbtpro.base.wrapping.Wrapping.resolve*row*stack*kwargs "vectorbtpro.generic.splitting.base.Splitter.resolve*row*stack*kwargs") and [Wrapping.resolve*stack*kwargs](https://vectorbt.pro/pvt*ff8edc14/api/base/wrapping/#vectorbtpro.base.wrapping.Wrapping.resolve*stack*kwargs "vectorbtpro.generic.splitting.base.Splitter.resolve*stack*kwargs").

[Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") :   New [Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") instance with row-stacked wrappers.

Retrieve indices corresponding to selected splits and sets.

Interpret selections for splits and sets, which can be provided as integers, labels, or wrapped in `PosSel` or `LabelSel`. Multiple values are allowed, in which case the corresponding ranges are merged. When labels are of an integer data type, they are treated as labels unless the associated index or grouping indicates positions.

If `split*group*by` and/or `set*group*by` is provided, grouper objects are created using [BaseIDXAccessor.get*grouper](https://vectorbt.pro/pvt*ff8edc14/api/base/accessors/#vectorbtpro.base.accessors.BaseIDXAccessor.get*grouper "vectorbtpro.base.accessors.BaseIDXAccessor.get*grouper") so that the selections are interpreted relative to groups. If `split` or `set_` is not provided, all indices for that category are selected.

**```split```** :&ensp;`Optional[Selection]` :   Selection criteria for splits.

**```set_```** :&ensp;`Optional[Selection]` :   Selection criteria for sets.

**```split*group*by```** :&ensp;`AnyGroupByLike` :   Grouping specification for defining splits.

**```set*group*by```** :&ensp;`AnyGroupByLike` :   Grouping specification for defining sets.

`Tuple[Array1d, Array1d, Array1d, Array1d]` :   Tuple containing:

Pass additional keyword arguments to [Splitter.select*indices](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.select*indices "vectorbtpro.generic.splitting.base.Splitter.select*indices") to obtain the indices for the selected splits and sets. If more than one range corresponds to these indices, merge them using [Splitter.merge*split](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.merge*split "vectorbtpro.generic.splitting.base.Splitter.merge*split").

**```merge*split*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for [Splitter.merge*split](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.merge*split "vectorbtpro.generic.splitting.base.Splitter.merge*split").

**```**select*indices*kwargs```** :   Keyword arguments for [Splitter.select*indices](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.select*indices "vectorbtpro.generic.splitting.base.Splitter.select*indices").

`RangeLike` :   Selected range, or the merged range if multiple ranges are found.

Set coverage computed with default parameters from [Splitter.get*set*coverage](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*set*coverage "vectorbtpro.generic.splitting.base.Splitter.get*set_coverage").

`Series` :   Pandas Series of set coverage.

`Index` :   Labels for sets.

Overlap matrix computed with `get*overlap*matrix` using `by="set"`.

`Frame` :   DataFrame representing the set overlap matrix.

Shuffle the splits by randomly selecting indices.

**```size```** :&ensp;`Union[None, str, int]` :   Number or specification of splits to select.

**```replace```** :&ensp;`bool` :   Whether to sample with replacement.

**```p```** :&ensp;`Optional[Array1d]` :   Probabilities associated with each split.

**```seed```** :&ensp;`Optional[int]` :   Random seed for deterministic output.

**```wrapper_kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for configuring the wrapper.

**```**init_kwargs```** :   Keyword arguments for replacing the splitter.

[Splitter](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") :   New splitter instance with the shuffled splits.

Split an index and apply a function to each segment.

**```index```** :&ensp;`IndexLike` :   Index to be split.

**```apply_func```** :&ensp;`Callable` :   Function to apply to each split segment.

**```*apply*args```** :   Positional arguments for [Splitter.apply](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.apply "vectorbtpro.generic.splitting.base.Splitter.apply").

**```splitter```** :&ensp;`Union[None, str, Splitter, Callable]` :   Splitter instance, the name of a factory method (e.g. "from*n*rolling"), or the factory method itself.

**```splitter*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for [Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter").

**```apply*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for [Splitter.apply](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.apply "vectorbtpro.generic.splitting.base.Splitter.apply").

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```**var*kwargs```** :   Keyword arguments to be distributed between `splitter*kwargs` and `apply_kwargs`.

`Any` :   Result returned by [Splitter.apply](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.apply "vectorbtpro.generic.splitting.base.Splitter.apply").

Split an index and take values from an object.

**```index```** :&ensp;`IndexLike` :   Index to be split.

**```obj```** :&ensp;`Any` :   Object from which values are extracted.

**```splitter```** :&ensp;`Union[None, str, Splitter, Callable]` :   Splitter instance, the name of a factory method (e.g. "from*n*rolling"), or the factory method itself.

**```splitter*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for [Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter").

**```take*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for [Splitter.take](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.take "vectorbtpro.generic.splitting.base.Splitter.take").

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```**var*kwargs```** :   Keyword arguments to be distributed between `splitter*kwargs` and `take_kwargs`.

`Any` :   Result returned by [Splitter.take](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.take "vectorbtpro.generic.splitting.base.Splitter.take").

Split coverage computed with default parameters from [Splitter.get*split*coverage](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*split*coverage "vectorbtpro.generic.splitting.base.Splitter.get*split_coverage").

`Series` :   Pandas Series of split coverage.

`Index` :   Labels for splits.

Overlap matrix computed with `get*overlap*matrix` using `by="split"`.

`Frame` :   DataFrame representing the split overlap matrix.

Split a fixed range into multiple fixed ranges.

This method splits an input range into several sub-ranges based on the provided `new*split` specification. The input range (`range*`) may be defined as a template, callable, tuple (start and stop), slice, sequence of indices, or mask, and it is mapped onto the given index.

**```range_```** :&ensp;`FixRangeLike` :   Input range specified as a template, callable, tuple (start, stop), slice, sequence of indices, or mask.

**```new*split```** :&ensp;`SplitLike` :   Specification for splitting `range*`.

**```backwards```** :&ensp;`bool` :   Whether to split the range in reverse order.

**```allow*zero*len```** :&ensp;`bool` :   Permit ranges with zero length.

**```range_format```** :&ensp;`Optional[str]` :   Format for the range.

**```wrap*with*template```** :&ensp;`bool` :   Whether to wrap the resulting ranges with a template of type [Rep](https://vectorbt.pro/pvt_ff8edc14/api/utils/template/#vectorbtpro.utils.template.Rep "vectorbtpro.utils.template.Rep").

**```wrap*with*fixrange```** :&ensp;`Optional[bool]` :   If True, wrap the merged range with [FixRange](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.FixRange "vectorbtpro.generic.splitting.base.FixRange").

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```index```** :&ensp;`Optional[IndexLike]` :   Index onto which `range_` is mapped.

**```freq```** :&ensp;`Optional[FrequencyLike]` :   Frequency of the index (e.g., "daily", "15 min", "index_mean").

`FixSplit` :   Tuple of fixed ranges resulting from splitting `range_` relative to the provided index.

Split a set into multiple sets using a new splitting specification.

This method applies [Splitter.split*range](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.split*range "vectorbtpro.generic.splitting.base.Splitter.split*range") to a specific column (or the only set) to generate new ranges.

!!! note The `column` parameter must be provided when multiple sets exist.

**```new_split```** :&ensp;`SplitLike` :   Specification for splitting ranges.

**```column```** :&ensp;`Optional[Hashable]` :   Identifier of the column to select.

**```new*set*labels```** :&ensp;`Optional[Sequence[Hashable]]` :   Labels to assign to the new sets.

**```wrapper_kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for configuring the wrapper.

**```init_kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for updating the splitter.

**```**split*range*kwargs```** :   Keyword arguments for [Splitter.split*range](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.split*range "vectorbtpro.generic.splitting.base.Splitter.split*range").

[Splitter](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") :   New splitter instance with the updated sets.

Splits array as a DataFrame.

`Frame` :   DataFrame representing the splits.

2D array representing splits.

The first axis represents splits and the second axis represents sets. Each element is a range defined as a slice, a sequence of indices, a mask, or a callable returning such.

`SplitsArray` :   2D array representing splits.

Default configuration for [StatsBuilderMixin.stats](https://vectorbt.pro/pvt*ff8edc14/api/generic/stats*builder/#vectorbtpro.generic.stats_builder.StatsBuilderMixin.stats "vectorbtpro.generic.splitting.base.Splitter.stats").

Merges the defaults from [StatsBuilderMixin.stats*defaults](https://vectorbt.pro/pvt*ff8edc14/api/generic/stats*builder/#vectorbtpro.generic.stats*builder.StatsBuilderMixin.stats*defaults "vectorbtpro.generic.stats*builder.StatsBuilderMixin.stats*defaults") with the `stats` configuration from [splitter](https://vectorbt.pro/pvt*ff8edc14/api/*settings/#vectorbtpro.*settings.splitter "vectorbtpro._settings.splitter").

`Kwargs` :   Dictionary containing the default configuration for the stats builder.

Subplots configuration for [Splitter](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter").

This property returns a hybrid copy of `Splitter._subplots` created at instance initialization, ensuring that modifications do not affect the class-level configuration.

To modify the subplots, update the configuration in-place, override this property, or assign a new value to `Splitter._subplots` on the instance.

`Config` :   Hybrid copy of the subplots configuration.

Take all ranges from an array-like object and optionally column-stack them.

This method uses [Splitter.select*indices](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.select*indices "vectorbtpro.generic.splitting.base.Splitter.select*indices") to determine indices for selected splits and sets. Grouping is applied via `split*group*by` and `set*group*by` so that ranges within the same group are merged.

For each split and set combination, the method:

If `attach*bounds` is enabled, the method computes bounds for each range and attaches them as an additional level in the final index hierarchy. Supported options for `attach*bounds` are:

The `into` parameter controls the output format:

Prepend any stacked option with "from*start*" (or "reset*") or "from*end_" to reset the index from the start or end.

**```obj```** :&ensp;`Any` :   Array-like object from which to extract ranges.

**```split```** :&ensp;`Optional[Selection]` :   Selection criteria for splits.

**```set_```** :&ensp;`Optional[Selection]` :   Selection criteria for sets.

**```split*group*by```** :&ensp;`AnyGroupByLike` :   Grouping specification for defining splits.

**```set*group*by```** :&ensp;`AnyGroupByLike` :   Grouping specification for defining sets.

**```squeeze*one*split```** :&ensp;`bool` :   Whether to squeeze the output if only one split exists.

**```squeeze*one*set```** :&ensp;`bool` :   Whether to squeeze the output if only one set exists.

**```into```** :&ensp;`Optional[str]` :   Specifies the output format.

**```remap*to*obj```** :&ensp;`bool` :   Whether to remap the range to the object's index.

**```obj_index```** :&ensp;`Optional[IndexLike]` :   Target index for remapping, if available.

**```obj*freq```** :&ensp;`Optional[FrequencyLike]` :   Frequency of the target index (e.g., "daily", "15 min", "index*mean").

**```range_format```** :&ensp;`str` :   Format of the returned range.

**```point_wise```** :&ensp;`bool` :   Whether to perform point-wise range extraction.

**```attach_bounds```** :&ensp;`Union[bool, str]` :   Specifies if and how to attach bounds to the result.

**```right_inclusive```** :&ensp;`bool` :   Whether the right bound is inclusive.

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```silence_warnings```** :&ensp;`bool` :   Flag to suppress warning messages.

**```index*combine*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for combining indexes.

**```stack_axis```** :&ensp;`int` :   Axis along which to stack slices (0 for rows, 1 for columns).

**```stack_kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for the stacking merge function.

**```freq```** :&ensp;`Optional[FrequencyLike]` :   Frequency of the index (e.g., "daily", "15 min", "index_mean").

`Any` :   Extracted range, which may be a single slice, a merged object, or a Pandas Series depending on the `into` parameter.

Roll a window and stack it along columns by keeping the index:

Disregard the index and attach index bounds to the column hierarchy:

Take a ready range from an array-like object.

Extract a segment from the object using the provided ready range. If `point_wise` is True, select one range point at a time and return a tuple.

**```obj```** :&ensp;`Any` :   Array-like object to index.

**```ready_range```** :&ensp;`ReadyRangeLike` :   Preprocessed range used for indexing.

**```point_wise```** :&ensp;`bool` :   Whether to perform point-wise range extraction.

`Any` :   Extracted segment of the object, or a tuple of elements if `point_wise` is True.

Take a range from a takeable object.

Process the provided `range*` from a takeable object's field `obj` by ensuring it aligns with the object's index. If remapping is enabled (or an `obj*index` is provided), obtain the ready range using `get*ready*obj*range`. For objects of type `CustomTemplate`, substitute templates using a merged context; otherwise, extract the slice using `take*range`.

**```takeable```** :&ensp;[Takeable](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Takeable "vectorbtpro.generic.splitting.base.Takeable") :   Takeable object containing the data and configuration for range extraction.

**```range_```** :&ensp;`FixRangeLike` :   Original range to be processed.

**```remap*to*obj```** :&ensp;`bool` :   Whether to remap the range to the object's index.

**```obj_index```** :&ensp;`Optional[IndexLike]` :   Target index for remapping, if available.

**```obj*freq```** :&ensp;`Optional[FrequencyLike]` :   Frequency of the target index (e.g., "daily", "15 min", "index*mean").

**```point_wise```** :&ensp;`bool` :   Whether to perform point-wise range extraction.

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```return*obj*meta```** :&ensp;`bool` :   Whether to return metadata about the object.

**```return*obj*meta```** :&ensp;`bool` :   Whether to return metadata about the object.

**```**ready*obj*range*kwargs```** :   Keyword arguments for [Splitter.get*ready*obj*range](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*ready*obj*range "vectorbtpro.generic.splitting.base.Splitter.get*ready*obj_range").

`Any` :   Extracted range from the takeable object, or a tuple containing metadata and the range if requested.

Convert relative ranges into fixed ranges and return a new [Splitter](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") instance.

**```split*range*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for range splitting.

**```**kwargs```** :   Keyword arguments for [Configured.replace](https://vectorbt.pro/pvt_ff8edc14/api/utils/config/#vectorbtpro.utils.config.Configured.replace "vectorbtpro.generic.splitting.base.Splitter.replace").

[Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") :   New [Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") instance with fixed ranges.

Merge ranges within the same group.

Merge ranges across both dimensions using group indices derived from the provided grouping parameters. A new [Splitter](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") instance is returned with its wrapper's index and columns replaced by the corresponding group labels and with a splits array containing the merged ranges.

**```split```** :&ensp;`Optional[Selection]` :   Selection criteria for splits.

**```set_```** :&ensp;`Optional[Selection]` :   Selection criteria for sets.

**```split*group*by```** :&ensp;`AnyGroupByLike` :   Grouping specification for defining splits.

**```set*group*by```** :&ensp;`AnyGroupByLike` :   Grouping specification for defining sets.

**```merge*split*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for [Splitter.merge*split](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.merge*split "vectorbtpro.generic.splitting.base.Splitter.merge*split").

**```**kwargs```** :   Keyword arguments for [Configured.replace](https://vectorbt.pro/pvt_ff8edc14/api/utils/config/#vectorbtpro.utils.config.Configured.replace "vectorbtpro.generic.splitting.base.Splitter.replace").

[Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") :   New [Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter") instance with merged ranges.

Class representing an object from which a range can be taken.

**Inherited members**

Identifier(s) at which to evaluate this instance.

Frequency associated with [Takeable.index](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Takeable.index "vectorbtpro.generic.splitting.base.Takeable.index").

Index associated with the object.

If not provided, [Splitter.get*obj*index](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*obj*index "vectorbtpro.generic.splitting.base.Splitter.get*obj_index") is used to retrieve it.

Object from which the range is taken.

Boolean indicating whether to select one range point at a time and return a tuple.

Boolean indicating whether to remap [Splitter.index](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.index "vectorbtpro.generic.splitting.base.Splitter.index") to the index of [Takeable.obj](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Takeable.obj "vectorbtpro.generic.splitting.base.Takeable.obj").

If False, it is assumed that the object already has the same index.

Exception raised when a range has a zero length.

**Examples:**

Example 1 (python):
```python
FixRange(
    range_
)
```

Example 2 (python):
```python
RelRange(
    offset=0,
    offset_anchor='prev_end',
    offset_space='free',
    length=1.0,
    length_space='free',
    out_of_bounds='warn',
    is_gap=False
)
```

Example 3 (text):
```text
depending on which comes first in the direction of [RelRange.length](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.RelRange.length "vectorbtpro.generic.splitting.base.RelRange.length").
```

Example 4 (python):
```python
RelRange.to_slice(
    total_len,
    prev_start=0,
    prev_end=0,
    index=None,
    freq=None
)
```

---

## decorators

**URL:** https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/decorators.md

**Contents:**
- cv_split <span class="dobjtype">function</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/generic/splitting/decorators.py#L328-L592" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.generic.splitting.decorators.cv_split data-toc-label="cv\_split" }
- split <span class="dobjtype">function</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/generic/splitting/decorators.py#L25-L325" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.generic.splitting.decorators.split data-toc-label="split" }

Module providing decorators for splitting functionality.

Combine cross-validation splitting and parameterized execution for decorated functions.

Decorator that integrates [split](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/decorators/#vectorbtpro.generic.splitting.decorators.split "vectorbtpro.generic.splitting.decorators.split") and [parameterized](https://vectorbt.pro/pvt*ff8edc14/api/utils/params/#vectorbtpro.utils.params.parameterized "vectorbtpro.utils.params.parameterized") to facilitate cross-validation. For each split/set range, the decorated function is applied as follows:

Handles errors by either skipping an iteration (if `skip*errored` is True or a `NoResultsException` is raised) or propagating the exception based on `raise*no_results`.

!!! warning Train and test sets within each split must execute in the same thread/process due to the way grid results are stored and accessed using `grid*results*map`.

**```func```** :&ensp;`Callable` :   Function to be decorated.

**```parameterized*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for [parameterized](https://vectorbt.pro/pvt*ff8edc14/api/utils/params/#vectorbtpro.utils.params.parameterized "vectorbtpro.utils.params.parameterized").

**```selection```** :&ensp;`Union[str, Selection]` :   Selection method for evaluating grid results.

**```return_grid```** :&ensp;`Union[bool, str]` :   Determines whether to return grid results along with the selection.

**```skip_errored```** :&ensp;`bool` :   If True, skips the current iteration upon encountering an error or `NoResultsException`, omitting it from the final results.

**```raise*no*results```** :&ensp;`bool` :   Flag indicating whether to raise a [NoResultsException](https://vectorbt.pro/pvt_ff8edc14/api/utils/execution/#vectorbtpro.utils.execution.NoResultsException "vectorbtpro.utils.execution.NoResultsException") exception if no results remain.

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```**split*kwargs```** :   Keyword arguments for [split](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/decorators/#vectorbtpro.generic.splitting.decorators.split "vectorbtpro.generic.splitting.decorators.split").

`Callable` :   Decorated function that applies cross-validation via splitting and parameterized execution.

Permutate a series and pick the first value. Make the seed parameterizable. Cross-validate based on the highest picked value:

Extend the example above to also return the grid results of each set:

Decorator that splits the inputs of a function.

Resolves a `Splitter` instance and applies splitting to the inputs of the decorated function.

The decorator performs the following operations:

Arguments `splitter*kwargs` are forwarded to the splitter factory method, and `apply*kwargs` are passed to [Splitter.apply](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.apply "vectorbtpro.generic.splitting.base.Splitter.apply"). If variable keyword arguments are provided, they are used to update `splitter*kwargs` or `apply*kwargs` based on the context. An error is raised if both `splitter*kwargs` and `apply_kwargs` are explicitly set.

**```func```** :&ensp;`Callable` :   Function to be decorated.

**```splitter```** :&ensp;`Union[None, str, Splitter, Callable]` :   Splitter instance, the name of a factory method (e.g. "from*n*rolling"), or the factory method itself.

**```splitter_cls```** :&ensp;`Optional[Type[Splitter]]` :   Splitter class to use.

**```splitter*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for [Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter "vectorbtpro.generic.splitting.base.Splitter").

**```index```** :&ensp;`Optional[IndexLike]` :   Index used for splitting.

**```index_from```** :&ensp;`Optional[AnnArgQuery]` :   Argument name or position used to extract the index when `index` is not supplied.

**```takeable*args```** :&ensp;`Optional[MaybeIterable[AnnArgQuery]]` :   Argument name(s) or position(s) to be wrapped with [Takeable](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Takeable "vectorbtpro.generic.splitting.base.Takeable").

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```forward*kwargs*as```** :&ensp;`KwargsLike` :   Mapping for renaming keyword arguments when forwarding them.

**```return_splitter```** :&ensp;`bool` :   If True, returns the constructed splitter instance instead of applying it to the function.

**```apply*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for [Splitter.apply](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.apply "vectorbtpro.generic.splitting.base.Splitter.apply").

**```**var*kwargs```** :   Keyword arguments to be distributed between `splitter*kwargs` and `apply_kwargs`.

`Callable` :   Wrapper function that executes the original function using the splitter.

Split a Series and return its sum:

Perform a split manually:

Construct splitter and mark arguments as "takeable" manually:

Split multiple timeframes using a custom index:

**Examples:**

Example 1 (python):
```python
cv_split(
    *args,
    parameterized_kwargs=None,
    selection='max',
    return_grid=False,
    skip_errored=False,
    raise_no_results=True,
    template_context=None,
    **split_kwargs
)
```

Example 2 (text):
```text
and its results are stored.
```

Example 3 (text):
```text
that determines the best parameter combination, which is then executed.
```

Example 4 (text):
```text
controlled by `return_grid`.
```

---

## purged

**URL:** https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/purged.md

**Contents:**
- BasePurgedCV <span class="dobjtype">class</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/generic/splitting/purged.py#L52-L189" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.generic.splitting.purged.BasePurgedCV data-toc-label="BasePurgedCV" }
  - eval_times <span class="dobjtype">class property</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/generic/splitting/purged.py#L104-L111" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.generic.splitting.purged.BasePurgedCV.eval_times data-toc-label="eval\_times" }
  - indices <span class="dobjtype">class property</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/generic/splitting/purged.py#L113-L120" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.generic.splitting.purged.BasePurgedCV.indices data-toc-label="indices" }
  - n_folds <span class="dobjtype">class property</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/generic/splitting/purged.py#L77-L84" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.generic.splitting.purged.BasePurgedCV.n_folds data-toc-label="n\_folds" }
  - pred_times <span class="dobjtype">class property</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/generic/splitting/purged.py#L95-L102" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.generic.splitting.purged.BasePurgedCV.pred_times data-toc-label="pred\_times" }
  - purge <span class="dobjtype">method</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/generic/splitting/purged.py#L122-L142" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.generic.splitting.purged.BasePurgedCV.purge data-toc-label="purge" }
  - purge_td <span class="dobjtype">class property</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/generic/splitting/purged.py#L86-L93" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.generic.splitting.purged.BasePurgedCV.purge_td data-toc-label="purge\_td" }
  - split <span class="dobjtype">method</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/generic/splitting/purged.py#L144-L189" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.generic.splitting.purged.BasePurgedCV.split data-toc-label="split" }
- PurgedKFoldCV <span class="dobjtype">class</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/generic/splitting/purged.py#L367-L519" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.generic.splitting.purged.PurgedKFoldCV data-toc-label="PurgedKFoldCV" }
  - compute_test_set <span class="dobjtype">method</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/generic/splitting/purged.py#L476-L498" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.generic.splitting.purged.PurgedKFoldCV.compute_test_set data-toc-label="compute\_test\_set" }

Module providing classes for purged cross-validation in time series.

As described in Advances in Financial Machine Learning by Marcos Lopez de Prado (2018).

Abstract class for purged time series cross-validation.

Time series cross-validation requires each sample to have:

Unlike standard scikit-learn cross-validation, the inputs `X`, `y`, `pred*times`, and `eval*times` must be Pandas DataFrame/Series with matching indices, and the samples must be ordered by prediction time.

**```n_folds```** :&ensp;`int` :   Total number of folds.

**```purge_td```** :&ensp;`TimedeltaLike` :   Time period added to evaluation times for purging training samples.

**Inherited members**

Time stamps at which responses become available for error computation.

`Optional[Series]` :   Evaluation times.

Array of indices corresponding to the dataset samples.

`Optional[Array1d]` :   Array of indices.

Number of folds used in cross-validation.

`int` :   Number of folds.

Time stamps at which predictions are made for each sample.

`Optional[Series]` :   Prediction times.

Remove training samples based on evaluation times and purge period.

**```train_indices```** :&ensp;`Array1d` :   Array of indices corresponding to the training set.

**```test*fold*start```** :&ensp;`int` :   Left boundary index indicating the start of the test set.

**```test*fold*end```** :&ensp;`int` :   Right boundary index indicating the end of the test set.

`Array1d` :   Training indices after purging samples to prevent data leakage.

Timedelta period added to evaluation times for purging training samples.

`PandasTimedelta` :   Purge period.

Yield training and test indices for time series cross-validation.

**```X```** :&ensp;`SeriesFrame` :   DataFrame or Series containing the input data.

**```y```** :&ensp;`Optional[Series]` :   Series containing the target values.

**```pred_times```** :&ensp;`Union[None, Index, Series]` :   Indices for prediction times.

**```eval_times```** :&ensp;`Union[None, Index, Series]` :   Indices for evaluation times.

`Tuple[Array1d, Array1d]` :   Tuple containing training and test indices.

Class for purged and embargoed combinatorial cross-validation.

The samples are decomposed into `n*folds` folds containing equal numbers of samples, without shuffling. In each cross-validation round, `n*test*folds` folds are used as the test set, while the remaining folds form the training set. There are as many rounds as there are combinations of `n*test*folds` folds among the `n*folds` folds.

Each sample should be tagged with a prediction time and an evaluation time. The split is such that the intervals [`pred*times`, `eval*times`] associated with samples in the train and test sets do not overlap (overlapping samples are dropped). In addition, an embargo period is defined to enforce a minimum time gap between a test set evaluation time and a training set prediction time, avoiding potential contamination.

**```n_folds```** :&ensp;`int` :   Total number of folds.

**```n*test*folds```** :&ensp;`int` :   Total number of folds allocated for testing.

**```purge_td```** :&ensp;`TimedeltaLike` :   Time interval used to purge samples with overlapping prediction and evaluation periods.

**```embargo_td```** :&ensp;`TimedeltaLike` :   Time interval defining the embargo period between test set evaluation times and training predictions.

**Inherited members**

Compute consolidated test fold boundaries and corresponding sample indices.

**```fold*bound*list```** :&ensp;`List[Tuple[int, int]]` :   List of tuples representing fold boundaries for the test set.

`Tuple[List[Tuple[int, int]], Array1d]` :   Tuple containing the consolidated test fold boundaries and an array of test set sample indices.

Compute the training set indices after applying purging and embargo procedures.

**```test*fold*bounds```** :&ensp;`List[Tuple[int, int]]` :   List of tuples specifying the start and end indices of test folds.

**```test_indices```** :&ensp;`Array1d` :   Array of indices corresponding to the test set.

`Array1d` :   Array of training sample indices after purging overlapping samples and applying the embargo.

Apply embargo to the training set by excluding samples with prediction times falling within the embargo period after the test set evaluation.

This procedure removes training samples whose prediction time occurs within [PurgedKFoldCV.embargo*td](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/purged/#vectorbtpro.generic.splitting.purged.PurgedKFoldCV.embargo*td "vectorbtpro.generic.splitting.purged.PurgedKFoldCV.embargo*td") after the latest evaluation time among the test set samples. The embargo is applied only to the segment of the training set immediately following the end of the test fold specified by `test*fold*end`.

**```train_indices```** :&ensp;`Array1d` :   Array of indices corresponding to the training set.

**```test_indices```** :&ensp;`Array1d` :   Array of indices corresponding to the test set.

**```test*fold*end```** :&ensp;`int` :   Right boundary index indicating the end of the test set.

`Array1d` :   Modified training sample indices after applying the embargo procedure.

Embargo period duration enforcing a minimum gap between test set evaluation times and training set prediction times.

`PandasTimedelta` :   Embargo period.

Number of folds reserved for testing in each cross-validation round.

`int` :   Number of test folds.

Class for purged walk-forward cross-validation.

The samples are decomposed into `n*folds` folds with an equal number of samples or equal time intervals without shuffling. In each cross-validation round, `n*test*folds` contiguous folds are used as the test set while the training set consists of between `min*train*folds` and `max*train_folds` immediately preceding folds.

Each sample must be tagged with a prediction time and an evaluation time. The splitting ensures that the intervals [`pred*times`, `eval*times`] associated with samples in the train and test sets do not overlap, with overlapping samples being dropped.

With `split*by*time=True` in [PurgedWalkForwardCV.split](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/purged/#vectorbtpro.generic.splitting.purged.BasePurgedCV.split "vectorbtpro.generic.splitting.purged.PurgedWalkForwardCV.split"), folds can span equal time intervals based on prediction times, rather than containing an equal number of samples.

**```n_folds```** :&ensp;`int` :   Total number of folds.

**```n*test*folds```** :&ensp;`int` :   Total number of folds allocated for testing.

**```min*train*folds```** :&ensp;`int` :   Minimum number of consecutive folds to use for training preceding the test set.

**```max*train*folds```** :&ensp;`Optional[int]` :   Maximum number of consecutive folds to use for training preceding the test set.

**```split*by*time```** :&ensp;`bool` :   Whether to partition folds based on equal time intervals using prediction times.

**```purge_td```** :&ensp;`TimedeltaLike` :   Duration used to purge overlapping samples between train and test sets.

**Inherited members**

Compute the left boundary indices of folds used to partition the data.

When `split*by*time` is True, the boundaries are determined based on equal time intervals from prediction times. Otherwise, the indices are split into groups with an approximately equal number of samples.

`List[int]` :   List of left boundary indices for each fold.

Compute the indices of test samples for a given fold.

**```fold_bound```** :&ensp;`int` :   Boundary index of the current fold.

**```count_folds```** :&ensp;`int` :   Number of folds processed so far.

`Array1d` :   Array of indices representing the test samples.

Compute the indices of training samples for a given fold.

**```fold_bound```** :&ensp;`int` :   Boundary index of the current fold.

**```count_folds```** :&ensp;`int` :   Number of folds processed so far.

`Array1d` :   Array of indices representing the training samples after purging.

List of indices representing the left boundaries of folds.

`List[int]` :   List of indices representing the left boundaries of folds.

Maximum number of folds for the training set.

`int` :   Maximum number of training folds.

Minimum number of folds for the training set.

`int` :   Minimum number of training folds.

Number of folds used as the test set.

`int` :   Number of test folds.

Flag indicating whether folds are based on equal time intervals.

If False, the folds contain an approximately equal number of samples.

`bool` :   True if folds are based on equal time intervals, False otherwise.

**Examples:**

Example 1 (python):
```python
BasePurgedCV(
    n_folds=10,
    purge_td=0
)
```

Example 2 (python):
```python
BasePurgedCV.purge(
    train_indices,
    test_fold_start,
    test_fold_end
)
```

Example 3 (python):
```python
BasePurgedCV.split(
    X,
    y=None,
    pred_times=None,
    eval_times=None
)
```

Example 4 (text):
```text
If None, the index of `X` is used.
```

---

## Cross-validation

**URL:** https://vectorbt.pro/pvt_ff8edc14/cookbook/cross-validation.md

**Contents:**
- Splitting
  - Taking
- Testing

!!! question Learn more in the [Cross-validation tutorial](https://vectorbt.pro/pvt_ff8edc14/tutorials/cross-validation/).

To select a fixed number of windows and optimize the window length so that they collectively cover the maximum area of the index while keeping the train or test set non-overlapping, use [Splitter.from*n*rolling](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.from*n_rolling) with `length="optimize"`. Under the hood, SciPy is used to minimize any empty space.

<div class="separator-container"> <hr class="separator"> <span class="separator-text">+</span> <hr class="separator"> </div>

When using [Splitter.from*rolling](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.from_rolling) and the last window does not fit, it will be removed, causing a gap on the right-hand side. To remove the oldest window instead, use `backwards="sorted"`.

<div class="separator-container"> <hr class="separator"> <span class="separator-text">+</span> <hr class="separator"> </div>

To create a gap between the train set and the test set, use [RelRange](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.RelRange) with `is*gap=True`.

Otherwise, `1.0` (100%) will be calculated first and will take up the entire split.

<div class="separator-container"> <hr class="separator"> <span class="separator-text">+</span> <hr class="separator"> </div>

To roll a time-periodic window, use [Splitter.from*ranges](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.from*ranges) with the `every` and `lookback*period` arguments as date offsets.

To split an object along the index (time) axis, first create a [Splitter](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter) instance and then "take" chunks from that object.

<div class="separator-container"> <hr class="separator"> <span class="separator-text">+</span> <hr class="separator"> </div>

Most VBT objects also have a `split` method that can combine both operations into a single step. This method will automatically determine the correct splitting operation based on the supplied arguments.

The option `into="reset_stacked"` is enabled automatically.

To cross-validate a function that takes only one parameter combination at a time across a grid of parameter combinations, use [`@vbt.cv*split`](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/decorators/#vectorbtpro.generic.splitting.decorators.cv*split). This decorator combines [`@vbt.parameterized`](https://vectorbt.pro/pvt*ff8edc14/api/utils/params/#vectorbtpro.utils.params.parameterized) (which applies a function to each combination of parameters from a grid and merges the results), and [`@vbt.split`](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/decorators/#vectorbtpro.generic.splitting.decorators.split) (which applies a function to each split and set combination).

VBT know that the returned value is a label, not a position, in case it is an integer. Also, wrap the value with a list to display the parameter combination in the final index.

to control the execution of split and set combinations.

the results of all parameter combinations into a single Pandas Series.

all of the Pandas Series into a single Pandas Series.

as single values. Any takeable argument (here, `data`) will include only values that correspond to the current split and set combination.

to the function by prepending the underscore.

<div class="separator-container"> <hr class="separator"> <span class="separator-text">+</span> <hr class="separator"> </div>

To skip a parameter combination, return [NoResult](https://vectorbt.pro/pvt_ff8edc14/api/utils/params/#vectorbtpro.utils.params.NoResult). This helps exclude parameter combinations that raise an error. `NoResult` can also be returned by the selection function to skip an entire split and set combination. Once excluded, the combination will not appear in the final index.

(that is, the position was not liquidated) and the number of trades is 20 or higher.

<div class="separator-container"> <hr class="separator"> <span class="separator-text">+</span> <hr class="separator"> </div>

To warm up one or more indicators, instruct VBT to pass a date range instead of selecting it from the data, and prepend a buffer to this date range. Then, manually select this extended date range from the data and run your indicators on that date range. Finally, remove the buffer from the indicator(s).

**Examples:**

Example 1 (text):
```text
splitter = vbt.Splitter.from_n_rolling(
    data.index,
    n=20,
    length="optimize",
    split=0.7,  # (1)!
    optimize_anchor_set=1,  # (2)!
    set_labels=["train", "test"]
)
```

Example 2 (text):
```text
length = 1000
ratio = 0.95
train_length = round(length * ratio)
test_length = length - train_length

splitter = vbt.Splitter.from_rolling(
    data.index,
    length=length,
    split=train_length,
    offset_anchor_set=None,
    offset=-test_length,
    backwards="sorted"
)
```

Example 3 (text):
```text
splitter = vbt.Splitter.from_expanding(
    data.index,
    min_length=130,
    offset=10,  # (1)!
    split=(1.0, vbt.RelRange(length=10, is_gap=True), 20),
    split_range_kwargs=dict(backwards=True)  # (2)!
)
```

Example 4 (text):
```text
splitter = vbt.Splitter.from_ranges(
    data.index,
    every="Y",
    lookback_period="4Y",
    split=(
        vbt.RepEval("index.year != index.year[-1]"),  # (1)!
        vbt.RepEval("index.year == index.year[-1]")  # (2)!
    )
)
```

---

## text_splitting

**URL:** https://vectorbt.pro/pvt_ff8edc14/api/knowledge/text_splitting.md

**Contents:**
- resolve_text_splitter <span class="dobjtype">function</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/text_splitting.py#L1338-L1380" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.text_splitting.resolve_text_splitter data-toc-label="resolve\_text\_splitter" }
- split_text <span class="dobjtype">function</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/text_splitting.py#L1383-L1401" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.text_splitting.split_text data-toc-label="split\_text" }
- LlamaIndexSplitter <span class="dobjtype">class</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/text_splitting.py#L1224-L1335" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.text_splitting.LlamaIndexSplitter data-toc-label="LlamaIndexSplitter" }
  - node_parser <span class="dobjtype">class property</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/text_splitting.py#L1321-L1328" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.text_splitting.LlamaIndexSplitter.node_parser data-toc-label="node\_parser" }
- MarkdownSplitter <span class="dobjtype">class</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/text_splitting.py#L950-L1221" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.text_splitting.MarkdownSplitter data-toc-label="MarkdownSplitter" }
  - max_section_level <span class="dobjtype">class property</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/text_splitting.py#L1004-L1011" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.text_splitting.MarkdownSplitter.max_section_level data-toc-label="max\_section\_level" }
  - should_split_section <span class="dobjtype">method</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/text_splitting.py#L1013-L1025" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.text_splitting.MarkdownSplitter.should_split_section data-toc-label="should\_split\_section" }
  - split_by <span class="dobjtype">class property</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/text_splitting.py#L993-L1002" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.text_splitting.MarkdownSplitter.split_by data-toc-label="split\_by" }
- PythonSplitter <span class="dobjtype">class</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/text_splitting.py#L781-L947" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.text_splitting.PythonSplitter data-toc-label="PythonSplitter" }
  - max_stmt_level <span class="dobjtype">class property</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/text_splitting.py#L850-L857" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.text_splitting.PythonSplitter.max_stmt_level data-toc-label="max\_stmt\_level" }

Module providing classes and utilities for splitting documents.

Resolve a [TextSplitter](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/text*splitting/#vectorbtpro.knowledge.text*splitting.TextSplitter "vectorbtpro.knowledge.text*splitting.TextSplitter") subclass or instance.

!!! info For default settings, see `chat` in [knowledge](https://vectorbt.pro/pvt*ff8edc14/api/*settings/#vectorbtpro.*settings.knowledge "vectorbtpro.*settings.knowledge").

**```text*splitter```** :&ensp;`TextSplitterLike` :   Identifier, subclass, or instance of [TextSplitter](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/text*splitting/#vectorbtpro.knowledge.text*splitting.TextSplitter "vectorbtpro.knowledge.text_splitting.TextSplitter").

[TextSplitter](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/text*splitting/#vectorbtpro.knowledge.text*splitting.TextSplitter "vectorbtpro.knowledge.text*splitting.TextSplitter") :   Resolved text splitter subclass or instance.

Split text into chunks using a specified text splitter.

**```text```** :&ensp;`str` :   Input text to be split.

**```text*splitter```** :&ensp;`TextSplitterLike` :   Identifier, subclass, or instance of [TextSplitter](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/text*splitting/#vectorbtpro.knowledge.text*splitting.TextSplitter "vectorbtpro.knowledge.text_splitting.TextSplitter").

**```**kwargs```** :   Keyword arguments to initialize or update `text_splitter`.

`List[str]` :   List of text chunks.

Splitter class based on a node parser from LlamaIndex that divides text into chunks using nodes.

!!! info For default settings, see `chat.text*splitter*configs.llama*index` in [knowledge](https://vectorbt.pro/pvt*ff8edc14/api/*settings/#vectorbtpro.*settings.knowledge "vectorbtpro._settings.knowledge").

**```node_parser```** :&ensp;`Union[None, str, NodeParser]` :   Node parser to use, specified as a string key, class, or instance.

**```node*parser*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments to node parser initialization.

**```**kwargs```** :   Keyword arguments for [TextSplitter](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/text*splitting/#vectorbtpro.knowledge.text*splitting.TextSplitter "vectorbtpro.knowledge.text*splitting.TextSplitter") or used as `node*parser*kwargs`.

**Inherited members**

LlamaIndex node parser instance used for splitting text.

`NodeParser` :   Node parser instance used for splitting text.

Splitter class for Markdown source code.

This class is responsible for splitting Markdown source code into chunks based on headers and paragraphs. It uses a custom algorithm to identify headers and split the content accordingly.

!!! info For default settings, see `chat.text*splitter*configs.markdown` in [knowledge](https://vectorbt.pro/pvt*ff8edc14/api/*settings/#vectorbtpro.*settings.knowledge "vectorbtpro.*settings.knowledge").

**```split_by```** :&ensp;`Optional[str]` :   Method to split the source code.

**```max*section*level```** :&ensp;`Optional[int]` :   Maximum level of sections to include in the split.

**```**kwargs```** :   Keyword arguments for [SourceSplitter](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/text*splitting/#vectorbtpro.knowledge.text*splitting.SourceSplitter "vectorbtpro.knowledge.text*splitting.SourceSplitter").

**Inherited members**

Maximum level of sections to include in the split.

`Optional[int]` :   Maximum section level; None if all levels are included.

Determine whether to split the given section.

**```section```** :   Section to evaluate.

**```level```** :   Current level of the section.

`bool` :   True if the section should be split; False otherwise.

Method to split the source code.

Options are "header" or "paragraph".

`str` :   Method used to split the source code.

Splitter class for Python source code.

This class is used to split Python source code using the `ast` module. All module-level statements become the zero level, which can be split into nested levels. The class supports splitting statements based on a whitelist and blacklist of statement types. It also allows for limiting the maximum statement level.

!!! info For default settings, see `chat.text*splitter*configs.python` in [knowledge](https://vectorbt.pro/pvt*ff8edc14/api/*settings/#vectorbtpro.*settings.knowledge "vectorbtpro.*settings.knowledge").

**```stmt_whitelist```** :&ensp;`Optional[Iterable[str]]` :   Statement types to include in the split.

**```stmt_blacklist```** :&ensp;`Optional[Iterable[str]]` :   Statement types to exclude from the split.

**```max*stmt*level```** :&ensp;`Optional[int]` :   Maximum level of statements to include in the split.

**```**kwargs```** :   Keyword arguments for [SourceSplitter](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/text*splitting/#vectorbtpro.knowledge.text*splitting.SourceSplitter "vectorbtpro.knowledge.text*splitting.SourceSplitter").

**Inherited members**

Maximum level of statements to include in the split.

`Optional[int]` :   Maximum statement level; None if all levels are included.

Check if the statement should be split based on its type and level.

**```stmt```** :&ensp;`ast.stmt` :   Statement to check.

**```level```** :&ensp;`int` :   Level of the statement.

`bool` :   True if the statement should be split, False otherwise.

Statement types to exclude from the split.

`Tuple[str, ...]` :   Tuple of statement types.

Statement types to include in the split.

Effective only if `max*stmt*level` is met.

`Tuple[str, ...]` :   Tuple of statement types.

Splitter class for segments based on specified separators.

This class iteratively splits text by applying nested layers of separators. If a segment exceeds the allowed size and no valid previous chunk exists or the token count falls below the minimum, the next layer of separators is used. To split into tokens, set a separator to None; to split into individual characters, use an empty string.

!!! info For default settings, see `chat.text*splitter*configs.segment` in [knowledge](https://vectorbt.pro/pvt*ff8edc14/api/*settings/#vectorbtpro.*settings.knowledge "vectorbtpro.*settings.knowledge").

**```separators```** :&ensp;`List[List[Optional[str]]]` :   Nested list of separators grouped by layers used for splitting text.

**```min*chunk*size```** :&ensp;`Union[int, float]` :   Minimum number of tokens required per chunk.

**```fixed_overlap```** :&ensp;`bool` :   Indicates whether fixed overlap is applied.

**```**kwargs```** :   Keyword arguments for [TokenSplitter](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/text*splitting/#vectorbtpro.knowledge.text*splitting.TokenSplitter "vectorbtpro.knowledge.text*splitting.TokenSplitter").

**Inherited members**

Whether fixed overlap is applied.

`bool` :   True if fixed overlap is applied, False otherwise.

Minimum number of tokens per chunk. If provided as a float, it is interpreted relative to [SegmentSplitter.chunk*size](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/text*splitting/#vectorbtpro.knowledge.text*splitting.TokenSplitter.chunk*size "vectorbtpro.knowledge.text*splitting.SegmentSplitter.chunk_size").

`int` :   Minimum number of tokens required per chunk.

Nested list of separators grouped by layers.

`List[List[Optional[str]]]` :   (Nested) list of separators used for splitting text.

Split text into segments using the provided separator.

If `separator` is None, split the text into tokens using [TokenSplitter.split*into*tokens](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/text*splitting/#vectorbtpro.knowledge.text*splitting.TokenSplitter.split*into*tokens "vectorbtpro.knowledge.text*splitting.SegmentSplitter.split*into*tokens"). If `separator` is an empty string, split the text into individual characters; otherwise, split the text at each occurrence of `separator`.

**```text```** :&ensp;`str` :   Text to be split.

**```separator```** :&ensp;`Optional[str]` :   Separator to insert between data items.

`Tuple[int, int, bool]` :   Tuple containing the segment's start index, end index, and a flag indicating if the segment is a separator.

Splitter class for source code.

This class is used to split source code into chunks by parsing the structure of the code. It divides nodes of the code into levels and performs splitting based on the specified chunk size and overlap.

!!! info For default settings, see `chat.text*splitter*configs.source` in [knowledge](https://vectorbt.pro/pvt*ff8edc14/api/*settings/#vectorbtpro.*settings.knowledge "vectorbtpro.*settings.knowledge").

**```uniform_chunks```** :&ensp;`Optional[bool]` :   Whether each chunk should start and end at the same base level.

**```**kwargs```** :   Keyword arguments for [TokenSplitter](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/text*splitting/#vectorbtpro.knowledge.text*splitting.TokenSplitter "vectorbtpro.knowledge.text*splitting.TokenSplitter").

**Inherited members**

Split the source code into chunks.

!!! abstract This method should be overridden in a subclass.

**```source```** :&ensp;`str` :   Source code to be split.

`Tuple[str, int]` :   Tuple containing the source code chunk and its base level.

Whether each chunk should start and end at the same base level.

If nested chunks (with level > base) are present, includes them only if they fit as a whole.

`bool` :   True if uniform chunks are enabled, False otherwise.

Abstract class for text splitters.

!!! info For default settings, see [knowledge](https://vectorbt.pro/pvt*ff8edc14/api/*settings/#vectorbtpro.*settings.knowledge "vectorbtpro.*settings.knowledge") and its sub-configurations `chat` and `chat.text*splitter*config`.

**```first*chunk*template```** :&ensp;`Optional[CustomTemplateLike]` :   Template used to format the first text chunk.

**```chunk_template```** :&ensp;`Optional[CustomTemplateLike]` :   Template used to format each subsequent text chunk.

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```**kwargs```** :   Keyword arguments for [Configured](https://vectorbt.pro/pvt_ff8edc14/api/utils/config/#vectorbtpro.utils.config.Configured "vectorbtpro.utils.config.Configured").

**Inherited members**

Template used for formatting subsequent text chunks.

Can use the following context: `chunk*idx`, `chunk*start`, `chunk*end`, `chunk*text`, and `text`.

The template can be a string, a function, or an instance of [CustomTemplate](https://vectorbt.pro/pvt_ff8edc14/api/utils/template/#vectorbtpro.utils.template.CustomTemplate "vectorbtpro.utils.template.CustomTemplate").

`Kwargs` :   Context mapping used for expression evaluation.

Template used for formatting the first text chunk.

Can use the following context: `chunk*idx`, `chunk*start`, `chunk*end`, `chunk*text`, and `text`.

The template can be a string, a function, or an instance of [CustomTemplate](https://vectorbt.pro/pvt_ff8edc14/api/utils/template/#vectorbtpro.utils.template.CustomTemplate "vectorbtpro.utils.template.CustomTemplate").

`Kwargs` :   Context mapping used for expression evaluation.

Yield the start and end character indices for each text chunk in the given text.

!!! abstract This method should be overridden in a subclass.

**```text```** :&ensp;`str` :   Input text to split.

`Tuple[int, int]` :   Tuple representing the start and end indices of a text chunk.

Yield formatted text chunks generated from the input text by applying the chunk template.

The method substitutes the chunk template with context derived from each chunk's position and text.

**```text```** :&ensp;`str` :   Text to split.

`str` :   Formatted text chunk.

Additional context for template substitution.

`Kwargs` :   Dictionary of context variables for template substitution.

Splitter class for tokens.

!!! info For default settings, see `chat.text*splitter*configs.token` in [knowledge](https://vectorbt.pro/pvt*ff8edc14/api/*settings/#vectorbtpro.*settings.knowledge "vectorbtpro.*settings.knowledge").

**```chunk_size```** :&ensp;`Optional[int]` :   Maximum number of tokens per chunk; None if disabled.

**```chunk_overlap```** :&ensp;`Union[None, int, float]` :   Number or fraction of tokens overlapping between consecutive chunks.

**```tokenizer```** :&ensp;`TokenizerLike` :   Identifier, subclass, or instance of [Tokenizer](https://vectorbt.pro/pvt_ff8edc14/api/knowledge/tokenization/#vectorbtpro.knowledge.tokenization.Tokenizer "vectorbtpro.knowledge.tokenization.Tokenizer").

**```tokenizer_kwargs```** :&ensp;`KwargsLike` :   Keyword arguments to initialize or update `tokenizer`.

**```**kwargs```** :   Keyword arguments for [TextSplitter](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/text*splitting/#vectorbtpro.knowledge.text*splitting.TextSplitter "vectorbtpro.knowledge.text*splitting.TextSplitter").

**Inherited members**

Number of overlapping tokens between chunks.

If specified as a float between 0 and 1, it is scaled by [TokenSplitter.chunk*size](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/text*splitting/#vectorbtpro.knowledge.text*splitting.TokenSplitter.chunk*size "vectorbtpro.knowledge.text*splitting.TokenSplitter.chunk_size").

`int` :   Number of overlapping tokens between chunks.

Maximum number of tokens per chunk.

`int` :   Maximum number of tokens allowed in each chunk; None if disabled.

Yield start and end indices for each token in the given text.

The method encodes the text into tokens and decodes each token to determine its character span.

**```text```** :&ensp;`str` :   Text to tokenize.

`Tuple[int, int]` :   Start and end indices of each token.

[Tokenizer](https://vectorbt.pro/pvt_ff8edc14/api/knowledge/tokenization/#vectorbtpro.knowledge.tokenization.Tokenizer "vectorbtpro.knowledge.tokenization.Tokenizer") instance used to tokenize input text.

`Tokenizer` :   Tokenizer instance used for encoding and decoding.

**Examples:**

Example 1 (python):
```python
resolve_text_splitter(
    text_splitter=None
)
```

Example 2 (text):
```text
Supported identifiers:

* "token" for [TokenSplitter](https://vectorbt.pro/pvt_ff8edc14/api/knowledge/text_splitting/#vectorbtpro.knowledge.text_splitting.TokenSplitter "vectorbtpro.knowledge.text_splitting.TokenSplitter")
* "segment" for [SegmentSplitter](https://vectorbt.pro/pvt_ff8edc14/api/knowledge/text_splitting/#vectorbtpro.knowledge.text_splitting.SegmentSplitter "vectorbtpro.knowledge.text_splitting.SegmentSplitter")
* "llama_index" for [LlamaIndexSplitter](https://vectorbt.pro/pvt_ff8edc14/api/knowledge/text_splitting/#vectorbtpro.knowledge.text_splitting.LlamaIndexSplitter "vectorbtpro.knowledge.text_splitting.LlamaIndexSplitter")
```

Example 3 (python):
```python
split_text(
    text,
    text_splitter=None,
    **kwargs
)
```

Example 4 (text):
```text
Resolved using [resolve_text_splitter](https://vectorbt.pro/pvt_ff8edc14/api/knowledge/text_splitting/#vectorbtpro.knowledge.text_splitting.resolve_text_splitter "vectorbtpro.knowledge.text_splitting.resolve_text_splitter").
```

---

## Splitter

**URL:** https://vectorbt.pro/pvt_ff8edc14/tutorials/cross-validation/splitter.md

**Contents:**
- Schema
  - Range format
    - Relative
  - Array format
- Preparation
  - Splits
  - Method
- Generation
  - Rolling
  - Anchored

The manual approach we used earlier can be divided into three distinct steps: splitting the entire period into sub-periods, applying a UDF to each sub-period and merging its outputs, and analyzing the merged outputs with data science tools. The first two steps are easy to automate. For example, [scikit-learn](https://scikit-learn.org/stable/) provides several [classes for cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html), each designed to take an array and operate on chunks of it. However, that otherwise excellent Python package lacks robust cross-validation schemes for time series data, tools for charting and analyzing split distributions, and an easy-to-extend interface for custom use cases. It is also focused on machine learning (ML) models trained on one dataset and validated on another by making predictions (as the name scikit-learn suggests), while rule-based algorithms that do not predict, but instead produce a set of scores (one per test rather than per data point), receive less attention.

That's why VBT takes a different approach and offers functionality designed for the needs of quantitative analysts rather than ML practitioners. The core of this functionality is the class [Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter), whose main purpose is to create arbitrary splits and perform operations on them. The workings of this class are straightforward: you call one of the class methods with the `from*` prefix (which should feel familiar) to generate splits. In response, a splitter instance is returned, with splits and their labels stored in a memory-efficient array format. This instance can be used to analyze split distribution, chunk array-like objects, and run UDFs. Get ready—this class alone contains twice as many lines of code as the entire [backtesting.py](https://github.com/kernc/backtesting.py) library :smiling_imp:

Let's create a splitter for the schema from our first example:

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/cv/splitter.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/cv/splitter.dark.svg#only-dark){: .iimg loading=lazy }

That's it! We now have a splitter that can manipulate the periods (blue and orange boxes on the plot) and the data within them any way we like, with no more while-loops necessary. Before we dive into the many built-in generation and analysis techniques, let's look under the hood and get familiar with some basic concepts first.

The smallest unit of a splitter is a *range*, which is a period of time that can be mapped onto the data. In the plot above, you can count a total of 18 ranges: 9 blue and 9 orange. Multiple ranges placed side by side and representing a single test are called a *split*. There are 9 splits shown in the chart, so we expect one pipeline to be tested on 9 different data ranges. Different range types within each split are called *sets*. Usually, there is either one set; two sets—such as "training" and "test" (commonly used in backtesting); or three sets—"training," "validation," and "test" (commonly used in ML). The number of sets stays the same across all splits.

This schema fits perfectly into the philosophy of VBT, as we can represent everything in an array format where rows are splits, columns are sets, and the elements are ranges:

Notice that the index contains split labels and the columns contain set labels. Unlike other classes in VBT, the wrapper for this class does not represent time and assets, but splits and sets. Time is tracked separately as [Splitter.index](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.index), while assets are not tracked at all, since they have no effect on splitting.

This design has a useful property: you can apply indexing directly to a splitter instance to select specific splits and sets. Let's select the OOS set:

This operation creates a completely new splitter for OOS ranges :open_mouth:

Why is this useful? Because you can select one set and apply a UDF to it, then select another set and apply a completely different UDF to that one. Sounds like a prerequisite for CV, right?

So, what do ranges look like? In the first example of this tutorial, we used a start and end date to slice the data with `loc`. However, as we learned, the end date in a `loc` operation should be inclusive, which makes it a bit tricky to ensure that neighboring ranges do not overlap. Also, dates cannot be used to slice NumPy arrays unless you first convert them into positions. That's why the splitter uses integer-location based indexing and accepts the following range formats. These can be used to slice both Pandas objects (using [pandas.DataFrame.iloc](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.iloc.html)) and NumPy arrays:

output for indexing (one of the above formats).

For example, the slice `slice(1, 7)` covers the indices `[0, 1, 2, 3, 4, 5, 6]`:

Separating the index and integer-location based ranges makes it much easier to design non-overlapping, bug-free ranges.

The range format introduced above is called "fixed" because ranges do not depend on each other. However, there is another range format called "relative," which makes one range depend on the previous range. For example, instead of defining a range between fixed index positions `110` and `150`, you can define a range that starts `10` points after the end of the previous range and has a length of `40`. Such an instruction can be created using [RelRange](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.RelRange):

This instruction will be evaluated later by calling [RelRange.to*slice](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.RelRange.to_slice):

Relative ranges are typically converted into fixed ones before building a splitter instance, but splitter instances can also hold relative ranges if the user wants this behavior.

How do we efficiently store such range formats? The most flexible formats are index arrays and masks because they allow gaps and enable classical [k-fold cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html), but they may use a lot of memory even for simple cases. For example, consider a range covering one year of 1-minute data. This requires about 4MB of RAM as an integer array, or 0.5MB as a mask:

This means that just 100 splits and 2 sets would use 800MB and 100MB of RAM, respectively. This is just for holding the splitter metadata in memory. Most "ranges" do not need to be that complex: they usually only need predefined start and end points (which use at most 18 bytes of memory), while still being able to pull the exact period of data as their integer or boolean array equivalents. That's why the [Splitter](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter) class tries to convert any array into a slice whenever possible.

To make sure users can work with lightweight ranges, complex arrays, and relative ranges using the same API, the array that stores ranges has an object data type:

is the NumPy (raw) version of [Splitter.splits](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.splits).

!!! info If an element of an array is a complex object, the array does not store the whole object— it only stores a [reference](https://realpython.com/lessons/object-value-vs-object-identity/) to the object.

The object data type is totally valid. It only becomes an issue if you try to pass it to Numba, but the splitting functionality is entirely in Python because the number of ranges (splits x sets) is usually quite low. The main bottleneck is in running UDFs, not iterating over ranges (and don't worry, UDFs can still be run in Numba :relieved:). Another drawback is that the array can no longer be processed numerically with NumPy or Pandas. That's why we use the [Splitter](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter) class, which can extract the meaning out of such an array.

This array format provides even more flexibility: you can use different range formats across different splits, store index arrays of different lengths, and since the `splits` array only stores references, you do not need to duplicate an array if two range values point to the same object. For example, let's build a splitter where ranges of different sizes are stored as integer-location based arrays:

!!! tip Why is the value of [FixRange](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.FixRange) called `range*` and not `range`? Because `range` is a reserved keyword in Python.

As we can see, each element of the splits array is a NumPy array wrapped with [FixRange](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.FixRange), which works perfectly fine. Why are arrays wrapped while slices are not? If sub-arrays were not wrapped, the entire array would expand to three dimensions, which is not well-supported by Pandas.

In short, a splitter instance manages three objects:

While you can prepare these objects manually, convenient methods are available to automate this process. The main class method, which serves as the foundation for most other class methods, is [Splitter.from*splits](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.from_splits). This method accepts a sequence of splits, optionally performs some pre-processing on each split, and converts the sequence into an appropriate array format. It also generates the labels and the wrapper. However, let's first focus on preparing the splits.

Splitting involves dividing a larger range into smaller subranges. This is accomplished using the [Splitter.split*range](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.split*range) method. This method requires a fixed range `range*` and a split specification `new_split`, and returns a tuple of new fixed ranges. The returned ranges are always fixed, meaning this method is also used to convert relative ranges into fixed ones. Its main function is to ensure that the provided specification is valid and does not exceed any bounds. For example, you can generate two ranges: one occupying 75% of the space and the other taking up the remaining 25%.

See [this explanation](https://stackoverflow.com/a/509295).

!!! tip This method is a hybrid: it can be called as either a class method or an instance method. If you call it on an instance, you do not need to provide the index, since it is already stored:

These slices can then be used to slice your data:

The two relative ranges above can also be replaced with a single number, which represents the length reserved for the first range, with the remaining space assigned to the second range:

In cross-validation, you often want to set a fixed length for the OOS period and assign the rest to the IS period. You can do this with a negative number, which reverses the processing order. For example, to make the OOS period 25% of the total:

!!! tip Why do the results differ? This is due to rounding:

You can also do this manually:

Relative ranges defined only by length can be replaced with numbers for convenience. For instance, to make the OOS period 30 data points long:

!!! tip How does the method decide if the length is relative or absolute? If the number is between 0 and 1, it is treated as a relative length; otherwise, it is treated as the number of data points.

When using relative lengths, you can specify the reference space for the length using [RelRange.length*space](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.RelRange.length_space). By default, the length is relative to the remaining space (from the right-most bound of the previous range to the right-most bound of the whole period), but you can set it to be relative to the entire space instead. For example, here we define three ranges: 40%, 40%, and 20%:

To create a gap between two ranges, use an offset. Offsets, like lengths, can be relative or absolute. Each offset also has an anchor, which defaults to the right-most bound of the previous range (if one exists, otherwise 0). For example, to require a gap of 1 point between the two ranges:

You can achieve the same result by placing a relative range of 1 data point between the ranges and enabling [RelRange.is*gap](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.RelRange.is_gap):

This method is not only useful for converting relative ranges into fixed ones, but also for optimizing target ranges for better memory efficiency. For example, if you make the first range an array without gaps and the second range an array with gaps, you will see:

Here, the method optimized the first array into a slice, but not the second. If you do not want this conversion, you can disable it using the `range_format` argument:

Since [Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter) uses integer-location and mask-based indexing internally, you cannot use dates and times directly to slice arrays. Fortunately, [Splitter.split*range](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.split*range) accepts slices and arrays as `pd.Timestamp`, `np.datetime64`, `datetime.datetime`, or even datetime-like strings, and automatically converts them to integers for you. It also manages timezones.

The same applies to relative ranges, where the `offset` and `length` arguments can be provided as `pd.Timedelta`, `np.timedelta64`, `datetime.timedelta`, or timedelta-like strings:

Returning to [Splitter.from*splits](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.from*splits). As shown earlier, each split is created by converting a split specification into a sequence of ranges, one for each set. By passing multiple such specifications, you get a two-dimensional array, which is available under [Splitter.splits](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.splits). Let's manually generate expanding splits, with the OOS set having a fixed length of 25%:

backwards (see below), the operation starts at the end of the period and moves to the left.

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/cv/manual*splitter.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/cv/manual*splitter.dark.svg#only-dark){: .iimg loading=lazy }

We know how to build a splitter manually, but most CV schemes involve generating splits through iteration, similar to what we did with the while-loop in our first example. Additionally, the starting point of a split often depends on the previous split, which would require you to explicitly call [Splitter.split*range](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.split*range) on each split to determine its boundaries. To reduce the amount of boilerplate code needed for this workflow, [Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter) includes a collection of class methods, such as [Splitter.from*rolling](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.from_rolling), that can generate a logically coherent schema from a simple user query.

Most of these methods first divide the entire period into windows (either in advance or iteratively), and then split each sub-period using the `split` argument, which is passed directly to [Splitter.split*range](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.split*range) as `new*split`. In this way, the split specification becomes relative to the sub-period and not to the entire period as we did earlier.

!!! info Internally, `slice(None)` (which we have used every time so far) is replaced by the window slice, so that `0.5` would split only the window in half, not the entire period.

The most important method for CV is [Splitter.from*rolling](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.from_rolling), which uses a simple while-loop to append splits until any split exceeds the right boundary of the index. If the last split is shorter than the requested length, it is discarded, so there is usually some unused space at the end of the backtesting period.

But the most interesting question is: where should we place the next split? By default, if there is only one set, the next split is placed immediately after the previous one. If there are multiple sets, the next split is placed right after the first (IS) range in the previous split, so that IS ranges never overlap between splits. Of course, you can control the offset behavior using `offset*anchor*set` (which range in the previous split acts as an anchor?), `offset*anchor` (whether the left or right bound of that range acts as the anchor?), `offset` (the positive or negative distance from the anchor), and `offset*space` (see [RelRange](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.RelRange)).

=== "One set with a gap"

=== "One set with overlaps"

=== "Two sets without overlaps"

Another common approach is to divide the entire period into `n` equally spaced, potentially overlapping windows, as implemented by [Splitter.from*n*rolling](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.from*n*rolling). If the window length is `None` (that is, not provided), it simply calls [Splitter.from*rolling](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.from*rolling) with the length set to `len(index) // n`. Note that unlike the previous method, this one does not allow you to control the offset.

=== "Without length"

=== "With length and without overlaps"

=== "With length and with overlaps"

The windows we generated above all have the same length, which makes it easier to conduct fair experiments in backtesting. However, sometimes, especially when training ML models, we need each training period to include all previous history. Such windows are called expanding and can be generated automatically with [Splitter.from*expanding](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.from*expanding), which works similarly to its rolling counterpart, except that the offset controls the number of windows, the offset anchor is always the end of the previous split (window), and the `min*length` argument specifies a minimum window length. There is also a method [Splitter.from*n*expanding](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.from*n_expanding) that lets you generate a predefined number of expanding windows.

=== "Using number of windows"

Consider a scenario where you want to generate a set of splits, each lasting one year. Using any of the approaches above, you would get splits that last for one year but would most likely start somewhere in the middle of the year. But what if you want each split to start exactly at the beginning of the year? Such time anchors are only possible by grouping or resampling. There are two class methods in [Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter) that enable this behavior: [Splitter.from*ranges](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.from*ranges) and [Splitter.from*grouper](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.from_grouper).

The first method uses [get*index*ranges](https://vectorbt.pro/pvt*ff8edc14/api/base/indexing/#vectorbtpro.base.indexing.get*index_ranges) to translate a user query into a set of start and end indices. It allows you to provide custom start and end dates, resample using a lookback period, select a time range within each day, and more—just like resampling but with even more flexibility :pill:

=== "Quarterly from year start"

=== "Last month for OOS"

=== "Expanding with last quarter for OOS"

The second method takes a grouping or resampling instruction and converts each group into a split. It is based on the method [BaseIDXAccessor.get*grouper](https://vectorbt.pro/pvt*ff8edc14/api/base/accessors/#vectorbtpro.base.accessors.BaseIDXAccessor.get*grouper) and accepts a variety of formats from both VBT and Pandas, including [pandas.Grouper](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Grouper.html) and [pandas.Resampler](https://pandas.pydata.org/docs/reference/resampling.html). The only issue you may encounter is incomplete splits, which can be filtered out using a template provided as `split*check*template` and forwarded down to [Splitter.from*splits](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.from*splits).

=== "Resampling annually"

=== "Removing incomplete years"

=== "Formatting labels"

=== "Using grouping"

So far, we have generated windows based on a predefined schema. However, randomness also plays an important role in CV, especially when it comes to [bootstrapping](https://en.wikipedia.org/wiki/Bootstrapping*(statistics)) and [block bootstrap](https://en.wikipedia.org/wiki/Bootstrapping*(statistics)#Block*bootstrap) in particular. The method [Splitter.from*n*random](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.from*n*random) draws a given number of windows of (optionally) variable length. At the core of this method are two callbacks: `length*choice*func` and `start*choice*func`, which select the next window's length and start point, respectively. By default, they use [numpy.random.Generator.choice](https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.choice.html), which generates a random sample with replacement (meaning the same window can occur more than once). Two additional callbacks, `length*p*func` and `start*p*func`, control the probabilities of picking each entry (for example, to select more windows toward the end of the period).

=== "Variable length"

=== "With probabilities"

For k-fold and many other standard CV schemes where scikit-learn excels, there is a method [Splitter.from*sklearn](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.from_sklearn) that can parse almost any cross-validator that subclasses scikit-learn's `BaseCrossValidator` class.

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/cv/from*sklearn.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/cv/from*sklearn.dark.svg#only-dark){: .iimg loading=lazy }

!!! warning There is a temporal dependency between observations: it makes no sense to use values from the future to forecast values in the past, so ensure that the test period always follows the training period.

The final and most flexible generation method involves calling a UDF that takes a context, including all previously generated splits, and returns a new split to append. This all happens in an infinite while loop; to break out of the loop, the UDF must return `None`. As with many other methods in VBT that take functions as arguments, this method also uses templates to substitute information from the context. The context itself includes the appended and resolved splits (`splits`) and the bounds of each range in each split (but only when `fix_ranges=True`), making the generation process a breeze.

=== "Roll one-year window each month"

=== "Train one business week, test next"

Consider the following splitter that divides the entire period into years, creating one split per year:

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/cv/flawed*splitter.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/cv/flawed*splitter.dark.svg#only-dark){: .iimg loading=lazy }

By default, `closed*end` is set to `False` so that neighboring ranges do not overlap. In this example, however, we intentionally made a mistake by setting `closed*end` to `True`. This causes the splits to overlap by exactly one bar. How can we detect such a mistake after the fact? The [Splitter](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter) class provides several tools to help with this.

The first tool is calculating the bounds of each range. Bounds are represented by two numbers (`index*bounds=False`) or dates (`index*bounds=True`): the start (always inclusive) and the end (exclusive, unless you include it by using `right*inclusive=True`). Depending on your analysis needs, bounds can be returned in two different formats. The first format is a three-dimensional NumPy array, returned by [Splitter.get*bounds*arr](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*bounds*arr). In this array, the first axis corresponds to splits, the second to sets, and the third to bounds:

Another, perhaps more user-friendly, format is a DataFrame returned by [Splitter.get*bounds](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get_bounds). In this DataFrame, each row represents a range and the columns represent the bounds:

and [Splitter.index*bounds](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.index_bounds).

With this, you can see that some IS ranges start before the preceding OOS range ends:

Another tool works with range masks. Since the index is shared by every range, we can convert a range into a mask with the same length as the index, and then stack all masks into a single array. Another benefit of masks is that you can combine them, use logical operators, reduce them, and check for `True` values. The main drawback is memory usage: as shown earlier, 100 splits and 2 sets of 1 year of 1-minute data would use up 100MB of RAM. Just like bounds, there are two methods available: one returns a three-dimensional NumPy array and the other a DataFrame: [Splitter.get*mask*arr](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*mask*arr) and [Splitter.get*mask](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*mask). Let's retrieve the mask in DataFrame format:

In contrast to bounds, the DataFrame lists split and set labels (range labels) in columns instead of rows. To illustrate how masks can be useful, let's answer this question: which ranges cover the year 2021?

You will notice the mistake again: there is an OOS range that clearly extends into the next year. Here is another question: how many dates are covered by each set in each year?

To address potential memory issues, there are special approaches that convert only a subset of ranges into a mask at a time. These approaches use two iteration schemes: by split and by set, implemented by [Splitter.get*iter*split*masks](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*iter*split*masks) and [Splitter.get*iter*set*masks](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*iter*set*masks), respectively. Each method returns a [Python generator](https://realpython.com/introduction-to-python-generators/) that you can use in a loop. Here is how you can answer the question above in a memory-efficient way (if needed):

Bounds and masks are convenient range formats that let's analyze ranges from different perspectives. To save users extra work, there are additional methods that automate this analysis. Since we are mainly interested in whether and how much splits, sets, and ranges overlap, there are four methods that quickly provide these insights: [Splitter.get*split*coverage](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*split*coverage) for split coverage, [Splitter.get*set*coverage](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*set*coverage) for set coverage, [Splitter.get*range*coverage](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*range*coverage) for range coverage, and [Splitter.get*coverage](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.get*coverage) for any of the above. For example, split-relative coverage will return the percentage of bars in the index covered by each split, while total coverage returns the percentage of bars in the index covered by any range.

!!! warning Most of the methods below, except for the plotting method, require the entire mask array to be loaded in memory.

!!! note The default arguments always return a metric relative to the length of the index.

As we saw above, the first split covers 19.24% of the entire period, while both ranges in that split occupy 9.62%, which is exactly 50% of the split. Both sets cover about the same period of time: 38.53% of the entire period. The last metric tells us that 23.14% of the period is not covered by the splitter, which makes sense since the years 2017 and 2022 are incomplete, so no split was made for those years. Finally, why do all ranges cover the same time except for the OOS set in split `2`? It is because that year was a leap year, so the final months had one more day than those months in other years:

So far, we have analyzed coverage relative to the full index. However, there is a special argument, `relative`, that lets us analyze splits and sets relative to total coverage, and ranges relative to split coverage. For example, here is how to get the fraction of IS and OOS sets in their respective splits:

Most periods, except for the leap year, have a near-perfect 50/50 split as expected. We can expand our analysis to check whether the sets overall also follow this 50/50 split:

These two numbers do not sum to one, which (again) points to overlapping ranges. Using the `overlapping` argument, we can check for any overlap of sets within each split, overlap of splits within each set, and any overlaps of ranges globally:

Ranges do not overlap within each split or within each set. However, some overlapping ranges are detected globally, which means they belong to different splits and sets. To get a better view, we can visualize the coverage using [Splitter.plot*coverage](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.plot_coverage):

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/cv/plot*coverage.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/cv/plot*coverage.dark.svg#only-dark){: .iimg loading=lazy }

The Y-axis shows the total number of ranges that cover a particular date. You can see that there are three dates covered by two ranges at the same time.

The last and most powerful tool for detecting overlap is the overlap matrix, which calculates overlaps between splits (`by="split"`), sets (`by="set"`), or ranges (`by="range"`). If `normalize` is True, which is the default, the intersection of two range masks will be normalized by their union. Although this operation is Numba-compiled, it can still be quite expensive: 100 splits with 2 sets would require comparing all `200 * 200 = 40000` range pairs to build the range overlap matrix. Let's finally clarify which ranges are overlapping:

[Splitter.range*overlap*matrix](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.range*overlap_matrix).

Each method above (and many others, including [Splitter.plot](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.plot)) accepts the arguments `split*group*by` and `set*group*by`, which let you group splits and sets, respectively. Their format matches the `group*by` argument, which appears throughout the VBT codebase. For example, if you pass `True`, you can put all ranges in the same bucket and merge them. You can also pass a list with the same length as the number of splits or sets, so that splits or sets with the same unique value will be merged. The actual merging is done by the method [Splitter.merge*split](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.merge_split).

For example, let's retrieve the bounds of each entire split:

This makes certain types of analysis much easier :magic_wand:

We will end this page with an overview of the methods that can be used to modify a splitter. Let's build a splitter that includes just one set representing the current year:

Since the class [Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter) is a subclass of [Analyzable](https://vectorbt.pro/pvt*ff8edc14/documentation/building-blocks/#analyzing), we can get a quick and insightful overview of key metrics and plots:

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/cv/plots1.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/cv/plots1.dark.svg#only-dark){: .iimg loading=lazy }

!!! info Since there is only one split, most metrics are hidden from the statistics.

As we have seen, you can select specific splits and sets using standard Pandas indexing (which is another great feature of [Analyzable](https://vectorbt.pro/pvt_ff8edc14/documentation/building-blocks/#analyzing)). Since we are not interested in incomplete years, let's remove the first and last splits:

Now, let's split the only set into three: a train set covering the first two quarters, a validation set covering the third quarter, and a test set covering the last quarter. This is possible using the method [Splitter.split*set](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.split*set), which accepts the split specification and the labels for the new sets as `new*split` and `new*set*labels`, respectively. We will use a function template to divide the set:

covered by the original set. Why not the entire index? Because we are only splitting a subset of it.

[Splitter.split*range](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.split_range), which is used to split each range of the original set.

!!! info Each operation on a splitter returns a new splitter: no information is changed in place, to avoid interfering with caching and to keep the splitter (like any other VBT object) side effect free.

Take a look at the new splitter:

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/cv/plots2.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/cv/plots2.dark.svg#only-dark){: .iimg loading=lazy }

As you might have guessed, there is also a method that can merge multiple sets: [Splitter.merge*sets](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.merge_sets). Your homework is to merge the "valid" and "test" sets into "test" :wink:

We have done our job perfectly, so let's move on to applications! :airplane:

[:material-language-python: Python code](https://vectorbt.pro/pvt*ff8edc14/assets/jupytext/tutorials/cross-validation/splitter.py.txt){ .md-button target="blank*" } [:material-notebook-outline: Notebook](https://github.com/polakowo/vectorbt.pro/blob/notebooks/CrossValidation.ipynb){ .md-button target="blank_" }

**Examples:**

Example 1 (pycon):
```pycon
>>> splitter = vbt.Splitter.from_rolling(
...     data.index, 
...     length=360, 
...     split=0.5,
...     set_labels=["IS", "OOS"]
... )
>>> splitter.plot().show()
```

Example 2 (pycon):
```pycon
>>> splitter.splits
set                         IS                      OOS
split                                                  
0          slice(0, 180, None)    slice(180, 360, None)
1        slice(180, 360, None)    slice(360, 540, None)
2        slice(360, 540, None)    slice(540, 720, None)
3        slice(540, 720, None)    slice(720, 900, None)
4        slice(720, 900, None)   slice(900, 1080, None)
5       slice(900, 1080, None)  slice(1080, 1260, None)
6      slice(1080, 1260, None)  slice(1260, 1440, None)
7      slice(1260, 1440, None)  slice(1440, 1620, None)
8      slice(1440, 1620, None)  slice(1620, 1800, None)
```

Example 3 (pycon):
```pycon
>>> splitter.index
DatetimeIndex(['2017-08-17 00:00:00+00:00', '2017-08-18 00:00:00+00:00',
               '2017-08-19 00:00:00+00:00', '2017-08-20 00:00:00+00:00',
               ...
               '2022-10-28 00:00:00+00:00', '2022-10-29 00:00:00+00:00',
               '2022-10-30 00:00:00+00:00', '2022-10-31 00:00:00+00:00'],
    dtype='datetime64[ns, UTC]', name='Open time', length=1902, freq='D')
              
>>> splitter.wrapper.index
RangeIndex(start=0, stop=9, step=1, name='split')

>>> splitter.wrapper.columns
Index(['IS', 'OOS'], dtype='object', name='set')
```

Example 4 (pycon):
```pycon
>>> oos_splitter = splitter["OOS"]
>>> oos_splitter.splits
split
0      slice(180, 360, None)
1      slice(360, 540, None)
2      slice(540, 720, None)
3      slice(720, 900, None)
4     slice(900, 1080, None)
5    slice(1080, 1260, None)
6    slice(1260, 1440, None)
7    slice(1440, 1620, None)
8    slice(1620, 1800, None)
Name: OOS, dtype: object
```

---

## Cross-validation

**URL:** https://vectorbt.pro/pvt_ff8edc14/tutorials/cross-validation.md

??? youtube "Cross-validation on YouTube" <iframe class="youtube-video" src="https://www.youtube.com/embed/_BSSPZplLHs?si=s-lqiyASBqeGigW9" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

After developing a rule-based or machine learning-based strategy, it is time to backtest it. If our first backtest yields a low Sharpe ratio, we might tweak the strategy to try to improve it. After several rounds of parameter adjustments, we may arrive at a "flawless" set of parameters and a strategy showing an exceptional Sharpe ratio. However, in live trading, the strategy may perform poorly, resulting in losses. What went wrong?

Markets naturally contain noise—small and frequent inconsistencies in price data. When designing a strategy, we should avoid optimizing for a single period, because the model may fit the historical data so closely that it fails to predict the future effectively. This is similar to tuning a car for one specific racetrack and expecting it to perform equally well everywhere. Especially with VBT, which allows us to search large databases of historical market data for patterns, it can be easy to create complex rules that appear highly accurate at predicting price changes (see [*p*-hacking](https://en.wikipedia.org/wiki/Data_dredging)) but make random guesses when applied to data outside the sample used to build the model.

Overfitting (also known as [curve fitting](https://en.wikipedia.org/wiki/Curve*fitting)) typically occurs for one or more of these reasons: mistaking noise for signal, or excessively tweaking too many parameters. To avoid overfitting, we should use [cross-validation](https://en.wikipedia.org/wiki/Cross-validation*(statistics)) (CV), which involves splitting a data sample into complementary subsets, analyzing one subset called the training or *in-sample* (IS) set, and validating the analysis on the other subset called the validation or *out-of-sample* (OOS) set. This procedure is repeated until we have multiple OOS periods and can calculate statistics from all these results combined. The key questions we need to ask are: are our parameter choices robust in the IS periods? Is our performance robust in the OOS periods? If not, we are essentially guessing, and as quant investors we should not leave room for second-guessing when real money is at stake.

Let's consider a simple strategy based on a moving average crossover.

First, we will pull some data:

Next, let's create a parameterized mini-pipeline that takes data and parameters and returns the Sharpe ratio, which should reflect our strategy's performance on that test period:

`sma*crossover*perf` to accept arguments wrapped with [Param](https://vectorbt.pro/pvt*ff8edc14/api/utils/params/#vectorbtpro.utils.params.Param), build the grid of parameter combinations, run `sma*crossover_perf` for each, and combine the results using concatenation.

Let's test a grid of `fast*window` and `slow*window` combinations over one year of that data:

`sma*crossover*perf`.

Remember, the right bound is inclusive.

reduce parameter combinations.

decorator must be prefixed with `_`.

to execute each parameter combination. This engine accepts arguments to clear the cache and collect memory garbage. Here, we do this every 50 iterations to manage memory usage.

[=100% "Combination 990/990"]{: .candystripe .candystripe-animate }

It took 30 seconds to test 990 parameter combinations, or about 30 milliseconds per run. Below, we sort the Sharpe ratios in descending order to find the best parameter combinations:

It appears that `fast*window=15` and `slow*window=20` could make us very wealthy! But before putting all our savings on that configuration, let's test it on the following year:

if they are single values or if we do not want to build a parameter grid. They are simply forwarded to `sma*crossover*perf`.

The result is disappointing, but did we at least outperform a baseline? Let's calculate the Sharpe ratio for the buy-and-hold strategy during that year:

portfolio method names. The first run may take some time because it needs to be compiled.

It seems that our strategy performed very poorly :speak*no*evil:

But this was only one optimization test. What if that period was an outlier and our strategy actually performs well *on average*? Let's try to answer this by repeating the test above on each consecutive 180-day period in the data:

so it can be added to [pandas.Timestamp](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Timestamp.html).

and optimization performance for each IS period.

process one split, increment the starting date, and repeat. This works naturally as a while-loop, and we continue as long as both periods are fully covered by our index.

left bound of the OOS period. Since [pandas.DataFrame.loc](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.loc.html) includes the right bound, we simply subtract one nanosecond from it (keep this trick in mind!).

index so we know which parameter combination it corresponds to.

[=100% "Period 9/9"]{: .candystripe .candystripe-animate }

[pandas.DataFrame.from*dict](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.from*dict.html#pandas.DataFrame.from_dict) to combine them into a single DataFrame.

let's create just one Series keyed by period.

to concatenate them into a single Series.

from the corresponding OOS set. Since both Series are linked by `split`, `fast*window`, and `slow*window`, remove `period` before doing this operation.

We have collected information for 9 splits and 10 periods. Now it is time to evaluate the results! The index of each Series makes it easy to connect information and analyze everything together: the `split` level connects elements within the same split, the `period` level links elements in the same time period, and `fast*window` and `slow*window` relate elements by parameter combination. To begin, let's compare their distributions:

Although the OOS results are much lower than the best IS results, our strategy still outperforms the baseline on average! Over 50% of periods have a Sharpe ratio of 0.96 or higher, while the baseline's median sits at only -0.03. Another way to analyze this data is by plotting it. Since all these Series can be linked by period, we will use the `period` level as the X-axis and the performance (Sharpe in this case) as the Y-axis. Most Series can be shown as lines, but because IS sets include multiple parameter combinations, we should show their distributions as boxes instead:

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/cv/example.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/cv/example.dark.svg#only-dark){: .iimg loading=lazy }

Here is how to interpret the plot above.

The green line tracks the performance of the best parameter combination in each IS set. The fact that it touches the highest point in each box shows that our best-parameter selection algorithm works correctly. The dashed orange line represents the performance of the "buy-and-hold" strategy during each period as the baseline. The red line shows the test performance; it starts at the second range and corresponds to the parameter combination that delivered the best result in the previous period (that is, the previous green dot).

The semi-transparent blue boxes show the distribution of Sharpe ratios during the IS (training) periods, meaning each box summarizes 990 parameter combinations tested in each optimization period. There is no box on the far right because the last period is an OOS (test) period. For example, period `6` (which is the seventh period, since counting starts at 0) includes all Sharpe ratios from `1.07` to `4.64`. That likely means there was an upward trend during that period. Here is the proof:

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/cv/example*candlestick.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/cv/example*candlestick.dark.svg#only-dark){: .iimg loading=lazy }

No matter which parameter combination we select for that time, the Sharpe ratio remains relatively high and could give us a false sense of strategy performance. To make sure this is not the case, we need to compare the test performance to other points. That's the main reason we drew lines over the [box plot](https://en.wikipedia.org/wiki/Box_plot). For example, we can see that for period `6`, both the baseline and test performances are below the first quartile (or 25th percentile). They are worse than at least 75% of the parameter combinations tested during that time range:

parameter combination used for testing.

The chart gives us mixed feelings: on the one hand, the chosen parameter combination outperforms most of the combinations tested during 5 different time periods. On the other hand, it fails to beat even the lowest-performing 25% of parameter combinations in 3 other periods. In defense of our strategy, the number of splits is relatively low. Most statisticians agree that at least 100 samples are needed for meaningful results, so this analysis offers only a small glimpse into the true performance of the SMA crossover.

So, how can we make all of this simpler?

[:material-language-python: Python code](https://vectorbt.pro/pvt*ff8edc14/assets/jupytext/tutorials/cross-validation/index.py.txt){ .md-button target="blank*" } [:material-notebook-outline: Notebook](https://github.com/polakowo/vectorbt.pro/blob/notebooks/CrossValidation.ipynb){ .md-button target="blank_" }

**Examples:**

Example 1 (pycon):
```pycon
>>> from vectorbtpro import *

>>> data = vbt.BinanceData.pull("BTCUSDT", end="2022-11-01 UTC")
>>> data.index
DatetimeIndex(['2017-08-17 00:00:00+00:00', '2017-08-18 00:00:00+00:00',
               '2017-08-19 00:00:00+00:00', '2017-08-20 00:00:00+00:00',
               ...
               '2022-10-28 00:00:00+00:00', '2022-10-29 00:00:00+00:00',
               '2022-10-30 00:00:00+00:00', '2022-10-31 00:00:00+00:00'],
    dtype='datetime64[ns, UTC]', name='Open time', length=1902, freq='D')
```

Example 2 (pycon):
```pycon
>>> @vbt.parameterized(merge_func="concat")  # (1)!
... def sma_crossover_perf(data, fast_window, slow_window):
...     fast_sma = data.run("sma", fast_window, short_name="fast_sma")  # (2)!
...     slow_sma = data.run("sma", slow_window, short_name="slow_sma")
...     entries = fast_sma.real_crossed_above(slow_sma)
...     exits = fast_sma.real_crossed_below(slow_sma)
...     pf = vbt.Portfolio.from_signals(
...         data, entries, exits, direction="both")  # (3)!
...     return pf.sharpe_ratio  # (4)!
```

Example 3 (pycon):
```pycon
>>> perf = sma_crossover_perf(  # (1)!
...     data["2020":"2020"],  # (2)!
...     vbt.Param(np.arange(5, 50), condition="x < slow_window"),  # (3)!
...     vbt.Param(np.arange(5, 50)),  # (4)!
...     _execute_kwargs=dict(  # (5)!
...         clear_cache=50,  # (6)!
...         collect_garbage=50
...     )
... )
>>> perf
fast_window  slow_window
5            6              0.625318
             7              0.333243
             8              1.171861
             9              1.062940
             10             0.635302
                                 ...   
46           48             0.534582
             49             0.573196
47           48             0.445239
             49             0.357548
48           49            -0.826995
Length: 990, dtype: float64
```

Example 4 (pycon):
```pycon
>>> perf.sort_values(ascending=False)
fast_window  slow_window
15           20             3.669815
14           19             3.484855
15           18             3.480444
14           21             3.467951
13           19             3.457093
                                 ...   
36           41             0.116606
             37             0.075805
42           43             0.004402
10           12            -0.465247
48           49            -0.826995
Length: 990, dtype: float64
```

---

## Applications

**URL:** https://vectorbt.pro/pvt_ff8edc14/tutorials/cross-validation/applications.md

**Contents:**
- Taking
  - Without stacking
    - Complex objects
  - Column stacking
  - Row stacking
- Applying
  - Iteration schemes
  - Merging
  - Decorators
- Modeling

Now that we have a splitter instance, what should we do next?

Remember, cross-validation (CV) involves running a backtesting job on each range. Thanks to VBT's ability to process two-dimensional data, there are two main approaches:

There is also a hybrid approach. For instance, you can build a two-dimensional array for each set and backtest it independently from the other sets. The best method depends on your RAM requirements and performance needs. Two-dimensional arrays are processed faster, but adding too many columns can reduce performance because your system may start using swap memory.

Taking refers to extracting one or more "slices" from an array-like object. This is handled by the [Splitter.take](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.take) method. This method receives an object, iterates over each specified range, and extracts the range from the object using [Splitter.take*range](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.take*range). This straightforward method performs `arr.iloc[range*]` on Pandas-like arrays and `arr[range*]` on NumPy arrays.

Since many VBT classes inherit the indexing schema of Pandas, this method can also extract slices from VBT objects such as [Portfolio](https://vectorbt.pro/pvt_ff8edc14/api/portfolio/base/#vectorbtpro.portfolio.base.Portfolio).

After collecting all slices, you can stack them by rows (`stack*axis=0`), by columns (`stack*axis=1`, which is the default), stack only splits and sets, or choose not to stack them at all. If some slices should not be stacked, they will be returned as a single Pandas Series containing the slices as values. This may seem unusual—having an array as a value within another array—but it is more convenient for indexing than using a list.

Let's split the close price using the default arguments:

If you are wondering about this format: it is a regular Pandas Series with the split and set labels as the index and the close price slices as values—in other words, a `pd.Series` inside a `pd.Series`. :stuck*out*tongue: Keep in mind that array values can be any complex Python objects. For example, let's get the close price for the test set in 2020:

And here is how easy it is to apply a UDF to each range:

One of the unique features of VBT is the standardized behavior of its classes. Since this package is highly specialized in processing Pandas and NumPy arrays, most classes act as a proxy between the user and a set of such arrays. Each class essentially extends the features of Pandas and NumPy and allows you to build connections between multiple arrays based on shared metadata stored in a [wrapper](https://vectorbt.pro/pvt*ff8edc14/documentation/building-blocks/#wrapping). Because this wrapper can be sliced just like a regular Pandas array, you can also slice most VBT objects that contain this wrapper, including [Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter). You can slice these objects using the same indexing API provided by Pandas arrays (thanks to [indexing](https://vectorbt.pro/pvt*ff8edc14/documentation/building-blocks/#indexing)), which means you can pass most VBT objects directly to [Splitter.take](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.take)!

For example, let's analyze the performance of a portfolio during different market regimes. First, we will use the forward-looking label generator [TRENDLB](https://vectorbt.pro/pvt_ff8edc14/api/labels/generators/trendlb/#vectorbtpro.labels.generators.trendlb.TRENDLB) to label each data point with either 1 (uptrend), 0 (downtrend), or NaN (unclassified). Given the volatility of our data, we will mark an uptrend when the price rises by 100% from its previous low, and a downtrend when the price falls by 50% from its previous high:

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/cv/trendlb.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/cv/trendlb.dark.svg#only-dark){: .iimg loading=lazy }

!!! tip If you are unsure which pair of thresholds to use, take a look at the plot produced by the labeler and choose the thresholds that work best for your needs.

Next, we will build a splitter that converts the labels into splits:

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/cv/trend*splitter1.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/cv/trend*splitter1.dark.svg#only-dark){: .iimg loading=lazy }

In the next step, we will run the full grid of parameter combinations on the entire period using column stacking, and extract the returns accessor of the type [ReturnsAccessor](https://vectorbt.pro/pvt_ff8edc14/api/returns/accessors/#vectorbtpro.returns.accessors.ReturnsAccessor), which will let's analyze the returns. For comparison, we will also do the same with our baseline model.

Now, take both slices from the accessor (remember that most VBT objects are indexable, including accessors) and plot the Sharpe heatmap for each market regime:

We can see that it takes a lot of effort (and some may even say luck) to pick the right parameter combination and consistently outperform the baseline. Since both pictures are completely different, we cannot rely on a single parameter combination. Instead, we have to recognize the current market regime and adjust our actions accordingly, which is a major challenge itself. This analysis should be used with caution, though: there may be position overflow from one market regime to another, which can skew the results, since both periods are part of a single backtest. Still, we have gained another piece of valuable information :detective:

But what if we try to take slices from the portfolio itself? This operation would fail because each split contains gaps, and a portfolio can only be indexed using non-interrupting ranges, not splits with gaps. Therefore, we need to break up each split into multiple smaller splits, also called "split parts". Fortunately, there are two features that can help with this: [Splitter.split*range](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.split*range) accepts an option "by*gap" as `new*split` to split a range by gaps, while [Splitter.break*up*splits](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.break*up*splits) can apply this operation to each split. This way, we can flatten the splits so that only one trend period is processed at a time. We will also sort the splits by their starting index so they appear in the same temporal order as the labels:

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/cv/trend*splitter2.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/cv/trend*splitter2.dark.svg#only-dark){: .iimg loading=lazy }

One more trick: instead of calling [Splitter.take](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.take), you can call `split` on the object directly!

Let's analyze the median. This means there are 50 percent of the parameter combinations with the same value or better, and, conversely, 50 percent with the same value or worse.

Now, let's visualize it. Replace the labels in `trendlb` with the newly computed values.

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/cv/trend*perf.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/cv/trend*perf.dark.svg#only-dark){: .iimg loading=lazy }

Do you notice anything unusual? At least 50 percent of the parameter combinations during the last uptrend have a negative Sharpe :thinking: My explanation is that moving averages are lagging indicators, and by the time they reacted to the previous sharp decline, the market had already reached the next top. In other words, the rebound happened so quickly that any short positions from the earlier decline were not able to close out on time.

This section explores the second approach mentioned at the start of the page, where you apply a UDF to each range separately. But what if you stack all the slices into a single array and apply `get*total*return` just once for a performance improvement? As it turns out, you can manually stack the slices using [pandas.concat](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.concat.html):

As you can see, even though this operation produces a lot of NaNs, the resulting format is perfectly acceptable to VBT. Let's apply our UDF to this array:

Pure magic :sparkles:

However, the stacking approach above works only when splitting Pandas objects. What about NumPy arrays and more complex VBT objects? You can instruct [Splitter.take](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.take) to handle the stacking for you. This method uses [column*stack*merge](https://vectorbt.pro/pvt*ff8edc14/api/base/merging/#vectorbtpro.base.merging.column*stack*merge) to efficiently stack any array-like objects. For example, you can replicate the format above with a single line of code:

To reduce the number of NaNs in the stacked data, you can reset the index of each slice before stacking by adding the prefix "reset_" to any "stacked" option provided as `into`:

You can also tell the method to align each slice by its end point instead of its start point, which will move NaNs to the beginning of the array:

!!! tip If all slices have the same length, both alignments will produce the same array.

As you can see, there are two potential issues with this operation: the final array does not have a datetime index, and the slices can have different lengths, which means there may still be some NaNs in the array. Additionally, stacking training and test sets together is not always what you want since they belong to different pipelines. Instead, stack only the splits that belong to the same set, which will also make the slices roughly the same length, by using "reset*stacked*splits" as `into`:

This format might look a bit unusual, but it is simply a Series with the set labels as the index and the stacked close price slices as the values:

By resetting the index, we save a significant amount of RAM: our arrays now store only `182 * 8 = 1456` values instead of `1461 * 8 = 11688`, which is an 88% reduction in memory usage. But how do we access the index associated with each column? We can slice it just like a regular array!

Another way to obtain index information is by attaching the bounds to the range labels using `attach*bounds`. This argument can be set to `True` or "index" to attach the bounds in either integer or datetime format. Let's use the latter and also enable `right*inclusive` to make the right bound inclusive, which is useful for indexing with `loc`:

However, to keep the index clean, we will start with the arrays without bounds. We now have two arrays: one for training and another for testing. Next, let's modify our `sma*crossover*perf` pipeline from the first page to run on a single set. Replace the `data` argument with `close`, and add an argument for the frequency required by Sharpe since our index is no longer datetime-like.

Apply this function on the training set to get performance for each parameter combination and split:

[=100% "Combination 990/990"]{: .candystripe .candystripe-animate }

A total of 990 parameter combinations ran in 20 seconds, or 20ms per run :fire:

Now, let's generate a performance heatmap for each split:

<div class="grid cards width-eighty" markdown>

Looking at the plot above, you can spot several yellow points that may be strong candidates for the strategy. However, rather than picking the best parameter combination as we did on the first page, let's take a more robust approach by performing a neighborhood analysis. We will look for Sharpe ratios that are surrounded by other high Sharpe ratios, which helps to reduce the influence of outliers and to build a more robust optimizer.

This approach is well quantified by first converting the `train*perf` Series into a DataFrame using the [BaseAccessor.unstack*to*df](https://vectorbt.pro/pvt*ff8edc14/api/base/accessors/#vectorbtpro.base.accessors.BaseAccessor.unstack*to*df) accessor method, then applying [GenericAccessor.proximity*apply](https://vectorbt.pro/pvt*ff8edc14/api/generic/accessors/#vectorbtpro.generic.accessors.GenericAccessor.proximity_apply), which rolls a two-dimensional window over the matrix and applies a UDF for reduction. This mini-pipeline should be applied separately to each split. We will use a window size of 2, meaning two rows and columns around the central point, for a total of `(n * 2 + 1) ** 2 = 25` values. As a UDF, we will use the median, so each value will indicate that at least 50% of its neighbors are better than it. The UDF will also filter out windows that have fewer than 20 valid values.

window flattened to one dimension.

Level names could also be used here.

At first glance, it might seem that all values are NaN, but let's check this:

<div class="grid cards width-eighty" markdown>

Fans of [computer vision](https://en.wikipedia.org/wiki/Computer_vision) might recognize what we did above: we used a 5x5 neighboring window as a [filter](https://ai.stanford.edu/~syyeung/cvweb/tutorial1.html) that replaces each pixel with the median pixel value from itself and its neighboring pixels. The result is a smoother image with sharp features removed (in our case, Sharpe outliers). For example, in the first split, the highest Sharpe decreased from `2.5` to `1.3`, which is still impressive, because it means there are points with at least 50% of neighboring points having a Sharpe of `1.3` or higher! We can now search in each split for the parameter combination with the highest proximity performance:

What are we waiting for? Let's test these combinations on our test set! But how do we apply each parameter combination to each column in the test array? Normally, each parameter combination would be applied to the entire input, but here's the trick: use templates to instruct the `parameterized` decorator to provide only one column at a time, matching the parameter combination being processed.

config). Here, we select the column from our test data with the same index as the parameter config. The index is wrapped in a list to run the pipeline on a DataFrame with meaningful columns.

level to avoid computing a product between them.

Let's compare these values to the baseline:

Not bad! Our model outperforms the baseline for three years in a row.

Just as we stacked ranges along columns, we can also stack ranges along rows. The major difference is that column stacking is intended for independent tests, while row stacking combines ranges into the same test, introducing temporal dependency between them.

Row stacking is ideal for block resampling, which is essential for time-series bootstrapping. The bootstrap is a flexible and powerful statistical tool used to quantify uncertainty. Instead of obtaining independent datasets (which are scarce in finance), we repeatedly generate new datasets by sampling observations from the original dataset. Each of these "bootstrap datasets" is created by sampling *with replacement*, resulting in a dataset of the same size as the original. This means that some observations may appear multiple times, while others may not appear at all (about two-thirds of the original data points are present in each bootstrap sample). Since we are working with time series, we should not simply sample observations with replacement; instead, we create blocks of consecutive observations and sample those. Afterward, we paste the sampled blocks together to create a bootstrap dataset (learn more [here](https://asbates.rbind.io/2019/03/30/time-series-bootstrap-methods/)).

For our example, we will use the [moving block bootstrap](https://en.wikipedia.org/wiki/Bootstrapping*(statistics)#Time*series:*Moving*block_bootstrap), which involves rolling a fixed-size window with an offset of one bar:

We have generated 1864 blocks. Next, we need to sample. To create one sample, shuffle the blocks (i.e., splits) with replacement. You can do this easily using [Splitter.shuffle*splits](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.shuffle_splits). We also need to limit the number of blocks so that the total number of data points roughly matches the original dataset:

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/cv/sample*splitter.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/cv/sample*splitter.dark.svg#only-dark){: .iimg loading=lazy }

Let's calculate the returns, extract the slices that correspond to the blocks in the splitter, and stack them along the rows:

We have created a "frankenstein" price series!

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/cv/frankenstein.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/cv/frankenstein.dark.svg#only-dark){: .iimg loading=lazy }

However, one sample is not enough. To improve the accuracy of our estimates, we should generate 100, 1000, or even 10000 samples.

[=100% "Sample 1000/1000"]{: .candystripe .candystripe-animate }

We can now analyze the distribution of any statistic of interest:

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/cv/sharpe*boxplot.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/cv/sharpe*boxplot.dark.svg#only-dark){: .iimg loading=lazy }

This histogram provides an estimate of the distribution shape of the sample Sharpe, allowing us to answer questions about how much the Sharpe varies across samples. Because this bootstrap distribution is symmetric, we can use percentile-based confidence intervals. For example, a 95% confidence interval is given by the 2.5th and 97.5th percentiles:

This approach can be applied to almost any statistic or estimator, including more complex backtesting metrics.

While the "taking" approach lets us work with object slices directly, the "applying" approach uses [Splitter.apply](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.apply) to run a UDF on each range. This not only takes care of the "taking" for us, but also makes it easy to combine the outputs from the UDF. First, this method determines the ranges to iterate over. Like other methods, it accepts `split*group*by` and `set*group*by` to merge ranges, as well as the arguments `split` and `set*` to select specific (merged) ranges. Next, while iterating over each range, it substitutes any templates and other instructions in the positional and keyword arguments that are meant for the UDF. For example, by wrapping an argument with the class [Takeable](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Takeable), the method will select a slice from it and replace the instruction with that slice. The arguments prepared for each iteration are collected into a list and passed to the executor, [execute](https://vectorbt.pro/pvt*ff8edc14/api/utils/execution/#vectorbtpro.utils.execution.execute), which you may already be familiar with. The executor performs all iterations lazily and can also combine the outputs. *Lazy* here means that none of the arrays are sliced until the range is executed—which is great for memory usage :heartbeat:

Let's look at a simple example that calculates the total return for each close slice:

You could also pass this as a keyword argument, for example, `sr=vbt.Takeable(data.close)`.

It's really that easy!

Templates can be used as well:

Or, you can manually select the range inside your function:

!!! tip Results are slightly different because slicing returns is more accurate than slicing the price.

You can also take slices from more complex VBT objects:

Let's run the function above on the whole split:

If you want to select specific ranges to run the pipeline on, just use `split` and `set_`, which can be an integer, a label, or a sequence of such values:

Now, let's apply this approach to cross-validate our SMA crossover strategy:

parameter combinations and show only the one for splits below.

[=100% "Split 4/4"]{: .candystripe .candystripe-animate }

Let's find the best parameter combinations and pass them to the test set using templates:

and `best*slow*windows` appear in the same order as the splits in the splitter. If the order is different, use `split_label` instead.

We have now effectively outsourced the steps of range iteration, taking, and execution.

The method [Splitter.apply](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.apply) supports multiple iteration schemes. For example, it can iterate over the selected ranges in either split-major or set-major order as a single sequence. It can also group the splits/sets of the same set/split into a single bucket and run them as one iteration—split-wise and set-wise, respectively. Why is this important? Consider a scenario where your UDF needs to write results to an object and then access those results in a specific order. For instance, you might want an OOS range to read the results from the previous IS range, which is common in parameterized CV. In that case, the iteration can be in any order if execution is sequential, in any major order if (carefully) running across multiple threads, and in split-wise order if execution uses multiple processes, since sets need to share memory.

Let's cross-validate our SMA crossover strategy in a single call! When an IS range is processed, find the parameter combination with the highest Sharpe ratio and return it. When an OOS range is processed, access the parameter combination from the previous IS range and use it for testing. If you look at the context available in each iteration, there is no variable that holds previous results: you need to manually store, write, and access them. We will use set-major iteration so that the splits in the training set are processed first.

Wrap it with a list to return a Series, rather than a single value. This gives a nicer index.

to return a Series instead of a single value for a better index.

[=100% "Iteration 8/8"]{: .candystripe .candystripe-animate }

We end up with 8 iterations, one per range: the first 4 iterations are for the training ranges, which took the most time to run, and the last 4 iterations are for the test ranges, which ran almost instantly due to having just one parameter combination. Let's concatenate the training results from `train*perf*dict` and take a look at what is inside `cv_perf`:

Same results, awesome!

Another powerful feature of this method is that it can merge a wide range of outputs: from single values and Series, to DataFrames, and even tuples of them. There are two main merging options: merging all outputs into a single object (`merge*all=True`), and merging by the main unit of iteration (`merge*all=False`). The first option works as follows: it flattens all outputs into a single sequence, resolves the merging function using [resolve*merge*func](https://vectorbt.pro/pvt*ff8edc14/api/base/merging/#vectorbtpro.base.merging.resolve*merge_func), and applies the merging function to that sequence. If no merging function is specified, it wraps the sequence into a Pandas Series (even if each output is a complex object). If each output is a tuple, it returns multiple such Series. Let's see this in action by returning both entries and exits, and stacking them along the columns:

You can then replace NaN values with `False` and backtest the results. If you prefer not to have as many NaN values, use "reset*column*stack" as the `merge_func`. You can also provide multiple merging functions (as a tuple) if your UDF returns outputs in different formats.

!!! note Even though you can return multiple different formats, the formats must remain the same across all ranges.

As mentioned earlier, you can also merge outputs by the main unit of iteration. Let's run the same UDF but only stack the masks that belong to the same split:

With this approach, each mask covers a full year and can be backtested as a whole. The additional `set` level provides information about which set each timestamp belongs to.

If the start and end dates for a range cannot be determined from the merged data alone, you can instruct the method to attach this information. Let's get the total number of signals:

Finally, to show just how powerful merging functions can be, let's create a custom merging function that plots the returned signals based on the set!

To determine which results belong to which set, we can use `keys`.

and [SignalsAccessor.plot*as*exits](https://vectorbt.pro/pvt*ff8edc14/api/signals/accessors/#vectorbtpro.signals.accessors.SignalsAccessor.plot*as_exits) to plot the signals as entry and exit markers, respectively.

interactions in the same way.

otherwise, duplicates may appear.

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/cv/plot*entries*and*exits.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/cv/plot*entries*and*exits.dark.svg#only-dark){: .iimg loading=lazy }

As you can see, [Splitter.apply](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.apply) is a flexible method that can execute any UDF on each range in the splitter. It can not only return arrays in an analysis-friendly format, but also post-process and merge the outputs using another UDF, making it ideal for quick CV.

Even the method above is not the limit of automation that VBT provides. Just like the decorator [@parameterized](https://vectorbt.pro/pvt*ff8edc14/api/utils/params/#vectorbtpro.utils.params.parameterized), which can enhance any function with parameter processing logic, there is also a decorator [@split](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/decorators/#vectorbtpro.generic.splitting.decorators.split) that can enrich almost any function with split processing logic. This decorator works simply: it wraps a function, resolves a splitting specification into a splitter, and forwards all arguments to [Splitter.apply](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.apply). This makes the CV process pipeline-centric instead of splitter-centric.

There are several ways to make a function splittable:

If you do not pass any arguments to the decorator, or if you want to override an argument, you can add a prefix `*` to an argument name to direct it to [@split](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/decorators/#vectorbtpro.generic.splitting.decorators.split) rather than to the function itself:

One potential inconvenience with this approach is that for each new data input, you need to manually construct a splitter using the index from the same data. To solve this, the decorator can also accept instructions on how to create a splitter from the provided data. The instruction consists of a method name (or an actual callable) provided as `splitter`, such as "from*rolling", along with keyword arguments to this method as `splitter*kwargs`. For example, let's roll a window of 30 days for the year 2020:

To avoid wrapping each object to be sliced with [Takeable](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Takeable), you can also provide a list of such arguments as `takeable*args`:

In this example, a new splitter is created from every data instance you provide.

You can also combine multiple decorators. For example, take the `sma*crossover*perf` function from the first page, which we already decorated with [@parameterized](https://vectorbt.pro/pvt_ff8edc14/api/utils/params/#vectorbtpro.utils.params.parameterized), and decorate it so it splits the entire period into 60 percent for the training set and 40 percent for the test set:

to build a single split.

[Splitter.apply](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.apply).

Next, we will run the full parameter grid on the training set only.

[@parameterized](https://vectorbt.pro/pvt*ff8edc14/api/utils/params/#vectorbtpro.utils.params.parameterized) accept `execute*kwargs`. To distinguish between them, we pass `p*execute*kwargs`, let [@split](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/decorators/#vectorbtpro.generic.splitting.decorators.split) rename it to `*execute*kwargs` using `forward*kwargs*as`, and then forward the argument to [@parameterized](https://vectorbt.pro/pvt*ff8edc14/api/utils/params/#vectorbtpro.utils.params.parameterized).

[Splitter.apply](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.apply), you can pass it directly to [@split](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/decorators/#vectorbtpro.generic.splitting.decorators.split), or include it in `*apply*kwargs` when calling an already decorated function.

[=100% "Split 1/1"]{: .candystripe .candystripe-animate }

We can now validate the optimization performance on the test set:

[=100% "Split 1/1"]{: .candystripe .candystripe-animate }

!!! tip If you want to receive a proper Series instead of a single value, disable `squeeze*one*split` and `squeeze*one*set` in [Splitter.apply](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter.apply) using `*apply_kwargs`.

However, even this decorator is not the final step in automation: there is a special decorator [@cv*split](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/decorators/#vectorbtpro.generic.splitting.decorators.cv*split) that combines [@split](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/decorators/#vectorbtpro.generic.splitting.decorators.split) and [@parameterized](https://vectorbt.pro/pvt*ff8edc14/api/utils/params/#vectorbtpro.utils.params.parameterized) to run the full parameter grid on the first set, and the best parameter combination on the remaining sets. How is the best parameter combination chosen? The `selection` argument can be a template that receives previous results (available as `grid*results` in the context) and returns the integer position of the parameter combination you define as best. Additionally, the decorator can return only the best results (`return*grid=False`), include the grid results from the training set (`return*grid=True`), or provide the grid for all sets (`return_grid="all"`).

Since running the entire grid of parameter combinations can take a long time, let's rewrite our pipeline with Numba to return the Sharpe ratio for a single parameter combination:

Test the function on the full history:

!!! note All Numba functions used here expect a two-dimensional NumPy array as input.

Finally, let's define and run CV in parallel:

will also be automatically passed to [@parameterized](https://vectorbt.pro/pvt_ff8edc14/api/utils/params/#vectorbtpro.utils.params.parameterized). Both decorators can use different merging functions if needed.

so we need to pass the wrapper to assign each value to its corresponding column name.

and can be used to provide an index if none can be extracted from the "takeable" arrays.

Note that the test set will still use the previous grid, not its own.

!!! info By default, the highest value is selected. To select the lowest value, set `selection="min"` in [@split](https://vectorbt.pro/pvt_ff8edc14/api/generic/splitting/decorators/#vectorbtpro.generic.splitting.decorators.split). Also, remember to adjust the selection template if you use a different merging function.

[=100% "Split 9/9"]{: .candystripe .candystripe-animate }

That was fast! :dash:

!!! question Why is the performance so different compared to the previous version, which, by the way, uses the same Numba functions under the hood? Remember, when running a function a thousand times, even a 1-millisecond longer execution time adds up to a 1-second longer **total** execution time.

Let's take a look at the CV results:

For example, the test results show a negative correlation with the training results. This means that the parameter combinations with the highest Sharpe often underperform when they had previously outperformed. This actually makes sense, as BTC market regimes tend to change frequently.

To analyze further, let's look at the cross-set correlation for each parameter combination. This shows how the performance of a parameter combination in the training set correlates with its performance in the test set:

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/cv/param*cross*set*corr.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/cv/param*cross*set*corr.dark.svg#only-dark){: .iimg loading=lazy }

Another way to analyze is by comparing the test performance of the best parameter combinations to the test performance of all parameter combinations. Let's find the proportion of parameter combinations that outperform the selected one in each split:

The selected parameter combinations seem to outperform most others tested in the same period, but some splits stand out—in splits `1`, `5`, and `6`, the selected parameter performed worse than over 90% of the other combinations.

Finally, let's compare these results to the buy-and-hold baseline. To do this, we need to extract prices for each split, but how can we do that without a splitter? It turns out [@split](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/decorators/#vectorbtpro.generic.splitting.decorators.split) has an argument to return the splitter itself without running the pipeline :stuck*out_tongue:

As we can see, the "taking" and "applying" approaches can be safely combined because the underlying splitter is guaranteed to be built the same way and produce the same results, unless the splitter method uses randomness and no seed has been set.

The [Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter) class can also be useful for cross-validating ML models. For example, you might use the [SplitterCV](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/sklearn*/#vectorbtpro.generic.splitting.sklearn*.SplitterCV) class, which acts as a regular scikit-learn cross-validator by subclassing `BaseCrossValidator`. We will demonstrate its usage on a simple classification problem that predicts the best entry and exit times.

Before we begin, we need to decide on features and labels, which are the predictor and response variables, respectively. Features are typically multi-column time series DataFrames, where each row contains several data points (one per column) that should predict the same row in the labels. Labels are usually a single-column time series Series to be predicted. Consider the following questions to guide your decision:

the next bar, the average price change over the next week, a vector of weights for rebalancing, a boolean signal, or something else?"_

news sentiment index, past backtesting results, or something else?"_

As an example, we will fit a [random forest classifier](https://en.wikipedia.org/wiki/Random*forest) using all [TA-Lib](https://github.com/mrjbq7/ta-lib) indicators stacked as columns to predict the binary labels generated by the label generator [TRENDLB](https://vectorbt.pro/pvt*ff8edc14/api/labels/generators/trendlb/#vectorbtpro.labels.generators.trendlb.TRENDLB), where 1 means an uptrend and 0 means a downtrend. Sounds like fun :relieved:

First, run all the TA-Lib indicators on the data to obtain the feature set `X`:

This gives us 1902 rows (dates) and 174 columns (features).

Next, generate the labels `y` (using the same configuration as before):

Both the features and the labels contain NaNs, which we need to handle carefully. If we remove rows with at least one NaN, we would lose all the data. Instead, we first remove columns that are all NaNs or have only a single unique value. Also, since `X` and `y` must have the same length, we need to filter rows in both datasets at the same time:

!!! warning If you have used ML before, you will recognize the risk in the first logical operation: we are checking a condition for the entire column, which can introduce [look-ahead bias](https://www.investopedia.com/terms/l/lookaheadbias.asp). While our operation is not very dangerous since we only remove columns that would likely remain irrelevant in the future, other transformations like data normalization should always be included in a [Pipeline](https://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html) that is executed per split instead of once across all data.

We have successfully removed a total of 129 rows and 30 columns.

Next, we will define our classifier, which will learn `X` to predict `y`:

!!! question Why did we not rescale, normalize, or reduce the dimensionality of the features? Random forests are robust modeling techniques and can handle high noise levels and a large number of features.

To cross-validate the classifier, we will create a [SplitterCV](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/sklearn*/#vectorbtpro.generic.splitting.sklearn_.SplitterCV) instance that splits the entire period into expanding windows with non-overlapping test periods of 180 bars:

![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/cv/sklsplitter.light.svg#only-light){: .iimg loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/images/tutorials/cv/sklsplitter.dark.svg#only-dark){: .iimg loading=lazy }

Finally, we will run the classifier on each training period and check the accuracy of its predictions on the corresponding test period. Although the accuracy score is the most basic classification metric and has limitations, we will keep things simple for now:

As we can see, only two splits underperform, and two splits even reach 100% accuracy. How is this possible? Let's investigate! We need the raw predictions: we will use the actual splitter to slice `X` and `y`, generate predictions for each test set using our classifier, and concatenate all predictions into a single Series.

Let's compare the actual labels (left tab) to the predictions (right tab):

The model appears to correctly classify many major uptrends and even issues an exit signal at the most recent peak in a timely manner! Nevertheless, we should not rely solely on visual intuition. Let's backtest the predictions.

We have achieved some impressive statistics :star2:

If you are up for a challenge: build a pipeline to impute and (standard-)normalize the data, [reduce the dimensionality](https://scikit-learn.org/stable/auto*examples/compose/plot*digits*pipe.html) of the features, and fit one of the [linear models](https://scikit-learn.org/stable/modules/linear*model.html) to predict the average price change over the next `n` bars (making it a regression task). Based on each prediction, you can then decide whether opening or closing a position is justified.

Backtesting requires rethinking traditional cross-validation schemes centered around ML, and VBT provides the necessary tools. The core of this functionality is the powerful [Splitter](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/base/#vectorbtpro.generic.splitting.base.Splitter) class, which not only provides time-series-safe splitting schemes but also lets you thoroughly analyze generated splits and efficiently apply them to complex data. For example, we can leverage its flexibility to either split data into slices for manual CV or construct a pipeline and let the splitter handle slicing and execution for us. There is even a decorator for parameterizing and cross-validating any Python function: [@cv*split](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/decorators/#vectorbtpro.generic.splitting.decorators.cv*split). For ML tasks, the [SplitterCV](https://vectorbt.pro/pvt*ff8edc14/api/generic/splitting/sklearn*/#vectorbtpro.generic.splitting.sklearn_.SplitterCV) class offers a splitter-enhanced interface compatible with scikit-learn and many other packages, including the scikit-learn compatible neural network library [skorch](https://github.com/skorch-dev/skorch), which wraps PyTorch. As a result, validating both rule-based and ML-based models has never been easier :butterfly:

[:material-language-python: Python code](https://vectorbt.pro/pvt*ff8edc14/assets/jupytext/tutorials/cross-validation/applications.py.txt){ .md-button target="blank*" } [:material-notebook-outline: Notebook](https://github.com/polakowo/vectorbt.pro/blob/notebooks/CrossValidation.ipynb){ .md-button target="blank_" }

**Examples:**

Example 1 (pycon):
```pycon
>>> close_slices = splitter.take(data.close)
>>> close_slices
split_year  set  
2018        train    Open time
2018-01-01 00:00:00+00:00    13380.0...
            test     Open time
2018-07-01 00:00:00+00:00    6356.81...
2019        train    Open time
2019-01-01 00:00:00+00:00     3797.1...
            test     Open time
2019-07-01 00:00:00+00:00    10624.9...
2020        train    Open time
2020-01-01 00:00:00+00:00    7200.85...
            test     Open time
2020-07-01 00:00:00+00:00     9232.0...
2021        train    Open time
2021-01-01 00:00:00+00:00    29331.6...
            test     Open time
2021-07-01 00:00:00+00:00    33504.6...
dtype: object
```

Example 2 (pycon):
```pycon
>>> close_slices[2020, "test"]
Open time
2020-07-01 00:00:00+00:00     9232.00
2020-07-02 00:00:00+00:00     9086.54
2020-07-03 00:00:00+00:00     9058.26
                                  ...
2020-12-29 00:00:00+00:00    27385.00
2020-12-30 00:00:00+00:00    28875.54
2020-12-31 00:00:00+00:00    28923.63
Freq: D, Name: Close, Length: 184, dtype: float64
```

Example 3 (pycon):
```pycon
>>> def get_total_return(sr):
...     return sr.vbt.to_returns().vbt.returns.total()

>>> close_slices.apply(get_total_return)  # (1)!
split_year  set  
2018        train   -0.522416
            test    -0.417491
2019        train    1.858493
            test    -0.322797
2020        train    0.269093
            test     2.132976
2021        train    0.194783
            test     0.379417
dtype: float64
```

Example 4 (pycon):
```pycon
>>> trendlb = data.run("trendlb", 1.0, 0.5)
>>> trendlb.plot().show()
```

---
