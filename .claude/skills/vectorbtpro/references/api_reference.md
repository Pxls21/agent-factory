# Vectorbtpro_Docs - Api Reference

**Pages:** 1

---

## cli

**URL:** https://vectorbt.pro/pvt_ff8edc14/api/cli.md

**Contents:**
- Entry points
- Command layout
- Discovering commands and tools
- Flexible invocation with `--call`
- cli_registry <span class="dobjtype">list</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/cli.py#L136-L137" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.cli.cli_registry data-toc-label="cli\_registry" }
- build_app <span class="dobjtype">function</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/cli.py#L658-L673" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.cli.build_app data-toc-label="build\_app" }
- build_mcp_app <span class="dobjtype">function</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/cli.py#L525-L568" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.cli.build_mcp_app data-toc-label="build\_mcp\_app" }
- build_tool_signature <span class="dobjtype">function</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/cli.py#L420-L462" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.cli.build_tool_signature data-toc-label="build\_tool\_signature" }
- build_wrapped_command_help <span class="dobjtype">function</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/cli.py#L571-L595" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.cli.build_wrapped_command_help data-toc-label="build\_wrapped\_command\_help" }
- chat_command <span class="dobjtype">function</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/cli.py#L598-L612" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.cli.chat_command data-toc-label="chat\_command" }

Command-line interface for VectorBT PRO.

This module exposes a Typer-based CLI for interacting with VectorBT PRO from the shell, including:

The CLI is intended to be friendly both for humans and for AI agents operating in a terminal environment.

After installing the package with its console script, the CLI can be invoked as:

The same interface is also available via the module entry point:

The `mcp` group contains:

Tool names are exposed as hyphenated command names. For example:

List top-level commands:

List all MCP-related commands, including all registered tools:

Get help for a specific command or tool:

The help text for tool commands is derived from the underlying function docstrings and preserves paragraph breaks to make long API-style documentation more readable in the terminal.

Many commands also expose a `--call` option intended as an escape hatch for agents and advanced users. It accepts JSON or a Python literal and can supply arbitrary positional and keyword arguments to the underlying function.

Explicitly passed CLI options override matching values from `--call`.

Registry of explicitly declared CLI commands.

Build the top-level Typer application.

`typer.Typer` :   Configured top-level Typer application.

Build the `mcp` command group.

`typer.Typer` :   Nested Typer application for MCP commands.

Build a Typer-safe signature for a dynamic tool command.

Unsupported or variadic parameters are omitted from the direct CLI surface and can still be supplied through `--call`.

**```func```** :&ensp;`Callable` :   Tool function.

`inspect.Signature` :   Signature safe to expose through Typer.

Build help text for a wrapped knowledge command.

**```command*name```** :&ensp;`str` :   Name of the function in [vectorbtpro.knowledge.custom*assets](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/custom*assets/ "vectorbtpro.knowledge.custom_assets").

`str` :   CLI help text including the original function docstring.

Ask VectorBT PRO using asset context via the shell.

Decorate and register a function as a Typer CLI command.

**```arg```** :&ensp;`Union[None, str, Callable]` :   Function to decorate or command name.

**```name```** :&ensp;`Optional[str]` :   Explicit command name.

**```help```** :&ensp;`Optional[Any]` :   Command help text or a callable returning it.

**```**kwargs```** :   Extra keyword arguments passed to `Typer.command`.

`Callable` :   Decorator or the decorated function.

Format help text for Click/Typer without collapsing paragraph newlines.

Click preserves line breaks for paragraphs that begin with the backspace marker ``. This function adds that marker to each paragraph separated by blank lines so docstrings keep their manual formatting in CLI help.

**```help_text```** :&ensp;`Optional[str]` :   Raw help text or docstring.

`Optional[str]` :   Help text formatted for Click/Typer.

Return parameters supplied explicitly on the command line.

**```ctx```** :&ensp;`click.Context` :   Current Click context.

**```exclude```** :&ensp;`Optional[Set[str]]` :   Parameter names to ignore.

`Dict[str, Any]` :   Mapping of explicitly passed parameter names to values.

Ask VectorBT PRO with tool use enabled via the shell.

Check if a type annotation represents a list-like structure.

**```annotation```** :&ensp;`Any` :   Type annotation to check.

`bool` :   True if the annotation is list-like, False otherwise.

Run the VectorBT PRO CLI.

**```argv```** :&ensp;`Optional[Sequence[str]]` :   Command-line arguments to parse.

Merge a `--call` payload with explicit CLI arguments.

The payload acts as a flexible base call specification, while explicitly passed CLI arguments override matching parameters.

**```func```** :&ensp;`Callable` :   Target callable.

**```call```** :&ensp;`Optional[str]` :   Structured payload string.

**```cli_overrides```** :&ensp;`Optional[Dict[str, Any]]` :   Explicit CLI arguments.

`Tuple[List[Any], Dict[str, Any]]` :   Positional and keyword arguments ready to call.

Parse a structured `--call` payload.

The payload can be JSON or a Python literal. Supported shapes are:

**```call```** :&ensp;`Optional[str]` :   Raw payload string.

`Tuple[List[Any], Dict[str, Any]]` :   Parsed positional and keyword arguments.

Print CLI output to standard output.

**```output```** :&ensp;`Any` :   Output value to print.

Ask VectorBT PRO using the quick chat preset via the shell.

Resolve and format CLI help text.

**```help_value```** :&ensp;`Optional[Any]` :   Help text or a callable returning help text.

`Optional[str]` :   Help text formatted for Click/Typer.

Run a chat-like command with merged arguments.

This function intentionally avoids overriding the formatter so the configured chat formatter can stream output directly to the terminal in interactive fashion.

**```func```** :&ensp;`Callable` :   Target `chat`-like function.

**```call```** :&ensp;`Optional[str]` :   Structured payload string.

**```cli_overrides```** :&ensp;`Dict[str, Any]` :   Explicit CLI arguments.

**```ctx```** :&ensp;`click.Context` :   Current command context.

Validate that all required function parameters are present after CLI/`--call` merging.

**```func```** :&ensp;`Callable` :   Target callable whose required parameters should be checked.

**```args```** :&ensp;`Sequence[Any]` :   Positional arguments after merging `--call` and CLI overrides.

**```kwargs```** :&ensp;`Dict[str, Any]` :   Keyword arguments after merging `--call` and CLI overrides.

**```ctx```** :&ensp;`click.Context` :   Current Click context used to attach usage errors to the command.

Wrap a tool function so the CLI prints its return value.

**```func```** :&ensp;`Callable` :   Tool function.

`Callable` :   Wrapped Typer command.

Metadata describing a registered CLI command.

**Inherited members**

Function invoked by the CLI command.

Help text displayed by Typer, or a callable returning it.

Extra keyword arguments passed to `Typer.command`.

Public command name.

**Examples:**

Example 1 (bash):
```bash
vbt ...
```

Example 2 (bash):
```bash
python -m vectorbtpro ...
```

Example 3 (bash):
```bash
vbt chat "What is PFO?"
python -m vectorbtpro interact "List attributes of PFO"
vbt mcp serve
python -m vectorbtpro mcp find "PFO"
```

Example 4 (bash):
```bash
vbt --help
```

---
