# Vectorbtpro_Docs - Knowledge Mcp

**Pages:** 11

---

## tokenization

**URL:** https://vectorbt.pro/pvt_ff8edc14/api/knowledge/tokenization.md

**Contents:**
- detokenize <span class="dobjtype">function</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/tokenization.py#L429-L447" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.tokenization.detokenize data-toc-label="detokenize" }
- resolve_tokenizer <span class="dobjtype">function</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/tokenization.py#L362-L405" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.tokenization.resolve_tokenizer data-toc-label="resolve\_tokenizer" }
- tokenize <span class="dobjtype">function</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/tokenization.py#L408-L426" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.tokenization.tokenize data-toc-label="tokenize" }
- HFTokenizer <span class="dobjtype">class</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/tokenization.py#L265-L359" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.tokenization.HFTokenizer data-toc-label="HFTokenizer" }
  - hf_tokenizer <span class="dobjtype">class property</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/tokenization.py#L339-L346" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.tokenization.HFTokenizer.hf_tokenizer data-toc-label="hf\_tokenizer" }
  - model <span class="dobjtype">class property</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/tokenization.py#L330-L337" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.tokenization.HFTokenizer.model data-toc-label="model" }
- TikTokenizer <span class="dobjtype">class</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/tokenization.py#L153-L262" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.tokenization.TikTokenizer data-toc-label="TikTokenizer" }
  - encoding <span class="dobjtype">class property</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/tokenization.py#L220-L227" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.tokenization.TikTokenizer.encoding data-toc-label="encoding" }
  - tokens_per_message <span class="dobjtype">class property</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/tokenization.py#L229-L236" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.tokenization.TikTokenizer.tokens_per_message data-toc-label="tokens\_per\_message" }
  - tokens_per_name <span class="dobjtype">class property</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/tokenization.py#L238-L245" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.tokenization.TikTokenizer.tokens_per_name data-toc-label="tokens\_per\_name" }

Module providing classes and utilities for tokenization.

Detokenize tokens into text using a resolved [Tokenizer](https://vectorbt.pro/pvt_ff8edc14/api/knowledge/tokenization/#vectorbtpro.knowledge.tokenization.Tokenizer "vectorbtpro.knowledge.tokenization.Tokenizer").

**```tokens```** :&ensp;`Tokens` :   List of tokens to decode.

**```tokenizer```** :&ensp;`TokenizerLike` :   Identifier, subclass, or instance of [Tokenizer](https://vectorbt.pro/pvt_ff8edc14/api/knowledge/tokenization/#vectorbtpro.knowledge.tokenization.Tokenizer "vectorbtpro.knowledge.tokenization.Tokenizer").

**```**kwargs```** :   Keyword arguments to initialize or update `tokenizer`.

`str` :   Decoded text.

Resolve a [Tokenizer](https://vectorbt.pro/pvt_ff8edc14/api/knowledge/tokenization/#vectorbtpro.knowledge.tokenization.Tokenizer "vectorbtpro.knowledge.tokenization.Tokenizer") subclass or instance.

!!! info For default settings, see `chat` in [knowledge](https://vectorbt.pro/pvt*ff8edc14/api/*settings/#vectorbtpro.*settings.knowledge "vectorbtpro.*settings.knowledge").

**```tokenizer```** :&ensp;`TokenizerLike` :   Identifier, subclass, or instance of [Tokenizer](https://vectorbt.pro/pvt_ff8edc14/api/knowledge/tokenization/#vectorbtpro.knowledge.tokenization.Tokenizer "vectorbtpro.knowledge.tokenization.Tokenizer").

[Tokenizer](https://vectorbt.pro/pvt_ff8edc14/api/knowledge/tokenization/#vectorbtpro.knowledge.tokenization.Tokenizer "vectorbtpro.knowledge.tokenization.Tokenizer") :   Resolved tokenizer type or instance.

Tokenize text using a resolved [Tokenizer](https://vectorbt.pro/pvt_ff8edc14/api/knowledge/tokenization/#vectorbtpro.knowledge.tokenization.Tokenizer "vectorbtpro.knowledge.tokenization.Tokenizer").

**```text```** :&ensp;`str` :   Text to tokenize.

**```tokenizer```** :&ensp;`TokenizerLike` :   Identifier, subclass, or instance of [Tokenizer](https://vectorbt.pro/pvt_ff8edc14/api/knowledge/tokenization/#vectorbtpro.knowledge.tokenization.Tokenizer "vectorbtpro.knowledge.tokenization.Tokenizer").

**```**kwargs```** :   Keyword arguments to initialize or update `tokenizer`.

`Tokens` :   List of tokens representing the input text.

Tokenizer class for HuggingFace Transformers.

Uses `transformers.AutoTokenizer` to load a tokenizer by model name or path if not provided directly.

!!! info For default settings, see `chat.tokenizer*configs.hf` in [knowledge](https://vectorbt.pro/pvt*ff8edc14/api/*settings/#vectorbtpro.*settings.knowledge "vectorbtpro._settings.knowledge").

**```model```** :&ensp;`Optional[str]` :   Model name or path for `transformers.AutoTokenizer.from_pretrained`.

**```hf_tokenizer```** :&ensp;`Optional[PreTrainedTokenizerBase]` :   Pre-initialized HuggingFace tokenizer instance.

**```hf*tokenizer*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for `transformers.AutoTokenizer.from_pretrained`.

**```**kwargs```** :   Keyword arguments for [Tokenizer](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/tokenization/#vectorbtpro.knowledge.tokenization.Tokenizer "vectorbtpro.knowledge.tokenization.Tokenizer") or used as `hf*tokenizer_kwargs`.

**Inherited members**

HuggingFace tokenizer instance.

[HFTokenizer](https://vectorbt.pro/pvt_ff8edc14/api/knowledge/tokenization/#vectorbtpro.knowledge.tokenization.HFTokenizer "vectorbtpro.knowledge.tokenization.HFTokenizer") :   HuggingFace tokenizer.

`str` :   Model identifier.

Tokenizer class for tiktoken.

Encoding can be a model name, an encoding name, or an encoding object for tokenization.

!!! info For default settings, see `chat.tokenizer*configs.tiktoken` in [knowledge](https://vectorbt.pro/pvt*ff8edc14/api/*settings/#vectorbtpro.*settings.knowledge "vectorbtpro._settings.knowledge").

**```encoding```** :&ensp;`Union[None, str, Encoding]` :   Encoding specification as a model name, encoding name, or encoding object.

**```model```** :&ensp;`Optional[str]` :   Model identifier used to determine the encoding.

**```tokens*per*message```** :&ensp;`Optional[int]` :   Number of tokens charged per message.

**```tokens*per*name```** :&ensp;`Optional[int]` :   Additional token count for message names.

**```**kwargs```** :   Keyword arguments for [Tokenizer](https://vectorbt.pro/pvt_ff8edc14/api/knowledge/tokenization/#vectorbtpro.knowledge.tokenization.Tokenizer "vectorbtpro.knowledge.tokenization.Tokenizer").

**Inherited members**

Token encoding object used for tokenization.

`Encoding` :   Encoding object.

Token count charged per message.

`int` :   Number of tokens charged per message.

Additional token count for message names.

`int` :   Number of tokens charged for message names.

Abstract class for tokenizers.

!!! info For default settings, see [knowledge](https://vectorbt.pro/pvt*ff8edc14/api/*settings/#vectorbtpro.*settings.knowledge "vectorbtpro.*settings.knowledge") and its sub-configurations `chat` and `chat.tokenizer_config`.

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```**kwargs```** :   Keyword arguments for [Configured](https://vectorbt.pro/pvt_ff8edc14/api/utils/config/#vectorbtpro.utils.config.Configured "vectorbtpro.utils.config.Configured").

**Inherited members**

Return the total number of tokens in the provided text.

**```text```** :&ensp;`str` :   Text for token counting.

`int` :   Number of tokens.

Return the total number of tokens across the provided messages.

!!! abstract This method should be overridden in a subclass.

**```messages```** :&ensp;`ChatMessages` :   List of dictionaries representing the conversation history.

`int` :   Total token count.

Return the text obtained by decoding the given list of tokens.

!!! abstract This method should be overridden in a subclass.

**```tokens```** :&ensp;`list` :   List of tokens to decode.

`str` :   Decoded text.

Return the text decoded from the provided single token.

**```token```** :   Token to decode.

`str` :   Decoded text.

Return a list of tokens corresponding to the given text.

!!! abstract This method should be overridden in a subclass.

**```text```** :&ensp;`str` :   Text to encode.

`list` :   List of tokens representing the input text.

Return a single token encoded from the given text.

**```text```** :&ensp;`str` :   Text to encode.

`Token` :   Single token representing the input text.

`ValueError` :   If the text contains multiple tokens.

Additional context for template substitution.

`Kwargs` :   Dictionary of context variables for template substitution.

**Examples:**

Example 1 (python):
```python
detokenize(
    tokens,
    tokenizer=None,
    **kwargs
)
```

Example 2 (text):
```text
Resolved using [resolve_tokenizer](https://vectorbt.pro/pvt_ff8edc14/api/knowledge/tokenization/#vectorbtpro.knowledge.tokenization.resolve_tokenizer "vectorbtpro.knowledge.tokenization.resolve_tokenizer").
```

Example 3 (python):
```python
resolve_tokenizer(
    tokenizer=None
)
```

Example 4 (text):
```text
Supported identifiers:

* "tiktoken" for [TikTokenizer](https://vectorbt.pro/pvt_ff8edc14/api/knowledge/tokenization/#vectorbtpro.knowledge.tokenization.TikTokenizer "vectorbtpro.knowledge.tokenization.TikTokenizer")
* "hf" for [HFTokenizer](https://vectorbt.pro/pvt_ff8edc14/api/knowledge/tokenization/#vectorbtpro.knowledge.tokenization.HFTokenizer "vectorbtpro.knowledge.tokenization.HFTokenizer")
```

---

## provider_utils

**URL:** https://vectorbt.pro/pvt_ff8edc14/api/knowledge/provider_utils.md

**Contents:**
- check_ollama_available <span class="dobjtype">function</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/provider_utils.py#L16-L32" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.provider_utils.check_ollama_available data-toc-label="check\_ollama\_available" }
- resolve_provider <span class="dobjtype">function</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/provider_utils.py#L35-L115" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.provider_utils.resolve_provider data-toc-label="resolve\_provider" }

Module providing utilities for knowledge providers.

Check if Ollama is installed and its daemon is reachable.

`bool` :   True if Ollama is available, False otherwise.

Resolve the provider based on the given mode and candidates.

**```provider```** :&ensp;`str` :   Provider or mode to resolve the provider.

**```remote_candidates```** :&ensp;`Sequence[Tuple[str, Union[bool, Callable]]]` :   Sequence of remote provider candidates.

**```local_candidates```** :&ensp;`Sequence[Tuple[str, Union[bool, Callable]]]` :   Sequence of local provider candidates.

**```remote*fallback*candidates```** :&ensp;`Sequence[Tuple[str, Union[bool, Callable]]]` :   Sequence of remote fallback provider candidates.

**```local*fallback*candidates```** :&ensp;`Sequence[Tuple[str, Union[bool, Callable]]]` :   Sequence of local fallback provider candidates.

**```fallback_candidates```** :&ensp;`Sequence[Tuple[str, Union[bool, Callable]]]` :   Sequence of fallback provider candidates.

**```provider_name```** :&ensp;`str` :   Name of the provider argument for error messages.

`Optional[str]` :   The name of the resolved provider, or None if no provider is available.

**Examples:**

Example 1 (python):
```python
check_ollama_available()
```

Example 2 (python):
```python
resolve_provider(
    provider,
    remote_candidates=(),
    local_candidates=(),
    remote_fallback_candidates=(),
    local_fallback_candidates=(),
    fallback_candidates=(),
    provider_name='provider'
)
```

Example 3 (text):
```text
Supported modes are:

* "auto": Choose R, then L, then RF, then LF, then F.
* "prefer_remote": Choose R, then RF, then L, then LF, then F.
* "prefer_local": Choose L, then LF, then R, then RF, then F.
* "only_remote": Choose R, then RF.
* "only_local": Choose L, then LF.
* Any other value is treated as a provider name.
```

Example 4 (text):
```text
Each candidate is a tuple of (name, is_available), where is_available can be a boolean
or a callable that returns a boolean.
```

---

## doc_ranking

**URL:** https://vectorbt.pro/pvt_ff8edc14/api/knowledge/doc_ranking.md

**Contents:**
- embed_documents <span class="dobjtype">function</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/doc_ranking.py#L1766-L1809" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.doc_ranking.embed_documents data-toc-label="embed\_documents" }
- rank_documents <span class="dobjtype">function</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/doc_ranking.py#L1812-L1872" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.doc_ranking.rank_documents data-toc-label="rank\_documents" }
- Contextable <span class="dobjtype">class</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/doc_ranking.py#L1952-L2097" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.doc_ranking.Contextable data-toc-label="Contextable" }
  - chat <span class="dobjtype">class method</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/doc_ranking.py#L2051-L2097" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.doc_ranking.Contextable.chat data-toc-label="chat" }
  - count_tokens <span class="dobjtype">method</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/doc_ranking.py#L1976-L2007" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.doc_ranking.Contextable.count_tokens data-toc-label="count\_tokens" }
  - create_chat <span class="dobjtype">method</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/doc_ranking.py#L2009-L2049" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.doc_ranking.Contextable.create_chat data-toc-label="create\_chat" }
  - to_context <span class="dobjtype">method</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/doc_ranking.py#L1961-L1974" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.doc_ranking.Contextable.to_context data-toc-label="to\_context" }
- DocumentRanker <span class="dobjtype">class</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/doc_ranking.py#L78-L1763" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.doc_ranking.DocumentRanker data-toc-label="DocumentRanker" }
  - SPLIT_PATTERN <span class="dobjtype">Pattern</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/doc_ranking.py#L1036-L1038" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.doc_ranking.DocumentRanker.SPLIT_PATTERN data-toc-label="SPLIT\_PATTERN" }
  - TOKEN_PATTERN <span class="dobjtype">Pattern</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/doc_ranking.py#L1040-L1042" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.doc_ranking.DocumentRanker.TOKEN_PATTERN data-toc-label="TOKEN\_PATTERN" }

Module providing classes and utilities for ranking documents.

Embed the provided documents using a [DocumentRanker](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/doc*ranking/#vectorbtpro.knowledge.doc*ranking.DocumentRanker "vectorbtpro.knowledge.doc*ranking.DocumentRanker").

**```documents```** :&ensp;`Iterable[StoreDocument]` :   Collection of documents to embed.

**```refresh```** :&ensp;`bool` :   Flag to refresh both documents and embeddings.

**```refresh_documents```** :&ensp;`Optional[bool]` :   Flag to refresh documents; defaults to `refresh`.

**```refresh_embeddings```** :&ensp;`Optional[bool]` :   Flag to refresh embeddings; defaults to `refresh`.

**```return_embeddings```** :&ensp;`bool` :   Flag indicating whether to return embeddings.

**```return_documents```** :&ensp;`bool` :   If True, include original document objects in the output.

**```doc*ranker```** :&ensp;`Optional[MaybeType[DocumentRanker]]` :   [DocumentRanker](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/doc*ranking/#vectorbtpro.knowledge.doc*ranking.DocumentRanker "vectorbtpro.knowledge.doc_ranking.DocumentRanker") class or instance.

**```**kwargs```** :   Keyword arguments to initialize or update `doc_ranker`.

`Optional[EmbeddedDocuments]` :   Embedded documents output.

Rank documents based on their relevance to a query using a [DocumentRanker](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/doc*ranking/#vectorbtpro.knowledge.doc*ranking.DocumentRanker "vectorbtpro.knowledge.doc*ranking.DocumentRanker").

**```query```** :&ensp;`str` :   Query string for ranking.

**```documents```** :&ensp;`Optional[Iterable[StoreDocument]]` :   Collection of documents to rank.

**```top_k```** :&ensp;`TopKLike` :   Number or percentage of top documents to return, or a method to determine it.

**```min*top*k```** :&ensp;`TopKLike` :   Minimum limit for determining top documents.

**```max*top*k```** :&ensp;`TopKLike` :   Maximum limit for determining top documents.

**```cutoff```** :&ensp;`Optional[float]` :   Score threshold to filter documents.

**```refresh```** :&ensp;`bool` :   Flag to refresh both documents and embeddings.

**```refresh_documents```** :&ensp;`Optional[bool]` :   Flag to refresh documents; defaults to `refresh`.

**```refresh_embeddings```** :&ensp;`Optional[bool]` :   Flag to refresh embeddings; defaults to `refresh`.

**```return_chunks```** :&ensp;`bool` :   Whether to return document chunks.

**```return_scores```** :&ensp;`bool` :   Whether to return scored documents with their scores.

**```doc*ranker```** :&ensp;`Optional[MaybeType[DocumentRanker]]` :   [DocumentRanker](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/doc*ranking/#vectorbtpro.knowledge.doc*ranking.DocumentRanker "vectorbtpro.knowledge.doc_ranking.DocumentRanker") class or instance.

**```**kwargs```** :   Keyword arguments to initialize or update `doc_ranker`.

`RankedDocuments` :   Ranked documents based on the query relevance.

Abstract class that provides functionality to generate a textual context.

!!! info For default settings, see [knowledge](https://vectorbt.pro/pvt*ff8edc14/api/*settings/#vectorbtpro.*settings.knowledge "vectorbtpro.*settings.knowledge") and its sub-configuration `chat`.

**Inherited members**

Chat with a language model using the instance as context.

!!! note Context is recalculated each time this method is invoked. For multiple turns, it's more efficient to use [Contextable.create*chat](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/doc*ranking/#vectorbtpro.knowledge.doc*ranking.Contextable.create*chat "vectorbtpro.knowledge.doc*ranking.Contextable.create_chat").

**```message```** :&ensp;`str` :   Message to send to the language model.

**```chat_history```** :&ensp;`Optional[ChatHistory]` :   Chat history, a list of dictionaries with defined roles.

**```return_chat```** :&ensp;`bool` :   Flag indicating whether to return both the completion and the chat instance.

**```**kwargs```** :   Keyword arguments for [Contextable.create*chat](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/doc*ranking/#vectorbtpro.knowledge.doc*ranking.Contextable.create*chat "vectorbtpro.knowledge.doc*ranking.Contextable.create_chat").

`MaybeChatOutput` :   Completion response or a tuple of the response and the chat instance.

Count the number of tokens in the generated context. tokenizer_kwargs (KwargsLike): Keyword arguments to initialize or update `tokenizer`.

**```to*context*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for [Contextable.to*context](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/doc*ranking/#vectorbtpro.knowledge.doc*ranking.Contextable.to*context "vectorbtpro.knowledge.doc*ranking.Contextable.to_context").

**```tokenizer```** :&ensp;`TokenizerLike` :   Identifier, subclass, or instance of [Tokenizer](https://vectorbt.pro/pvt_ff8edc14/api/knowledge/tokenization/#vectorbtpro.knowledge.tokenization.Tokenizer "vectorbtpro.knowledge.tokenization.Tokenizer").

`int` :   Number of tokens in the context.

Create a chat interface using the generated context.

**```to*context*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for [Contextable.to*context](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/doc*ranking/#vectorbtpro.knowledge.doc*ranking.Contextable.to*context "vectorbtpro.knowledge.doc*ranking.Contextable.to_context").

**```completions```** :&ensp;`CompletionsLike` :   Identifier, subclass, or instance of [Completions](https://vectorbt.pro/pvt_ff8edc14/api/knowledge/completions/#vectorbtpro.knowledge.completions.Completions "vectorbtpro.knowledge.completions.Completions").

**```**kwargs```** :   Keyword arguments to initialize or update `completions`.

`Completions` :   Instance of [Completions](https://vectorbt.pro/pvt_ff8edc14/api/knowledge/completions/#vectorbtpro.knowledge.completions.Completions "vectorbtpro.knowledge.completions.Completions") configured with the generated context.

**Overridden by methods**

Convert the instance into a textual context.

!!! abstract This method should be overridden in a subclass.

**```*args```** :   Additional positional arguments.

**```**kwargs```** :   Additional keyword arguments.

`str` :   Textual context representation.

**Overridden by methods**

Class for embedding, scoring, and ranking documents.

!!! info For default settings, see [knowledge](https://vectorbt.pro/pvt*ff8edc14/api/*settings/#vectorbtpro.*settings.knowledge "vectorbtpro.*settings.knowledge") and its sub-configurations `chat` and `chat.doc*ranker*config`.

**```dataset_id```** :&ensp;`Optional[str]` :   Identifier for the dataset.

**```embeddings```** :&ensp;`EmbeddingsLike` :   Identifier, subclass, or instance of [Embeddings](https://vectorbt.pro/pvt_ff8edc14/api/knowledge/embeddings/#vectorbtpro.knowledge.embeddings.Embeddings "vectorbtpro.knowledge.embeddings.Embeddings").

**```embeddings_kwargs```** :&ensp;`KwargsLike` :   Keyword arguments to initialize or update `embeddings`.

**```doc*store```** :&ensp;`ObjectStoreLike` :   Identifier, subclass, or instance of [ObjectStore](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/doc*storing/#vectorbtpro.knowledge.doc*storing.ObjectStore "vectorbtpro.knowledge.doc_storing.ObjectStore") for documents.

**```doc*store*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments to initialize or update `doc_store`.

**```cache*doc*store```** :&ensp;`Optional[bool]` :   Flag to indicate if `doc_store` should be cached.

**```emb*store```** :&ensp;`ObjectStoreLike` :   Identifier, subclass, or instance of [ObjectStore](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/doc*storing/#vectorbtpro.knowledge.doc*storing.ObjectStore "vectorbtpro.knowledge.doc_storing.ObjectStore") for embeddings.

**```emb*store*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments to initialize or update `emb_store`.

**```cache*emb*store```** :&ensp;`Optional[bool]` :   Flag to indicate if `emb_store` should be cached.

**```search_method```** :&ensp;`Optional[str]` :   Strategy for document search.

**```bm25_tokenizer```** :&ensp;`Optional[BM25Tokenizer]` :   BM25 tokenizer instance or type for processing text.

**```bm25*tokenizer*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments to initialize `bm25_tokenizer`.

**```bm25_retriever```** :&ensp;`Optional[MaybeType[BM25]]` :   BM25 retriever instance or type for document retrieval.

**```bm25*retriever*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments to initialize `bm25_retriever`.

**```bm25*mirror*store_id```** :&ensp;`Optional[str]` :   Identifier for the BM25 mirror store.

**```rrf_k```** :&ensp;`Optional[int]` :   K parameter for RRF (Reciprocal Rank Fusion).

**```rrf*bm25*weight```** :&ensp;`Optional[float]` :   BM25 weight for RRF (Reciprocal Rank Fusion).

**```score_func```** :&ensp;`Union[None, str, Callable]` :   Function or identifier for scoring documents.

**```score*agg*func```** :&ensp;`Union[None, str, Callable]` :   Function or identifier for aggregating scores.

**```normalize_scores```** :&ensp;`Optional[bool]` :   Whether scores should be normalized before filtering.

**```rerank```** :&ensp;`Optional[bool]` :   Whether to perform reranking after initial scoring.

**```reranker```** :&ensp;`RerankerLike` :   Identifier, subclass, or instance of [Reranker](https://vectorbt.pro/pvt_ff8edc14/api/knowledge/reranking/#vectorbtpro.knowledge.reranking.Reranker "vectorbtpro.knowledge.reranking.Reranker").

**```reranker_kwargs```** :&ensp;`KwargsLike` :   Keyword arguments to initialize or update `reranker`.

**```rerank_limit```** :&ensp;`Optional[int]` :   Maximum number of top documents to send to the reranker.

**```rerank*top*chunks```** :&ensp;`Union[None, bool, int]` :   Number of top-scoring chunks per document to send to the reranker.

**```show_progress```** :&ensp;`Optional[bool]` :   Flag indicating whether to display the progress bar.

**```pbar_kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for configuring the progress bar.

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```**kwargs```** :   Keyword arguments for [Configured](https://vectorbt.pro/pvt_ff8edc14/api/utils/config/#vectorbtpro.utils.config.Configured "vectorbtpro.utils.config.Configured").

**Inherited members**

Regular expression pattern used by [DocumentRanker.bm25*splitter](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/doc*ranking/#vectorbtpro.knowledge.doc*ranking.DocumentRanker.bm25*splitter "vectorbtpro.knowledge.doc*ranking.DocumentRanker.bm25_splitter") to split text at transitions between lowercase and uppercase letters or underscores.

Regular expression pattern used by [DocumentRanker.bm25*splitter](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/doc*ranking/#vectorbtpro.knowledge.doc*ranking.DocumentRanker.bm25*splitter "vectorbtpro.knowledge.doc*ranking.DocumentRanker.bm25_splitter") to extract tokens with at least two characters.

Keyword arguments for the `retrieve` method of `bm25s.BM25`.

`Kwargs` :   Dictionary of parameters for the retrieval process.

BM25 retriever instance from `bm25s.BM25`.

`Optional[BM25]` :   BM25 retriever instance used for document retrieval; None if not set.

Return BM25 relevance scores for documents matching a query.

**```query```** :&ensp;`str` :   Query string for relevance scoring.

**```documents```** :&ensp;`Optional[Iterable[StoreDocument]]` :   Collection of documents to score.

**```refresh```** :&ensp;`bool` :   Flag to refresh both documents and embeddings.

**```refresh_documents```** :&ensp;`Optional[bool]` :   Flag to refresh documents; defaults to `refresh`.

**```return_chunks```** :&ensp;`bool` :   Whether to return document chunks.

**```return_documents```** :&ensp;`bool` :   If True, include original document objects in the output.

`ScoredDocuments` :   Computed BM25 scores for each document, as either numeric scores or [ScoredDocument](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/doc*ranking/#vectorbtpro.knowledge.doc*ranking.ScoredDocument "vectorbtpro.knowledge.doc*ranking.ScoredDocument") objects.

Return a list of lowercase tokens extracted from the input text using BM25 tokenization.

**```text```** :&ensp;`str` :   Text to tokenize.

`List[str]` :   Lowercase tokens extracted from the input text.

Keyword arguments for the `tokenize` method of `bm25s.tokenization.Tokenizer`.

`Kwargs` :   Dictionary of parameters for the tokenization process.

BM25 tokenizer instance from `bm25s.tokenization.Tokenizer`.

`Optional[BM25Tokenizer]` :   BM25 tokenizer instance used for processing text; None if not set.

Compute similarity or distance scores between embeddings.

Compute scores between embedding vectors using the configured scoring function. Supported functions include "cosine", "euclidean", and "dot". Alternatively, a callable metric can be supplied that accepts two arrays and returns a 2D ndarray.

**```emb1```** :&ensp;`Union[MaybeIterable[List[float]], Array]` :   First embedding or collection of embeddings.

**```emb2```** :&ensp;`Union[MaybeIterable[List[float]], Array]` :   Second embedding or collection of embeddings.

`Union[float, Array]` :   Computed score or score matrix between the embeddings.

Instance of [ObjectStore](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/doc*storing/#vectorbtpro.knowledge.doc*storing.ObjectStore "vectorbtpro.knowledge.doc*storing.ObjectStore") used for documents.

`ObjectStore` :   Document store instance used for managing documents.

Instance of [ObjectStore](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/doc*storing/#vectorbtpro.knowledge.doc*storing.ObjectStore "vectorbtpro.knowledge.doc*storing.ObjectStore") used for embeddings.

`ObjectStore` :   Embedding store instance used for managing embeddings.

Embed documents by optionally refreshing stored documents and embeddings.

Without refreshing, persisted objects from the respective stores are used.

**```documents```** :&ensp;`Iterable[StoreDocument]` :   Collection of documents to embed.

**```refresh```** :&ensp;`bool` :   Flag to refresh both documents and embeddings.

**```refresh_documents```** :&ensp;`Optional[bool]` :   Flag to refresh documents; defaults to `refresh`.

**```refresh_embeddings```** :&ensp;`Optional[bool]` :   Flag to refresh embeddings; defaults to `refresh`.

**```return_embeddings```** :&ensp;`bool` :   Flag indicating whether to return embeddings.

**```return_documents```** :&ensp;`bool` :   If True, include original document objects in the output.

**```with*fallback```** :&ensp;`bool` :   If True, raise [FallbackError](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/doc*ranking/#vectorbtpro.knowledge.doc*ranking.FallbackError "vectorbtpro.knowledge.doc_ranking.FallbackError") if new embeddings are needed.

`Optional[EmbeddedDocuments]` :   Embedded documents or embeddings based on the specified return flags.

Instance of [Embeddings](https://vectorbt.pro/pvt_ff8edc14/api/knowledge/embeddings/#vectorbtpro.knowledge.embeddings.Embeddings "vectorbtpro.knowledge.embeddings.Embeddings").

`Embeddings` :   Embeddings engine or class used for processing document embeddings; None if not set.

Recursively extract paired scores from embedding and BM25 scored documents.

**```emb*scored*documents```** :&ensp;`List[ScoredDocument]` :   Documents scored using embeddings.

**```bm25*scored*documents```** :&ensp;`List[ScoredDocument]` :   Documents scored using BM25.

`List[Tuple[float, float]]` :   Pairs of scores from corresponding documents and their child documents.

Extract scores from a list of scored documents.

**```scored_documents```** :&ensp;`List[ScoredDocument]` :   Documents with existing scores.

**```recursive```** :&ensp;`bool` :   Whether to recursively include child document scores.

`List[float]` :   Scores extracted from each document and optionally its child documents.

Filter scored documents based on top-k parameters and score cutoff.

!!! note This method assumes that documents are already sorted by score in descending order.

**```scored_documents```** :&ensp;`List[ScoredDocument]` :   Documents with existing scores.

**```top_k```** :&ensp;`TopKLike` :   Number or percentage of top documents to return, or a method to determine it.

**```min*top*k```** :&ensp;`TopKLike` :   Minimum limit for determining top documents.

**```max*top*k```** :&ensp;`TopKLike` :   Maximum limit for determining top documents.

**```cutoff```** :&ensp;`Optional[float]` :   Score threshold to filter documents.

`List[ScoredDocument]` :   Filtered list of scored documents.

Fuse paired (embedding, BM25) scores with Reciprocal-Rank Fusion (RRF).

**```doc*pair*scores```** :&ensp;`Iterable[Tuple[float, float]]` :   Paired scores (embedding, BM25) to fuse.

`ndarray` :   Array of fused scores.

Fuse embedding and BM25 scored documents by merging and updating their scores.

**```emb*scored*documents```** :&ensp;`List[ScoredDocument]` :   Documents scored using embeddings.

**```bm25*scored*documents```** :&ensp;`List[ScoredDocument]` :   Documents scored using BM25.

`List[ScoredDocument]` :   Fused scored documents with updated scores.

Normalize a collection of scores using min-max scaling.

**```scores```** :&ensp;`Iterable[float]` :   Iterable of scores to normalize.

**```score_range```** :&ensp;`Optional[Tuple[float, float]]` :   Known (min, max) bounds for the scores.

`ndarray` :   Array of normalized scores in [0, 1].

Normalize the scores of scored documents using min-max scaling.

**```scored_documents```** :&ensp;`List[ScoredDocument]` :   Documents with existing scores.

**```score_range```** :&ensp;`Optional[Tuple[float, float]]` :   Known (min, max) bounds for the scores.

**```recursive```** :&ensp;`bool` :   Whether to recursively normalize child document scores.

`List[ScoredDocument]` :   Documents with normalized scores.

Whether scores should be normalized before filtering.

`bool` :   True if scores should be normalized; otherwise, False.

Keyword arguments for [ProgressBar](https://vectorbt.pro/pvt_ff8edc14/api/pbar/core/#vectorbtpro.pbar.core.ProgressBar "vectorbtpro.pbar.core.ProgressBar").

`Kwargs` :   Keyword arguments for the progress bar.

Rank documents based on their relevance to a query.

The method retrieves scored documents using embedding and BM25 strategies (or both in hybrid mode), fuses and normalizes their scores, and then sorts them to identify the most relevant documents. Top-k parameters and score cutoff are resolved using [DocumentRanker.resolve*top*k](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/doc*ranking/#vectorbtpro.knowledge.doc*ranking.DocumentRanker.resolve*top*k "vectorbtpro.knowledge.doc*ranking.DocumentRanker.resolve*top*k") and [DocumentRanker.top*k*from*cutoff](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/doc*ranking/#vectorbtpro.knowledge.doc*ranking.DocumentRanker.top*k*from*cutoff "vectorbtpro.knowledge.doc*ranking.DocumentRanker.top*k*from_cutoff").

When reranking is enabled, `top*k`, `cutoff`, `min*top*k`, and `max*top*k` are applied to the reranked scores rather than the initial scores. Only `rerank*limit` controls how many documents are sent to the reranker.

**```query```** :&ensp;`str` :   Query string to evaluate document relevance.

**```documents```** :&ensp;`Optional[Iterable[StoreDocument]]` :   Collection of documents to rank.

**```top_k```** :&ensp;`TopKLike` :   Number or percentage of top documents to return, or a method to determine it.

**```min*top*k```** :&ensp;`TopKLike` :   Minimum limit for determining top documents.

**```max*top*k```** :&ensp;`TopKLike` :   Maximum limit for determining top documents.

**```cutoff```** :&ensp;`Optional[float]` :   Score threshold to filter documents.

**```refresh```** :&ensp;`bool` :   Flag to refresh both documents and embeddings.

**```refresh_documents```** :&ensp;`Optional[bool]` :   Flag to refresh documents; defaults to `refresh`.

**```refresh_embeddings```** :&ensp;`Optional[bool]` :   Flag to refresh embeddings; defaults to `refresh`.

**```return_chunks```** :&ensp;`bool` :   Whether to return document chunks.

**```return_scores```** :&ensp;`bool` :   Whether to return scored documents with their scores.

`RankedDocuments` :   Documents ranked by relevance to the query.

Recursively replace scores in paired embedding and BM25 documents with new scores.

**```emb*scored*documents```** :&ensp;`List[ScoredDocument]` :   Documents scored using embeddings.

**```bm25*scored*documents```** :&ensp;`List[ScoredDocument]` :   Documents scored using BM25.

**```new_scores```** :&ensp;`List[float]` :   New scores to assign, consumed in order.

`List[ScoredDocument]` :   Updated documents with replaced paired scores.

Replace scores in documents with new scores.

**```scored_documents```** :&ensp;`List[ScoredDocument]` :   Documents with existing scores.

**```new_scores```** :&ensp;`List[float]` :   New scores to assign, consumed in order.

**```recursive```** :&ensp;`bool` :   Whether to recursively replace child document scores.

`List[ScoredDocument]` :   Updated documents with replaced scores.

Rerank scored documents using a reranker model.

**```query```** :&ensp;`str` :   Query string to evaluate document relevance.

**```scored_documents```** :&ensp;`List[ScoredDocument]` :   Documents with existing scores.

`List[ScoredDocument]` :   Reranked list of scored documents.

Maximum number of top documents to send to the reranker.

Only the first `rerank_limit` documents (by initial ranking score) are reranked.

`Optional[int]` :   Maximum document count for reranking.

Number of top-scoring chunks per document to send to the reranker.

If None, the full document content is used.

`Optional[int]` :   Number of chunks to use for reranking.

Instance of [Reranker](https://vectorbt.pro/pvt_ff8edc14/api/knowledge/reranking/#vectorbtpro.knowledge.reranking.Reranker "vectorbtpro.knowledge.reranking.Reranker").

`Optional[Reranker]` :   Reranker instance; None if not set.

Return a tuple containing a resolved instance of `bm25s.BM25` and retrieval keyword arguments.

**```bm25_retriever```** :&ensp;`Optional[BM25]` :   BM25 retriever instance or type.

**```**kwargs```** :   Keyword arguments for initializing `bm25_retriever` and retrieval.

`Tuple[BM25T, Kwargs]` :   Resolved BM25 retriever and the retrieval keyword arguments.

Return a tuple containing a resolved instance of `bm25s.tokenization.Tokenizer` and tokenization keyword arguments.

**```bm25_tokenizer```** :&ensp;`Optional[BM25Tokenizer]` :   BM25 tokenizer instance or type.

**```**kwargs```** :   Keyword arguments for initializing `bm25_tokenizer` and tokenization.

`Tuple[BM25TokenizerT, Kwargs]` :   Resolved BM25 tokenizer and the tokenization keyword arguments.

Resolve the `top_k` value from sorted scores.

**```scores```** :&ensp;`Iterable[float]` :   Sorted document scores.

**```top*k```** :&ensp;`TopKLike` :   Parameter specifying the `top*k` selection method, which can be an integer, a float percentage, a string ('elbow' or 'kmeans'), or a callable.

`Optional[int]` :   Resolved `top*k` value, or None if `top*k` is not provided.

BM25 weight for RRF (Reciprocal Rank Fusion).

The embedding weight is computed as 1 minus this value.

`float` :   BM25 weight used in RRF.

K parameter for RRF (Reciprocal Rank Fusion).

`int` :   K parameter used in RRF.

Function used to aggregate scores.

`Callable` :   Function used for aggregating scores.

Score documents by relevance to a query.

Optionally refresh and embed documents before scoring their relevance to a query. If no documents are provided, the document store is used. When `return_chunks` is True, document chunks are scored instead of parent documents. The query is embedded and compared against document embeddings to compute relevance scores.

**```query```** :&ensp;`str` :   Query string for scoring relevance.

**```documents```** :&ensp;`Optional[Iterable[StoreDocument]]` :   Collection of documents to score.

**```refresh```** :&ensp;`bool` :   Flag to refresh both documents and embeddings.

**```refresh_documents```** :&ensp;`Optional[bool]` :   Flag to refresh documents; defaults to `refresh`.

**```refresh_embeddings```** :&ensp;`Optional[bool]` :   Flag to refresh embeddings; defaults to `refresh`.

**```return_chunks```** :&ensp;`bool` :   Whether to return document chunks.

**```return_documents```** :&ensp;`bool` :   If True, include original document objects in the output.

**```with*fallback```** :&ensp;`bool` :   If True, raise [FallbackError](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/doc*ranking/#vectorbtpro.knowledge.doc*ranking.FallbackError "vectorbtpro.knowledge.doc_ranking.FallbackError") if new embeddings are needed.

`ScoredDocuments` :   Collection of documents with their computed relevance scores.

Score function or its name used for computing document scores.

See [DocumentRanker.compute*score](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/doc*ranking/#vectorbtpro.knowledge.doc*ranking.DocumentRanker.compute*score "vectorbtpro.knowledge.doc*ranking.DocumentRanker.compute_score").

`Union[str, Callable]` :   Score function used for computing document scores.

Strategy for document search.

Supported strategies:

`str` :   Search method used for document retrieval.

Whether to display a progress bar.

`Optional[bool]` :   True if progress bar is shown, False otherwise.

Sort scored documents.

**```scored_documents```** :&ensp;`List[ScoredDocument]` :   Documents with existing scores.

**```reverse```** :&ensp;`bool` :   Whether to sort in descending order of scores.

`List[ScoredDocument]` :   Documents sorted by score.

Additional context for template substitution.

`Kwargs` :   Dictionary of context variables for template substitution.

Determine the number of top documents based on a cutoff threshold from sorted scores.

**```scores```** :&ensp;`Iterable[float]` :   Sorted document scores.

**```cutoff```** :&ensp;`Optional[float]` :   Score threshold to filter documents.

`Optional[int]` :   Count of scores greater than or equal to the cutoff, or None if cutoff is None.

Define an abstract class for embedded documents.

**Inherited members**

List of embedded child documents.

Primary document content.

Embedding instance representing the document's content.

Exception raised when a fallback is triggered.

Abstract class combining [Rankable](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/doc*ranking/#vectorbtpro.knowledge.doc*ranking.Rankable "vectorbtpro.knowledge.doc*ranking.Rankable") and [Contextable](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/doc*ranking/#vectorbtpro.knowledge.doc*ranking.Contextable "vectorbtpro.knowledge.doc*ranking.Contextable") functionalities.

This abstract class integrates ranking with contextual chat processing by applying ranking methods to chat queries when ranking parameters are provided.

**Inherited members**

Return the chat output with optional ranking applied.

If `rank` is True, or if `rank` is None and any ranking parameter (`top*k`, `min*top*k`, `max*top*k`, `cutoff`, or `return*chunks`) is specified, process the query using [Rankable.rank](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/doc*ranking/#vectorbtpro.knowledge.doc*ranking.Rankable.rank "vectorbtpro.knowledge.doc*ranking.Rankable.rank") before delegating to [Contextable.chat](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/doc*ranking/#vectorbtpro.knowledge.doc*ranking.Contextable.chat "vectorbtpro.knowledge.doc*ranking.Contextable.chat").

**```message```** :&ensp;`str` :   Message to send to the language model.

**```chat_history```** :&ensp;`Optional[ChatHistory]` :   Chat history, a list of dictionaries with defined roles.

**```incl*past*queries```** :&ensp;`Optional[bool]` :   Whether to include past queries in the ranking process.

**```rank```** :&ensp;`Optional[bool]` :   Flag indicating whether to apply ranking.

**```top_k```** :&ensp;`TopKLike` :   Number or percentage of top documents to return, or a method to determine it.

**```min*top*k```** :&ensp;`TopKLike` :   Minimum limit for determining top documents.

**```max*top*k```** :&ensp;`TopKLike` :   Maximum limit for determining top documents.

**```cutoff```** :&ensp;`Optional[float]` :   Score threshold to filter documents.

**```return_chunks```** :&ensp;`Optional[bool]` :   Whether to return document chunks.

**```rank*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for [Rankable.rank](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/doc*ranking/#vectorbtpro.knowledge.doc*ranking.Rankable.rank "vectorbtpro.knowledge.doc_ranking.Rankable.rank").

**```**kwargs```** :   Keyword arguments for [Contextable.chat](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/doc*ranking/#vectorbtpro.knowledge.doc*ranking.Contextable.chat "vectorbtpro.knowledge.doc*ranking.Contextable.chat").

`MaybeChatOutput` :   Completion response or a tuple of the response and the chat instance.

Abstract class representing an entity that supports embedding and ranking operations.

!!! info For default settings, see [knowledge](https://vectorbt.pro/pvt*ff8edc14/api/*settings/#vectorbtpro.*settings.knowledge "vectorbtpro.*settings.knowledge") and its sub-configuration `chat`.

**Inherited members**

Embed the instance's documents.

!!! abstract This method should be overridden in a subclass.

**```refresh```** :&ensp;`bool` :   Flag to refresh both documents and embeddings.

**```refresh_documents```** :&ensp;`Optional[bool]` :   Flag to refresh documents; defaults to `refresh`.

**```refresh_embeddings```** :&ensp;`Optional[bool]` :   Flag to refresh embeddings; defaults to `refresh`.

**```return_embeddings```** :&ensp;`bool` :   Flag indicating whether to return embeddings.

**```return_documents```** :&ensp;`bool` :   If True, include original document objects in the output.

**```**kwargs```** :   Additional keyword arguments.

`Optional[Rankable]` :   Updated instance with embedded documents, if available.

**Overridden by methods**

Rank documents based on their relevance to a provided query.

!!! abstract This method should be overridden in a subclass.

**```query```** :&ensp;`str` :   Query string to evaluate document relevance.

**```top_k```** :&ensp;`TopKLike` :   Number or percentage of top documents to return, or a method to determine it.

**```min*top*k```** :&ensp;`TopKLike` :   Minimum limit for determining top documents.

**```max*top*k```** :&ensp;`TopKLike` :   Maximum limit for determining top documents.

**```cutoff```** :&ensp;`Optional[float]` :   Score threshold to filter documents.

**```refresh```** :&ensp;`bool` :   Flag to refresh both documents and embeddings.

**```refresh_documents```** :&ensp;`Optional[bool]` :   Flag to refresh documents; defaults to `refresh`.

**```refresh_embeddings```** :&ensp;`Optional[bool]` :   Flag to refresh embeddings; defaults to `refresh`.

**```return_chunks```** :&ensp;`bool` :   Whether to return document chunks.

**```return_scores```** :&ensp;`bool` :   Whether to return scored documents with their scores.

**```**kwargs```** :   Additional keyword arguments.

[Rankable](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/doc*ranking/#vectorbtpro.knowledge.doc*ranking.Rankable "vectorbtpro.knowledge.doc*ranking.Rankable") :   Updated instance with ranked documents.

**Overridden by methods**

Define an abstract class for scored documents with an associated numerical score.

**Inherited members**

List of scored child documents.

Primary document content.

Numeric score assigned to the document.

**Examples:**

Example 1 (python):
```python
embed_documents(
    documents,
    refresh=False,
    refresh_documents=None,
    refresh_embeddings=None,
    return_embeddings=False,
    return_documents=False,
    doc_ranker=None,
    **kwargs
)
```

Example 2 (python):
```python
rank_documents(
    query,
    documents=None,
    top_k=None,
    min_top_k=None,
    max_top_k=None,
    cutoff=None,
    refresh=False,
    refresh_documents=None,
    refresh_embeddings=None,
    return_chunks=False,
    return_scores=False,
    doc_ranker=None,
    **kwargs
)
```

Example 3 (text):
```text
If None, documents from the document store are used.
```

Example 4 (python):
```python
Contextable()
```

---

## Knowledge

**URL:** https://vectorbt.pro/pvt_ff8edc14/cookbook/knowledge.md

**Contents:**
- Assets
  - VBT assets
  - Generic assets
- Describing
- Manipulating
- Querying
  - Code
  - Links
  - Objects
  - Nodes

Knowledge assets are instances of [KnowledgeAsset](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base_assets.KnowledgeAsset) that contain a list of Python objects (most often dicts) and provide various methods to manipulate them. For usage examples, see the API documentation for each specific method.

There are two knowledge assets in VBT: 1) website pages, and 2) Discord messages. The first asset includes pages and headings from the (mainly private) website. Each data item represents either a page or a page heading. Pages generally point to one or more other pages or headings, while headings contain text content, all reflecting the structure of Markdown files. The second asset consists of messages from the "vectorbt.pro" Discord server, where each data item is a Discord message, which may reference other messages through replies.

The assets are attached to each [release](https://github.com/polakowo/vectorbt.pro/releases) as `pages.json.gz` and `messages.json.gz`. These are GZIP-compressed JSON files, managed by [PagesAsset](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/custom*assets/#vectorbtpro.knowledge.custom*assets.PagesAsset) and [MessagesAsset](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/custom*assets/#vectorbtpro.knowledge.custom*assets.MessagesAsset) classes, respectively. You can load them automatically or manually. For automatic loading, a GitHub token is required.

!!! tip The first pull will download the assets, and subsequent pulls will use cached versions. After upgrading VBT, new assets will be downloaded automatically.

__$user*cache*dir/knowledge/vbt/$release*name/pages/assets/** for pages and **$user*cache*dir/knowledge/vbt/$release*name/messages/assets/__ for messages.

Knowledge assets are not limited to VBT assets—you can build an asset from any list!

Knowledge assets behave like regular lists, so to describe an asset, you should describe it as a list. This enables many analysis options, such as checking the length, printing out a random data item, and more advanced options like printing out the field schema. Most data items in an asset are dicts, so you can describe them by their fields.

Works on all assets where data items are dicts.

A knowledge asset is simply an advanced list: it looks like a VBT object, but behaves like a list. For manipulation, it provides a collection of methods ending with `item` or `items` to get, set, or remove data items—either by returning a new asset instance (default) or modifying the asset in place.

A wide range of methods are available to query an asset: [get](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.get) / [select](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.select), [query](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.query) / [filter](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.filter), and [find](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base_assets.KnowledgeAsset.find). The first pair is used to get and process one or more fields from each data item. The `get` method returns the raw output, while the `select` method returns a new asset instance. The second pair lets you run queries on the asset using various engines, such as JMESPath. Again, the `query` method returns the raw output, while the `filter` method returns a new asset instance. Finally, the `find` method is specialized for searching across one or more fields. By default, it returns a new asset instance.

skip data items where it is missing.

with the data item referred to as "x" and its fields accessed by name.

similarly to the source expression in `get`.

it would act as a filter and return the data items matching the condition.

Here, get the heading name for every data item with object type "class", and sort.

If `find_all` is False, the conjunction would be "or".

!!! tip To make chained calls easier to read, use either of the following styles:

There is a specialized method for finding code, either in single backticks or code blocks.

Custom knowledge assets like pages and messages have specialized methods for finding data items by their link. The default behavior matches the target against the end of each link. This approach ensures that searching for both "https://vectorbt.pro/become-a-member/" and "become-a-member/" will consistently return "https://vectorbt.pro/become-a-member/". When using "exact" or "end" mode, a variant with or without a slash is automatically included. This way, searching for "become-a-member" (without a slash) will still return "https://vectorbt.pro/become-a-member/". The method also ignores other matched links like "https://vectorbt.pro/become-a-member/#become-a-member" since they belong to the same page.

You can also find headings that correspond to VBT objects.

You can also traverse pages and messages in a way similar to navigating nodes within a graph.

!!! note Each operation requires at least one full data pass; use sparingly.

"Find" and many other methods rely on [KnowledgeAsset.apply](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply), which executes a function on each data item. These are called asset functions and consist of two parts: argument preparation and function calling. The main advantage is that arguments are prepared only once, then passed to each function call. Execution is managed by the powerful [execute](https://vectorbt.pro/pvt*ff8edc14/api/utils/execution/#vectorbtpro.utils.execution.execute) function, which supports parallelization.

either a new asset instance or the raw output is returned.

Most examples show how to run a chain of standalone operations, but each operation processes the data at least once. To process data just once, regardless of the number of operations, use asset pipelines. There are two types: basic and complex. Basic pipelines take a list of tasks (such as functions and their arguments) and compose them into a single operation that acts on a data item. This composed operation is then applied to all data items. Complex pipelines use a Python expression in a functional style, where one function receives a data item and returns a result that becomes the argument for the next function.

!!! info In both pipeline types, arguments are prepared only once during initialization.

[Reducing](https://realpython.com/python-reduce-function/) means merging all data items into one. This requires a function that takes two data items. Initially, these two data items are the initializer (such as an empty dict) and the first data item. If the initializer is unknown, the first two data items are used. The result of this first iteration is then used as the first data item in the next iteration. Execution is handled by [KnowledgeAsset.reduce](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base_assets.KnowledgeAsset.reduce) and cannot be parallelized since each iteration depends on the previous one.

Depending on the function, either a new asset instance or the raw output is returned.

<div class="separator-container"> <hr class="separator"> <span class="separator-text">+</span> <hr class="separator"> </div>

You can also split a knowledge asset into groups and reduce those groups. Group iteration is handled by the [execute](https://vectorbt.pro/pvt_ff8edc14/api/utils/execution/#vectorbtpro.utils.execution.execute) function, which supports parallelization.

Since headings are represented as individual data items, they can be aggregated back into their parent page. This is useful when you want to [format](#formatting) or [display](#browsing) the page. Note that only headings can be aggregated; pages themselves cannot be aggregated into other pages.

<div class="separator-container"> <hr class="separator"> <span class="separator-text">+</span> <hr class="separator"> </div>

Messages, on the other hand, can be aggregated across multiple levels: *"message"*, *"block"*, *"thread"*, and *"channel"*. Aggregation here means collecting messages that belong to the specified level, and dumping them into the content of a single, bigger message.

do not reference anything. The link for the block is the link of the first message in the block.

The link for the thread is the link of the first message in the thread.

Most Python objects can be dumped (that is, serialized) into strings.

<div class="separator-container"> <hr class="separator"> <span class="separator-text">+</span> <hr class="separator"> </div>

Custom knowledge assets such as pages and messages can be converted, and optionally saved, in Markdown or HTML format. Only the "content" field will be converted; other fields are used to build the metadata block shown at the start of each file.

!!! note Without [aggregation](#aggregating), each page heading will become a separate file.

By default, saves to __$user*cache*dir/knowledge/vbt/$release*name/pages/markdown/** for pages and **$user*cache*dir/knowledge/vbt/$release*name/messages/markdown/__ for messages.

By default, saves to __$user*cache*dir/knowledge/vbt/$release*name/pages/html/** for pages and **$user*cache*dir/knowledge/vbt/$release*name/pages/html/__ for messages.

Pages and messages can be displayed and browsed using static HTML files. When displaying a single item, VBT creates a temporary HTML file and opens it in the default browser. All links in this file remain **external**. When displaying multiple items, VBT creates a single HTML file where the items are shown as iframes that you can navigate using pagination.

<div class="separator-container"> <hr class="separator"> <span class="separator-text">+</span> <hr class="separator"> </div>

If you want to browse one or more pages (or headings) like a website, VBT can convert all data items to HTML and replace all external links with **internal** links, allowing you to navigate from one page to another locally. But which page appears first? Pages and headings create a directed graph. If there is a single page from which all other pages can be accessed, that page is displayed first. If there are multiple such pages, VBT creates an index page with metadata blocks that let you access the other pages (unless you specify `entry_link`).

__$user*cache*dir/knowledge/vbt/$release*name/pages/html/** for pages and **$user*cache*dir/knowledge/vbt/$release*name/messages/html/__ for messages.

Assets can be easily combined. If the target class is not specified, their common superclass is used. For example, combining [PagesAsset](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/custom*assets/#vectorbtpro.knowledge.custom*assets.PagesAsset) and [MessagesAsset](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/custom*assets/#vectorbtpro.knowledge.custom*assets.MessagesAsset) produces an instance of [VBTAsset](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/custom*assets/#vectorbtpro.knowledge.custom_assets.VBTAsset), which includes features shared by both assets, such as the "link" and "content" fields.

<div class="separator-container"> <hr class="separator"> <span class="separator-text">+</span> <hr class="separator"> </div>

If both assets contain the same number of data items, you can also merge them at the data item level. This method works for complex containers, such as nested dictionaries and lists, by flattening their nested structures into flat dictionaries, merging them, and then unflattening them back into the original container types.

<div class="separator-container"> <hr class="separator"> <span class="separator-text">+</span> <hr class="separator"> </div>

You can also merge all data items in a single asset into one data item.

There are four methods for searching for any VBT object in pages and messages. The first method searches for the API documentation of the object. The second method searches for mentions of the object in the non-API (human-readable) documentation. The third method searches for mentions of the object in Discord messages. The last method searches for mentions of the object in the code of both pages and messages.

It includes the (aggregated) base classes, such as [Configured](https://vectorbt.pro/pvt*ff8edc14/api/utils/pickling/#vectorbtpro.utils.pickling.Configured), and (non-aggregated) parent modules, such as [portfolio.pfopt.base](https://vectorbt.pro/pvt*ff8edc14/api/portfolio/pfopt/base/#vectorbtpro.portfolio.pfopt.base).

It includes (aggregated) base methods, such as [Wrapping.row*stack](https://vectorbt.pro/pvt*ff8edc14/api/base/wrapping/#vectorbtpro.base.wrapping.Wrapping.row*stack), (non-aggregated) parent objects such as [PortfolioOptimizer](https://vectorbt.pro/pvt*ff8edc14/api/portfolio/pfopt/base/#vectorbtpro.portfolio.pfopt.base.PortfolioOptimizer), and (non-aggregated) references.

across all non-API pages. It searches for full reference names, shortcuts (such as `vbt.PFO`), imports (such as `from ... import PFO`), typical instance names (such as `pfo =`), and access or call notations (such as `PFO.`).

it takes the (aggregated) parent instead. Here, it takes the entire page if any mention is found.

it includes the parent page as well.

related to targets (the first block in `find*docs` recipes) and does not accept arguments related to pages (the second block in `find*docs` recipes).

<div class="separator-container"> <hr class="separator"> <span class="separator-text">+</span> <hr class="separator"> </div>

The first three methods are guaranteed not to overlap, while the last method may return examples that can also be found by the first three methods. There is also another method that, by default, calls the first three methods and combines their results into a single asset. This approach allows you to gather all relevant knowledge about a VBT object.

You can search not only for knowledge related to a specific VBT object but also for any VBT items that match a query in natural language. This process works by embedding both the query and the data items, calculating their pairwise similarity scores, and sorting the data items by their mean score in descending order. Since the result contains all the data items from the original set, just in a different order, it is recommended to select the top-k results before displaying them.

All the methods discussed in [objects](#for-objects) can also be used on queries!

<div class="separator-container"> <hr class="separator"> <span class="separator-text">+</span> <hr class="separator"> </div>

There is also a specialized [search](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/custom*assets/#vectorbtpro.knowledge.custom*assets.search) function that calls [find*assets](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/custom*assets/#vectorbtpro.knowledge.custom*assets.find*assets), caches the documents (so the next search runs much faster), and displays the top results as a static HTML page.

!!! info The first time you run this command, it may take up to 15 minutes to prepare and embed documents. However, most preparation steps are cached and stored, so future searches will be significantly faster without repeating the process.

<div class="separator-container"> <hr class="separator"> <span class="separator-text">+</span> <hr class="separator"> </div>

Building an index of embeddings for searching is not always necessary. Instead, you can use BM25, a fast and reliable algorithm that works completely offline.

!!! tip Use this method when your query contains specific keywords. For vague queries, embeddings are a better choice.

Knowledge assets can be used as context when chatting with LLMs. The main method for chatting is [Contextable.chat](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/doc*ranking/#vectorbtpro.knowledge.doc_ranking.Contextable.chat), which [dumps](#formatting) the asset instance, combines it with your question and chat history into messages, sends them to the LLM service, then displays and saves the response. The response can be shown in various formats, including raw text, Markdown, and HTML. All three formats support streaming. This method is compatible with multiple LLM APIs, such as OpenAI, LiteLLM, and LLamaIndex.

Another option is passing `api_key` directly or saving it in the settings, as shown for `model` below.

If you do not know the private hash, you can paste the suffix. See [querying](#querying).

By default, the context is trimmed to 100,000 tokens (the exact allowance depends on the model, e.g., GPT-4o supports 128,000). Content is shuffled to prevent placing more weight on older or newer content when trimming the context.

in descending order, and merge them into a single list. When embeddings are unavailable, this is a common workflow when there is too much data.

__$user*cache*dir/knowledge/vbt/$release_name/chat__.

[VBTAsset.to*html](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/custom*assets/#vectorbtpro.knowledge.custom*assets.VBTAsset.to_html).

Note that when displaying HTML, the minimum update interval is 1 second.

You can chat about a VBT object using [chat*about](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/custom*assets/#vectorbtpro.knowledge.custom*assets.chat*about). This function calls the method above, but operates only on code examples. When you pass arguments, they are automatically distributed between [find*assets](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/custom*assets/#vectorbtpro.knowledge.custom*assets.find*assets) and [KnowledgeAsset.chat](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base_assets.KnowledgeAsset.chat) (see [chatting](#chatting) for recipes).

and ask a question using this knowledge as context.

[Portfolio](https://vectorbt.pro/pvt_ff8edc14/api/portfolio/base/#vectorbtpro.portfolio.base.Portfolio) class.

100,000 tokens. Also, set the user role instead of the system role for the initial instruction.

You can also ask questions about objects that do not technically exist in VBT or about general keywords, such as "quantstats", which will search for mentions of "quantstats" within pages and messages.

Similar to the global [search](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/custom*assets/#vectorbtpro.knowledge.custom*assets.search) function, there is a global function for chatting: [chat](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/custom*assets/#vectorbtpro.knowledge.custom*assets.chat). It processes documents in the same way, but instead of displaying results, it sends them to an LLM for completion.

!!! info The first time you run this command, it may take up to 15 minutes to prepare and embed documents. Most preparation steps are cached and stored, so future searches will be much faster and do not need to repeat the process.

By default, up to 100 document chunks are used.

<div class="separator-container"> <hr class="separator"> <span class="separator-text">+</span> <hr class="separator"> </div>

Building an index of embeddings for chatting is not always required. Instead, you can use BM25, a quick and reliable algorithm that works entirely offline. Additionally, this function will use a smaller context and a less expensive model for completions, such as "gpt-4o-mini" instead of "gpt-4o".

!!! tip Use this when your query contains distinctive keywords. For vague queries, embeddings are a better option.

If you have a basic question, want to save money, or prefer chatting from a mobile device, check out [QuantGPT](https://www.quantgpt.chat/), a free service generously hosted by our member @simrell. QuantGPT uses the same knowledge base (website and Discord) as our ChatVBT function, powered by the OpenAI Assistants API, which we have replicated with our own RAG.

<div class="grid cards width-fifty" markdown>

!!! info Both tools should give similar answers, but ChatVBT (that is, `vbt.chat()`) offers clickable references, full control over the knowledge base (which may improve completions), and the flexibility to use any LLM, not just OpenAI.

In addition to the context-based chat functionality, VBT also supports tool calls to interact with the MCP server and any user-defined functions. This functionality is also available in `vbt.chat()`.

It will become immediately available in the MCP server.

!!! tip When defining a tool function, 1) use `def` instead of `lambda`, 2) use annotations for the input types, and 3) write comprehensive documentation as a (preferably) Google-formatted docstring.

VBT uses a set of components for standard RAG. Most of these are orchestrated and deployed automatically whenever you globally [search](#globally) for knowledge on VBT or [chat](#globally_1) about VBT.

The [Tokenizer](https://vectorbt.pro/pvt_ff8edc14/api/knowledge/tokenization/#vectorbtpro.knowledge.tokenization.Tokenizer) class and its subclasses provide an interface for converting text into tokens.

The [Embeddings](https://vectorbt.pro/pvt_ff8edc14/api/knowledge/embeddings/#vectorbtpro.knowledge.embeddings.Embeddings) class and its subclasses provide an interface for generating vector representations of text.

The [Completions](https://vectorbt.pro/pvt_ff8edc14/api/knowledge/completions/#vectorbtpro.knowledge.completions.Completions) class and its subclasses provide an interface for generating text completions based on user queries. For arguments such as `formatter`, see [chatting](#chatting).

The [TextSplitter](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/text*splitting/#vectorbtpro.knowledge.text_splitting.TextSplitter) class and its subclasses provide an interface for splitting text.

words (if the sentence is too long), and then tokens (if the word is too long).

The [ObjectStore](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/doc*storing/#vectorbtpro.knowledge.doc*storing.ObjectStore) class and its subclasses provide an interface for efficiently storing and retrieving arbitrary Python objects, such as text documents and embeddings. These objects must subclass [StoreObject](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/doc*storing/#vectorbtpro.knowledge.doc*storing.StoreObject).

lifetime of the Python process.

Patching means that additional changes are saved as separate files.

for the lifetime of the Python process.

The [Reranker](https://vectorbt.pro/pvt_ff8edc14/api/knowledge/reranking/#vectorbtpro.knowledge.reranking.Reranker) class and its subclasses provide an interface for reranking documents based on a query.

It returns a list of tuples containing the document index and its score, sorted by score in descending order.

The [DocumentRanker](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/doc*ranking/#vectorbtpro.knowledge.doc_ranking.DocumentRanker) class provides an interface for embedding, scoring, and ranking documents.

You can also choose to return the embedded documents or the embeddings themselves.

You can also specify whether to return the scores for the chunks (by default they are aggregated), or the documents along with their scores.

this reorders the documents, but you can also choose to return the documents with their scores.

The components described above can enhance RAG pipelines, extending their utility beyond the VBT scope.

VBT supports a variety of providers for document embedding and completion tasks. Below you can find common configurations for each provider. These configurations can be set globally or per-query.

[OpenAI](https://openai.com/) is the default provider in VBT.

OpenAI requires you to set the `OPENAI*API*KEY` environment variable or pass it directly as `api_key`.

??? abstract "Embeddings"

??? abstract "Completions"

Set the appropriate base URL and API key to use [OpenRouter](https://openrouter.ai/) or other OpenAI-compatible providers.

[Anthropic](https://www.anthropic.com/) with Claude is a popular LLM provider.

Anthropic requires you to set the `ANTHROPIC*API*KEY` environment variable or pass it directly as `api_key`.

!!! info Anthropic does not currently support embeddings.

??? abstract "Completions"

[Gemini](https://ai.google.dev/) is Google's latest LLM offering.

Google requires you to set the `GEMINI*API*KEY` environment variable or pass it directly as `api_key`.

??? abstract "Embeddings"

??? abstract "Completions"

[Hugging Face](https://huggingface.co/) provides a wide range of models and APIs. The Inference API allows you to use these models for embeddings and completions without needing to host your own infrastructure.

Hugging Face requires you to set the `HF*TOKEN` environment variable or pass it directly as `api*key`.

??? abstract "Embeddings"

??? abstract "Completions"

Here's the configuration that is used by @polakowo to pre-generate local embeddings using a custom Hugging Face Inference endpoint. To create an endpoint, visit the [Model Catalog](https://endpoints.huggingface.co/polakowo/catalog), select a model, and click "Create Endpoint". Then, use the provided URL and your Hugging Face API token in the settings below.

then uploaded to GitHub Releases by @polakowo.

[LiteLLM](https://www.litellm.ai/) is an LLM gateway in OpenAI format.

There isn't a specific API key for LiteLLM; you need to set the environment variable for the provider you want to use, such as `DEEPSEEK*API*KEY` for DeepSeek, or pass it directly as `api_key`. See the [LiteLLM documentation](https://docs.litellm.ai/) for more details.

??? abstract "Embeddings"

??? abstract "Completions"

[LlamaIndex](https://llamaindex.ai/) is a framework for building LLM applications that supports various data sources and integrations. While it provides a (somewhat) unified interface for working with different LLM providers, you may need to install and configure each provider individually.

There isn't a specific API key for LlamaIndex; you need to set the environment variable for the provider you want to use, such as `DEEPSEEK*API*KEY` for DeepSeek, or pass it directly as `api_key`. See the [LlamaIndex documentation](https://docs.llamaindex.ai/) for more details.

??? abstract "Embeddings"

??? abstract "Completions"

LlamaIndex can be configured to use local Hugging Face models for embeddings and completions.

[Ollama](https://ollama.com/) is a platform for running LLMs on your own hardware.

??? abstract "Embeddings"

??? abstract "Completions"

[GPT-OSS](https://openai.com/index/introducing-gpt-oss/) is OpenAI's open-source alternative to ChatGPT mini models, designed to provide similar capabilities while being freely available.

To clear any knowledge caches, such as embeddings and completions caches, remove the cache directory. This may be useful to free up disk space and when changing LLM providers or models to avoid using outdated cached data.

**Examples:**

Example 1 (text):
```text
env["GITHUB_TOKEN"] = "<YOUR_GITHUB_TOKEN>"  # (1)!
pages_asset = vbt.PagesAsset.pull()
messages_asset = vbt.MessagesAsset.pull()

# ______________________________________________________________

vbt.settings.set("knowledge.assets.vbt.token", "YOUR_GITHUB_TOKEN")  # (2)!
pages_asset = vbt.PagesAsset.pull()
messages_asset = vbt.MessagesAsset.pull()

# ______________________________________________________________

pages_asset = vbt.PagesAsset(/MessagesAsset).pull(release_name="v2024.8.20") # (3)!
pages_asset = vbt.PagesAsset(/MessagesAsset).pull(cache_dir="my_cache_dir") # (4)!
pages_asset = vbt.PagesAsset(/MessagesAsset).pull(clear_cache=True) # (5)!
pages_asset = vbt.PagesAsset(/MessagesAsset).pull(cache=False)  # (6)!

# ______________________________________________________________

pages_asset = vbt.PagesAsset.from_json_file("pages.json.gz") # (7)!
messages_asset = vbt.MessagesAsset.from_json_file("messages.json.gz")
```

Example 2 (text):
```text
asset = vbt.KnowledgeAsset(my_list)  # (1)!
asset = vbt.KnowledgeAsset.from_json_file("my_list.json")  # (2)!
asset = vbt.KnowledgeAsset.from_json_bytes(vbt.load_bytes("my_list.json"))  # (3)!
```

Example 3 (text):
```text
print(len(asset))  # (1)!

asset.sample().print()  # (2)!
asset.print_sample()

asset.print_schema()  # (3)!

vbt.pprint(messages_asset.describe())  # (4)!

pages_asset.print_site_schema()  # (5)!
```

Example 4 (text):
```text
d = asset.get_items(0)  # (1)!
d = asset[0]
data = asset[0:100]  # (2)!
data = asset[mask]  # (3)!
data = asset[indices]  # (4)!

# ______________________________________________________________

new_asset = asset.set_items(0, new_d)  # (5)!
asset.set_items(0, new_d, inplace=True)  # (6)!
asset[0] = new_d  # (7)!
asset[0:100] = new_data
asset[mask] = new_data
asset[indices] = new_data

# ______________________________________________________________

new_asset = asset.delete_items(0)  # (8)!
asset.delete_items(0, inplace=True)
asset.remove(0)
del asset[0]
del asset[0:100]
del asset[mask]
del asset[indices]

# ______________________________________________________________

new_asset = asset.append_item(new_d)  # (9)!
asset.append_item(new_d, inplace=True)
asset.append(new_d)

# ______________________________________________________________

new_asset = asset.extend_items([new_d1, new_d2])  # (10)!
asset.extend_items([new_d1, new_d2], inplace=True)
asset.extend([new_d1, new_d2])
asset += [new_d1, new_d2]

# ______________________________________________________________

print(d in asset)  # (11)!
print(asset.index(d))  # (12)!
print(asset.count(d))  # (13)!

# ______________________________________________________________

for d in asset:  # (14)!
    ...
```

---

## custom_asset_funcs

**URL:** https://vectorbt.pro/pvt_ff8edc14/api/knowledge/custom_asset_funcs.md

**Contents:**
- AggBlockAssetFunc <span class="dobjtype">class</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/custom_asset_funcs.py#L601-L803" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.custom_asset_funcs.AggBlockAssetFunc data-toc-label="AggBlockAssetFunc" }
  - prepare <span class="dobjtype">class method</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/custom_asset_funcs.py#L609-L687" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.custom_asset_funcs.AggBlockAssetFunc.prepare data-toc-label="prepare" }
- AggChannelAssetFunc <span class="dobjtype">class</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/custom_asset_funcs.py#L902-L1016" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.custom_asset_funcs.AggChannelAssetFunc data-toc-label="AggChannelAssetFunc" }
  - get_channel_link <span class="dobjtype">class method</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/custom_asset_funcs.py#L908-L929" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.custom_asset_funcs.AggChannelAssetFunc.get_channel_link data-toc-label="get\_channel\_link" }
- AggMessageAssetFunc <span class="dobjtype">class</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/custom_asset_funcs.py#L477-L598" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.custom_asset_funcs.AggMessageAssetFunc data-toc-label="AggMessageAssetFunc" }
  - prepare <span class="dobjtype">class method</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/custom_asset_funcs.py#L485-L551" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.custom_asset_funcs.AggMessageAssetFunc.prepare data-toc-label="prepare" }
- AggThreadAssetFunc <span class="dobjtype">class</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/custom_asset_funcs.py#L806-L899" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.custom_asset_funcs.AggThreadAssetFunc data-toc-label="AggThreadAssetFunc" }
- ToHTMLAssetFunc <span class="dobjtype">class</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/custom_asset_funcs.py#L230-L474" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.custom_asset_funcs.ToHTMLAssetFunc data-toc-label="ToHTMLAssetFunc" }
  - get_html_content <span class="dobjtype">class method</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/custom_asset_funcs.py#L379-L400" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.custom_asset_funcs.ToHTMLAssetFunc.get_html_content data-toc-label="get\_html\_content" }
  - get_html_metadata <span class="dobjtype">class method</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/custom_asset_funcs.py#L316-L377" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.custom_asset_funcs.ToHTMLAssetFunc.get_html_metadata data-toc-label="get\_html\_metadata" }

Module providing custom asset function classes.

Asset function class for aggregating block messages with [MessagesAsset.aggregate*blocks](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/custom*assets/#vectorbtpro.knowledge.custom*assets.MessagesAsset.aggregate*blocks "vectorbtpro.knowledge.custom*assets.MessagesAsset.aggregate_blocks").

**Inherited members**

Prepare positional and keyword arguments for an asset function call.

**```aggregate_fields```** :&ensp;`Union[None, bool, Iterable[str]]` :   Fields to aggregate instead of including in child metadata; True aggregates all lists; False aggregates none.

**```parent*links*only```** :&ensp;`Optional[bool]` :   If True, excludes links from the metadata.

**```minimize_metadata```** :&ensp;`Optional[bool]` :   Whether to minimize metadata.

**```minimize_keys```** :&ensp;`Optional[MaybeList[PathLikeKey]]` :   Keys specifying which metadata to minimize.

**```clean_metadata```** :&ensp;`Optional[bool]` :   If True, remove empty metadata fields.

**```clean*metadata*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for cleaning metadata.

**```dump*metadata*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for dumping metadata.

**```metadata_fence```** :&ensp;`Optional[str]` :   Metadata fence to use for formatting.

**```to*markdown*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for markdown conversion.

**```link_map```** :&ensp;`Optional[Dict[str, dict]]` :   Mapping of links to their corresponding data items.

**```asset_cls```** :&ensp;`Optional[Type[KnowledgeAsset]]` :   Asset class to use for resolving settings.

**```**kwargs```** :   Additional keyword arguments.

`ArgsKwargs` :   Tuple containing the positional arguments and keyword arguments.

Asset function class for aggregating channel messages with [MessagesAsset.aggregate*channels](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/custom*assets/#vectorbtpro.knowledge.custom*assets.MessagesAsset.aggregate*channels "vectorbtpro.knowledge.custom*assets.MessagesAsset.aggregate_channels").

**Inherited members**

Return the channel link extracted from a message link.

**```link```** :&ensp;`str` :   Message link to process.

`str` :   Extracted channel link.

Asset function class for aggregating messages with [MessagesAsset.aggregate*messages](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/custom*assets/#vectorbtpro.knowledge.custom*assets.MessagesAsset.aggregate*messages "vectorbtpro.knowledge.custom*assets.MessagesAsset.aggregate_messages").

**Inherited members**

Prepare positional and keyword arguments for an asset function call.

**```minimize_metadata```** :&ensp;`Optional[bool]` :   Whether to minimize metadata.

**```minimize_keys```** :&ensp;`Optional[MaybeList[PathLikeKey]]` :   Keys specifying which metadata to minimize.

**```clean_metadata```** :&ensp;`Optional[bool]` :   If True, remove empty metadata fields.

**```clean*metadata*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for cleaning metadata.

**```dump*metadata*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for dumping metadata.

**```metadata_fence```** :&ensp;`Optional[str]` :   Metadata fence to use for formatting.

**```to*markdown*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for markdown conversion.

**```asset_cls```** :&ensp;`Optional[Type[KnowledgeAsset]]` :   Asset class to use for resolving settings.

**```**kwargs```** :   Additional keyword arguments.

`ArgsKwargs` :   Tuple containing the positional arguments and keyword arguments.

Asset function class for aggregating thread messages with [MessagesAsset.aggregate*threads](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/custom*assets/#vectorbtpro.knowledge.custom*assets.MessagesAsset.aggregate*threads "vectorbtpro.knowledge.custom*assets.MessagesAsset.aggregate_threads").

**Inherited members**

Asset function class for converting asset data to HTML with [VBTAsset.to*html](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/custom*assets/#vectorbtpro.knowledge.custom*assets.VBTAsset.to*html "vectorbtpro.knowledge.custom*assets.VBTAsset.to_html").

**Inherited members**

Return HTML formatted content by converting data to markdown using [ToMarkdownAssetFunc.get*markdown*content](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/custom*asset*funcs/#vectorbtpro.knowledge.custom*asset*funcs.ToMarkdownAssetFunc.get*markdown*content "vectorbtpro.knowledge.custom*asset*funcs.ToHTMLAssetFunc.get*markdown*content") and then to HTML using [to*html](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/formatting/#vectorbtpro.knowledge.formatting.to*html "vectorbtpro.knowledge.formatting.to_html").

**```d```** :&ensp;`dict` :   Asset data dictionary.

**```to*markdown*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for markdown conversion.

**```**kwargs```** :   Keyword arguments for [to*html](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/formatting/#vectorbtpro.knowledge.formatting.to*html "vectorbtpro.knowledge.formatting.to*html").

`str` :   HTML formatted content.

Return HTML formatted metadata by converting data to markdown using [ToMarkdownAssetFunc.get*markdown*metadata](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/custom*asset*funcs/#vectorbtpro.knowledge.custom*asset*funcs.ToMarkdownAssetFunc.get*markdown*metadata "vectorbtpro.knowledge.custom*asset*funcs.ToHTMLAssetFunc.get*markdown*metadata") and then to HTML using [to*html](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/formatting/#vectorbtpro.knowledge.formatting.to*html "vectorbtpro.knowledge.formatting.to_html").

**```d```** :&ensp;`dict` :   Asset data dictionary.

**```root*metadata*key```** :&ensp;`Optional[Key]` :   Key under which to nest metadata.

**```allow_empty```** :&ensp;`Optional[bool]` :   Whether to allow empty metadata.

**```minimize_metadata```** :&ensp;`bool` :   If True, remove specified keys to minimize metadata.

**```minimize_keys```** :&ensp;`Optional[List[PathLikeKey]]` :   Keys to minimize in the metadata.

**```clean_metadata```** :&ensp;`bool` :   If True, clean the metadata to remove empty or irrelevant values.

**```clean*metadata*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for cleaning metadata.

**```dump*metadata*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for dumping metadata.

**```metadata_fence```** :&ensp;`str` :   Metadata fence to use for formatting.

**```to*markdown*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for markdown conversion.

**```**to*html*kwargs```** :   Keyword arguments for [to*html](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/formatting/#vectorbtpro.knowledge.formatting.to*html "vectorbtpro.knowledge.formatting.to*html").

`str` :   HTML formatted metadata.

Prepare positional and keyword arguments for an asset function call.

**```root*metadata*key```** :&ensp;`Optional[Key]` :   Key under which to nest metadata.

**```minimize_metadata```** :&ensp;`Optional[bool]` :   Whether to minimize metadata.

**```minimize_keys```** :&ensp;`Optional[MaybeList[PathLikeKey]]` :   Keys specifying which metadata to minimize.

**```clean_metadata```** :&ensp;`Optional[bool]` :   If True, remove empty metadata fields.

**```clean*metadata*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for cleaning metadata.

**```dump*metadata*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for dumping metadata.

**```metadata_fence```** :&ensp;`Optional[str]` :   Metadata fence to use for formatting.

**```to*markdown*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for markdown conversion.

**```format*html*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for HTML formatting.

**```asset_cls```** :&ensp;`Optional[Type[KnowledgeAsset]]` :   Asset class to use for resolving settings.

**```**to*html*kwargs```** :   Keyword arguments for [to*html](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/formatting/#vectorbtpro.knowledge.formatting.to*html "vectorbtpro.knowledge.formatting.to*html").

`ArgsKwargs` :   Tuple containing the positional arguments and keyword arguments.

Asset function class for formatting asset metadata and content as Markdown with [VBTAsset.to*markdown](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/custom*assets/#vectorbtpro.knowledge.custom*assets.VBTAsset.to*markdown "vectorbtpro.knowledge.custom*assets.VBTAsset.to_markdown").

**Inherited members**

Return Markdown formatted content by converting data to markdown using [to*markdown](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/formatting/#vectorbtpro.knowledge.formatting.to*markdown "vectorbtpro.knowledge.formatting.to*markdown").

**```d```** :&ensp;`dict` :   Asset data dictionary.

**```**kwargs```** :   Keyword arguments for [to*markdown](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/formatting/#vectorbtpro.knowledge.formatting.to*markdown "vectorbtpro.knowledge.formatting.to*markdown").

`str` :   Markdown formatted content string.

Return Markdown formatted metadata by converting data to markdown using [to*markdown](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/formatting/#vectorbtpro.knowledge.formatting.to*markdown "vectorbtpro.knowledge.formatting.to*markdown").

**```d```** :&ensp;`dict` :   Asset data dictionary.

**```root*metadata*key```** :&ensp;`Optional[Key]` :   Key under which to nest metadata.

**```allow_empty```** :&ensp;`Optional[bool]` :   Whether to allow empty metadata.

**```minimize_metadata```** :&ensp;`bool` :   If True, remove specified keys to minimize metadata.

**```minimize_keys```** :&ensp;`Optional[Union[PathLikeKey, list]]` :   Key or list of keys to remove during minimization.

**```clean_metadata```** :&ensp;`bool` :   If True, clean the metadata to remove empty or irrelevant values.

**```clean*metadata*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for cleaning metadata.

**```dump*metadata*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for dumping metadata.

**```metadata_fence```** :&ensp;`str` :   Metadata fence to use for formatting.

**```**to*markdown*kwargs```** :   Keyword arguments for [to*markdown](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/formatting/#vectorbtpro.knowledge.formatting.to*markdown "vectorbtpro.knowledge.formatting.to*markdown").

`str` :   Markdown formatted metadata string.

Prepare positional and keyword arguments for an asset function call.

**```root*metadata*key```** :&ensp;`Optional[Key]` :   Key under which to nest metadata.

**```minimize_metadata```** :&ensp;`Optional[bool]` :   Whether to minimize metadata.

**```minimize_keys```** :&ensp;`Optional[MaybeList[PathLikeKey]]` :   Keys specifying which metadata to minimize.

**```clean_metadata```** :&ensp;`Optional[bool]` :   If True, remove empty metadata fields.

**```clean*metadata*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for cleaning metadata.

**```dump*metadata*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for dumping metadata.

**```metadata_fence```** :&ensp;`Optional[str]` :   Metadata fence to use for formatting.

**```asset_cls```** :&ensp;`Optional[Type[KnowledgeAsset]]` :   Asset class to use for resolving settings.

**```**to*markdown*kwargs```** :   Keyword arguments for [to*markdown](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/formatting/#vectorbtpro.knowledge.formatting.to*markdown "vectorbtpro.knowledge.formatting.to*markdown").

`ArgsKwargs` :   Tuple containing the positional arguments and keyword arguments.

**Examples:**

Example 1 (python):
```python
AggBlockAssetFunc()
```

Example 2 (python):
```python
AggBlockAssetFunc.prepare(
    aggregate_fields=None,
    parent_links_only=None,
    minimize_metadata=None,
    minimize_keys=None,
    clean_metadata=None,
    clean_metadata_kwargs=None,
    dump_metadata_kwargs=None,
    metadata_fence=None,
    to_markdown_kwargs=None,
    link_map=None,
    asset_cls=None,
    **kwargs
)
```

Example 3 (text):
```text
See [FindRemoveAssetFunc](https://vectorbt.pro/pvt_ff8edc14/api/knowledge/base_asset_funcs/#vectorbtpro.knowledge.base_asset_funcs.FindRemoveAssetFunc "vectorbtpro.knowledge.base_asset_funcs.FindRemoveAssetFunc").
```

Example 4 (text):
```text
See [DumpAssetFunc](https://vectorbt.pro/pvt_ff8edc14/api/knowledge/base_asset_funcs/#vectorbtpro.knowledge.base_asset_funcs.DumpAssetFunc "vectorbtpro.knowledge.base_asset_funcs.DumpAssetFunc").
```

---

## mcp

**URL:** https://vectorbt.pro/pvt_ff8edc14/api/mcp.md

**Contents:**
- current_kernel <span class="dobjtype">variable</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/mcp.py#L783-L784" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.mcp.current_kernel data-toc-label="current\_kernel" }
- tool_registry <span class="dobjtype">dict</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/mcp.py#L25-L26" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.mcp.tool_registry data-toc-label="tool\_registry" }
- auto_cast <span class="dobjtype">function</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/mcp.py#L53-L62" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.mcp.auto_cast data-toc-label="auto\_cast" }
- find <span class="dobjtype">function</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/mcp.py#L272-L417" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.mcp.find data-toc-label="find" }
- get_attrs <span class="dobjtype">function</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/mcp.py#L647-L736" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.mcp.get_attrs data-toc-label="get\_attrs" }
- get_message <span class="dobjtype">function</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/mcp.py#L472-L516" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.mcp.get_message data-toc-label="get\_message" }
- get_message_block <span class="dobjtype">function</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/mcp.py#L519-L580" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.mcp.get_message_block data-toc-label="get\_message\_block" }
- get_message_thread <span class="dobjtype">function</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/mcp.py#L583-L644" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.mcp.get_message_thread data-toc-label="get\_message\_thread" }
- get_page <span class="dobjtype">function</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/mcp.py#L420-L469" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.mcp.get_page data-toc-label="get\_page" }
- get_source <span class="dobjtype">function</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/mcp.py#L739-L780" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.mcp.get_source data-toc-label="get\_source" }

Module providing MCP tool definitions and the tool registry.

Tools registered here are used by the MCP server ([vectorbtpro.mcp*server](https://vectorbt.pro/pvt*ff8edc14/api/mcp*server/ "vectorbtpro.mcp*server")) and the CLI ([vectorbtpro.cli](https://vectorbt.pro/pvt_ff8edc14/api/cli/ "vectorbtpro.cli")).

Currently running Jupyter kernel for executing code snippets.

Registry mapping tool names to functions for execution.

Automatically cast a string to an appropriate Python literal type.

Find information relevant to specific objects.

This can be used to find assets mentioning specific VectorBT PRO (vectorbtpro, VBT) objects, such as modules, classes, functions, and instances. For example, searching for "Portfolio" will generate targets such as `vbt.Portfolio`, `Portfolio(...)`, `pf = ...`, etc.

If any of the mentioned targets are found in an asset, it will be returned.

!!! note All references must be valid; if any reference cannot be resolved, will raise an error. Thus, when passing multiple references, use [resolve*refnames](https://vectorbt.pro/pvt*ff8edc14/api/mcp/#vectorbtpro.mcp.resolve*refnames "vectorbtpro.mcp.resolve*refnames") to verify them first.

**```refnames```** :&ensp;`List[str]` :   Reference names of the objects.

**```resolve```** :&ensp;`bool` :   Whether to resolve the reference to an actual object.

**```asset_names```** :&ensp;`Optional[List[str]]` :   Asset names to search. Supported names:

**```aggregate_api```** :&ensp;`bool` :   Whether to aggregate all children of the object into a single context.

**```aggregate_messages```** :&ensp;`bool` :   Whether to aggregate messages belonging to the same thread (question-reply chain).

**```return_metadata```** :&ensp;`str` :   Metadata to return with the results. Supported options:

**```dump_engine```** :&ensp;`Optional[str]` :   Engine used to serialize results to strings.

**```max_tokens```** :&ensp;`Optional[int]` :   Maximum number of tokens to return.

**```n```** :&ensp;`Optional[int]` :   Number of results to return per page.

**```page```** :&ensp;`int` :   Page number to return (1-indexed).

**```progress```** :&ensp;`bool` :   Show progress bars while processing the query.

`str` :   Context string containing the search results.

Get a list of attributes of an object with their types and reference names.

Similar to `dir()`, but with more information and better formatting. Can be used to discover the API of VectorBT PRO (vectorbtpro, VBT). For example, use it to find out what methods and properties are available on a specific class, or to explore the objects defined in a module.

Each line is formatted as `<name> [<type>] (@ <refname>)`, where the `@ <refname>` suffix is shown only when the attribute is not defined directly on the object.

**```refname```** :&ensp;`str` :   Reference name of the object.

**```own_only```** :&ensp;`bool` :   If True, include only attributes that are defined directly on the object (i.e., attributes defined elsewhere, such as inherited attributes, will be excluded).

**```incl_private```** :&ensp;`bool` :   If True, include private attributes (those starting with an underscore).

**```incl_types```** :&ensp;`bool` :   If True, include attribute types in the output (e.g., `classmethod`).

**```incl*refnames```** :&ensp;`bool` :   If True, include attribute reference names in the output (e.g., [Base.chat](https://vectorbt.pro/pvt*ff8edc14/api/utils/base/#vectorbtpro.utils.base.Base.chat "vectorbtpro.utils.base.Base.chat")).

**```dump_engine```** :&ensp;`Optional[str]` :   Engine used to serialize results to strings.

**```max_tokens```** :&ensp;`Optional[int]` :   Maximum number of tokens to return.

**```n```** :&ensp;`Optional[int]` :   Number of results to return per page.

**```page```** :&ensp;`int` :   Page number to return (1-indexed).

`str` :   String containing the list of attributes, each on a new line.

Get the content of a Discord message by its URL.

**```url```** :&ensp;`str` :   URL of the Discord message.

**```return_metadata```** :&ensp;`str` :   Metadata to return with the results. Supported options:

**```dump_engine```** :&ensp;`Optional[str]` :   Engine used to serialize results to strings.

**```max_tokens```** :&ensp;`Optional[int]` :   Maximum number of tokens to return.

`str` :   Content of the Discord message.

Get the content of a Discord message block by its URL.

A block is a group of messages sent by the same user in a short time frame. The URL of a block is the same as the URL of the first message in the block.

**```url```** :&ensp;`str` :   URL of the Discord message block.

**```return_metadata```** :&ensp;`str` :   Metadata to return with the results. Supported options:

**```dump_engine```** :&ensp;`Optional[str]` :   Engine used to serialize results to strings.

**```max_tokens```** :&ensp;`Optional[int]` :   Maximum number of tokens to return.

**```n```** :&ensp;`Optional[int]` :   Number of results to return per page.

**```page```** :&ensp;`int` :   Page number to return (1-indexed).

`str` :   Content of the Discord message block.

Get the content of a Discord message thread by its URL.

A thread is a question-reply chain. The URL of a thread is the same as the URL of the initial message in the thread.

**```url```** :&ensp;`str` :   URL of the Discord message thread.

**```return_metadata```** :&ensp;`str` :   Metadata to return with the results. Supported options:

**```dump_engine```** :&ensp;`Optional[str]` :   Engine used to serialize results to strings.

**```max_tokens```** :&ensp;`Optional[int]` :   Maximum number of tokens to return.

**```n```** :&ensp;`Optional[int]` :   Number of results to return per page.

**```page```** :&ensp;`int` :   Page number to return (1-indexed).

`str` :   Content of the Discord message thread.

Get the content of a documentation page by its URL.

**```url```** :&ensp;`str` :   URL of the documentation page. Supported formats:

**```return_metadata```** :&ensp;`str` :   Metadata to return with the results. Supported options:

**```dump_engine```** :&ensp;`Optional[str]` :   Engine used to serialize results to strings.

**```max_tokens```** :&ensp;`Optional[int]` :   Maximum number of tokens to return.

`str` :   Content of the documentation page.

Get the source code of any object.

This can be used to inspect the implementation of VectorBT PRO (vectorbtpro, VBT) objects, such as modules, classes, functions, and instances. It uses AST parsing to retrieve the source code of any object, including named tuples, class variables, dataclasses, and other objects that may not have a traditional source code representation.

**```refname```** :&ensp;`str` :   Reference name of the object.

**```max_tokens```** :&ensp;`Optional[int]` :   Maximum number of tokens to return.

`str` :   Source code of the object.

Decorator to register a function in [tool*registry](https://vectorbt.pro/pvt*ff8edc14/api/mcp/#vectorbtpro.mcp.tool*registry "vectorbtpro.mcp.tool*registry").

**```arg```** :&ensp;`Union[None, str, Callable]` :   Tool function or its name.

**```name```** :&ensp;`Optional[str]` :   Custom name for the tool (if not using the function name).

`Callable` :   Registered tool function.

Resolve reference names to their fully qualified names.

**```refnames```** :&ensp;`List[str]` :   Reference names to resolve.

**```dump_engine```** :&ensp;`Optional[str]` :   Engine used to serialize results to strings.

**```max_tokens```** :&ensp;`Optional[int]` :   Maximum number of tokens to return.

**```n```** :&ensp;`Optional[int]` :   Number of results to return per page.

**```page```** :&ensp;`int` :   Page number to return (1-indexed).

`str` :   Output string containing the resolution results.

Run a code snippet with all the necessary imports and return the output.

This spins up a Jupyter kernel if it is not already running, and automatically imports `from vectorbtpro import *`, which includes `vbt`, `pd` (Pandas), `np` (NumPy), `njit` (from Numba), and other commonly used modules from the documentation. Running this the second time will reuse the existing kernel and all variables defined earlier.

Use this tool to develop and test code snippets in the VectorBT PRO (vectorbtpro, VBT) environment, similar to a Jupyter notebook. You can backtest a strategy, debug a function, or explore data interactively.

!!! note VBT is centered around easy-to-use APIs and high-performance computing, thus you should put priority on discovering and using VBT APIs. Before running this tool, use other MCP tools to search for relevant information, such as existing code examples, API references, and documentation. This will help you understand how to use VBT effectively and avoid reinventing the wheel. If a custom implementation is needed, consider extending existing VBT functionality or using high-performance libraries such as Numba.

!!! warning Ensure that the code is safe, as this tool can execute arbitrary code in the current environment. Do not run code that has side effects, such as installing new dependencies, modifying global state, or performing I/O operations, unless explicitly granted permission!

**```code```** :&ensp;`str` :   Code snippet to run.

**```restart```** :&ensp;`bool` :   Whether to restart the kernel before running the code.

**```exec_timeout```** :&ensp;`Optional[float]` :   Timeout for the code execution in seconds.

**```max_tokens```** :&ensp;`Optional[int]` :   Maximum number of tokens to return.

`str` :   Output of the executed code.

Search for information relevant to the query.

!!! note This tool is designed to search for general information about VectorBT PRO (vectorbtpro, VBT). For specific information about a specific object (such as `vbt.Portfolio`), use tools that take a reference name. They operate on the actual objects.

**```query```** :&ensp;`str` :   Search query.

**```asset_names```** :&ensp;`Optional[List[str]]` :   Asset names to search. Supported names:

**```search_method```** :&ensp;`str` :   Strategy for document search. Supported strategies:

**```with_fallback```** :&ensp;`bool` :   Whether to fallback to class search if some embeddings are not available; otherwise, missing embeddings will be generated, which may take longer.

**```rerank```** :&ensp;`bool` :   Whether to rerank top results using a cross-encoder for better relevance.

**```rerank_limit```** :&ensp;`int` :   Number of top results to rerank.

**```return_chunks```** :&ensp;`bool` :   Whether to return the chunks of the results; otherwise, returns the full results.

**```return_metadata```** :&ensp;`str` :   Metadata to return with the results. Supported options:

**```dump_engine```** :&ensp;`Optional[str]` :   Engine used to serialize results to strings.

**```max_tokens```** :&ensp;`Optional[int]` :   Maximum number of tokens to return.

**```n```** :&ensp;`Optional[int]` :   Number of results to return per page.

**```page```** :&ensp;`int` :   Page number to return (1-indexed).

**```progress```** :&ensp;`bool` :   Show progress bars while processing the query.

`str` :   Context string containing the search results.

**Examples:**

Example 1 (python):
```python
auto_cast(
    value
)
```

Example 2 (python):
```python
find(
    refnames,
    resolve=True,
    asset_names=None,
    aggregate_api=False,
    aggregate_messages=False,
    return_metadata='minimal',
    dump_engine='json',
    max_tokens=4000,
    n=None,
    page=1,
    progress=False
)
```

Example 3 (text):
```text
A reference name may be a fully qualified dotted path ("vectorbtpro.data.base.Data"),
a library re-export ("vectorbtpro.Data"), a common alias ("vbt.Data"),
or a simple name ("Data") that uniquely identifies an object.

Returns a code example if any of the references are found in the code example.
```

Example 4 (text):
```text
Set to False to find any string, not just VBT objects, such as "SQLAlchemy".
In this case, `refname` becomes a simple string to match against.
Defaults to True.
```

---

## knowledge

**URL:** https://vectorbt.pro/pvt_ff8edc14/api/knowledge.md

**Contents:**
- Sub-modules

Package providing utility functions and classes for constructing and managing knowledge assets.

Run for the examples:

!!! info For default settings, see [knowledge](https://vectorbt.pro/pvt*ff8edc14/api/*settings/#vectorbtpro.*settings.knowledge "vectorbtpro.*settings.knowledge").

**Examples:**

Example 1 (pycon):
```pycon
>>> dataset = [
...     {"s": "ABC", "b": True, "d2": {"c": "red", "l": [1, 2]}},
...     {"s": "BCD", "b": True, "d2": {"c": "blue", "l": [3, 4]}},
...     {"s": "CDE", "b": False, "d2": {"c": "green", "l": [5, 6]}},
...     {"s": "DEF", "b": False, "d2": {"c": "yellow", "l": [7, 8]}},
...     {"s": "EFG", "b": False, "d2": {"c": "black", "l": [9, 10]}, "xyz": 123}
... ]
>>> asset = vbt.KnowledgeAsset(dataset)
```

---

## base_assets

**URL:** https://vectorbt.pro/pvt_ff8edc14/api/knowledge/base_assets.md

**Contents:**
- asset_cache <span class="dobjtype">dict</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/base_assets.py#L35-L36" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.base_assets.asset_cache data-toc-label="asset\_cache" }
- AssetCacheManager <span class="dobjtype">class</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/base_assets.py#L39-L266" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.base_assets.AssetCacheManager data-toc-label="AssetCacheManager" }
  - cache_dir <span class="dobjtype">class property</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/base_assets.py#L150-L157" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.base_assets.AssetCacheManager.cache_dir data-toc-label="cache\_dir" }
  - cleanup_cache_dir <span class="dobjtype">method</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/base_assets.py#L231-L245" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.base_assets.AssetCacheManager.cleanup_cache_dir data-toc-label="cleanup\_cache\_dir" }
  - generate_cache_key <span class="dobjtype">class method</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/base_assets.py#L190-L209" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.base_assets.AssetCacheManager.generate_cache_key data-toc-label="generate\_cache\_key" }
  - load_asset <span class="dobjtype">method</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/base_assets.py#L211-L229" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.base_assets.AssetCacheManager.load_asset data-toc-label="load\_asset" }
  - load_cache_kwargs <span class="dobjtype">class property</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/base_assets.py#L179-L188" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.base_assets.AssetCacheManager.load_cache_kwargs data-toc-label="load\_cache\_kwargs" }
  - max_cache_count <span class="dobjtype">class property</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/base_assets.py#L159-L166" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.base_assets.AssetCacheManager.max_cache_count data-toc-label="max\_cache\_count" }
  - persist_cache <span class="dobjtype">class property</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/base_assets.py#L141-L148" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.base_assets.AssetCacheManager.persist_cache data-toc-label="persist\_cache" }
  - save_asset <span class="dobjtype">method</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/base_assets.py#L247-L266" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.base_assets.AssetCacheManager.save_asset data-toc-label="save\_asset" }

Module providing base classes for managing knowledge assets.

See [vectorbtpro.knowledge](https://vectorbt.pro/pvt_ff8edc14/api/knowledge/ "vectorbtpro.knowledge") for the toy dataset.

Cache for storing knowledge assets, keyed by a unique identifier.

Class for managing cached knowledge assets.

!!! info For default settings, see [knowledge](https://vectorbt.pro/pvt*ff8edc14/api/*settings/#vectorbtpro.*settings.knowledge "vectorbtpro.*settings.knowledge").

**```persist_cache```** :&ensp;`Optional[bool]` :   Whether to persist the cache to disk.

**```cache_dir```** :&ensp;`Optional[PathLike]` :   Directory for saving knowledge assets.

**```cache*mkdir*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for cache directory creation.

**```clear_cache```** :&ensp;`Optional[bool]` :   Remove the cache directory before operation if True.

**```max*cache*count```** :&ensp;`Optional[int]` :   Maximum number of assets to retain, evicting older ones.

**```save*cache*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for saving assets to disk.

**```load*cache*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for loading assets from disk.

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```**kwargs```** :   Keyword arguments for [Configured](https://vectorbt.pro/pvt_ff8edc14/api/utils/config/#vectorbtpro.utils.config.Configured "vectorbtpro.utils.config.Configured").

**Inherited members**

Directory path for storing cached assets.

`Path` :   Path of the cache directory.

Remove older cached assets, retaining only the most recent ones based on modification time.

Generate a cache key based on the current VectorBT version, asset settings, and provided parameters.

**```**kwargs```** :   Additional parameters contributing to the cache key.

`str` :   Unique cache key as a hexadecimal string.

Load a knowledge asset from the cache.

**```cache_key```** :&ensp;`str` :   Unique identifier for the cached asset.

`Optional[MaybeKnowledgeAsset]` :   Loaded knowledge asset if found, otherwise None.

Keyword arguments for loading assets from disk.

See [load](https://vectorbt.pro/pvt_ff8edc14/api/utils/pickling/#vectorbtpro.utils.pickling.load "vectorbtpro.utils.pickling.load").

`Kwargs` :   Keyword arguments used for loading assets from disk.

Maximum number of assets to retain, evicting older ones.

`Optional[int]` :   Maximum number of assets to retain in the cache.

Whether to persist the cache to disk.

`bool` :   True if cache persistence is enabled, otherwise False.

Save a knowledge asset to the cache.

Caches the asset in memory and, if persistence is enabled, writes it to disk.

**```asset```** :&ensp;`MaybeKnowledgeAsset` :   Knowledge asset to cache.

**```cache_key```** :&ensp;`str` :   Unique identifier for the cached asset.

`Optional[Path]` :   File path where the asset was saved if persistence is enabled, otherwise None.

Keyword arguments for saving assets to disk.

See [save](https://vectorbt.pro/pvt_ff8edc14/api/utils/pickling/#vectorbtpro.utils.pickling.save "vectorbtpro.utils.pickling.save").

`Kwargs` :   Keyword arguments used for saving assets to disk.

Class for working with a knowledge asset.

This class behaves like a mutable sequence.

!!! info For default settings, see [knowledge](https://vectorbt.pro/pvt*ff8edc14/api/*settings/#vectorbtpro.*settings.knowledge "vectorbtpro.*settings.knowledge").

**```data```** :&ensp;`Optional[List[Any]]` :   List of data items for the asset.

**```single_item```** :&ensp;`bool` :   Indicates whether the asset holds a single data item.

**```**kwargs```** :   Keyword arguments for [Configured](https://vectorbt.pro/pvt_ff8edc14/api/utils/config/#vectorbtpro.utils.config.Configured "vectorbtpro.utils.config.Configured").

**Inherited members**

Append a new data item to the asset.

**```d```** :&ensp;`Any` :   Data item to append.

**```inplace```** :&ensp;`bool` :   If True, modify the asset in place.

`Optional[KnowledgeAsset]` :   New asset with the appended item, or None if modified in place.

Apply a function or pipeline to each data item in the asset.

The `func` parameter accepts various types:

Execution is handled by [execute](https://vectorbt.pro/pvt_ff8edc14/api/utils/execution/#vectorbtpro.utils.execution.execute "vectorbtpro.utils.execution.execute").

**```func```** :&ensp;`MaybeList[Union[AssetFuncLike, AssetPipeline]]` :   Function, pipeline, or expression to apply.

**```*args```** :   Positional arguments for the asset pipeline or function.

**```execute_kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for the execution handler.

**```wrap```** :&ensp;`Optional[bool]` :   If True, return the result wrapped as an asset.

**```single_item```** :&ensp;`Optional[bool]` :   Determines if a single item should not be wrapped in a list.

**```return_iterator```** :&ensp;`bool` :   If True, return an iterator instead of executing tasks.

**```**kwargs```** :   Keyword arguments for the asset pipeline or function.

`MaybeKnowledgeAsset` :   New asset with processed data if `wrap` is True; otherwise, raw output.

Collect values for each key across all data items.

**```sort_keys```** :&ensp;`Optional[bool]` :   Whether to sort the keys.

**```**kwargs```** :   Keyword arguments for [KnowledgeAsset.reduce](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.reduce "vectorbtpro.knowledge.base*assets.KnowledgeAsset.reduce").

`MaybeKnowledgeAsset` :   New asset containing collected values for each key.

Combine multiple [KnowledgeAsset](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset "vectorbtpro.knowledge.base*assets.KnowledgeAsset") instances into one.

**```*objs```** :&ensp;`MaybeSequence[KnowledgeAsset]` :   (Additional) [KnowledgeAsset](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset "vectorbtpro.knowledge.base*assets.KnowledgeAsset") instances to combine.

**```**kwargs```** :   Keyword arguments for [KnowledgeAsset.merge*lists](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.merge*lists "vectorbtpro.knowledge.base*assets.KnowledgeAsset.merge*lists") or [KnowledgeAsset.merge*dicts](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.merge*dicts "vectorbtpro.knowledge.base*assets.KnowledgeAsset.merge*dicts") or [KnowledgeAsset](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset "vectorbtpro.knowledge.base*assets.KnowledgeAsset").

[KnowledgeAsset](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset "vectorbtpro.knowledge.base*assets.KnowledgeAsset") :   New asset containing merged data.

List of data items in the asset.

`List[Any]` :   Data items contained in the asset.

Delete one or more data items from the asset.

**```index```** :&ensp;`Union[int, slice, Iterable[Union[bool, int]]]` :   Index specifying the item(s) to remove.

**```inplace```** :&ensp;`bool` :   If True, delete the items in place.

`Optional[KnowledgeAsset]` :   New asset with the selected items removed, or None if modified in place.

Collect and describe values for each key in data items.

Retrieve values using [KnowledgeAsset.collect](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.collect "vectorbtpro.knowledge.base*assets.KnowledgeAsset.collect") and compute descriptive statistics for each key using `pd.Series.describe`. For keys containing collection values, additional length statistics are computed. If `wrap` is True, the description is wrapped as a single-item asset via [Configured.replace](https://vectorbt.pro/pvt*ff8edc14/api/utils/config/#vectorbtpro.utils.config.Configured.replace "vectorbtpro.knowledge.base*assets.KnowledgeAsset.replace").

**```ignore_empty```** :&ensp;`Optional[bool]` :   Whether to ignore empty values.

**```describe_kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for `pd.Series.describe`.

**```wrap```** :&ensp;`bool` :   If True, wraps the description in a single-item asset.

**```**kwargs```** :   Keyword arguments for [KnowledgeAsset.collect](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.collect "vectorbtpro.knowledge.base*assets.KnowledgeAsset.collect").

`Union[KnowledgeAssetT, dict]` :   Data asset or dictionary containing descriptive statistics.

Describe a list of lengths.

Compute descriptive statistics for the input lengths, excluding count and standard deviation.

**```lengths```** :&ensp;`list` :   List of numerical lengths.

**```**describe_kwargs```** :   Keyword arguments for `pd.Series.describe`.

`dict` :   Dictionary of descriptive statistics with keys prefixed by "len_".

Dump asset data items using a specified dump engine.

This method applies [KnowledgeAsset.apply](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply "vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply") with [DumpAssetFunc](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*asset*funcs/#vectorbtpro.knowledge.base*asset*funcs.DumpAssetFunc "vectorbtpro.knowledge.base*asset_funcs.DumpAssetFunc") to format asset data.

Supported dump engines:

The `source` argument can be a string, callable, or custom template to preprocess the data. In the template, "i" represents the index, "d" represents the data item, and its fields are accessible by name.

**```source```** :&ensp;`Optional[CustomTemplateLike]` :   Template or function to preprocess the source data.

**```dump_engine```** :&ensp;`Optional[str]` :   Name of the dump engine.

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```**kwargs```** :   Keyword arguments for [KnowledgeAsset.apply](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply "vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply").

`MaybeKnowledgeAsset` :   New asset with dumped data.

Dump asset data list into a single asset representation.

This method uses [AssetFunc.prepare*and*call](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*asset*funcs/#vectorbtpro.knowledge.base*asset*funcs.AssetFunc.prepare*and*call "vectorbtpro.knowledge.base*asset*funcs.DumpAssetFunc.prepare*and_call") on the asset's data with the provided parameters.

**```source```** :&ensp;`Optional[CustomTemplateLike]` :   Template or function to preprocess the source data.

**```dump_engine```** :&ensp;`Optional[str]` :   Name of the dump engine.

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```**kwargs```** :   Keyword arguments for [AssetFunc.prepare*and*call](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*asset*funcs/#vectorbtpro.knowledge.base*asset*funcs.AssetFunc.prepare*and*call "vectorbtpro.knowledge.base*asset*funcs.DumpAssetFunc.prepare*and_call").

`str` :   Dumped asset data as a string.

Embed documents in the asset.

Converts the asset's data to [TextDocument](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/doc*storing/#vectorbtpro.knowledge.doc*storing.TextDocument "vectorbtpro.knowledge.doc*storing.TextDocument") format using [KnowledgeAsset.to*documents](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.to*documents "vectorbtpro.knowledge.base*assets.KnowledgeAsset.to*documents") if needed, then embeds them with [embed*documents](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/doc*ranking/#vectorbtpro.knowledge.doc*ranking.embed*documents "vectorbtpro.knowledge.doc*ranking.embed*documents") using provided keyword arguments. Optionally unwraps the embedded documents if `wrap_documents` is False.

**```to*documents*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for [KnowledgeAsset.to*documents](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.to*documents "vectorbtpro.knowledge.base*assets.KnowledgeAsset.to_documents").

**```wrap_documents```** :&ensp;`Optional[bool]` :   Flag indicating whether to preserve the document embedding structure.

**```**kwargs```** :   Keyword arguments for [embed*documents](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/doc*ranking/#vectorbtpro.knowledge.doc*ranking.embed*documents "vectorbtpro.knowledge.doc*ranking.embed_documents").

`Optional[MaybeKnowledgeAsset]` :   New asset with embedded documents, or None if embedding fails.

**Overridden methods**

**Overridden by methods**

Extend the asset with additional data items.

**```data```** :&ensp;`Iterable[Any]` :   Iterable of data items to append.

**```inplace```** :&ensp;`bool` :   If True, modify the asset in place.

`Optional[KnowledgeAsset]` :   New asset with extended data, or None if modified in place.

Return a new [KnowledgeAsset](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset "vectorbtpro.knowledge.base*assets.KnowledgeAsset") instance by calling [KnowledgeAsset.query](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.query "vectorbtpro.knowledge.base*assets.KnowledgeAsset.query").

**```*args```** :   Positional arguments for [KnowledgeAsset.query](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.query "vectorbtpro.knowledge.base*assets.KnowledgeAsset.query").

**```**kwargs```** :   Keyword arguments for [KnowledgeAsset.query](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.query "vectorbtpro.knowledge.base*assets.KnowledgeAsset.query").

[KnowledgeAsset](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset "vectorbtpro.knowledge.base*assets.KnowledgeAsset") :   New asset containing the filtered data.

Return a new [KnowledgeAsset](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset "vectorbtpro.knowledge.base*assets.KnowledgeAsset") instance with found occurrences based on the target.

Uses [KnowledgeAsset.apply](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply "vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply") on [FindAssetFunc](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*asset*funcs/#vectorbtpro.knowledge.base*asset*funcs.FindAssetFunc "vectorbtpro.knowledge.base*asset_funcs.FindAssetFunc").

Searches each data item with [contains*in*obj](https://vectorbt.pro/pvt*ff8edc14/api/utils/search*/#vectorbtpro.utils.search*.contains*in*obj "vectorbtpro.utils.search*.contains*in*obj") when `return*type` is "item", "field", or "bool", and uses [find*in*obj](https://vectorbt.pro/pvt*ff8edc14/api/utils/search*/#vectorbtpro.utils.search*.find*in*obj "vectorbtpro.utils.search*.find*in*obj") and [find](https://vectorbt.pro/pvt*ff8edc14/api/utils/search*/#vectorbtpro.utils.search*.find "vectorbtpro.utils.search_.find") for all other return types.

Target can be one or multiple data items. If there are multiple targets and `find_all` is True, the match function will return True only if all targets have been found.

Use argument `source` instead of `path` or in addition to `path` to also preprocess the source. It can be a string or function (will become a template), or any custom template. In this template, the index of the data item is represented by "i", the data item itself is represented by "d", the data item under the path is represented by "x" while its fields are represented by their names.

**```target```** :&ensp;`MaybeList[Any]` :   Target value(s) or callable(s) to determine if a match occurs.

**```path```** :&ensp;`Optional[MaybeList[PathLikeKey]]` :   Path(s) within the data item to search (e.g. "x.y[0].z").

**```per_path```** :&ensp;`Optional[bool]` :   If True, consider targets provided per path.

**```find_all```** :&ensp;`Optional[bool]` :   Require all targets to be found when multiple targets are provided.

**```keep_path```** :&ensp;`Optional[bool]` :   If True, returns results structured as nested dictionaries mirroring the specified path.

**```skip_missing```** :&ensp;`Optional[bool]` :   If True, skips data items where the specified path is missing.

**```source```** :&ensp;`Optional[CustomTemplateLike]` :   Template or function to preprocess the source data.

**```in_dumps```** :&ensp;`Optional[bool]` :   If True, converts the entire data item to string for searching.

**```dump_kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for dumping structured data.

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```return_type```** :&ensp;`Optional[str]` :   Indicates the return type: "item", "field", or "bool".

**```return_path```** :&ensp;`Optional[bool]` :   Specifies whether to include the path in the returned result.

**```merge_matches```** :&ensp;`Optional[bool]` :   If False, keeps empty lists when searching for matches.

**```merge_fields```** :&ensp;`Optional[bool]` :   If False, keeps empty lists when searching for fields.

**```unique_matches```** :&ensp;`Optional[bool]` :   If False, allows duplicate matches.

**```unique_fields```** :&ensp;`Optional[bool]` :   If False, allows duplicate fields.

**```**kwargs```** :   Keyword arguments for [KnowledgeAsset.apply](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply "vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply").

`MaybeKnowledgeAsset` :   New asset with the found data items.

Return code segments from the asset data that match the specified target pattern and language criteria.

This method constructs a regular expression based on the provided target, language, and block settings, and then uses [KnowledgeAsset.find](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.find "vectorbtpro.knowledge.base*assets.KnowledgeAsset.find") to search the asset data.

!!! info For default settings, see `code` in [knowledge](https://vectorbt.pro/pvt*ff8edc14/api/*settings/#vectorbtpro.*settings.knowledge "vectorbtpro.*settings.knowledge").

**```target```** :&ensp;`Optional[Iterable[Any]]` :   Target pattern(s) to locate in the asset.

**```language```** :&ensp;`Union[None, bool, Iterable[str]]` :   Language specification(s) to filter code blocks.

**```in_blocks```** :&ensp;`Optional[bool]` :   If True, search within code blocks rather than inline code.

**```escape_target```** :&ensp;`bool` :   If True, escape regex special characters in the target.

**```escape_language```** :&ensp;`bool` :   If True, escape regex special characters in the language.

**```return_type```** :&ensp;`Optional[str]` :   Type of result to return.

**```flags```** :&ensp;`int` :   Additional flags for compiling the regular expression.

**```**kwargs```** :   Keyword arguments for [KnowledgeAsset.find](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.find "vectorbtpro.knowledge.base*assets.KnowledgeAsset.find").

`MaybeKnowledgeAsset` :   New asset with segments that match the search criteria.

Remove occurrences of a target from the asset data and return a new [KnowledgeAsset](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset "vectorbtpro.knowledge.base*assets.KnowledgeAsset") instance.

This method applies a removal operation on nested data items using [KnowledgeAsset.apply](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply "vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply") with [FindRemoveAssetFunc](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*asset*funcs/#vectorbtpro.knowledge.base*asset*funcs.FindRemoveAssetFunc "vectorbtpro.knowledge.base*asset_funcs.FindRemoveAssetFunc").

Similar to [KnowledgeAsset.find*replace](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.find*replace "vectorbtpro.knowledge.base*assets.KnowledgeAsset.find_replace").

**```target```** :&ensp;`Union[dict, MaybeList[Any]]` :   Value or mapping used to identify occurrences for removal.

**```path```** :&ensp;`Optional[MaybeList[PathLikeKey]]` :   Path(s) within the data item to search (e.g. "x.y[0].z").

**```per_path```** :&ensp;`Optional[bool]` :   If True, consider targets provided per path.

**```find_all```** :&ensp;`Optional[bool]` :   Require all targets to be found when multiple targets are provided.

**```keep_path```** :&ensp;`Optional[bool]` :   If True, returns results structured as nested dictionaries mirroring the specified path.

**```skip_missing```** :&ensp;`Optional[bool]` :   If True, skips data items where the specified path is missing.

**```make_copy```** :&ensp;`Optional[bool]` :   If True, operates on a copy rather than modifying the original data.

**```changed_only```** :&ensp;`Optional[bool]` :   If True, returns only data items that were modified.

**```**kwargs```** :   Keyword arguments for [KnowledgeAsset.apply](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply "vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply").

`MaybeKnowledgeAsset` :   New asset with the specified occurrences removed.

Remove empty objects from the asset data.

This method uses a predefined emptiness check via [FindRemoveAssetFunc.is*empty*func](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*asset*funcs/#vectorbtpro.knowledge.base*asset*funcs.FindRemoveAssetFunc.is*empty*func "vectorbtpro.knowledge.base*asset*funcs.FindRemoveAssetFunc.is*empty_func") to remove empty objects.

**```**kwargs```** :   Keyword arguments for [KnowledgeAsset.find*remove](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.find*remove "vectorbtpro.knowledge.base*assets.KnowledgeAsset.find_remove").

`MaybeKnowledgeAsset` :   New asset with empty objects removed.

Return a new [KnowledgeAsset](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset "vectorbtpro.knowledge.base*assets.KnowledgeAsset") with occurrences replaced according to the specified criteria.

This method applies a find-and-replace operation on the asset data using [FindReplaceAssetFunc](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*asset*funcs/#vectorbtpro.knowledge.base*asset*funcs.FindReplaceAssetFunc "vectorbtpro.knowledge.base*asset*funcs.FindReplaceAssetFunc") via [KnowledgeAsset.apply](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply "vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply"). It uses [find*in*obj](https://vectorbt.pro/pvt*ff8edc14/api/utils/search*/#vectorbtpro.utils.search*.find*in*obj "vectorbtpro.utils.search*.find*in*obj") to locate occurrences and [replace*in*obj](https://vectorbt.pro/pvt*ff8edc14/api/utils/search*/#vectorbtpro.utils.search*.replace*in*obj "vectorbtpro.utils.search*.replace*in_obj") to perform the replacements.

The target can be provided as a single or multiple data items (list or dictionary). When multiple targets are used with `find*all` set to True, all targets must be found to register a match. The `path` parameter specifies the portion of the data item to search (e.g., "x.y[0].z" to access nested elements). If `keep*path` is True, the results will be returned as a nested dictionary keyed by the specified paths. Providing multiple paths will automatically enable `keep*path` and merge the results. If `skip*missing` is True, any data item missing the specified path will be skipped. When `per_path` is True, targets and replacements are applied per individual path.

Setting `make*copy` avoids modifying the original data. Enabling `changed*only` will return only data items that were modified.

**```target```** :&ensp;`Union[dict, List[Any]]` :   Data item(s) or pattern(s) to search for.

**```replacement```** :&ensp;`Optional[List[Any]]` :   Replacement value(s) for matched occurrences.

**```path```** :&ensp;`Optional[List[PathLikeKey]]` :   Specific path(s) within each data item to target.

**```per_path```** :&ensp;`Optional[bool]` :   If True, consider targets and replacements provided per path.

**```find_all```** :&ensp;`Optional[bool]` :   Require all targets to be found when multiple targets are provided.

**```keep_path```** :&ensp;`Optional[bool]` :   If True, returns results structured as nested dictionaries mirroring the specified path.

**```skip_missing```** :&ensp;`Optional[bool]` :   If True, skips data items where the specified path is missing.

**```make_copy```** :&ensp;`Optional[bool]` :   If True, operates on a copy rather than modifying the original data.

**```changed_only```** :&ensp;`Optional[bool]` :   If True, returns only data items that were modified.

**```**kwargs```** :   Keyword arguments for [KnowledgeAsset.apply](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply "vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply").

`MaybeKnowledgeAsset` :   New asset with the specified replacements applied.

Flatten nested elements in the asset data into a flat structure.

This method applies a flattening operation using [KnowledgeAsset.apply](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply "vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply") with [FlattenAssetFunc](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*asset*funcs/#vectorbtpro.knowledge.base*asset*funcs.FlattenAssetFunc "vectorbtpro.knowledge.base*asset*funcs.FlattenAssetFunc"). Specify the nested portion to flatten using the `path` argument. Multiple paths can be provided. If `skip*missing` is True and a specified path is missing, the data item will be skipped.

**```path```** :&ensp;`Optional[MaybeList[PathLikeKey]]` :   Path(s) within the data item to flatten (e.g. "x.y[0].z").

**```skip_missing```** :&ensp;`Optional[bool]` :   If True, skips data items where the specified path is missing.

**```make_copy```** :&ensp;`Optional[bool]` :   If True, operates on a copy rather than modifying the original data.

**```changed_only```** :&ensp;`Optional[bool]` :   If True, returns only data items that were modified.

**```**kwargs```** :   Keyword arguments for [KnowledgeAsset.apply](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply "vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply").

`MaybeKnowledgeAsset` :   New asset with flattened data.

Build a [KnowledgeAsset](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset "vectorbtpro.knowledge.base*assets.KnowledgeAsset") instance from JSON bytes.

[decompress](https://vectorbt.pro/pvt_ff8edc14/api/utils/pickling/#vectorbtpro.utils.pickling.decompress "vectorbtpro.utils.pickling.decompress")

**```bytes_```** :&ensp;`bytes` :   Byte stream containing the JSON object.

**```compression```** :&ensp;`CompressionLike` :   Compression algorithm.

**```decompress_kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for decompression.

**```**kwargs```** :   Keyword arguments for [KnowledgeAsset](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset "vectorbtpro.knowledge.base*assets.KnowledgeAsset").

[KnowledgeAsset](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset "vectorbtpro.knowledge.base*assets.KnowledgeAsset") :   New asset containing data from the JSON bytes.

Build a [KnowledgeAsset](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset "vectorbtpro.knowledge.base*assets.KnowledgeAsset") instance from a JSON file.

[load*bytes](https://vectorbt.pro/pvt*ff8edc14/api/utils/pickling/#vectorbtpro.utils.pickling.load*bytes "vectorbtpro.utils.pickling.load*bytes")

**```path```** :&ensp;`PathLike` :   Path to the JSON file.

**```compression```** :&ensp;`CompressionLike` :   Compression algorithm.

**```decompress_kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for decompression.

**```**kwargs```** :   Keyword arguments for [KnowledgeAsset](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset "vectorbtpro.knowledge.base*assets.KnowledgeAsset").

[KnowledgeAsset](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset "vectorbtpro.knowledge.base*assets.KnowledgeAsset") :   New asset populated with data from the JSON file.

Return specific data items or subsets of them.

This method retrieves complete data items or extracts portions specified by a nested path. It applies [GetAssetFunc](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*asset*funcs/#vectorbtpro.knowledge.base*asset*funcs.GetAssetFunc "vectorbtpro.knowledge.base*asset*funcs.GetAssetFunc") via [KnowledgeAsset.apply](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply "vectorbtpro.knowledge.base_assets.KnowledgeAsset.apply").

**```path```** :&ensp;`Optional[MaybeList[PathLikeKey]]` :   Path(s) within the data item to get (e.g. "x.y[0].z").

**```keep_path```** :&ensp;`Optional[bool]` :   If True, returns results structured as nested dictionaries mirroring the specified path.

**```skip_missing```** :&ensp;`Optional[bool]` :   If True, skips data items where the specified path is missing.

**```source```** :&ensp;`Optional[CustomTemplateLike]` :   Template, function, or string for preprocessing; in the template, "i" denotes the index, "d" the full data item, and "x" the extracted part.

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```single_item```** :&ensp;`Optional[bool]` :   Determines if a single item should not be wrapped in a list.

**```**kwargs```** :   Keyword arguments for [KnowledgeAsset.apply](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply "vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply").

`MaybeKnowledgeAsset` :   New asset containing the selected data.

Get one or more data items from the asset.

**```index```** :&ensp;`Union[int, slice, Iterable[Union[bool, int]]]` :   Index specifying the item(s) to retrieve.

`Union[Any, KnowledgeAsset]` :   Selected data element if an integer is provided, or a new asset containing the extracted items otherwise.

Return keys and grouping indices from a list of items.

When `uniform_groups` is True, consecutive identical items are grouped together. Otherwise, groups are formed based on the first occurrence of each unique item.

**```by```** :&ensp;`List[Any]` :   List of items to group.

**```uniform_groups```** :&ensp;`bool` :   If True, group consecutive identical items; otherwise, group all identical items.

`Tuple[List[Any], List[List[int]]]` :   Tuple containing a list of keys and a corresponding list of index groups.

Group data items by keys and reduce them.

Group data items based on keys obtained using the provided `by` parameter via [KnowledgeAsset.get](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.get "vectorbtpro.knowledge.base*assets.KnowledgeAsset.get"). If `uniform*groups` is True, only contiguous identical key values are grouped. For each group, apply [KnowledgeAsset.reduce](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.reduce "vectorbtpro.knowledge.base_assets.KnowledgeAsset.reduce") with the supplied function and additional arguments.

**```func```** :&ensp;`CustomTemplateLike` :   Reduction function, expression, or template.

**```*args```** :   Positional arguments for [KnowledgeAsset.reduce](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.reduce "vectorbtpro.knowledge.base*assets.KnowledgeAsset.reduce").

**```by```** :&ensp;`Optional[PathLikeKey]` :   Key or path used to group data items.

**```uniform_groups```** :&ensp;`Optional[bool]` :   Whether to group only contiguous identical key values.

**```get*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for retrieving keys via [KnowledgeAsset.get](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.get "vectorbtpro.knowledge.base_assets.KnowledgeAsset.get").

**```execute_kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for the execution handler.

**```return*group*keys```** :&ensp;`bool` :   If True, returns a dictionary mapping group keys to reduction results.

**```**kwargs```** :   Keyword arguments for [KnowledgeAsset.reduce](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.reduce "vectorbtpro.knowledge.base*assets.KnowledgeAsset.reduce").

`MaybeKnowledgeAsset` :   New asset with the reduced data items.

S.insert(index, value) -- insert value before index

Join string data items into a single string.

If no separator is provided, the method infers one based on the trailing characters of each string:

If the resulting string starts with '{' and ends with '}', it is converted to use square brackets.

**```separator```** :&ensp;`Optional[str]` :   Separator to insert between data items.

`str` :   Resulting concatenated string.

Merge multiple [KnowledgeAsset](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset "vectorbtpro.knowledge.base*assets.KnowledgeAsset") instances or the data items of a single instance.

When called as a class method or instance method with additional objects, combine the provided [KnowledgeAsset](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset "vectorbtpro.knowledge.base*assets.KnowledgeAsset") instances. When called as an instance method without additional objects, merge the data items within the instance.

**```*objs```** :&ensp;`MaybeSequence[KnowledgeAsset]` :   (Additional) [KnowledgeAsset](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset "vectorbtpro.knowledge.base*assets.KnowledgeAsset") instances to merge.

**```flatten_kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for flattening data items.

**```**kwargs```** :   Keyword arguments for [KnowledgeAsset.merge*lists](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.merge*lists "vectorbtpro.knowledge.base*assets.KnowledgeAsset.merge*lists") or [KnowledgeAsset.merge*dicts](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.merge*dicts "vectorbtpro.knowledge.base*assets.KnowledgeAsset.merge*dicts") or [KnowledgeAsset](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset "vectorbtpro.knowledge.base*assets.KnowledgeAsset").

[KnowledgeAsset](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset "vectorbtpro.knowledge.base*assets.KnowledgeAsset") :   New asset containing merged data.

Merge dictionary data items into a single dictionary.

**```**kwargs```** :   Keyword arguments for [merge*dicts](https://vectorbt.pro/pvt*ff8edc14/api/utils/config/#vectorbtpro.utils.config.merge*dicts "vectorbtpro.utils.config.merge*dicts").

`MaybeKnowledgeAsset` :   New asset with merged dictionary data.

Merge list data items into a single list.

**```**kwargs```** :   Keyword arguments for [KnowledgeAsset.reduce](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.reduce "vectorbtpro.knowledge.base*assets.KnowledgeAsset.reduce").

`MaybeKnowledgeAsset` :   New asset with merged list data.

Update the asset's data in place and synchronize its configuration.

Move data items or parts of them within the asset.

Uses [KnowledgeAsset.apply](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply "vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply") with [MoveAssetFunc](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*asset*funcs/#vectorbtpro.knowledge.base*asset*funcs.MoveAssetFunc "vectorbtpro.knowledge.base*asset*funcs.MoveAssetFunc") to reposition elements within data items. Specify the element to move using `path`. When `new*path` is provided, it designates the new token for the element; otherwise, `path` must be given as a dictionary mapping original paths to new tokens.

**```path```** :&ensp;`Union[PathMoveDict, MaybeList[PathLikeKey]]` :   Mapping or path(s) within the data item to move (e.g. "x.y[0].z").

**```new_path```** :&ensp;`Optional[MaybeList[PathLikeKey]]` :   Path(s) for the moved element(s) when `path` is not a dictionary.

**```skip_missing```** :&ensp;`Optional[bool]` :   If True, skips data items where the specified path is missing.

**```make_copy```** :&ensp;`Optional[bool]` :   If True, operates on a copy rather than modifying the original data.

**```changed_only```** :&ensp;`Optional[bool]` :   If True, returns only data items that were modified.

**```**kwargs```** :   Keyword arguments for [KnowledgeAsset.apply](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply "vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply").

`MaybeKnowledgeAsset` :   New asset with the modified data.

Print the asset as a context string.

Calls [KnowledgeAsset.to*context](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.to*context "vectorbtpro.knowledge.base*assets.KnowledgeAsset.to_context") with provided arguments to generate a context string, which is then printed.

**```*args```** :   Positional arguments for [KnowledgeAsset.to*context](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.to*context "vectorbtpro.knowledge.base*assets.KnowledgeAsset.to_context").

**```**kwargs```** :   Keyword arguments for [KnowledgeAsset.to*context](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.to*context "vectorbtpro.knowledge.base*assets.KnowledgeAsset.to_context").

Print a random sample of data items.

**```k```** :&ensp;`Optional[int]` :   Number of items to sample.

**```seed```** :&ensp;`Optional[int]` :   Random seed for deterministic output.

**```**kwargs```** :   Keyword arguments for [KnowledgeAsset.print](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.print "vectorbtpro.knowledge.base*assets.KnowledgeAsset.print").

Print the asset schema as a directory tree.

Keyword arguments are forwarded to [KnowledgeAsset.describe](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.describe "vectorbtpro.knowledge.base*assets.KnowledgeAsset.describe") and [dir*tree*from*paths](https://vectorbt.pro/pvt*ff8edc14/api/utils/path*/#vectorbtpro.utils.path*.dir*tree*from*paths "vectorbtpro.utils.path*.dir*tree*from_paths") to build the schema structure.

Query data items using a specified engine and return matching results.

Evaluates an expression or template over data items using one of the following engines:

Templates can also utilize functions from [search*config](https://vectorbt.pro/pvt*ff8edc14/api/utils/search*/#vectorbtpro.utils.search*.search*config "vectorbtpro.utils.search*.search_config") and operate on both single values and sequences.

**```expression```** :&ensp;`CustomTemplateLike` :   Query expression or template.

**```query_engine```** :&ensp;`Optional[str]` :   Name of the query engine.

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```return_type```** :&ensp;`Optional[str]` :   If "item", returns the matched data item; if "bool", returns a boolean indicating a match.

**```**kwargs```** :   Keyword arguments for [KnowledgeAsset.apply](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply "vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply") or the query engine.

`MaybeKnowledgeAsset` :   New asset with the matching data items.

Rank documents by their similarity to a query.

Converts the asset's data to [TextDocument](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/doc*storing/#vectorbtpro.knowledge.doc*storing.TextDocument "vectorbtpro.knowledge.doc*storing.TextDocument") format using [KnowledgeAsset.to*documents](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.to*documents "vectorbtpro.knowledge.base*assets.KnowledgeAsset.to*documents") if necessary, then ranks the documents with [rank*documents](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/doc*ranking/#vectorbtpro.knowledge.doc*ranking.rank*documents "vectorbtpro.knowledge.doc*ranking.rank*documents") using provided keyword arguments. If caching is enabled with `cache*documents` and `cache*key`, the generated text documents are stored or loaded via an asset cache manager.

**```query```** :&ensp;`str` :   Query string to rank document relevance.

**```to*documents*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for [KnowledgeAsset.to*documents](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.to*documents "vectorbtpro.knowledge.base*assets.KnowledgeAsset.to_documents").

**```wrap_documents```** :&ensp;`Optional[bool]` :   Flag indicating whether to preserve the document embedding structure.

**```cache_documents```** :&ensp;`bool` :   If True, will use an asset cache manager to cache the generated text documents after conversion.

**```cache_key```** :&ensp;`Optional[str]` :   Unique identifier for the cached asset.

**```asset*cache*manager```** :&ensp;`Optional[MaybeType[AssetCacheManager]]` :   Class or instance of [AssetCacheManager](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.AssetCacheManager "vectorbtpro.knowledge.base*assets.AssetCacheManager").

**```asset*cache*manager*kwargs```** :&ensp;`KwargsLike` :   Keyword arguments to initialize or update `asset*cache_manager`.

**```silence_warnings```** :&ensp;`bool` :   Flag to suppress warning messages.

**```**kwargs```** :   Keyword arguments for [rank*documents](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/doc*ranking/#vectorbtpro.knowledge.doc*ranking.rank*documents "vectorbtpro.knowledge.doc*ranking.rank_documents").

`MaybeKnowledgeAsset` :   New asset with documents ranked based on similarity to the query.

**Overridden methods**

**Overridden by methods**

Reduce asset data items using a binary operation.

The reduction function `func` can be a callable, a tuple pairing a function with its arguments, a [Task](https://vectorbt.pro/pvt*ff8edc14/api/utils/execution/#vectorbtpro.utils.execution.Task "vectorbtpro.utils.execution.Task") instance, a subclass (or its prefix/full name) of [AssetFunc](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*asset*funcs/#vectorbtpro.knowledge.base*asset*funcs.AssetFunc "vectorbtpro.knowledge.base*asset*funcs.AssetFunc"), or an expression/template. In templates, use "i" for the data item index and "d1"/"d2" (or "x1"/"x2") for operands.

If an initializer is provided, the reduction starts with `d1` as the initializer and `d2` as the first data item. Otherwise, it starts with the first two data items.

If `by` is specified, see [KnowledgeAsset.groupby*reduce](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.groupby*reduce "vectorbtpro.knowledge.base*assets.KnowledgeAsset.groupby*reduce") for grouped reduction. If `wrap` is True, the result is returned as a new [KnowledgeAsset](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset "vectorbtpro.knowledge.base_assets.KnowledgeAsset") instance.

**```func```** :&ensp;`CustomTemplateLike` :   Reduction function, expression, or template.

**```*args```** :   Positional arguments for [KnowledgeAsset.groupby*reduce](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.groupby*reduce "vectorbtpro.knowledge.base*assets.KnowledgeAsset.groupby_reduce") or the reduction function.

**```initializer```** :&ensp;`Optional[Any]` :   Initial value for the reduction.

**```by```** :&ensp;`Optional[PathLikeKey]` :   Key or path used to group data items.

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```show_progress```** :&ensp;`Optional[bool]` :   Flag indicating whether to display the progress bar.

**```pbar_kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for configuring the progress bar.

**```wrap```** :&ensp;`Optional[bool]` :   If True, wrap the result in a [KnowledgeAsset](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset "vectorbtpro.knowledge.base*assets.KnowledgeAsset") instance.

**```return_iterator```** :&ensp;`bool` :   If True, return an iterator instead of executing tasks.

**```**kwargs```** :   Keyword arguments for [KnowledgeAsset.groupby*reduce](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.groupby*reduce "vectorbtpro.knowledge.base*assets.KnowledgeAsset.groupby_reduce") or the reduction function.

`MaybeKnowledgeAsset` :   New asset with the result of reducing the asset data items.

Remove data items or parts of them from the asset.

Leverages [KnowledgeAsset.apply](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply "vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply") with [RemoveAssetFunc](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*asset*funcs/#vectorbtpro.knowledge.base*asset*funcs.RemoveAssetFunc "vectorbtpro.knowledge.base*asset_funcs.RemoveAssetFunc") to remove either an entire data item (when a numeric path is provided) or a specific element within a data item based on a hierarchical path (e.g., "x.y[0].z").

**```path```** :&ensp;`MaybeList[PathLikeKey]` :   Path or list of paths indicating the element(s) to remove.

**```skip_missing```** :&ensp;`Optional[bool]` :   If True, skips data items where the specified path is missing.

**```make_copy```** :&ensp;`Optional[bool]` :   If True, operates on a copy rather than modifying the original data.

**```changed_only```** :&ensp;`Optional[bool]` :   If True, returns only data items that were modified.

**```**kwargs```** :   Keyword arguments for [KnowledgeAsset.apply](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply "vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply").

`MaybeKnowledgeAsset` :   New asset with the specified data items removed.

Remove empty data items from the asset.

**```inplace```** :&ensp;`bool` :   If True, remove empty items in place.

`Optional[KnowledgeAsset]` :   New asset with empty items removed, or None if modified in place.

Rename data items or parts of them within the asset.

Leverages [KnowledgeAsset.apply](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply "vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply") with [RenameAssetFunc](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*asset*funcs/#vectorbtpro.knowledge.base*asset*funcs.RenameAssetFunc "vectorbtpro.knowledge.base*asset*funcs.RenameAssetFunc") to change the names of elements within data items. This function is similar to `move` but uses `new*token` to specify the new name.

**```path```** :&ensp;`Union[PathRenameDict, MaybeList[PathLikeKey]]` :   Mapping or list of paths indicating the element(s) to rename.

**```new_token```** :&ensp;`Optional[MaybeList[PathKeyToken]]` :   New token or list of tokens for renaming the element(s).

**```skip_missing```** :&ensp;`Optional[bool]` :   If True, skips data items where the specified path is missing.

**```make_copy```** :&ensp;`Optional[bool]` :   If True, operates on a copy rather than modifying the original data.

**```changed_only```** :&ensp;`Optional[bool]` :   If True, returns only data items that were modified.

**```**kwargs```** :   Keyword arguments for [KnowledgeAsset.apply](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply "vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply").

`MaybeKnowledgeAsset` :   New asset with the modified data.

Reorder data items or parts within each item.

Uses [KnowledgeAsset.apply](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply "vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply") with [ReorderAssetFunc](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*asset*funcs/#vectorbtpro.knowledge.base*asset*funcs.ReorderAssetFunc "vectorbtpro.knowledge.base*asset*funcs.ReorderAssetFunc") to reorder data. For dictionaries, keys are reordered using [reorder*dict](https://vectorbt.pro/pvt*ff8edc14/api/utils/config/#vectorbtpro.utils.config.reorder*dict "vectorbtpro.utils.config.reorder*dict"); for sequences, ordering follows [reorder*list](https://vectorbt.pro/pvt*ff8edc14/api/utils/config/#vectorbtpro.utils.config.reorder*list "vectorbtpro.utils.config.reorder_list").

**```new_order```** :&ensp;`Union[str, PathKeyTokens]` :   New order specification, which can be:

**```path```** :&ensp;`Optional[MaybeList[PathLikeKey]]` :   Path(s) within the data item to reorder (e.g. "x.y[0].z").

**```skip_missing```** :&ensp;`Optional[bool]` :   If True, skips data items where the specified path is missing.

**```make_copy```** :&ensp;`Optional[bool]` :   If True, operates on a copy rather than modifying the original data.

**```changed_only```** :&ensp;`Optional[bool]` :   If True, returns only data items that were modified.

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```**kwargs```** :   Keyword arguments for [KnowledgeAsset.apply](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply "vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply").

`MaybeKnowledgeAsset` :   New asset with the reordered data.

Return a random sample of data items from the asset.

**```k```** :&ensp;`Optional[int]` :   Number of items to sample.

**```seed```** :&ensp;`Optional[int]` :   Random seed for deterministic output.

**```wrap```** :&ensp;`bool` :   If True, wrap the sampled data in a new asset; otherwise, return raw data items.

`Any` :   Either a new asset with the sampled data if `wrap` is True, or a single item (when sampling one) or a list of items.

Return a new [KnowledgeAsset](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset "vectorbtpro.knowledge.base*assets.KnowledgeAsset") instance based on the output of [KnowledgeAsset.get](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.get "vectorbtpro.knowledge.base*assets.KnowledgeAsset.get").

**```*args```** :   Positional arguments for [KnowledgeAsset.get](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.get "vectorbtpro.knowledge.base*assets.KnowledgeAsset.get").

**```**kwargs```** :   Keyword arguments for [KnowledgeAsset.get](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.get "vectorbtpro.knowledge.base*assets.KnowledgeAsset.get").

[KnowledgeAsset](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset "vectorbtpro.knowledge.base*assets.KnowledgeAsset") :   New asset containing the selected data.

Set specific data items or their parts.

This method modifies data items by applying [SetAssetFunc](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*asset*funcs/#vectorbtpro.knowledge.base*asset*funcs.SetAssetFunc "vectorbtpro.knowledge.base*asset*funcs.SetAssetFunc") via [KnowledgeAsset.apply](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply "vectorbtpro.knowledge.base_assets.KnowledgeAsset.apply").

**```value```** :&ensp;`Any` :   Value, function, or template to set.

**```path```** :&ensp;`Optional[MaybeList[PathLikeKey]]` :   Path(s) within the data item to set (e.g. "x.y[0].z").

**```skip_missing```** :&ensp;`Optional[bool]` :   If True, skips data items where the specified path is missing.

**```make_copy```** :&ensp;`Optional[bool]` :   If True, operates on a copy rather than modifying the original data.

**```changed_only```** :&ensp;`Optional[bool]` :   If True, returns only data items that were modified.

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```**kwargs```** :   Keyword arguments for [KnowledgeAsset.apply](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply "vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply").

`MaybeKnowledgeAsset` :   New asset with the modified data.

Set one or more data items in the asset.

**```index```** :&ensp;`Union[int, slice, Iterable[Union[bool, int]]]` :   Index specifying the item(s) to update.

**```value```** :&ensp;`Any` :   New value or iterable of values to assign.

**```inplace```** :&ensp;`bool` :   If True, modify the asset in place.

`Optional[KnowledgeAsset]` :   New asset with updated data, or None if modified in place.

Shuffle the asset's data items randomly.

**```seed```** :&ensp;`Optional[int]` :   Random seed for deterministic output.

**```inplace```** :&ensp;`bool` :   If True, shuffle the data in place; otherwise, return a new asset instance.

[KnowledgeAsset](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset "vectorbtpro.knowledge.base*assets.KnowledgeAsset") :   New asset with shuffled data if `inplace` is False; otherwise, None.

Whether the asset holds a single item.

`bool` :   True if the asset contains a single item, otherwise False.

Sort data items based on keys extracted via [KnowledgeAsset.get](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.get "vectorbtpro.knowledge.base*assets.KnowledgeAsset.get").

**```*args```** :   Positional arguments for [KnowledgeAsset.get](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.get "vectorbtpro.knowledge.base*assets.KnowledgeAsset.get").

**```keys```** :&ensp;`Optional[Iterable[Key]]` :   Iterable of keys to sort by.

**```ascending```** :&ensp;`bool` :   True for ascending order, False for descending.

**```inplace```** :&ensp;`bool` :   If True, sort the data in place.

**```**kwargs```** :   Keyword arguments for [KnowledgeAsset.get](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.get "vectorbtpro.knowledge.base*assets.KnowledgeAsset.get").

`Optional[KnowledgeAsset]` :   New asset with sorted data, or None if sorted in place.

Split text content from the asset.

This method applies [SplitTextAssetFunc](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*asset*funcs/#vectorbtpro.knowledge.base*asset*funcs.SplitTextAssetFunc "vectorbtpro.knowledge.base*asset*funcs.SplitTextAssetFunc") via [KnowledgeAsset.apply](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply "vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply") to split text content using [split*text](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/text*splitting/#vectorbtpro.knowledge.text*splitting.split*text "vectorbtpro.knowledge.text*splitting.split*text").

**```text_path```** :&ensp;`Optional[PathLikeKey]` :   Path specifying the location of the text content.

**```document_cls```** :&ensp;`Optional[Type[StoreDocument]]` :   Document class to use for creating documents.

**```merge_chunks```** :&ensp;`Optional[bool]` :   If True, merge all text chunks into a single list.

**```**kwargs```** :   Keyword arguments for [KnowledgeAsset.apply](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply "vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply").

`MaybeKnowledgeAsset` :   New asset with its text content split into chunks.

Convert the asset to a context string.

Based on the `dump*all` flag, calls either [KnowledgeAsset.dump*all](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.dump*all "vectorbtpro.knowledge.base*assets.KnowledgeAsset.dump*all") or [KnowledgeAsset.dump](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.dump "vectorbtpro.knowledge.base*assets.KnowledgeAsset.dump") with provided arguments. The dumped data is then joined using [KnowledgeAsset.join](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.join "vectorbtpro.knowledge.base*assets.KnowledgeAsset.join") with the specified separator.

**```*args```** :   Positional arguments for the dump function.

**```dump_all```** :&ensp;`Optional[bool]` :   Flag determining which dump method to use.

**```separator```** :&ensp;`Optional[str]` :   Separator used for joining dumped data.

**```**kwargs```** :   Keyword arguments for the dump function.

`str` :   Resulting context string.

**Overridden methods**

**Overridden by methods**

Convert asset data items to text documents of type [TextDocument](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/doc*storing/#vectorbtpro.knowledge.doc*storing.TextDocument "vectorbtpro.knowledge.doc*storing.TextDocument").

Templates provided via keyword arguments can reference:

**```document_cls```** :&ensp;`Optional[Type[StoreDocument]]` :   Document class to use for creating documents.

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```**kwargs```** :   Keyword arguments for [KnowledgeAsset.apply](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply "vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply").

`MaybeKnowledgeAsset` :   New asset with data items converted to text documents.

Reconstruct nested structures from flattened asset data.

This method applies an unflattening operation using [KnowledgeAsset.apply](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply "vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply") with [UnflattenAssetFunc](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*asset*funcs/#vectorbtpro.knowledge.base*asset*funcs.UnflattenAssetFunc "vectorbtpro.knowledge.base*asset*funcs.UnflattenAssetFunc"). Specify the flattened portion to reconstruct using the `path` argument. Multiple paths can be provided. If `skip*missing` is True and a specified path is missing, the data item will be skipped.

**```path```** :&ensp;`Optional[MaybeList[PathLikeKey]]` :   Path(s) within the data item to unflatten (e.g. "x.y[0].z").

**```skip_missing```** :&ensp;`Optional[bool]` :   If True, skips data items where the specified path is missing.

**```make_copy```** :&ensp;`Optional[bool]` :   If True, operates on a copy rather than modifying the original data.

**```changed_only```** :&ensp;`Optional[bool]` :   If True, returns only data items that were modified.

**```**kwargs```** :   Keyword arguments for [KnowledgeAsset.apply](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply "vectorbtpro.knowledge.base*assets.KnowledgeAsset.apply").

`MaybeKnowledgeAsset` :   New asset with unflattened data.

De-duplicate data items using keys obtained via [KnowledgeAsset.get](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.get "vectorbtpro.knowledge.base*assets.KnowledgeAsset.get").

**```*args```** :   Positional arguments for [KnowledgeAsset.get](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.get "vectorbtpro.knowledge.base*assets.KnowledgeAsset.get").

**```keep```** :&ensp;`str` :   Indicates which duplicate to retain; valid options are "first" or "last".

**```inplace```** :&ensp;`bool` :   If True, de-duplicate the data in place.

**```**kwargs```** :   Keyword arguments for [KnowledgeAsset.get](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.get "vectorbtpro.knowledge.base*assets.KnowledgeAsset.get").

`Optional[KnowledgeAsset]` :   New asset with duplicates removed, or None if modified in place.

Metaclass for the [KnowledgeAsset](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset "vectorbtpro.knowledge.base*assets.KnowledgeAsset") class.

**Examples:**

Example 1 (python):
```python
AssetCacheManager(
    persist_cache=None,
    cache_dir=None,
    cache_mkdir_kwargs=None,
    clear_cache=None,
    max_cache_count=None,
    save_cache_kwargs=None,
    load_cache_kwargs=None,
    template_context=None,
    **kwargs
)
```

Example 2 (text):
```text
See [check_mkdir](https://vectorbt.pro/pvt_ff8edc14/api/utils/path_/#vectorbtpro.utils.path_.check_mkdir "vectorbtpro.utils.path_.check_mkdir").
```

Example 3 (text):
```text
See [save](https://vectorbt.pro/pvt_ff8edc14/api/utils/pickling/#vectorbtpro.utils.pickling.save "vectorbtpro.utils.pickling.save").
```

Example 4 (text):
```text
See [load](https://vectorbt.pro/pvt_ff8edc14/api/utils/pickling/#vectorbtpro.utils.pickling.load "vectorbtpro.utils.pickling.load").
```

---

## base_asset_funcs

**URL:** https://vectorbt.pro/pvt_ff8edc14/api/knowledge/base_asset_funcs.md

**Contents:**
- AssetFunc <span class="dobjtype">class</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/base_asset_funcs.py#L27-L82" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.base_asset_funcs.AssetFunc data-toc-label="AssetFunc" }
  - call <span class="dobjtype">class method</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/base_asset_funcs.py#L52-L67" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.base_asset_funcs.AssetFunc.call data-toc-label="call" }
  - prepare <span class="dobjtype">class method</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/base_asset_funcs.py#L39-L50" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.base_asset_funcs.AssetFunc.prepare data-toc-label="prepare" }
  - prepare_and_call <span class="dobjtype">class method</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/base_asset_funcs.py#L69-L82" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.base_asset_funcs.AssetFunc.prepare_and_call data-toc-label="prepare\_and\_call" }
- CollectAssetFunc <span class="dobjtype">class</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/base_asset_funcs.py#L2174-L2241" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.base_asset_funcs.CollectAssetFunc data-toc-label="CollectAssetFunc" }
  - prepare <span class="dobjtype">class method</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/base_asset_funcs.py#L2182-L2207" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.base_asset_funcs.CollectAssetFunc.prepare data-toc-label="prepare" }
  - sort_key <span class="dobjtype">class method</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/base_asset_funcs.py#L2209-L2220" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.base_asset_funcs.CollectAssetFunc.sort_key data-toc-label="sort\_key" }
- DumpAssetFunc <span class="dobjtype">class</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/base_asset_funcs.py#L1842-L1963" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.base_asset_funcs.DumpAssetFunc data-toc-label="DumpAssetFunc" }
  - prepare <span class="dobjtype">class method</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/base_asset_funcs.py#L1880-L1930" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.base_asset_funcs.DumpAssetFunc.prepare data-toc-label="prepare" }
  - resolve_dump_kwargs <span class="dobjtype">class method</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/base_asset_funcs.py#L1850-L1878" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.base_asset_funcs.DumpAssetFunc.resolve_dump_kwargs data-toc-label="resolve\_dump\_kwargs" }

Module providing base asset function classes.

Abstract base class for asset functions.

Provides methods to prepare arguments and execute asset function calls.

**Inherited members**

Call the asset function.

!!! abstract This method should be overridden in a subclass.

**```d```** :   Input data.

**```*args```** :   Additional positional arguments.

**```**kwargs```** :   Additional keyword arguments.

`Any` :   Result of the asset function call.

Prepare positional and keyword arguments for an asset function call.

**```*args```** :   Additional positional arguments.

**```**kwargs```** :   Additional keyword arguments.

`ArgsKwargs` :   Tuple containing the positional arguments and keyword arguments.

Prepare arguments and invoke the asset function.

**```d```** :   Input data.

**```*args```** :   Positional arguments for [AssetFunc.prepare](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*asset*funcs/#vectorbtpro.knowledge.base*asset*funcs.AssetFunc.prepare "vectorbtpro.knowledge.base*asset*funcs.AssetFunc.prepare") and ultimately to [AssetFunc.call](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*asset*funcs/#vectorbtpro.knowledge.base*asset*funcs.AssetFunc.call "vectorbtpro.knowledge.base*asset*funcs.AssetFunc.call").

**```**kwargs```** :   Keyword arguments for [AssetFunc.prepare](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*asset*funcs/#vectorbtpro.knowledge.base*asset*funcs.AssetFunc.prepare "vectorbtpro.knowledge.base*asset*funcs.AssetFunc.prepare") and ultimately to [AssetFunc.call](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*asset*funcs/#vectorbtpro.knowledge.base*asset*funcs.AssetFunc.call "vectorbtpro.knowledge.base*asset*funcs.AssetFunc.call").

`Any` :   Result returned by the asset function.

Asset function class for collecting data with [KnowledgeAsset.collect](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.collect "vectorbtpro.knowledge.base*assets.KnowledgeAsset.collect").

**Inherited members**

Prepare positional and keyword arguments for an asset function call.

**```sort_keys```** :&ensp;`Optional[bool]` :   Whether to sort the keys.

**```asset_cls```** :&ensp;`Optional[Type[KnowledgeAsset]]` :   Asset class to use for resolving settings.

**```**kwargs```** :   Additional keyword arguments.

`ArgsKwargs` :   Tuple containing the positional arguments and keyword arguments.

Return a tuple used as a sorting key.

**```k```** :&ensp;`Any` :   Key to be sorted.

`tuple` :   Tuple used for sorting, where the first element is 0 if `k` is a string, otherwise 1, and the second element is `k` itself.

Asset function class for performing the dump operation with [KnowledgeAsset.dump](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.dump "vectorbtpro.knowledge.base*assets.KnowledgeAsset.dump").

**Inherited members**

Prepare positional and keyword arguments for an asset function call.

**```source```** :&ensp;`Optional[CustomTemplateLike]` :   Template or function to preprocess the source data.

**```dump_engine```** :&ensp;`Optional[str]` :   Name of the dump engine.

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```asset_cls```** :&ensp;`Optional[Type[KnowledgeAsset]]` :   Asset class to use for resolving settings.

**```**kwargs```** :   Keyword arguments for [dump](https://vectorbt.pro/pvt_ff8edc14/api/utils/formatting/#vectorbtpro.utils.formatting.dump "vectorbtpro.utils.formatting.dump").

`ArgsKwargs` :   Tuple containing the positional arguments and keyword arguments.

Resolve and merge dumping-related keyword arguments based on asset settings and the provided dump engine.

**```dump_engine```** :&ensp;`Optional[str]` :   Name of the dump engine.

**```asset_cls```** :&ensp;`Optional[Type[KnowledgeAsset]]` :   Asset class to use for resolving settings.

**```**kwargs```** :   Additional keyword arguments to merge with the resolved settings.

`Kwargs` :   Dictionary containing the resolved dumping-related keyword arguments.

Asset function class for searching in asset data with [KnowledgeAsset.find](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.find "vectorbtpro.knowledge.base*assets.KnowledgeAsset.find").

Implements logic to locate assets using configurable search parameters.

**Inherited members**

Return whether the given data item matches the specified target criteria used in [FindAssetFunc.call](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*asset*funcs/#vectorbtpro.knowledge.base*asset*funcs.AssetFunc.call "vectorbtpro.knowledge.base*asset_funcs.FindAssetFunc.call").

This function evaluates `target` against the provided data `d` using different strategies:

A `target` may be a callable that takes a key and a value, and returns a boolean or an instance of [Not](https://vectorbt.pro/pvt*ff8edc14/api/utils/search*/#vectorbtpro.utils.search*.Not "vectorbtpro.utils.search*.Not") to indicate negation.

**```k```** :&ensp;`Optional[Hashable]` :   Key associated with the current element.

**```d```** :&ensp;`Any` :   Data item to test.

**```target```** :&ensp;`MaybeList[Any]` :   Target value(s) or callable(s) to determine if a match occurs.

**```find_all```** :&ensp;`bool` :   Flag specifying if all targets should be evaluated.

**```**kwargs```** :   Keyword arguments for [find](https://vectorbt.pro/pvt*ff8edc14/api/utils/search*/#vectorbtpro.utils.search*.find "vectorbtpro.utils.search*.find").

`bool` :   True if the data item matches the target criteria, False otherwise.

Prepare positional and keyword arguments for an asset function call.

**```target```** :&ensp;`MaybeList[Any]` :   Target value(s) or callable(s) to determine if a match occurs.

**```path```** :&ensp;`Optional[MaybeList[PathLikeKey]]` :   Path(s) within the data item to search (e.g. "x.y[0].z").

**```per_path```** :&ensp;`Optional[bool]` :   If True, consider targets provided per path.

**```find_all```** :&ensp;`Optional[bool]` :   Require all targets to be found when multiple targets are provided.

**```keep_path```** :&ensp;`Optional[bool]` :   If True, returns results structured as nested dictionaries mirroring the specified path.

**```skip_missing```** :&ensp;`Optional[bool]` :   If True, skips data items where the specified path is missing.

**```source```** :&ensp;`Optional[CustomTemplateLike]` :   Template or function to preprocess the source data.

**```in_dumps```** :&ensp;`Optional[bool]` :   If True, converts the entire data item to string for searching.

**```dump_kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for dumping structured data.

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```return_type```** :&ensp;`Optional[str]` :   Indicates the return type: "item", "field", or "bool".

**```return_path```** :&ensp;`Optional[bool]` :   Specifies whether to include the path in the returned result.

**```asset_cls```** :&ensp;`Optional[Type[KnowledgeAsset]]` :   Asset class to use for resolving settings.

**```**kwargs```** :   Keyword arguments distributed between [find*in*obj](https://vectorbt.pro/pvt*ff8edc14/api/utils/search*/#vectorbtpro.utils.search*.find*in*obj "vectorbtpro.utils.search*.find*in*obj") and [find](https://vectorbt.pro/pvt*ff8edc14/api/utils/search*/#vectorbtpro.utils.search*.find "vectorbtpro.utils.search*.find").

`ArgsKwargs` :   Tuple containing the positional arguments and keyword arguments.

Asset function class for executing removal with [KnowledgeAsset.find*remove](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.find*remove "vectorbtpro.knowledge.base*assets.KnowledgeAsset.find_remove").

**Inherited members**

Return whether the given object is empty.

**```d```** :&ensp;`Any` :   Data item to check for emptiness.

`bool` :   True if the data item is empty, False otherwise.

Prepare positional and keyword arguments for an asset function call.

**```target```** :&ensp;`Union[dict, MaybeList[Any]]` :   Value or mapping used to identify occurrences for removal.

**```path```** :&ensp;`Optional[MaybeList[PathLikeKey]]` :   Path(s) within the data item to search (e.g. "x.y[0].z").

**```per_path```** :&ensp;`Optional[bool]` :   If True, consider targets provided per path.

**```find_all```** :&ensp;`Optional[bool]` :   Require all targets to be found when multiple targets are provided.

**```keep_path```** :&ensp;`Optional[bool]` :   If True, returns results structured as nested dictionaries mirroring the specified path.

**```skip_missing```** :&ensp;`Optional[bool]` :   If True, skips data items where the specified path is missing.

**```make_copy```** :&ensp;`Optional[bool]` :   If True, operates on a copy rather than modifying the original data.

**```changed_only```** :&ensp;`Optional[bool]` :   If True, returns only data items that were modified.

**```asset_cls```** :&ensp;`Optional[Type[KnowledgeAsset]]` :   Asset class to use for resolving settings.

**```**kwargs```** :   Keyword arguments distributed between [find*in*obj](https://vectorbt.pro/pvt*ff8edc14/api/utils/search*/#vectorbtpro.utils.search*.find*in*obj "vectorbtpro.utils.search*.find*in*obj") and [find](https://vectorbt.pro/pvt*ff8edc14/api/utils/search*/#vectorbtpro.utils.search*.find "vectorbtpro.utils.search*.find").

`ArgsKwargs` :   Tuple containing the positional arguments and keyword arguments.

Asset function class for performing asset-level find and replace operations with [KnowledgeAsset.find*replace](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.find*replace "vectorbtpro.knowledge.base*assets.KnowledgeAsset.find_replace").

**Inherited members**

Prepare positional and keyword arguments for an asset function call.

**```target```** :&ensp;`Union[dict, List[Any]]` :   Data item(s) or pattern(s) to search for.

**```replacement```** :&ensp;`Optional[List[Any]]` :   Replacement value(s) for matched occurrences.

**```path```** :&ensp;`Optional[List[PathLikeKey]]` :   Specific path(s) within each data item to target.

**```per_path```** :&ensp;`Optional[bool]` :   If True, consider targets and replacements provided per path.

**```find_all```** :&ensp;`Optional[bool]` :   Require all targets to be found when multiple targets are provided.

**```keep_path```** :&ensp;`Optional[bool]` :   If True, returns results structured as nested dictionaries mirroring the specified path.

**```skip_missing```** :&ensp;`Optional[bool]` :   If True, skips data items where the specified path is missing.

**```make_copy```** :&ensp;`Optional[bool]` :   If True, operates on a copy rather than modifying the original data.

**```changed_only```** :&ensp;`Optional[bool]` :   If True, returns only data items that were modified.

**```asset_cls```** :&ensp;`Optional[Type[KnowledgeAsset]]` :   Asset class to use for resolving settings.

**```**kwargs```** :   Keyword arguments distributed between [find*in*obj](https://vectorbt.pro/pvt*ff8edc14/api/utils/search*/#vectorbtpro.utils.search*.find*in*obj "vectorbtpro.utils.search*.find*in*obj") and [replace](https://vectorbt.pro/pvt*ff8edc14/api/utils/search*/#vectorbtpro.utils.search*.replace "vectorbtpro.utils.search*.replace").

`ArgsKwargs` :   Tuple containing the positional arguments and keyword arguments.

Replace a value based on matching criteria.

This method is used by [FindReplaceAssetFunc.call](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*asset*funcs/#vectorbtpro.knowledge.base*asset*funcs.AssetFunc.call "vectorbtpro.knowledge.base*asset*funcs.FindReplaceAssetFunc.call") to determine the replacement for a matched value. For string inputs, it applies [replace](https://vectorbt.pro/pvt*ff8edc14/api/utils/search*/#vectorbtpro.utils.search*.replace "vectorbtpro.utils.search_.replace") for text substitution. For other types, it returns the replacement directly if the specified target condition is met. Both `target` and `replacement` may be callables that take a key and a value, where `target` returns a boolean indicating a match and `replacement` computes the new value.

**```k```** :&ensp;`Optional[Hashable]` :   Key associated with the current element.

**```d```** :&ensp;`Any` :   Original value to evaluate for a match.

**```target```** :&ensp;`MaybeList[Any]` :   Target value(s) or callable(s) to determine if a match occurs.

**```replacement```** :&ensp;`MaybeList[Any]` :   Replacement value or callable to apply when a match is found.

**```**kwargs```** :   Keyword arguments for [replace](https://vectorbt.pro/pvt*ff8edc14/api/utils/search*/#vectorbtpro.utils.search*.replace "vectorbtpro.utils.search*.replace").

`Any` :   Resulting value after replacement if a match is found; otherwise, the original value.

Asset function class for performing flattening with [KnowledgeAsset.flatten](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.flatten "vectorbtpro.knowledge.base*assets.KnowledgeAsset.flatten").

**Inherited members**

Prepare positional and keyword arguments for an asset function call.

**```path```** :&ensp;`Optional[MaybeList[PathLikeKey]]` :   Path(s) within the data item to flatten (e.g. "x.y[0].z").

**```skip_missing```** :&ensp;`Optional[bool]` :   If True, skips data items where the specified path is missing.

**```make_copy```** :&ensp;`Optional[bool]` :   If True, operates on a copy rather than modifying the original data.

**```changed_only```** :&ensp;`Optional[bool]` :   If True, returns only data items that were modified.

**```asset_cls```** :&ensp;`Optional[Type[KnowledgeAsset]]` :   Asset class to use for resolving settings.

**```**kwargs```** :   Keyword arguments for [flatten*obj](https://vectorbt.pro/pvt*ff8edc14/api/utils/search*/#vectorbtpro.utils.search*.flatten*obj "vectorbtpro.utils.search*.flatten_obj").

`ArgsKwargs` :   Tuple containing the positional arguments and keyword arguments.

Asset function class for retrieving asset data with [KnowledgeAsset.get](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.get "vectorbtpro.knowledge.base*assets.KnowledgeAsset.get").

Extracts data based on a specified path and optionally transforms it using a provided template.

**Inherited members**

Prepare positional and keyword arguments for an asset function call.

**```path```** :&ensp;`Optional[MaybeList[PathLikeKey]]` :   Path(s) within the data item to get (e.g. "x.y[0].z").

**```keep_path```** :&ensp;`Optional[bool]` :   If True, returns results structured as nested dictionaries mirroring the specified path.

**```skip_missing```** :&ensp;`Optional[bool]` :   If True, skips data items where the specified path is missing.

**```source```** :&ensp;`Optional[CustomTemplateLike]` :   Template, function, or string for preprocessing; in the template, "i" denotes the index, "d" the full data item, and "x" the extracted part.

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```asset_cls```** :&ensp;`Optional[Type[KnowledgeAsset]]` :   Asset class to use for resolving settings.

**```**kwargs```** :   Additional keyword arguments.

`ArgsKwargs` :   Tuple containing the positional arguments and keyword arguments.

Asset function class for merging dictionaries with [KnowledgeAsset.merge*dicts](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.merge*dicts "vectorbtpro.knowledge.base*assets.KnowledgeAsset.merge_dicts").

**Inherited members**

Asset function class for merging lists with [KnowledgeAsset.merge*lists](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.merge*lists "vectorbtpro.knowledge.base*assets.KnowledgeAsset.merge_lists").

**Inherited members**

Asset function class for moving an asset field within a knowledge asset with [KnowledgeAsset.move](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.move "vectorbtpro.knowledge.base*assets.KnowledgeAsset.move").

**Inherited members**

Prepare positional and keyword arguments for an asset function call.

**```path```** :&ensp;`Union[PathMoveDict, MaybeList[PathLikeKey]]` :   Mapping or path(s) within the data item to move (e.g. "x.y[0].z").

**```new_path```** :&ensp;`Optional[MaybeList[PathLikeKey]]` :   Path(s) for the moved element(s) when `path` is not a dictionary.

**```skip_missing```** :&ensp;`Optional[bool]` :   If True, skips data items where the specified path is missing.

**```make_copy```** :&ensp;`Optional[bool]` :   If True, operates on a copy rather than modifying the original data.

**```changed_only```** :&ensp;`Optional[bool]` :   If True, returns only data items that were modified.

**```asset_cls```** :&ensp;`Optional[Type[KnowledgeAsset]]` :   Asset class to use for resolving settings.

**```**kwargs```** :   Additional keyword arguments.

`ArgsKwargs` :   Tuple containing the positional arguments and keyword arguments.

Asset function class for querying asset data with [KnowledgeAsset.query](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.query "vectorbtpro.knowledge.base*assets.KnowledgeAsset.query").

**Inherited members**

Prepare positional and keyword arguments for an asset function call.

**```expression```** :&ensp;`CustomTemplateLike` :   Query expression or template.

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```return_type```** :&ensp;`Optional[str]` :   If "item", returns the matched data item; if "bool", returns a boolean indicating a match.

**```asset_cls```** :&ensp;`Optional[Type[KnowledgeAsset]]` :   Asset class to use for resolving settings.

**```**kwargs```** :   Additional keyword arguments.

`ArgsKwargs` :   Tuple containing the positional arguments and keyword arguments.

Abstract class defining an asset function for reducing data with [KnowledgeAsset.reduce](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.reduce "vectorbtpro.knowledge.base*assets.KnowledgeAsset.reduce").

**Inherited members**

Prepare arguments and invoke the asset function for reducing data.

**```d1```** :   First input data.

**```d2```** :   Second input data.

**```*args```** :   Positional arguments for [AssetFunc.prepare](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*asset*funcs/#vectorbtpro.knowledge.base*asset*funcs.AssetFunc.prepare "vectorbtpro.knowledge.base*asset*funcs.ReduceAssetFunc.prepare") and ultimately to [ReduceAssetFunc.call](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*asset*funcs/#vectorbtpro.knowledge.base*asset*funcs.AssetFunc.call "vectorbtpro.knowledge.base*asset*funcs.ReduceAssetFunc.call").

**```**kwargs```** :   Keyword arguments for [AssetFunc.prepare](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*asset*funcs/#vectorbtpro.knowledge.base*asset*funcs.AssetFunc.prepare "vectorbtpro.knowledge.base*asset*funcs.ReduceAssetFunc.prepare") and ultimately to [ReduceAssetFunc.call](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*asset*funcs/#vectorbtpro.knowledge.base*asset*funcs.AssetFunc.call "vectorbtpro.knowledge.base*asset*funcs.ReduceAssetFunc.call").

`Any` :   Result returned by the asset function.

Asset function class for removing an asset field from a knowledge asset with [KnowledgeAsset.remove](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.remove "vectorbtpro.knowledge.base*assets.KnowledgeAsset.remove").

**Inherited members**

Prepare positional and keyword arguments for an asset function call.

**```path```** :&ensp;`MaybeList[PathLikeKey]` :   Path or list of paths indicating the element(s) to remove.

**```skip_missing```** :&ensp;`Optional[bool]` :   If True, skips data items where the specified path is missing.

**```make_copy```** :&ensp;`Optional[bool]` :   If True, operates on a copy rather than modifying the original data.

**```changed_only```** :&ensp;`Optional[bool]` :   If True, returns only data items that were modified.

**```asset_cls```** :&ensp;`Optional[Type[KnowledgeAsset]]` :   Asset class to use for resolving settings.

**```**kwargs```** :   Additional keyword arguments.

`ArgsKwargs` :   Tuple containing the positional arguments and keyword arguments.

Asset function class for renaming an asset field in a knowledge asset with [KnowledgeAsset.rename](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.rename "vectorbtpro.knowledge.base*assets.KnowledgeAsset.rename").

Converts the rename operation into a move operation with token replacement.

**Inherited members**

Asset function class for reordering asset data with [KnowledgeAsset.reorder](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.reorder "vectorbtpro.knowledge.base*assets.KnowledgeAsset.reorder").

**Inherited members**

Prepare positional and keyword arguments for an asset function call.

**```new_order```** :&ensp;`Union[str, PathKeyTokens]` :   New order specification, which can be:

**```path```** :&ensp;`Optional[MaybeList[PathLikeKey]]` :   Path(s) within the data item to reorder (e.g. "x.y[0].z").

**```skip_missing```** :&ensp;`Optional[bool]` :   If True, skips data items where the specified path is missing.

**```make_copy```** :&ensp;`Optional[bool]` :   If True, operates on a copy rather than modifying the original data.

**```changed_only```** :&ensp;`Optional[bool]` :   If True, returns only data items that were modified.

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```asset_cls```** :&ensp;`Optional[Type[KnowledgeAsset]]` :   Asset class to use for resolving settings.

**```**kwargs```** :   Additional keyword arguments.

`ArgsKwargs` :   Tuple containing the positional arguments and keyword arguments.

Asset function class for setting asset data with [KnowledgeAsset.set](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.set "vectorbtpro.knowledge.base*assets.KnowledgeAsset.set").

Updates the asset data at specified paths with a given value, optionally applying transformations.

**Inherited members**

Prepare positional and keyword arguments for an asset function call.

**```value```** :&ensp;`Any` :   Value, function, or template to set.

**```path```** :&ensp;`Optional[MaybeList[PathLikeKey]]` :   Path(s) within the data item to set (e.g. "x.y[0].z").

**```skip_missing```** :&ensp;`Optional[bool]` :   If True, skips data items where the specified path is missing.

**```make_copy```** :&ensp;`Optional[bool]` :   If True, operates on a copy rather than modifying the original data.

**```changed_only```** :&ensp;`Optional[bool]` :   If True, returns only data items that were modified.

**```template_context```** :&ensp;`KwargsLike` :   Additional context for template substitution.

**```asset_cls```** :&ensp;`Optional[Type[KnowledgeAsset]]` :   Asset class to use for resolving settings.

**```**kwargs```** :   Additional keyword arguments.

`ArgsKwargs` :   Tuple containing the positional arguments and keyword arguments.

Asset function class for splitting text with [KnowledgeAsset.split*text](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.split*text "vectorbtpro.knowledge.base*assets.KnowledgeAsset.split_text").

**Inherited members**

Prepare positional and keyword arguments for an asset function call.

**```text_path```** :&ensp;`Optional[PathLikeKey]` :   Path specifying the location of the text content.

**```document_cls```** :&ensp;`Optional[Type[StoreDocument]]` :   Document class to use for creating documents.

**```asset_cls```** :&ensp;`Optional[Type[KnowledgeAsset]]` :   Asset class to use for resolving settings.

**```**split*text*kwargs```** :   Keyword arguments for [split*text](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/text*splitting/#vectorbtpro.knowledge.text*splitting.split*text "vectorbtpro.knowledge.text*splitting.split_text").

`ArgsKwargs` :   Tuple containing the positional arguments and keyword arguments.

Asset function class for converting asset data into document objects with [KnowledgeAsset.to*documents](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.to*documents "vectorbtpro.knowledge.base*assets.KnowledgeAsset.to_documents").

**Inherited members**

Prepare positional and keyword arguments for an asset function call.

**```document_cls```** :&ensp;`Optional[Type[StoreDocument]]` :   Document class to use for creating documents.

**```template_context```** :&ensp;`Union[KwargsLike, CustomTemplate]` :   Additional context for template substitution.

**```asset_cls```** :&ensp;`Optional[Type[KnowledgeAsset]]` :   Asset class to use for resolving settings.

**```**document*kwargs```** :   Keyword arguments for [StoreData.from*data](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/doc*storing/#vectorbtpro.knowledge.doc*storing.StoreData.from*data "vectorbtpro.knowledge.doc*storing.StoreData.from*data").

`ArgsKwargs` :   Tuple containing the positional arguments and keyword arguments.

Asset function class for applying the unflatten transformation with [KnowledgeAsset.unflatten](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*assets/#vectorbtpro.knowledge.base*assets.KnowledgeAsset.unflatten "vectorbtpro.knowledge.base*assets.KnowledgeAsset.unflatten").

**Inherited members**

Prepare positional and keyword arguments for an asset function call.

**```path```** :&ensp;`Optional[MaybeList[PathLikeKey]]` :   Path(s) within the data item to unflatten (e.g. "x.y[0].z").

**```skip_missing```** :&ensp;`Optional[bool]` :   If True, skips data items where the specified path is missing.

**```make_copy```** :&ensp;`Optional[bool]` :   If True, operates on a copy rather than modifying the original data.

**```changed_only```** :&ensp;`Optional[bool]` :   If True, returns only data items that were modified.

**```asset_cls```** :&ensp;`Optional[Type[KnowledgeAsset]]` :   Asset class to use for resolving settings.

**```**kwargs```** :   Keyword arguments for [unflatten*obj](https://vectorbt.pro/pvt*ff8edc14/api/utils/search*/#vectorbtpro.utils.search*.unflatten*obj "vectorbtpro.utils.search*.unflatten_obj").

`ArgsKwargs` :   Tuple containing the positional arguments and keyword arguments.

**Examples:**

Example 1 (python):
```python
AssetFunc()
```

Example 2 (python):
```python
AssetFunc.call(
    d,
    *args,
    **kwargs
)
```

Example 3 (python):
```python
AssetFunc.prepare(
    *args,
    **kwargs
)
```

Example 4 (python):
```python
AssetFunc.prepare_and_call(
    d,
    *args,
    **kwargs
)
```

---

## asset_pipelines

**URL:** https://vectorbt.pro/pvt_ff8edc14/api/knowledge/asset_pipelines.md

**Contents:**
- AssetPipeline <span class="dobjtype">class</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/asset_pipelines.py#L29-L146" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.asset_pipelines.AssetPipeline data-toc-label="AssetPipeline" }
  - resolve_task <span class="dobjtype">class method</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/asset_pipelines.py#L35-L129" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.asset_pipelines.AssetPipeline.resolve_task data-toc-label="resolve\_task" }
  - run <span class="dobjtype">method</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/asset_pipelines.py#L131-L143" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.asset_pipelines.AssetPipeline.run data-toc-label="run" }
- BasicAssetPipeline <span class="dobjtype">class</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/asset_pipelines.py#L157-L237" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.asset_pipelines.BasicAssetPipeline data-toc-label="BasicAssetPipeline" }
  - add_task <span class="dobjtype">method</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/asset_pipelines.py#L200-L213" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.asset_pipelines.BasicAssetPipeline.add_task data-toc-label="add\_task" }
  - compose_tasks <span class="dobjtype">class method</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/asset_pipelines.py#L215-L234" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.asset_pipelines.BasicAssetPipeline.compose_tasks data-toc-label="compose\_tasks" }
  - tasks <span class="dobjtype">class property</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/asset_pipelines.py#L191-L198" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.asset_pipelines.BasicAssetPipeline.tasks data-toc-label="tasks" }
- ComplexAssetPipeline <span class="dobjtype">class</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/asset_pipelines.py#L240-L477" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.asset_pipelines.ComplexAssetPipeline data-toc-label="ComplexAssetPipeline" }
  - context <span class="dobjtype">class property</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/asset_pipelines.py#L464-L471" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.asset_pipelines.ComplexAssetPipeline.context data-toc-label="context" }
  - expression <span class="dobjtype">class property</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/knowledge/asset_pipelines.py#L455-L462" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.knowledge.asset_pipelines.ComplexAssetPipeline.expression data-toc-label="expression" }

Module providing classes for creating and executing asset pipelines.

See [vectorbtpro.knowledge](https://vectorbt.pro/pvt_ff8edc14/api/knowledge/ "vectorbtpro.knowledge") for the toy dataset.

Abstract class representing an asset pipeline.

Provides functionality to resolve and execute tasks in an asset pipeline.

**Inherited members**

Return a [Task](https://vectorbt.pro/pvt_ff8edc14/api/utils/execution/#vectorbtpro.utils.execution.Task "vectorbtpro.utils.execution.Task") by resolving the provided asset function and its arguments.

**```func```** :&ensp;`AssetFuncLike` :   Asset function identifier, which may be a tuple, [Task](https://vectorbt.pro/pvt*ff8edc14/api/utils/execution/#vectorbtpro.utils.execution.Task "vectorbtpro.utils.execution.Task"), string, or subclass of [AssetFunc](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*asset*funcs/#vectorbtpro.knowledge.base*asset*funcs.AssetFunc "vectorbtpro.knowledge.base*asset*funcs.AssetFunc").

**```*args```** :   Positional arguments for [Task](https://vectorbt.pro/pvt_ff8edc14/api/utils/execution/#vectorbtpro.utils.execution.Task "vectorbtpro.utils.execution.Task").

**```prepare```** :&ensp;`bool` :   Flag indicating whether to prepare the function's arguments before execution.

**```prepare_once```** :&ensp;`bool` :   Flag indicating whether to prepare the function's arguments only once.

**```cond_kwargs```** :&ensp;`KwargsLike` :   Keyword arguments for conditional preparation.

**```asset*func*meta```** :&ensp;`Union[None, dict, list]` :   Metadata for the asset function.

**```**kwargs```** :   Keyword arguments for [Task](https://vectorbt.pro/pvt_ff8edc14/api/utils/execution/#vectorbtpro.utils.execution.Task "vectorbtpro.utils.execution.Task").

`Task` :   Callable task resolved from the provided definition.

Execute the asset pipeline on the provided data by applying all tasks sequentially.

!!! abstract This method should be overridden in a subclass.

**```d```** :&ensp;`Any` :   Data item to be processed.

`Any` :   Result of executing the pipeline on the data item.

Class representing a basic asset pipeline.

Creates a composite function by resolving and chaining individual asset tasks.

**```*args```** :   Positional arguments for [AssetPipeline.resolve*task](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/asset*pipelines/#vectorbtpro.knowledge.asset*pipelines.AssetPipeline.resolve*task "vectorbtpro.knowledge.asset*pipelines.BasicAssetPipeline.resolve_task").

**```**kwargs```** :   Keyword arguments for [AssetPipeline.resolve*task](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/asset*pipelines/#vectorbtpro.knowledge.asset*pipelines.AssetPipeline.resolve*task "vectorbtpro.knowledge.asset*pipelines.BasicAssetPipeline.resolve_task").

**Inherited members**

Add a task to the pipeline using the provided asset function and arguments.

**```func```** :&ensp;`AssetFuncLike` :   Asset function identifier, which may be a tuple, [Task](https://vectorbt.pro/pvt*ff8edc14/api/utils/execution/#vectorbtpro.utils.execution.Task "vectorbtpro.utils.execution.Task"), string, or subclass of [AssetFunc](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/base*asset*funcs/#vectorbtpro.knowledge.base*asset*funcs.AssetFunc "vectorbtpro.knowledge.base*asset*funcs.AssetFunc").

**```*args```** :   Positional arguments for [AssetPipeline.resolve*task](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/asset*pipelines/#vectorbtpro.knowledge.asset*pipelines.AssetPipeline.resolve*task "vectorbtpro.knowledge.asset*pipelines.BasicAssetPipeline.resolve_task").

**```**kwargs```** :   Keyword arguments for [AssetPipeline.resolve*task](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/asset*pipelines/#vectorbtpro.knowledge.asset*pipelines.AssetPipeline.resolve*task "vectorbtpro.knowledge.asset*pipelines.BasicAssetPipeline.resolve_task").

Compose multiple tasks into a single callable that applies them sequentially.

**```tasks```** :&ensp;`List[Task]` :   List of tasks to be composed.

`Callable` :   Callable that takes a data item and applies the tasks sequentially.

Tasks that have been added to the pipeline.

`List[Task]` :   List of tasks in the pipeline.

Class representing a complex asset pipeline.

This pipeline takes an expression string that may contain nested function calls and a context mapping. It resolves functions within the expression and evaluates the expression using [evaluate](https://vectorbt.pro/pvt*ff8edc14/api/utils/eval*/#vectorbtpro.utils.eval*.evaluate "vectorbtpro.utils.eval*.evaluate").

**```expression```** :&ensp;`str` :   Expression string to evaluate.

**```context```** :&ensp;`KwargsLike` :   Mapping of variables for expression evaluation.

**```prepare_once```** :&ensp;`bool` :   Flag indicating whether to prepare the function's arguments only once.

**```**resolve*task*kwargs```** :   Keyword arguments for task resolution.

**Inherited members**

Updated context mapping for the pipeline.

`Kwargs` :   Context mapping used for expression evaluation.

Processed expression string for the pipeline.

`str` :   Expression string after processing.

Resolve an expression and update its context.

Parses the expression string to extract function calls and their arguments, then removes the first positional argument from each function call. It also builds a new context by merging resolved functions with the existing context.

**```expression```** :&ensp;`str` :   Expression string to process.

**```context```** :&ensp;`KwargsLike` :   Mapping of context variables.

**```prepare```** :&ensp;`bool` :   Flag indicating whether to prepare the function's arguments before execution.

**```prepare_once```** :&ensp;`bool` :   Flag indicating whether to prepare the function's arguments only once.

**```**resolve*task*kwargs```** :   Keyword arguments for task resolution.

`Tuple[str, Kwargs]` :   Tuple containing the modified expression and the updated context.

Class representing an early return value for [BasicAssetPipeline](https://vectorbt.pro/pvt*ff8edc14/api/knowledge/asset*pipelines/#vectorbtpro.knowledge.asset*pipelines.BasicAssetPipeline "vectorbtpro.knowledge.asset*pipelines.BasicAssetPipeline").

**Inherited members**

**Examples:**

Example 1 (python):
```python
AssetPipeline()
```

Example 2 (python):
```python
AssetPipeline.resolve_task(
    func,
    *args,
    prepare=True,
    prepare_once=True,
    cond_kwargs=None,
    asset_func_meta=None,
    **kwargs
)
```

Example 3 (python):
```python
AssetPipeline.run(
    d
)
```

Example 4 (python):
```python
BasicAssetPipeline(
    *args,
    **kwargs
)
```

---

## mcp_server

**URL:** https://vectorbt.pro/pvt_ff8edc14/api/mcp_server.md

**Contents:**
- main <span class="dobjtype">function</span><a class="githublink" href="https://github.com/polakowo/vectorbt.pro/blob/6e18cf0aa37849cfc20848f40f1d26ecfdc771b4/vectorbtpro/mcp_server.py#L26-L55" target="_blank" title="Jump to source">:material-github:</a> { #vectorbtpro.mcp_server.main data-toc-label="main" }

Module providing the MCP server.

The module is meant to be executed as a script using the command:

**```argv```** :&ensp;`Optional[Sequence[str]]` :   Command-line arguments.

**Examples:**

Example 1 (bash):
```bash
python -m vectorbtpro.mcp_server
```

Example 2 (python):
```python
main(
    argv=None
)
```

---
