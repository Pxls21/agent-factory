# Vectorbtpro_Docs - Getting Started

**Pages:** 2

---

## Installation

**URL:** https://vectorbt.pro/pvt_ff8edc14/getting-started/installation.md

**Contents:**
- Requirements
  - Install Git
  - Install GitHub CLI
- Recommendations
  - Windows
  - New environment
    - Option 1: uv
    - Option 2: Conda
    - Option 3: IDE
- With pip

!!! important VectorBT® PRO (`vectorbtpro`) redesigns [VectorBT](https://github.com/polakowo/vectorbt) (`vectorbt`) to support groundbreaking features.

Check whether Git is already installed:

If this command prints a version, you can continue. If your terminal says that `git` is not found or not recognized, [install Git](https://git-scm.com/install/).

Check whether GitHub CLI is already installed:

If this command prints a version, you can continue. If your terminal says that `gh` is not found or not recognized, [install GitHub CLI](https://cli.github.com/).

After being added as a collaborator and accepting the repository invitation, authenticate from your terminal:

The first command signs you in to GitHub and stores credentials securely. The second command lets Git reuse those credentials, which is needed when `pip` installs `vectorbtpro` from the private GitHub repository via `git+https`.

!!! important If GitHub access stops working, run `gh auth status` first. Expired credentials or missing repository access are unrelated to your membership status.

!!! tip Creating a local environment is a great option for development because it gives you full control, better performance, and access to native tooling.

The following recommendations apply only to local installations.

If you are using Windows, it is recommended to use [WSL](https://learn.microsoft.com/en-us/windows/wsl/setup/environment) for development.

If you plan to use `vectorbtpro` locally, it is best to create a new environment dedicated to `vectorbtpro`.

The easiest way to get started is to install [uv](https://github.com/astral-sh/uv), a lightning-fast package manager that handles virtual environments and dependency resolution in one tool.

First, install `uv`:

=== "macOS (Homebrew)"

=== "pipx (cross-platform)"

After installing `uv`, create a new isolated environment (similar to a conda environment) for your project:

This creates a virtual environment named `vectorbtpro` located in the current directory. Now, activate it:

!!! note You need to activate the environment each time you start a new terminal session.

To check you're in the correct environment, your terminal prompt should now be prefixed with `(vectorbtpro)`.

That's it! You're using `uv` to manage environments and install packages with speed and simplicity.

Another easy option is to [download Anaconda](https://www.anaconda.com/download), which provides a graphical installer and includes many popular data science packages required by `vectorbtpro`, such as NumPy, Pandas, Plotly, and more.

After installing Anaconda, [create a new environment](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-with-commands):

[Activate the new environment](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#activating-an-environment):

!!! note You need to activate the environment each time you start a new terminal session.

You should now see `vectorbtpro` in the list of all environments, and it should be active (notice the `*`):

You are now ready to install the actual package.

If you primarily use an IDE, you can create a separate environment for each project:

The PRO version can be installed using `pip`.

!!! tip It is highly recommended to create a new virtual environment dedicated to `vectorbtpro`, such as one made with [Anaconda](https://www.anaconda.com/).

Uninstall the open-source version if it is already installed:

The Rust backend is optional. To enable it, install `vectorbtpro-rust` before `vectorbtpro`. The package is distributed as platform wheels in each GitHub release. Download the release wheels with GitHub CLI, which reuses your GitHub authentication, and then let `pip` pick the wheel matching your Python version, operating system, and CPU architecture:

Then install `vectorbtpro-rust` from the downloaded wheels:

Then install `vectorbtpro` using one of the commands below. Do not use `vectorbtpro[rust]` when installing from GitHub, because pip must resolve `vectorbtpro-rust` from the GitHub release wheels first.

!!! tip Installing `vectorbtpro-rust` from a wheel is preferred. Building it from source requires native compiler tooling, at least 16 GB of RAM, and a considerable amount of time.

Install the latest stable release of the PRO version (with recommended dependencies) using `git+https`:

!!! info This process may require at least 1GB of disk space and take several minutes to finish.

!!! tip If this command cannot access the private repository, run `gh auth status` and `gh auth setup-git`, then try again.

To install the lightweight version (with only required dependencies):

For more optional dependencies, see [pyproject.toml](https://github.com/polakowo/vectorbt.pro/blob/v2026.6.27/pyproject.toml).

To install the base version with `git+ssh`:

See [Connecting to GitHub with SSH](https://docs.github.com/en/authentication/connecting-to-github-with-ssh).

When a new version of `vectorbtpro` is released, the package **will not** update automatically. You will need to install the new version manually. Fortunately, you can use the exact same command you used to install the package to update it.

Append `@` followed by [a branch name](https://github.com/polakowo/vectorbt.pro/branches/all) to the command.

For example, to install the `develop` branch:

!!! note If you have the latest regular version installed, you must uninstall it first:

Append `@` followed by [a tag name](https://github.com/polakowo/vectorbt.pro/tags) to the command.

For example, to install the tag `v2024.1.30`:

With [setuptools](https://setuptools.readthedocs.io/en/latest/), you can add `vectorbtpro` as a dependency to your Python package by listing it in `setup.py` or in your [requirements files](https://pip.pypa.io/en/latest/user_guide/#requirements-files):

You can also clone `vectorbtpro` directly from Git:

Check out the latest stable release:

If you want to enable the Rust backend, install `vectorbtpro-rust` from the cloned repository first:

!!! tip Installing `vectorbtpro-rust` from a wheel is preferred. The script above builds it from source: it can install Rust with rustup when Cargo is missing, but it still requires native compiler tooling, at least 16 GB of RAM, and a considerable amount of time.

Install the package:

Later, to update to a new version:

Then, reinstall `vectorbtpro-rust` if you use the Rust backend, and reinstall the package.

The command above takes about 1GB of disk space. To create a shallow clone:

Then proceed with the installation as described above.

To update to a new version:

To convert the clone back into a complete one:

Using [Docker](https://www.docker.com/) is an excellent way to get started in just a few minutes, as it includes all dependencies pre-installed.

[This Docker image](https://github.com/polakowo/vectorbt.pro/blob/v2026.6.27/Dockerfile.jupyter) is based on [Jupyter Docker Stacks](https://jupyter-docker-stacks.readthedocs.io/en/latest/), a collection of ready-to-run Docker images that include Jupyter applications and interactive computing tools. Specifically, the image builds on [jupyter/scipy-notebook](https://jupyter-docker-stacks.readthedocs.io/en/latest/using/selecting.html#jupyter-scipy-notebook), which includes a minimally-functional JupyterLab server and preinstalled popular packages from the scientific Python ecosystem. It also extends the image with Plotly and Dash for interactive visualizations and plots, as well as `vectorbtpro` and all of its optional Python dependencies. The image requires the `vectorbtpro` source to be present in the current directory.

Before proceeding, make sure to [install Docker](https://docs.docker.com/install/).

Start Docker using Docker Desktop.

Clone the `vectorbtpro` repository if you have not already. Run this command from the directory where you want `vectorbtpro` to be located, such as in Documents/GitHub:

Check out the latest stable release:

Build the image (this may take some time):

To include the Rust backend, build the image with `INSTALL_RUST=1`:

!!! tip The Rust-enabled Docker build compiles `vectorbtpro-rust` from source. This requires at least 16 GB of RAM and can take a considerable amount of time.

Create a working directory inside the current directory:

Start a container running a JupyterLab server on port 8888:

!!! info The `-v` flag in this command mounts the working directory on the host (`{PWD/work}` in the example) as `/home/jovyan/work` in the container. The server logs will appear in the terminal. The [--rm flag](https://docs.docker.com/engine/reference/run/#clean-up---rm) tells Docker to automatically clean up the container and remove the file system when the container exits. However, any changes made to the `~/work` directory and its files inside the container will remain on the host. The [-it flag](https://docs.docker.com/engine/reference/commandline/run/#assign-name-and-allocate-pseudo-tty---name--it) allocates a pseudo-TTY.

If port 8888 is already in use, you can specify a different port (for example, 10000):

Once the server has started, go to its address in a browser. The address will be printed in the console, for example: `http://127.0.0.1:8888/lab?token=9e85949d9901633d1de9dad7a963b43257e29fb232883908`

!!! note Change the port if needed.

This will open JupyterLab, where you can create a new notebook and start working with `vectorbtpro` :tada:

To use files from your host, place them into the `work` directory on your host, and they will appear in the JupyterLab file browser. Alternatively, you can drag and drop files directly into the JupyterLab file browser.

To stop the container, first press ++ctrl+c++, and then when prompted, type `y` and press ++enter++.

To upgrade the Docker image to a new version of `vectorbtpro`, first update your local repository from the remote:

Then rebuild the image:

If you use the Rust backend, rebuild with the same build argument:

!!! info This will not rebuild the entire image, only the `vectorbtpro-rust` and `vectorbtpro` installation steps.

[This Docker image](https://github.com/polakowo/vectorbt.pro/blob/v2026.6.27/Dockerfile.dev) is recommended for local development workflows in Visual Studio Code, PyCharm (Professional), and remote connections. It includes `vectorbtpro` and all optional Python dependencies. The image requires the `vectorbtpro` source to be present in the current directory.

To include the Rust backend in the development image, pass `INSTALL_RUST=1` as a build argument. For example, in `.devcontainer/devcontainer.json`, use `build` instead of `dockerFile`:

This image also allows you to start developing right away in Visual Studio Code, without manually setting up Python, Jupyter, or any dependencies.

Make sure you have the following installed:

Clone the repository if you have not already:

Open the repository in Visual Studio Code.

When prompted, click "Reopen in Container".

!!! tip If you do not see the prompt, open the Command Palette (++ctrl+shift+p++) and run "Dev Containers: Reopen in Container".

Visual Studio Code will:

[:material-notebook-outline: Notebook](https://colab.research.google.com/drive/1A9RxtYgGkUT*NbRxp3Z8h-fTRnVR3WRa?usp=sharing){ .md-button target="blank*" }

If you experience connectivity issues, you can also install the package manually:

To install a custom wheel release:

Python version, operating system, and CPU architecture.

Replace `vectorbtpro*rust*filename` and `vectorbtpro_filename` with the actual file names.

!!! note If the file name ends with (1) because there is already a file with the same name, make sure to remove the previous file and remove the (1) suffix from the newer one.

If you receive the error "ModuleNotFoundError: No module named 'pybind11'", install `pybind11` before installing `vectorbtpro`:

If you receive the error "Cannot uninstall 'llvmlite'", install `llvmlite` before installing `vectorbtpro`:

If image generation hangs (for example, when calling `show_svg()`), downgrade the Kaleido package:

If you are on a Mac and encounter an error during the installation of the osqp package, install `cmake`:

These videos describe the general installation process, but they are not guaranteed to be up to date. Use the written guide above as the source of truth.

??? youtube "MacOS Installation Guide on YouTube" <iframe class="youtube-video" src="https://www.youtube.com/embed/lFmeqhFwH3M?si=2vNVrZu4Q1_hdoBd" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

??? youtube "Windows Installation Guide on YouTube" <iframe class="youtube-video" src="https://www.youtube.com/embed/bN5BOOb4Yd4?si=YeIo5p-ADMJhwzKm" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

??? youtube "Linux Installation Guide on YouTube" <iframe class="youtube-video" src="https://www.youtube.com/embed/TjsFsxuWY4I?si=lXtGhlEq1czCOeWT" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

**Examples:**

Example 1 (text):
```text
To avoid importing outdated code, make sure to import **`vectorbtpro`** only.
```

Example 2 (shell):
```shell
git --version
```

Example 3 (shell):
```shell
gh --version
```

Example 4 (shell):
```shell
gh auth login
gh auth setup-git
```

---

## Getting started

**URL:** https://vectorbt.pro/pvt_ff8edc14/index.md

**Contents:**
- Discord
- Website
- General design
- First steps
- AI workflows
  - llms.txt
  - :material-robot-love-outline: MCP server
    - ChatVBT
    - Apps

![](https://vectorbt.pro/pvt_ff8edc14/assets/logo/header.svg)

![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/version.svg) ![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/python.svg) ![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/license.svg) ![](https://vectorbt.pro/pvt*ff8edc14/assets/badges/build-passing.svg)

We're glad you're here!

We believe that powerful financial tools should not be reserved for the biggest players :shark:

Whether you're a seasoned trader, a PhD researcher, or simply curious and driven to learn, you should have access to the kind of technology that helps you make smarter decisions.

This tool is the first step in a growing ecosystem built around that belief. It already makes it easier to analyze financial data at a level that used to feel out of reach. All you need is the time and motivation to dig in and start finding insights in data that might otherwise look like just numbers.

??? youtube "Installation Guide + Subscriber Perks on YouTube" <iframe class="youtube-video" src="https://www.youtube.com/embed/GkJEQ4fm2_E?si=qUBfW-OoIImGm4bw" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

<iframe src="https://discord.com/widget?id=918629562441695344&theme=dark" width="350" height="500" allowtransparency="true" frameborder="0" sandbox="allow-popups allow-popups-to-escape-sandbox allow-same-origin allow-scripts"></iframe>

Before you get started with VBT, be sure to join our [Discord server](https://discord.gg/eQ9sVr5vb9). On our server, we support each other, report issues, request new features, and chat!

:octicons-light-bulb-16: After joining, please post your GitHub account name (for example, [polakowo](https://github.com/polakowo)) in the verification channel so we can manually link your Discord and GitHub accounts. We will then assign you a member role that unlocks all other channels. If you end your sponsorship, you will lose access to the server. If you restart your sponsorship, please repeat the steps above.

To ensure only sponsors can access exclusive content, this project is split into two websites: the public site at https://vectorbt.pro and the private site you are currently using. The link to the private website is provided in the private repository (bookmark this page: https://github.com/polakowo/vectorbt.pro/blob/pvt-links/README.md :bookmark:). The private website is a directory on the same host as the public site, but it is preceded by a random hash that changes periodically to help prevent information theft. You can tell which site you are on by checking the lock icon in the top left corner: a closed lock means the public site, and an open lock means the private site.

The website is organized into the following main sections:

<br> <div class="showcase-row" markdown> <div class="showcase-column" data-aos="fade-up" markdown> :material-clock-fast:{ .icon }

Contains the installation guide for `vectorbtpro` and the change log.

[:octicons-arrow-right-24: Installation](https://vectorbt.pro/pvt_ff8edc14/getting-started/installation/)

[:octicons-arrow-right-24: Release notes](https://vectorbt.pro/pvt_ff8edc14/getting-started/release-notes/) </div> <div class="showcase-column" data-aos="fade-up" markdown> :material-lightning-bolt:{ .icon }

Contains examples of major enhancements added with each release.

[:octicons-arrow-right-24: Features](https://vectorbt.pro/pvt_ff8edc14/features/overview/) </div> </div> <div class="showcase-row" markdown> <div class="showcase-column" data-aos="fade-up" markdown> :material-clipboard-check-outline:{ .icon }

Contains all the exclusive tutorials.

[:octicons-arrow-right-24: Tutorials](https://vectorbt.pro/pvt_ff8edc14/tutorials/basic-rsi/) </div> <div class="showcase-column" data-aos="fade-up" markdown> :material-format-font:{ .icon }

Contains user-friendly documentation for the latest version of `vectorbtpro`.

[:octicons-arrow-right-24: Documentation](https://vectorbt.pro/pvt_ff8edc14/documentation/fundamentals/) </div> </div> <div class="showcase-row" markdown> <div class="showcase-column" data-aos="fade-up" markdown> :material-connection:{ .icon }

Contains API documentation for the latest version of `vectorbtpro`.

[:octicons-arrow-right-24: API](https://vectorbt.pro/pvt_ff8edc14/api/) </div> <div class="showcase-column" data-aos="fade-up" markdown> :material-food-outline:{ .icon }

Contains short and practical examples for using `vectorbtpro`.

[:octicons-arrow-right-24: Cookbook](https://vectorbt.pro/pvt_ff8edc14/cookbook/) </div> </div>

If you have used other backtesting frameworks before, you may expect to implement your trading strategy by creating a Python class, overriding some methods, and working with a limited set of commands to communicate with the backtester, such as placing orders. Using VBT is quite different: since it is a quantitative analysis package that operates mainly on arrays, it is more similar to libraries like Pandas than to frameworks such as backtrader.

The main technical difference between a framework and a library comes down to something called inversion of control. When you use a framework, the *framework* controls the flow. It provides places for you to plug in your code, and then it calls your code as needed. When using a library, *you* are in control of the application's flow; you decide when and where to call the library. Because of this, VBT's functionality is distributed across many modules, each optional and typically with its own documentation.

For example, while VBT provides [this extensive module](https://vectorbt.pro/pvt*ff8edc14/api/data/base/) and [related documentation](https://vectorbt.pro/pvt*ff8edc14/documentation/data/) for storing and manipulating data, you can skip it entirely and use just Pandas and NumPy arrays. This flexibility makes it difficult to create a perfect getting-started guide, since each use case is different and requires a unique set of modules. As experience shows, you will end up using only a fraction of the functions that VBT offers!

After you have been added as a collaborator and accepted the repository invitation, the first step is to [install the package](https://vectorbt.pro/pvt_ff8edc14/getting-started/installation/).

What should you do next? Here are some recommended steps:

<br> <div class="showcase-row" markdown> <div class="showcase-column" data-aos="fade-up" markdown> :material-alphabetical-variant:{ .icon }

**1 - Fundamentals**

Learn the fundamental concepts of VBT. Why do we use Numba? What is represented by rows and columns? Why is broadcasting so important? How do most VBT classes work?

[:octicons-arrow-right-24: Fundamentals](https://vectorbt.pro/pvt_ff8edc14/documentation/fundamentals/)

[:octicons-arrow-right-24: Building blocks](https://vectorbt.pro/pvt_ff8edc14/documentation/building-blocks/) </div> <div class="showcase-column" data-aos="fade-up" markdown> :material-chart-line-variant:{ .icon }

**2 - Basic RSI strategy**

Apply the fundamental concepts to backtest a basic RSI strategy. Try running the example on your own data, test a different set of parameters, add trading commissions, and experiment!

[:octicons-arrow-right-24: Basic RSI strategy](https://vectorbt.pro/pvt_ff8edc14/tutorials/basic-rsi/) </div> </div> <div class="showcase-row" markdown> <div class="showcase-column" data-aos="fade-up" markdown> :material-lightning-bolt-outline:{ .icon }

**3 - SuperFast SuperTrend**

Learn to develop, compile, and backtest a Supertrend indicator. Adapt the example to an indicator that interests you. See [this documentation](https://vectorbt.pro/pvt_ff8edc14/documentation/indicators/) for help.

[:octicons-arrow-right-24: SuperFast SuperTrend](https://vectorbt.pro/pvt_ff8edc14/tutorials/superfast-supertrend/) </div> <div class="showcase-column" data-aos="fade-up" markdown> :material-broadcast:{ .icon }

**4 - Signal development**

After building an indicator, learn to detect events in the data and turn them into signals that can be backtested. This is one of the most important tutorials, so do not miss it!

[:octicons-arrow-right-24: Signal development](https://vectorbt.pro/pvt_ff8edc14/tutorials/signal-development/) </div> </div> <div class="showcase-row" markdown> <div class="showcase-column" data-aos="fade-up" markdown> :material-chart-areaspline:{ .icon }

After creating signal arrays, learn to simulate them and analyze their performance. To better understand how the engine works, see [this](https://vectorbt.pro/pvt*ff8edc14/documentation/portfolio/from-orders/) and then [this](https://vectorbt.pro/pvt*ff8edc14/documentation/portfolio/) documentation.

[:octicons-arrow-right-24: Portfolio](https://vectorbt.pro/pvt_ff8edc14/documentation/portfolio/from-signals/) </div> <div class="showcase-column" data-aos="fade-up" markdown> :material-check-all:{ .icon }

**5 - Cross-validation**

Do you have a promising trading strategy that performs well on historical data? It is time to cross-validate! Cross-validation not only helps detect overfitting, but it can also reveal the market conditions where your strategy performs best and worst.

[:octicons-arrow-right-24: Cross-validation](https://vectorbt.pro/pvt_ff8edc14/tutorials/cross-validation/) </div> </div> <div class="showcase-row" markdown> <div class="showcase-column" data-aos="fade-up" markdown> :material-bird:{ .icon }

By now, you should have enough experience to backtest signal-based strategies. Visit the remaining tutorials and documentation, and get familiar with the [API documentation](https://vectorbt.pro/pvt_ff8edc14/api/) to build a backtesting pipeline from scratch. Good luck! </div> <div class="showcase-column" data-aos="fade-up" markdown> :material-robot:{ .icon }

<a href="https://www.quantgpt.chat/" class="link-with-border" markdown> ![](https://vectorbt.pro/pvt*ff8edc14/assets/quantgpt.light.webp#only-light){: loading=lazy } ![](https://vectorbt.pro/pvt*ff8edc14/assets/quantgpt.dark.webp#only-dark){: loading=lazy } </a> </div> </div>

For the fastest setup, install [Claude Code](https://claude.com/product/claude-code), [Codex](https://openai.com/codex/), or another coding agent and ask it to install and configure VectorBT PRO for you. This is usually quicker than going through the process alone, unless you know software engineering well and want hands-on experience with a professional local setup.

Documentation is also available in [llms.txt format](https://llmstxt.org/), which is a simple markdown standard that LLMs can consume easily.

There are two ways to access the LLM-friendly documentation:

!!! info In addition, you can access the Markdown source files of the documentation by appending `.md` to the URL of any page. For example, the Markdown file for the first page of the cross-validation tutorial—[`/tutorials/cross-validation/`](https://vectorbt.pro/pvt*ff8edc14/tutorials/cross-validation/)—can be found at [`/tutorials/cross-validation.md`](https://vectorbt.pro/pvt*ff8edc14/tutorials/cross-validation.md).

[Model Context Protocol (MCP)](https://modelcontextprotocol.io/) is a new way to interact with software using LLMs. It enables your agents to access information they need without prior knowledge of the software. For example, you can ask an agent to *"list all arguments related to stop orders in `vbt.Portfolio.from*signals`"* and it will call the VBT's MCP server to retrieve the relevant information. Under the hood, the MCP server calls native VBT functions for retrieval, so it is always up-to-date with the latest version of VBT, but this also means that VBT must be [installed](https://vectorbt.pro/pvt*ff8edc14/getting-started/installation/) and running on your machine.

[ChatVBT](https://vectorbt.pro/pvt*ff8edc14/features/intelligence/#chatvbt) is a chat interface for VBT that you can run in a Jupyter notebook or any Python environment. It supports a wide range of LLMs, output formats, and can be configured to use different embedding providers and knowledge assets. It also can access the MCP server tools for real-time information on your VBT installation. To use the MCP server with ChatVBT, simply use `vbt.interact()` instead of `vbt.chat()`. For LLM configurations (such as how to generate embeddings and completions locally for free), see [this section](https://vectorbt.pro/pvt*ff8edc14/cookbook/knowledge/#provider-configs).

=== "Claude Desktop"

To find the absolute path to your Python interpreter, use the following command:

!!! note This must be the same Python interpreter that you used to install `vectorbtpro`.

You also need to set the `GITHUB*TOKEN` environment variable to download the knowledge assets if you haven't done so already. This happens automatically when you use [SearchVBT](https://vectorbt.pro/pvt*ff8edc14/features/intelligence/#searchvbt) or [ChatVBT](https://vectorbt.pro/pvt_ff8edc14/features/intelligence/#chatvbt) for the first time.

Generally, VBT does not require embeddings to function (it can use BM25 as a fallback), but they can enhance the search and chat features by providing better understanding of the content. By default, VBT uses either the OpenAI embeddings (paid) or the Hugging Face sentence transformers embeddings (free), depending on whether you have set the OpenAI API key or not. However, it supports a wide range of local and remote providers, including Google, Voyage, Ollama, and more. To change the provider, you can change the settings, [save them](https://vectorbt.pro/pvt*ff8edc14/cookbook/configuration/#settings), and then set the `VBT*SETTINGS_PATH` environment variable to point to the settings file in the `env` section of the MCP server configuration.

!!! note If you use the default local provider, model, and dimensions, VBT will automatically download the necessary embeddings for all documents from GitHub releases and persist them locally. For other configurations, you may need to generate and persist them yourself.

For example, you can use the following configuration to set the GitHub token and change the provider to Hugging Face to use embeddings locally for free:

!!! example "Cookbook" Explore [more provider configurations](https://vectorbt.pro/pvt_ff8edc14/cookbook/knowledge/#provider-configs).

!!! tip For API keys, you can use [this guide](https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety) to create and manage your keys globally.

And then set the `VBT*SETTINGS*PATH` environment variable in the MCP server configuration:

!!! tip Generally, it's recommended to test the [search and chat features](https://vectorbt.pro/pvt_ff8edc14/features/intelligence/) of VBT before setting up the MCP server. This way, you can ensure that the knowledge assets are downloaded and the embeddings are set up correctly. For example, you can use:

!!! important Also, make sure to use the same embedding configuration in both your local VBT installation and the MCP server to ensure consistency in responses.

Restart the app to apply the changes if needed.

You're now ready to chat with VBT! :sparkling_heart:{ .icon .heart }

**Examples:**

Example 1 (text):
```text
Follow [this guide](https://modelcontextprotocol.io/docs/develop/connect-local-servers)
to set up the MCP server for Claude Desktop.

Add the following "vectorbtpro" entry to the `mcpServers` section in `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "vectorbtpro": {
      "command": "/absolute/path/to/python",  // (1)!
      "args": [
        "-m",
        "vectorbtpro.mcp_server"
      ]
    }
  }
}
```

1. For absolute path to Python, see below.
```

Example 2 (text):
```text
Follow [this guide](https://code.claude.com/docs/en/mcp) to set up the MCP server for Claude Code.

You can add the MCP server directly from the Claude Code CLI:

```bash
claude mcp add --transport stdio vectorbtpro -- /absolute/path/to/python -m vectorbtpro.mcp_server  # (1)!
```

1. For absolute path to Python, see below.

Or add the following "vectorbtpro" entry to the `mcpServers` section in your Claude Code MCP configuration:

```json
{
  "mcpServers": {
    "vectorbtpro": {
      "command": "/absolute/path/to/python",  // (1)!
      "args": [
        "-m",
        "vectorbtpro.mcp_server"
      ]
    }
  }
}
```

1. For absolute path to Python, see below.
```

Example 3 (text):
```text
Follow [this guide](https://developers.openai.com/codex/mcp/) to set up the MCP server for Codex.

Add the following "vectorbtpro" entry to the "mcp_servers" section in your Codex configuration file:

```toml
[mcp_servers.vectorbtpro]
command = "/absolute/path/to/python"  # (1)!
args = ["-m", "vectorbtpro.mcp_server"]
```

1. For absolute path to Python, see below.
```

Example 4 (bash):
```bash
    which python
```

---
