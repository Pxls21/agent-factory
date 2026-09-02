# Vectorbtpro_Docs - Cookbook

**Pages:** 5

---

## Overview

**URL:** https://vectorbt.pro/pvt_ff8edc14/cookbook/overview.md

This repository contains concise examples and links to useful VBT recipes. These examples are streamlined, condensed, and crafted to be friendly for new users. In-line examples are included wherever possible to enhance tutorials, documentation, and the API. We encourage users to contribute to this documentation.

<div class="grid cards" markdown>

**Examples:**

Example 1 (text):
```text
from vectorbtpro import *  # (1)!
```

1. To see what is imported, call `whats_imported()`.
```

---

## Compilation

**URL:** https://vectorbt.pro/pvt_ff8edc14/cookbook/compilation.md

You can disable Numba globally by setting an environment variable or by changing the config (see [Environment variables](https://numba.readthedocs.io/en/stable/reference/envvars.html)).

!!! note Make sure to do this *before* importing VBT.

<div class="separator-container"> <hr class="separator"> <span class="separator-text">+</span> <hr class="separator"> </div>

You can also achieve this by creating a [configuration](https://vectorbt.pro/pvt_ff8edc14/cookbook/configuration/#settings) file with the following content:

!!! note All commands above must be executed before importing VBT.

<div class="separator-container"> <hr class="separator"> <span class="separator-text">+</span> <hr class="separator"> </div>

To check whether Numba is enabled, use [is*numba*enabled](https://vectorbt.pro/pvt*ff8edc14/api/utils/checks/#vectorbtpro.utils.checks.is*numba_enabled).

**Examples:**

Example 1 (text):
```text
import os

os.environ["NUMBA_DISABLE_JIT"] = "1"
```

Example 2 (text):
```text
from numba import config

config.DISABLE_JIT = True
```

Example 3 (text):
```text
    [numba]
    disable = True
```

Example 4 (text):
```text
    numba:
      disable: true
```

---

## Caching

**URL:** https://vectorbt.pro/pvt_ff8edc14/cookbook/caching.md

When performing a high-level task repeatedly (such as during parameter optimization), it is recommended to occasionally clear the cache using [clear*cache](https://vectorbt.pro/pvt*ff8edc14/api/caching/registry/#vectorbtpro.caching.registry.clear_cache) and collect memory garbage. This helps prevent RAM consumption from increasing due to cached and dead objects.

<div class="separator-container"> <hr class="separator"> <span class="separator-text">+</span> <hr class="separator"> </div>

To clear the cache for a specific class, method, or instance, pass it directly to the function.

<div class="separator-container"> <hr class="separator"> <span class="separator-text">+</span> <hr class="separator"> </div>

To display various statistics about the current cache, use [print*cache*stats](https://vectorbt.pro/pvt*ff8edc14/api/caching/registry/#vectorbtpro.caching.registry.print*cache_stats).

<div class="separator-container"> <hr class="separator"> <span class="separator-text">+</span> <hr class="separator"> </div>

To disable or enable caching globally, use [disable*caching](https://vectorbt.pro/pvt*ff8edc14/api/caching/registry/#vectorbtpro.caching.registry.disable*caching) and [enable*caching](https://vectorbt.pro/pvt*ff8edc14/api/caching/registry/#vectorbtpro.caching.registry.enable*caching), respectively.

<div class="separator-container"> <hr class="separator"> <span class="separator-text">+</span> <hr class="separator"> </div>

To disable or enable caching within a code block, use the context managers [CachingDisabled](https://vectorbt.pro/pvt*ff8edc14/api/caching/registry/#vectorbtpro.caching.registry.CachingDisabled) and [CachingEnabled](https://vectorbt.pro/pvt*ff8edc14/api/caching/registry/#vectorbtpro.caching.registry.CachingEnabled), respectively.

**Examples:**

Example 1 (text):
```text
for i in range(1_000_000):
    ...  # (1)!
    
    if i != 0 and i % 1000 == 0:
        vbt.flush()  # (2)!
```

Example 2 (text):
```text
vbt.clear_cache(vbt.PF)  # (1)!
vbt.clear_cache(vbt.PF.total_return)  # (2)!
vbt.clear_cache(pf)  # (3)!
```

Example 3 (text):
```text
vbt.print_cache_stats()  # (1)!
vbt.print_cache_stats(vbt.PF)  # (2)!
```

Example 4 (text):
```text
vbt.disable_caching()
```

---

## Signals

**URL:** https://vectorbt.pro/pvt_ff8edc14/cookbook/signals.md

**Contents:**
- Cleaning

!!! question Learn more in the [Signal development tutorial](https://vectorbt.pro/pvt_ff8edc14/tutorials/signal-development/).

You can clean only two arrays at a time. For more than two arrays, create a custom Numba function to handle the task.

!!! tip Convert each input array to NumPy with `arr = vbt.to*2d*array(df)`, and then convert each output array back to Pandas with `new_df = df.vbt.wrapper.wrap(arr)`.

**Examples:**

Example 1 (python):
```python
@njit
def custom_clean_nb(long_en, long_ex, short_en, short_ex):
    new_long_en = np.full_like(long_en, False)
    new_long_ex = np.full_like(long_ex, False)
    new_short_en = np.full_like(short_en, False)
    new_short_ex = np.full_like(short_ex, False)
    
    for col in range(long_en.shape[1]):  # (1)!
        position = 0  # (2)!
        for i in range(long_en.shape[0]):  # (3)!
            if long_en[i, col] and position != 1:
                new_long_en[i, col] = True  # (4)!
                position = 1
            elif short_en[i, col] and position != -1:
                new_short_en[i, col] = True
                position = -1
            elif long_ex[i, col] and position == 1:
                new_long_ex[i, col] = True
                position = 0
            elif short_ex[i, col] and position == -1:
                new_short_ex[i, col] = True
                position = 0
            
    return new_long_en, new_long_ex, new_short_en, new_short_ex
```

---

## Configuration

**URL:** https://vectorbt.pro/pvt_ff8edc14/cookbook/configuration.md

**Contents:**
- Objects
- Settings

!!! question Learn more in [Building blocks - Configuring documentation](https://vectorbt.pro/pvt_ff8edc14/documentation/building-blocks/#configuring).

VBT objects that subclass [Configured](https://vectorbt.pro/pvt_ff8edc14/api/utils/pickling/#vectorbtpro.utils.pickling.Configured) (which represent most of the implemented classes) store the keyword arguments passed to their initializer, available under `config`. Copying an object simply involves passing the same config to the class to create a new instance, which can be done automatically using the `copy()` method.

<div class="separator-container"> <hr class="separator"> <span class="separator-text">+</span> <hr class="separator"> </div>

Since changing any information in-place is strongly discouraged due to caching reasons, to replace something, copy the config, modify it, and pass it to the class. This can be done automatically with the `replace()` method.

<div class="separator-container"> <hr class="separator"> <span class="separator-text">+</span> <hr class="separator"> </div>

In many cases, a VBT object contains other VBT objects. To make changes to a deep VBT object, you can enable the `nested_` flag and pass the instruction as a nested dict.

<div class="separator-container"> <hr class="separator"> <span class="separator-text">+</span> <hr class="separator"> </div>

The same VBT objects can be saved as config files for easy editing. Such a config file has a format that is very similar to the [INI format](https://en.wikipedia.org/wiki/INI_file) but includes various extensions such as code expressions and nested dictionaries. This allows representing objects of any complexity. The same goes for VBT-enhanced YAML files.

Settings that control the default behavior of most functionalities in VBT are located under [*settings](https://vectorbt.pro/pvt*ff8edc14/api/*settings/#vectorbtpro.*settings). Each functionality has its own config; for example, [settings.portfolio](https://vectorbt.pro/pvt*ff8edc14/api/*settings/#vectorbtpro.*settings.portfolio) defines the defaults for the [Portfolio](https://vectorbt.pro/pvt*ff8edc14/api/portfolio/base/#vectorbtpro.portfolio.base.Portfolio) class. All configs are combined into a single config that you can access via `vbt.settings`.

<div class="separator-container"> <hr class="separator"> <span class="separator-text">+</span> <hr class="separator"> </div>

The initial state of any config can be accessed through `options*["reset*dct"]`.

<div class="separator-container"> <hr class="separator"> <span class="separator-text">+</span> <hr class="separator"> </div>

Any config can be reset to its initial state using the `reset()` method.

<div class="separator-container"> <hr class="separator"> <span class="separator-text">+</span> <hr class="separator"> </div>

For convenience, settings can be defined in a text file that will be loaded automatically the next time VBT is imported. The file should be placed in the directory of the script importing the package and be named `vbt.cfg`, `vbt.yml`, or `vbt.toml` (or other extension variants). Alternatively, you can set the path to the settings file by setting the environment variable `VBT*SETTINGS*PATH`. The file must use either the [INI format](https://en.wikipedia.org/wiki/INI*file#Format) with extensions provided by vectorbtpro (see [Pickleable.decode*config](https://vectorbt.pro/pvt*ff8edc14/api/utils/pickling/#vectorbtpro.utils.pickling.Pickleable.decode*config) for examples), the [YAML format](https://yaml.org/) (see [Pickleable.decode*yaml](https://vectorbt.pro/pvt*ff8edc14/api/utils/pickling/#vectorbtpro.utils.pickling.Pickleable.decode*yaml) for examples), or the [TOML format](https://toml.io/en/) (see [Pickleable.decode*toml](https://vectorbt.pro/pvt*ff8edc14/api/utils/pickling/#vectorbtpro.utils.pickling.Pickleable.decode*toml) for examples).

<div class="separator-container"> <hr class="separator"> <span class="separator-text">+</span> <hr class="separator"> </div>

This is especially useful for changing settings that only take effect on import, such as various Numba-related settings, caching, and chunking machinery.

<div class="separator-container"> <hr class="separator"> <span class="separator-text">+</span> <hr class="separator"> </div>

To save all settings or a specific config to a text file, modify it, and let VBT load it on import (or manually), use the `save()` method with `file*format="config"` or `file*format="yaml"`.

<div class="separator-container"> <hr class="separator"> <span class="separator-text">+</span> <hr class="separator"> </div>

If the readability of the file does not matter, you can modify the settings in place and then save them to a Pickle file in one Python session, allowing them to be automatically imported in the next session.

!!! warning This approach is discouraged if you plan to upgrade VBT frequently, as new releases may introduce changes to the settings.

**Examples:**

Example 1 (text):
```text
new_pf = pf.copy()
new_pf = vbt.PF(**pf.config)  # (1)!
```

Example 2 (text):
```text
new_pf = pf.replace(init_cash=1_000_000)
new_pf = vbt.PF(**vbt.merge_dicts(pf.config, dict(init_cash=1_000_000)))  # (1)!
```

Example 3 (text):
```text
new_pf = pf.replace(wrapper=dict(group_by=True), nested_=True)
new_pf = pf.replace(wrapper=pf.wrapper.replace(group_by=True))  # (1)!
```

Example 4 (text):
```text
    pf.save(file_format="config")

    # (1)!

    pf = vbt.PF.load()
```

---
