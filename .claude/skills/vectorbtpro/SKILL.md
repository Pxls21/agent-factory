---
name: vectorbtpro
description: "VectorBT PRO - a proprietary, high-performance Python engine for backtesting, algorithmic trading, and quantitative analysis. Use when writing or debugging VectorBT PRO code: portfolio simulation (Portfolio.from_signals/from_orders), indicators, data fetching, walk-forward/cross-validation splitting, parameter optimization, or the knowledge/MCP tooling."
version: 2026.6.27
---

# Vectorbtpro Skill

VectorBT PRO - a proprietary, high-performance Python engine for backtesting, algorithmic trading, and quantitative analysis. Use when writing or debugging VectorBT PRO code: portfolio simulation (Portfolio.from_signals/from_orders), indicators, data fetching, walk-forward/cross-validation splitting, parameter optimization, or the knowledge/MCP tooling.

## When to Use This Skill

Use this skill when you need to:
- understand vectorbtpro features, APIs, and workflows
- find concrete code examples before implementing or debugging
- navigate the official documentation quickly through categorized references

## Quick Reference

### High-Signal Examples

**Example 1** (python):
```python
build_call_seq(
    target_shape,
    group_lens,
    call_seq_type=0,
    seed=None,
    seed_offset=0
)
```

**Example 2** (python):
```python
build_call_seq_nb(
    target_shape,
    group_lens,
    call_seq_type=0,
    seed=None,
    seed_offset=0
)
```

**Example 3** (python):
```python
BaseDataMixin()
```

**Example 4** (python):
```python
BaseDataMixin.assert_has_feature(
    feature
)
```

**Example 5** (python):
```python
BaseDataMixin.assert_has_symbol(
    symbol
)
```

## Reference Files

This skill includes comprehensive documentation in `references/`:

- **api_reference.md** - Api Reference documentation
- **cookbook.md** - Cookbook documentation
- **data.md** - Data documentation
- **features.md** - Features documentation
- **fundamentals.md** - Fundamentals documentation
- **getting_started.md** - Getting Started documentation
- **indicators.md** - Indicators documentation
- **knowledge_mcp.md** - Knowledge Mcp documentation
- **optimization.md** - Optimization documentation
- **portfolio.md** - Portfolio documentation
- **splitting_cv.md** - Splitting Cv documentation
- **tutorials.md** - Tutorials documentation

Use `view` to read specific reference files when detailed information is needed.

## Working with This Skill

### Start Here
Start with the getting_started or tutorials reference files for foundational concepts.

### For Specific Features
Use the appropriate category reference file (api, guides, etc.) for detailed information.

### For Code Examples
Use the high-signal examples above first, then open the matching reference file for full context.

## Notes

- This skill was automatically generated from official documentation
- Reference files preserve the structure and examples from source docs
- Code examples include language detection for better syntax highlighting
- Quick reference entries are filtered to avoid low-signal placeholders and inline tokens

## Updating

To refresh this skill with updated documentation:
1. Re-run the scraper with the same configuration
2. The skill will be rebuilt with the latest information
