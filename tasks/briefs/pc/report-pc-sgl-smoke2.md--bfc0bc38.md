SGL-SMOKE2 report (task #454, PIN bfc0bc38, qwen-local/qwen3.8-27b-local, no file changes)

NOT done: none. Lane changed no file; report saved to /home/rocco/agent-factory/.lanes/pc-sgl-smoke2.md--bfc0bc38/report-draft.md.

1. PREMISE RE-RUN — all four measurements match the brief exactly:
   git rev-parse HEAD -> bfc0bc38c563799f3c70ffa6e7b4f8b1fd3e6593
   wc -l deploy/qwen.container deploy/sglang_start.py scripts/serving_ab/abwin2.sh -> 46 / 86 / 211, total 343
   grep -c 'gone()' scripts/serving_ab/abwin2.sh -> 2
   grep -n '^KEY_FILE_DEFAULT' deploy/sglang_start.py -> 22:KEY_FILE_DEFAULT = "/app/api_key.txt"
   No mismatch; continued per contract.

2. TOOL ROUND TRIPS (each one call, output pasted whole):
   - wc -l ... -> "   46 deploy/qwen.container /    86 deploy/sglang_start.py /   211 scripts/serving_ab/abwin2.sh /   343 total"
   - grep -c 'gone()' scripts/serving_ab/abwin2.sh -> "2"
   - git rev-parse HEAD -> "bfc0bc38c563799f3c70ffa6e7b4f8b1fd3e6593"

3. FILE READ — deploy/sglang_start.py:22 (via file tool) reads: KEY_FILE_DEFAULT = "/app/api_key.txt"
   Context for the count: gone() is defined at scripts/serving_ab/abwin2.sh:71 and appears in the comment at :18 (that is the 2 hits).

4. UNEXPECTED — None. No refused tool calls, no empty replies, no warnings about the model or the route.

DISCREPANCIES — None. report_lint (dispatcher's overlaid copy, worktree): "report_lint: 3 refs — OK 3, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)", rc=0, first round.

Evidence tiers: all items verified (ran and read in this session); no inferred or assumed values.

Retro: nothing to bake.
