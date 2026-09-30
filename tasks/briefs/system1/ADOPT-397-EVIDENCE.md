# ADOPT evaluation (task #397, D-116): gitleaks and titus as the scrubber's detector, the evidence of record

> **Coordinator note (2026-09-30 06:2xZ).** The gatherer's hand-back, saved verbatim below (a sandbox evidence-gatherer;
> harvest run s-20260930T062114Z-11e7f1: 515 assistant records, every one claude-opus-5-5, 0 refusal stops, 0 tool
> errors; hand-back sha256 prefix 34f18db6bfc9). It is evidence only; the reading below is the coordinator's.
> Screened before commit: `scripts/known_values_check.py` NO HIT; every planted value was made at run time and none is
> in the text (the one token-shaped string, at the Anthropic row, is a format description with no body).
>
> **The reading.**
> 1. Neither tool can replace the scrubber. On the PIN's own 98 values (part B2 (i)), the PIN hides 77 to 96 per view;
>    gitleaks alone covers 29 to 52 and titus 35 to 40. Neither has a rule for a bare `Bearer`, `Cookie:` and
>    `Set-Cookie:`, `pwd`, `passphrase`, the bridge link, an opaque run, or `*_PASS`.
> 2. Neither closes the blockers of rounds 1 to 4. Run over the PIN's output (D-115 option A's order, the "A1"
>    columns against "PIN hid", per view), gitleaks adds 1 to 3 of the 98 values, 1 to 4 of F1's 48 and 0 to 2 of
>    the 39 red values; titus adds 0 to 5 (the CLI 0 to 4), 0, and 0 to 4. Most red items are shapes neither tool has
>    a rule for.
> 3. gitleaks is safe to run as a LIBRARY: RE2, linear time, no network in a scan, no timeout on any of the 31
>    hostile families, about 2 to 9 ms per 10 KB text. Its CLI is not: it silently skips input that starts like a
>    binary file (MZ, %PDF, a Rich Text head) and missed a token that straddled a stdin chunk boundary; the library
>    found every one. Its generic rule drops a value that contains one of 1,446 stopwords ("token", "cookie", ...).
> 4. titus is not a fit. Its library and its server drop a match without a word when a regex times out (5 s), its
>    CLI writes found secrets in plaintext to a SQLite store in the working directory by default, and `scan` of a git
>    directory calls the GitHub API by default. Its rule count is 539 built-in (498 in the CLI default), not 487 (D-116
>    quoted its README).
> 5. The PIN's own F7 stays whatever is adopted: 26 s on a 60,000-character dash run (quadratic), in the live
>    exporter. Under option A the PIN runs first and whole, so only F7's one-rule fix removes it.
>
> So ADOPT fits only inside option A, as the second pass over the PIN's output: gitleaks' engine (the library, built
> from source at b58d3f1 and pinned) with its 222 maintained rules, and F1's new rules written as gitleaks rules, which
> RE2 keeps linear by construction. Open for the build lane: whether each F1 rule can be written without lookaround
> (RE2 has none; a rule that cannot falls back to a Python rule, still after the PIN), memory (not measured), and
> gitleaks' decoding (not probed). The owner picks (the ledger's TASK #397 HOME entry).

---

ADOPT EVALUATION LANE, task #397 (D-116): EVIDENCE REPORT
Written 2026-09-30 06:1xZ (last `date -u` read: 06:10:06Z). This report holds evidence only. It gives no verdict and no recommendation. Rows are marked SOLID or UNSURE. A gap is written as "unknown" or "not measured".

Paths: $S = /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/adopt397 (every lane write is under it). $TP = /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/thirdparty (the read-only clones). gitleaks file:line refers to $TP/gitleaks. titus file:line refers to $TP/titus.

======================================================================
0. PINS, INPUTS, VENUE
======================================================================
| item | value | mark |
|---|---|---|
| gitleaks | b58d3f102cf3a2c84cb7f923d05c25c9b1aed84b, dated 2026-07-22T09:50:33-07:00, MIT. Depth-1 clone (`rev-list --count` = 1). | SOLID |
| titus | 510c4076c81c17d73f254bdadaeb5286b3ec7dc3, dated 2026-09-27T14:26:42-05:00, Apache-2.0 with NOTICE. Depth-1 clone. | SOLID |
| Git dates of cited third-party files | Unknown. In a depth-1 clone, `git log` on every file returns only the pin commit. | UNSURE (gap) |
| PIN | /home/user/agent-factory/scripts/transcript_export.py, sha256 6ad316dccfca01474c7da0f716e4788407dd8e4c2699d2368e41ea96e5195f42, 383 lines, last commit cdbc1b8 2026-09-26T01:42:03Z. The scratch copies $S/pin/transcript_export.py and $S/pinroot/scripts/transcript_export.py match it (sha256 prefix 6ad316dccfca0147). | SOLID |
| Repo HEAD | 7b36aa6 at lane start and 7a195de at 06:10Z (other lanes committed in between). The PIN is unchanged. This lane wrote nothing in the tree. The two transcript_export .pyc files in scripts/__pycache__ are dated 2026-09-28 and 2026-09-29, before this lane. | SOLID |
| Red files | r2: $S/red/vscrub2r1r2_red.py, sha256 8498307a91f35f8c, the same as the blob at 2d46ba8 (2026-09-28T20:51:47Z). r3: sha256 10fac0733a8cbfb0, the same as the HEAD blob (9dabbef, 2026-09-29T10:57:41Z). r4: git blob d15d9e70220f1e79e04df93c600e49e35d8430de, the same as `index 0000000..d15d9e7` at tasks/briefs/system1/SCRUB2-R1-R5-lane.patch:324 (30f002f, 2026-09-29T20:30:15Z). The patch was never applied. On the scratch PIN, `python3 -m pytest -q -p no:cacheprovider tests/vscrub2r1r2_red.py tests/vscrub2r1r3_red.py tests/vscrub2r1r4_red.py` gave `39 passed in 0.06s`. | SOLID |
| Venue | Sandbox with 4 CPUs, shared with live lanes (the K2 round-4 builder and the LS-B12 builder). 1-minute load was 1.5 to 6.3 during the measurements; each timing row carries its own load. | SOLID |
| No-network wrapper | $S/bin/netless: `exec env -i PATH=/usr/local/bin:/usr/bin:/bin HOME=$S/home LANG=C.UTF-8 unshare --net "$@"`. Every tool process ran under it, with cwd set to a scratch run dir. The first wrapper used `env -u` and still passed credential-named variables, so it was replaced by `env -i` before any scan. | SOLID |
| Planted values | All were made at run time with the `secrets` module or `SystemRandom`. No secret file or transcript was read, and the PC bridge was not used. | SOLID |

======================================================================
PART A: CODE READ AT THE PINS
======================================================================
A1. Scan path for text, finding contents, redaction
| # | item | gitleaks b58d3f1 | titus 510c407 | mark |
|---|---|---|---|---|
| A1.1 | CLI text entry | `gitleaks stdin` (cmd/stdin.go:23-54). It loads config with initConfig(".") (:28), which reads the cwd. Config precedence: --config, then env GITLEAKS_CONFIG, then env GITLEAKS_CONFIG_TOML, then <target>/.gitleaks.toml, then the default (cmd/root.go:35-41). It reads .gitleaksignore from -i, default "." (root.go:90, 302-317). The scan call is DetectSource(sources.File{Content: os.Stdin}) at :39-45. | No stdin subcommand. `titus scan <file\|dir>` goes through the filesystem enumerator (cmd/titus/scan.go:151-453; pkg/enum/filesystem.go:132-179). `titus serve` is an NDJSON server over stdin/stdout (cmd/titus/serve.go:16-75; pkg/serve/server.go:47-176). It loads rules once; its default ruleset is "all" with include-noisy on (serve.go:40-41), which is 539 rules. | SOLID |
| A1.2 | Library entry | detect.NewDetectorDefaultConfig (detect/detect.go:135-151), then DetectString (:201-205), then Detect/DetectContext (:270, :276). DetectString does not call AddFinding; the only call site is DetectSource (:250). So findings do not pile up across calls. | titus.NewScanner (titus.go:286-355), then ScanString/ScanBytes (:368-388), which call matcher.Match only. The matcher chain is portable, then filtering, then dedup (pkg/matcher/matcher_default.go:10-23). | SOLID |
| A1.3 | How input is cut | The CLI reads in chunks: a 100,000-byte buffer (sources/file.go:21, :183), then a peek of up to 25,000 more bytes looking for "\n\n" (sources/common.go:16, :56-125; the comment at :16 says "10kb" while the value is 25,000). Chunks are scanned separately. The library scans the whole string. | The whole blob is read with os.ReadFile (filesystem.go:139). A blob of 10,000 bytes or more runs rules on GOMAXPROCS workers (regexp_portable.go:18, :136-138). | SOLID |
| A1.4 | Silent CLI input skips | While no newline has been counted in earlier chunks, each chunk is file-typed. A MIME type of "application" skips the REST of the input, with a DBG-level log only (sources/file.go:192-207). Measured in B2-edge: text starting with "MZ", "%PDF-1.4" or "{\rtf1" gives 0 findings and rc 0, for both stdin and dir. A one-line text with "MZ" at byte 125,000 skips the rest via `dir`. | A NUL byte in the first 8 KB makes the file count as binary, and it is skipped (filesystem.go:145-171, 198-205). Measured: "Scanned 0 B from 0 blobs", rc 0; ScanString still finds the value. Files over the 10 MiB max-file-size are skipped (scan.go:106; filesystem.go:64). There are 30 built-in ignore globs (pkg/enum/ignore/ignore.conf), for example **/*.min.js, package-lock.json, go.sum, /proc/**. | SOLID |
| A1.5 | Finding contents | report.Finding (report/finding.go:14-55) holds RuleID, Description, StartLine, EndLine, StartColumn, EndColumn, Line (json "-"), Match, Secret, File, Commit, Entropy, Tags, Fingerprint and more. Positions are line/column, not byte offsets. Match and Secret are plaintext. | types.Match (pkg/types/match.go:10-27) holds BlobID, StructuralID, FindingID, RuleID, RuleName, Location (byte offsets plus line/col), Groups, NamedGroups and Snippet{Before, Matching, After} (snippet.go:4-8). In JSON output the byte fields are base64 plaintext; B2 decoded them. The context is 3 lines in the CLI (scan.go:107) and 2 in the library (titus.go:289). | SOLID |
| A1.6 | Redaction | `--redact[=pct]`: the default is 0 and the bare flag means 100 (root.go:86-87, 288-289). Finding.Redact replaces Secret inside Line and Match (finding.go:77-89). With `--log-level debug`, AddFinding's logger carries finding.Secret (detect.go:711-720; DetectSource path only). | No redaction option in scan or the library. A grep for "redact" finds only pkg/validator/internal/vcrtest. | SOLID |
| A1.7 | Exit code | Findings give exit 1 by default (`--exit-code`, root.go:76; stdin.go:37, :53). In B2, rc was 1 on 192 of 1,142 texts and 0 on 950. | 0 with findings. Also 0 after timeouts and drops (E3, E4 and the sweep below). | SOLID |
| A1.8 | Rules that drop a match | generic-api-key: entropy 3.5 (gitleaks.toml:641; the check `entropy <= r.Entropy` is at detect.go:547). 1,446 stopwords (gitleaks.toml:664-2111) are matched as lowercase substrings of the Secret (config/allowlist.go:161-179; detect.go:846). Measured on fake `password=<v>`: v containing "about" (toml:669), "cookie" (:920), "basic" (:769) or "token" (:1941) gave 0 findings; the control with "abcde" gave 1. An inline "gitleaks:allow" on the line suppresses the finding (detect.go:28, :513). Measured: 1 finding became 0 for both stdin and DetectString. | Per-rule min_entropy through the post-filter (pkg/matcher/postfilter.go:25 findSecretCapture, :67 entropy check, :126-142 filterMatches). Example: kingfisher.curl.1 has min_entropy 3.0 (rules/curl.yml:7). | SOLID |

A2. Network paths with default flags
| # | path | gitleaks | titus | mark |
|---|---|---|---|---|
| A2.1 | Text scan, default flags | stdin and dir have no network code. The only net/http import is cmd/diagnostics.go (pprof on localhost:6060 only when --diagnostics=http is set, :142). The config extend-URL is a stub (config/config.go:416-418). strace of network and exec syscalls for `gitleaks stdin` under netless showed 0 socket, 0 connect and 1 execve (itself). $S/runs/strace/gl_stdin.trace | `scan` defaults to --accessibility "auto" (scan.go:124-126, 255-258). That runs `git -C <dir> config --get remote.origin.url` (pkg/accessibility/accessibility.go:143). If the remote is GitHub, GitLab or Bitbucket, it makes an HTTPS API call (accessibility.go:155/166, 225, 264), with tokens from env GITHUB_TOKEN, GITLAB_TOKEN or BITBUCKET_TOKEN (:87, :104, :121; scan.go:257). strace, `titus scan <file>`: 0 socket, 0 connect, and 1 execve of /usr/bin/git. strace, `titus scan <dir whose .git origin is https://github.com/example-org/example-repo.git>`: 12 socket and 12 connect calls to 8.8.8.8:53 and 8.8.4.4:53 (ENETUNREACH under netless), stderr "[info] could not determine repo accessibility via GitHub API (... lookup api.github.com ...); assuming private", rc 0. $S/runs/strace/ti_ghdir.trace | SOLID |
| A2.2 | Validation | None. | `--validate` defaults to false (scan.go:109). The library needs WithValidation to turn it on (titus.go:177-183, :318). serve attaches a validator engine at start (serve.go:73, 77-96) but runs it only on a "validate" request (server.go:107-108, 178-228). | SOLID |
| A2.3 | Scoring | None. | Static scoring runs locally in the CLI. Dynamic (network) modifiers are skipped unless ScopeEnabled (pkg/scoring/engine.go:111-114; scorer.go:39-51), and `--score-scope` defaults to false (scan.go:127-128). The library needs WithScoring (titus.go:194-195, :324). | SOLID |
| A2.4 | Other network features | git and detect modes exec git (sources/git.go:91, 93, 139, 141, 209, 485); not run. | Opt-in by target or command: enum, analyze, --git, --docker, the S3/Asana/GDrive targets, and serve's scan_git. Not run, by rule. | SOLID (code) |

A3. Regex engines and limits
| # | item | gitleaks | titus | mark |
|---|---|---|---|---|
| A3.1 | Engine | Without tags: Go stdlib regexp, RE2 semantics with no backtracking (regexp/stdlib_regex.go:1-11). With tag gore2regex: github.com/wasilibs/go-re2 v1.9.0 on wazero v1.9.0 (regexp/wasilibs_regex.go:1-11). Release builds set that tag (.goreleaser.yml:18-19). Both variants were built here. | A pure-Go build (no tags, CGO_ENABLED=0) uses github.com/dlclark/regexp2 v1.11.5, a backtracking engine (matcher_default.go:1-23). It compiles with RE2\|Multiline first and falls back to regexp2.None, for example for (?x) (regexp_portable.go:108-118). The default `make build` sets CGO_ENABLED=1 and tag vectorscan (Makefile:10-17, 52-54), giving a Hyperscan plus regexp2-fallback matcher (matcher_vectorscan.go:1; vectorscan.go:15-16, 56-58). That build was not made. | SOLID |
| A3.2 | Per-match limit | None. `--timeout` (root.go:93) limits the whole command and defaults to 0. | 5 s per match (regexp_portable.go:80, :91-92; also regexp.go:39 and vectorscan.go:152). The comments at regexp_portable.go:86 and vectorscan.go:61 say "500ms". Measured: timeouts fire at 5.0 s (E2 below, scan_s 5.013). | SOLID |
| A3.3 | On timeout | n/a | Warning text: "[warn] rule <id> regex timeout on blob <sha1> (skipping rule for this blob)" (regexp_portable.go:165, 194, 261, 283). Matches found before the timeout are kept (:186-203, :267-289; measured in E2b). | SOLID |
| A3.4 | Retry | n/a | The (content, blob, rule) triple is queued. DrainTimedOut replays it on one thread with a timeout of 10x, capped at 30 s (regexp_portable.go:388-500, :421-424). The CLI calls it after the parallel pass (scan.go:434, :461-462). The library never calls it: titus.go has no DrainTimedOut call, and ScanBytes is at :373-388. serve never calls it either (pkg/scanner/core.go:98-133). | SOLID |
| A3.5 | Blacklist | n/a | Per rule, per matcher instance, the 3rd timeout prints "[warn] rule <id> disabled after 3 timeouts (likely catastrophic backtracking — skipping remaining blobs)" and no retry follows. Later timeouts get no retry and no extra line (regexp_portable.go:21, 349-385). The count gates only the retry queue: the match loops (:151-203, :250-291) never read the blacklist. Measured in E4: the 4th blob still ran the rule for 5 s and printed a timeout line. | SOLID |
| A3.6 | Queue cap | n/a | 500 jobs. Past the cap, jobs are dropped and the drain prints "[warn] retry queue cap (500) reached; N (blob, rule) pairs were not retried" (regexp_portable.go:22, 377-384, 405-409). This was not triggered. | SOLID code; not measured |
| A3.7 | Retry-pass dedup | n/a | The DrainTimedOut output for all blobs goes through CrossRuleDeduplicator.Deduplicate (dedup_matcher.go:40-46). Its comment says it takes "all matches from a single blob" (crossrule.go:38-40). It unions matches that share any capture-group value (crossrule.go:85-99), and the key holds no blob id. Measured below: 2 files with the same username recovered 1 match of 2; with distinct usernames, 2 of 2. | SOLID |
| A3.8 | What a drop reports | n/a | CLI: warnings on stderr, exit 0, and the stats line "N/N new matches" (E3: "0/0 new matches"). Library: NewScanner wires no WarnFunc (titus.go:307-311), so there is no warning, err is nil and the match is missing. serve: a warning on stderr, the response says success:true, and the match is missing. | SOLID (measured) |
| A3.9 | Other limits | Chunking and file-type skip (A1.3, A1.4). --max-target-megabytes defaults to 0 (root.go:84). --max-decode-depth is 5 in the CLI (root.go:91, :255). The library NewDetector leaves MaxDecodeDepth at 0 (detect.go:115-133); the B2 harness set it to 5. | max-file-size 10 MiB, NUL skip and ignore globs (A1.4); workers default to NumCPU (scan.go:118-121). | SOLID |

A4. Build needs
| # | item | gitleaks | titus | mark |
|---|---|---|---|---|
| A4.1 | Go line | go.mod:3 `go 1.24.11`. The host has go1.24.7, so the build downloaded go1.24.11 ($S/logs/build_gitleaks.log:1-2). | go.mod:3 `go 1.27.0`. The build downloaded go1.27.0 ($S/logs/build_titus.log:1-2). | SOLID |
| A4.2 | cgo | The tree has no `import "C"` (grep). Built here with CGO_ENABLED=1, the default (`go version -m`). | The pure-Go path is CGO_ENABLED=0 with no tags; `make build-pure` is at Makefile:141-144. The default `make build` needs cgo and libhs. Its check-vectorscan target installs packages itself through brew, apt-get or `sudo dnf install -y vectorscan-devel` / `pkgconf-pkg-config` (Makefile:57-125). | SOLID |
| A4.3 | Build-time actions | `go build` runs none. config/gitleaks.toml is committed and embedded (config/config.go:19-20). It is regenerated only by a make target (Makefile:36-37; cmd/generate/config/main.go:18 go:generate). | `go build` runs none; the tree has no go:generate. Rules are embedded (pkg/rule/embed.go:7). | SOLID |
| A4.4 | Modules | 60 deps. The gore2regex build has 63 (+ go-re2 v1.9.0, wazero v1.9.0, wazero-helpers). | 135 deps for the CLI (includes modernc.org/sqlite v1.45.0). 44 for the library harness. regexp2 is v1.11.5. | SOLID |

A5. Rules: counts, format, and ids for the listed shapes
Counts. gitleaks: config/gitleaks.toml has 3,209 lines and 222 [[rules]] entries. Each rule has id, regex, entropy, keywords, allowlists and stopwords. titus: 539 built-in rules in 316 YAML files (pkg/rule/rules/*.yml). Rulesets: default lists 507 ids, np.assets 18, np.hashes 6. 9 rules are noisy. By harness `-count`, the CLI default (default ruleset minus noisy) loads 498 rules; NewScanner() and serve load all 539.
Claims: titus README.md:9 and :30 say "487 detection rules". D-116 (docs/08_DECISION_LOG.md:127) says "487 rules". Measured: 539, 507 and 498 as above. Recorded, not resolved.
| shape | gitleaks rule (gitleaks.toml line) | titus rule (file:line) | mark |
|---|---|---|---|
| Cookie / Set-Cookie | No generic rule; only gitlab-session-cookie (2275). "cookie" is a generic-api-key stopword (920). | No rule matches "cookie" (grep -il over rules/*.yml finds none). | SOLID |
| password / passwd / pwd | generic-api-key (638). Its keywords include passwd and password (643-654). The regex name part is `passw(?:or)?d`, so there is no "pwd". | np.generic.5, .6, .11 and .12 "Generic Password" (generic.yml:175, 262, 446, 474); np.generic.3 and .4 username+password (:60, :122); np.generic.19 JSON (:701). | SOLID |
| credentials | generic-api-key (keyword "credential"). | kingfisher.credentials.1 (credentials.yml:3; URL userinfo); np.generic.13 and .14 (generic.yml:497, :525). | SOLID |
| Authorization Bearer / Basic / Token / Negotiate | Only inside curl: curl-auth-header (359; regex :361 handles Basic, Bearer and (Api-)Token), and curl-auth-user (366). No rule for a bare `Authorization:` header. "basic" is a stopword (769). No Negotiate rule. | np.http.1 Basic (http.yml:5) and np.http.2 Bearer (http.yml:25), matching `Authorization (?: :\s+ \| \s*.{1, 5}\s*) Basic\|Bearer \s+`. No Token or Negotiate rule (grep). | SOLID |
| PEM | private-key (2785; needs 64+ chars and a `KEY-----` end). | np.pem.1 (pem.yml:6), np.pem.2 (:73), kingfisher.privkey.1 and .2 (privkey.yml:3, :48). | SOLID |
| generic | generic-api-key (638). | np.generic.1 to .19 (generic.yml:12 to :701). | SOLID |
| sk- (OpenAI) | openai-api-key (2704). | np.openai.1 (openai.yml:4). | SOLID |
| sk-ant- | anthropic-api-key (150), anthropic-admin-api-key (144). | np.anthropic.1 (anthropic.yml:4). | SOLID |
| ghp_ | github-pat (2159); gho_ github-oauth (2152); ghs_ github-app-token (2131); ghr_ github-refresh-token (2170). | np.github.1 (github.yml:4). The default ruleset lists np.github.1 to .4 and .6 to .8 (default.yml:94-100). | SOLID |
| github_pat_ | github-fine-grained-pat (2145). | np.github.7 (github.yml:161). | SOLID |
| AWS | aws-access-token (206). In B2 the secret key was found by generic-api-key. | np.aws.1 key id (aws.yml:4) is NOT in the default ruleset (default.yml:26-29 lists aws.2, .4, .5 and .6), so the CLI default misses it and NewScanner finds it. np.aws.2 secret (aws.yml:42); np.aws.6 (:413). | SOLID |
| curl -u / -H | curl-auth-user (366), curl-auth-header (359). | kingfisher.curl.1 and .2 (curl.yml:3, :18). The pattern `\bcurl\s.*(?:-u\|--user)...` backtracks (B3). | SOLID |

A6. Side effects
| # | gitleaks | titus | mark |
|---|---|---|---|
| A6.1 | Reads ./.gitleaks.toml or the env config and .gitleaksignore (A1.1). Writes nothing unless -r is given; -r - goes to stdout. `--diagnostics` writes profiles to cwd or serves pprof on localhost:6060 (diagnostics.go:142). Execs git only in git and detect modes. | Writes titus.ds/ in the cwd by default (--output default "titus.ds", scan.go:102). Measured in $S/runs/smoke/titus.ds: datastore.db (SQLite; tables schema_version, blobs, rules, matches, sqlite_sequence, findings, provenance, annotations), .gitignore, clones/ and scratch/. The file was 192,512 bytes after two tiny scans. All 6 fake tokens from the inputs were present as plaintext bytes. The second scan's JSON output held 5 matches: the first run's 4 plus 1 new. So results accumulate across runs. --store-blobs defaults to false (scan.go:111). | SOLID |
| A6.2 | No exec on the stdin path (strace). | Execs `git -C <dir> config --get remote.origin.url` on `scan` (strace: execve /usr/bin/git). Prints a banner to stderr unless -q (banner.go:30-42). serve prints the banner even with no flag. Reads env GITHUB_TOKEN (scan.go:257). | SOLID |

======================================================================
PART B: BUILT AND RUN
======================================================================
B1. Build notes
- Sources: `git archive` of each pin into $S/src/gitleaks and $S/src/titus. There is no .git, so binaries report "(devel)". Build env: GOPATH=$S/gopath, GOCACHE=$S/gocache, GOTMPDIR=$S/gotmp, HOME=$S/home. Modules and toolchains were downloaded at build time through the sandbox proxy. No vectorscan package was installed.
- Build settings, from `go version -m` buildinfo (SOLID): plain `go build`, with -buildmode=exe and -compiler=gc, no -ldflags and no -trimpath. gitleaks: go1.24.11, CGO_ENABLED=1, and -tags=gore2regex for the re2 variants. titus: go1.27.0, CGO_ENABLED=0, no tags, which gives the portable regexp2 matcher.
- Wall times from the logs: gitleaks 29.1 s real (toolchain plus modules), gitleaks-re2 6.3 s, titus 1m33.2 s.
- Binaries in $S/bin: gitleaks 23,557,438 B; gitleaks-re2 30,812,381; titus 77,995,935; gitleaks-lib 12,848,157; gitleaks-re2-lib 19,745,951; titus-lib 20,271,764.
- Harnesses (scratch only): $S/src/gitleaks/cmd/adopt397lib/main.go runs NewDetectorDefaultConfig, sets MaxDecodeDepth=5 and calls DetectString per JSONL line. $S/src/titus/cmd/adopt397lib/main.go has two modes. `-mode lib -rules all` is NewScanner() with no options, then ScanString. `-mode instr -rules cli` is matcher.New with a WarnFunc that records, using the CLI's default ruleset minus noisy, then Match and DrainTimedOut per text.

B2. Inputs through each tool (all under netless)
Commands:
1. `python3 $S/drv/b2_gen.py $S/runs/b2`. This built 165 items (class i 78, ii 48, iii 39) and 1,142 unique texts: the six views of each item plus the PIN's output in each view.
2. `python3 $S/drv/b2_run.py $S/runs/b2 gl_cli ti_cli gl_lib gl_re2_lib ti_lib ti_instr`. For each text, one `gitleaks stdin --no-banner --log-level error -r - -f json` process (1,142 processes). One `titus scan $S/runs/b2/files --output :memory: --format json -q` process over 1,142 files; its stderr, pasted: "Scanned 80270 B from 1142 blobs in 0 second (375669 B/s); 152/152 new matches". Plus the harnesses gitleaks-lib, gitleaks-re2-lib, `titus-lib -mode lib -rules all` and `titus-lib -mode instr -rules cli`.
3. `python3 $S/drv/b2_eval.py $S/runs/b2` and `python3 $S/drv/b2_tables.py $S/runs/b2`.
Outputs: $S/runs/b2/{items.json, texts.jsonl, res_*.jsonl, eval_rows.json, eval_noise.json, table_i.md, table_ii.md, table_iii.md}.

Definitions:
- Views follow the round-4 verifier's set (scratchpad/vscrub2r4/probes/lib.py:61-76). dig = scrub(t); txt = settle(t); call = settle(canon({"command":t})); call2 = settle(canon({"command":"echo "+json.dumps(json.dumps({"x":t}))})); pdig = scrub(json.dumps({"x":t})); ptxt = settle(json.dumps({"x":t})). settle is scrub_payload run to a fixed point, at most 4 passes.
- hidden(v,s) is true when no 8-character window of v, or of v JSON-escaped 1 to 3 times, occurs in s.
- Cover codes: F means the tool's secret string covers v (gitleaks Finding.Secret; titus: the capture chosen the way findSecretCapture chooses it, postfilter.go:25). m means only the whole match covers v. "-" means no finding touches v.
- T1/T2 simulate replacing the tool's secret or match strings in the original text, then test hidden. A1 is the same test run on the PIN's output, which is the D-115 option-A order. Neither tool rewrites text.
- "gl@PIN" and "ti@PIN" mean the tool ran over the PIN's output.
- Code strings are per view, in this order: dig, txt, call, call2, pdig, ptxt.

Cross-checks over all 1,142 texts (SOLID):
- gl_cli vs gl_lib: 0 texts differ. gl_lib vs gl_re2_lib: 0 differ. ti_cli vs ti_instr: 0 differ.
- ti_lib vs ti_cli: 4 texts differ, all np.aws.1 (only NewScanner loads it).
- Total findings: gitleaks 200, ti-cli 152, ti-instr 152, ti-lib 156. ti-instr retried 0 and warned 0.
- Findings on the PIN's outputs that touch no tracked value (eval_noise.json): gitleaks 10. Five are curl-auth-user matching the PIN's own placeholder (`curl --user 'svc:<redacted>'`). Five are generic-api-key on the untracked first fake of r3 N2R items (`credentials = sid=<fake c>`). titus had 0.

(i) The PIN's shapes. SECRET_PATTERNS rows are "S", PAYLOAD_PATTERNS rows are "P", and "ctl" rows are AWS controls. 98 values. Each PEM row has 3 body-line values; one is shown. ti-lib equals ti-cli except row 59 (np.aws.1, FFFFFF).
| # | group: shape | PIN | gl | gl rule(s) | ti-cli | ti rule(s) | gl@PIN | ti@PIN |
|---|---|---|---|---|---|---|---|---|
| 1 | S private-key block: `PEM RSA` | YYYYYY | FFFFFF | private-key | FFFFFF | kingfisher.privkey.2,np.pem.1 | ------ | ------ |
| 2 | S private-key block: `PEM PKCS8` | YYYYYY | FFFFFF | private-key | FFFFFF | kingfisher.privkey.2,np.pem.1 | ------ | ------ |
| 3 | S private-key block: `PEM EC` | YYYYYY | FFFFFF | private-key | FFFFFF | kingfisher.privkey.2,np.pem.1 | ------ | ------ |
| 4 | S private-key block: `PEM ENCRYPTED` | YYYYYY | FFFFFF | private-key | FFFFFF | kingfisher.privkey.2,np.pem.1 | ------ | ------ |
| 5 | S private-key block: `OpenSSH` | YYYYYY | FFFFFF | private-key | FFFFFF | kingfisher.privkey.2,np.pem.1 | ------ | ------ |
| 6 | S private-key block: `PGP private` | YYYYYY | FFFFFF | private-key | FFF-FF | np.pem.1 | ------ | ------ |
| 7 | S private-key block: `PGP 2.x secret` | YYYYYY | ------ | - | ------ | - | ------ | ------ |
| 8 | S private-key block: `PEM RSA, no END (cut at source)` | YYYYYY | ------ | - | ------ | - | ------ | ------ |
| 9 | S private-key block: `malformed: 4 dashes + spaces (lenient rule)` | YYYYYY | ------ | - | ------ | - | ------ | ------ |
| 10 | S private-key block: `malformed: 3 dashes (lenient rule)` | YYYYYY | ------ | - | ------ | - | ------ | ------ |
| 11 | S credential assignment: `token=<v>` | YYYYYY | FFF-FF | generic-api-key | ------ | - | ------ | ------ |
| 12 | S credential assignment: `TOKEN: <v>` | YYYYYY | FFF-FF | generic-api-key | ------ | - | ------ | ------ |
| 13 | S credential assignment: `password=<v>` | YYYYYY | FFF-FF | generic-api-key | ------ | - | ------ | ------ |
| 14 | S credential assignment: `password: "<v>"` | YYYYNY | FF---- | generic-api-key | FF---- | np.generic.5 | ------ | ------ |
| 15 | S credential assignment: `passwd=<v>` | YYYYYY | FFF-FF | generic-api-key | ------ | - | ------ | ------ |
| 16 | S credential assignment: `passphrase='<v>'` | YYYYYY | ------ | - | ------ | - | ------ | ------ |
| 17 | S credential assignment: `secret=<v>` | YYYYYY | FFF-FF | generic-api-key | ------ | - | ------ | ------ |
| 18 | S credential assignment: `client_secret = <v>` | YYYYYY | FFF-FF | generic-api-key | FFFFFF | np.google.3 | ------ | ------ |
| 19 | S credential assignment: `api_key=<v>` | YYYYYY | FFF-FF | generic-api-key | ------ | - | ------ | ------ |
| 20 | S credential assignment: `apiKey: <v>` | YYYYYY | FFF-FF | generic-api-key | ------ | - | ------ | ------ |
| 21 | S credential assignment: `api-key=<v>` | YYYYYY | FFF-FF | generic-api-key | ------ | - | ------ | ------ |
| 22 | S credential assignment: `STRIPE_KEY=<v>` | YYYYYY | FFF-FF | generic-api-key | ------ | - | ------ | ------ |
| 23 | S credential assignment: `"api_key": "<v>"` | YYYYNY | FF---- | generic-api-key | ------ | - | ------ | ------ |
| 24 | S credential assignment: `AGENT_TOKEN=<v>` | YYYYYY | FFF-FF | generic-api-key | ------ | - | ------ | ------ |
| 25 | S credential assignment: `PC_BRIDGE_TOKEN=<v>` | YYYYYY | FFF-FF | generic-api-key | ------ | - | ------ | ------ |
| 26 | S credential assignment: `X-Agent-Token: <v>` | YYYYYY | FFF-FF | generic-api-key | ------ | - | ------ | ------ |
| 27 | S credential assignment: `Authorization: <v>` | YYYYYY | ------ | - | ------ | - | ------ | ------ |
| 28 | S Bearer: `Bearer <v>` | YYYYYY | ------ | - | ------ | - | ------ | ------ |
| 29 | S Bearer: `Authorization: Bearer <v>` | YYYYYY | ------ | - | FFFFFF | np.http.2 | ------ | ------ |
| 30 | S Bearer: `curl -H 'Authorization: Bearer <v>' https://api.example.com` | YYYYYY | FFFFFF | curl-auth-header | FFFFFF | np.http.2 | ------ | ------ |
| 31 | S Cookie: `Cookie: sid=<v>; theme=dark` | YYYYYY | ------ | - | ------ | - | ------ | ------ |
| 32 | S Cookie: `Set-Cookie: session=<v>; Path=/; HttpOnly` | YYYYYY | ------ | - | ------ | - | ------ | ------ |
| 33 | S Cookie: `cookie: a=b; token=<v>` | YYYYYY | FFF-FF | generic-api-key | ------ | - | ------ | ------ |
| 34 | S Authorization + scheme: `Basic <v>` | YYYYYY | ------ | - | FFFFFF | np.http.1 | ------ | ------ |
| 35 | S Authorization + scheme: `Token <v>` | YYYYYY | ------ | - | ------ | - | ------ | ------ |
| 36 | S Authorization + scheme: `Digest <v>` | YYYYYY | ------ | - | ------ | - | ------ | ------ |
| 37 | S Authorization + scheme: `Negotiate <v>` | NNNNNN | ------ | - | ------ | - | ------ | ------ |
| 38 | S Authorization + scheme: `NTLM <v>` | YYYYYY | ------ | - | ------ | - | ------ | ------ |
| 39 | S Authorization + scheme: `ApiKey <v>` | YYYYYY | ------ | - | ------ | - | ------ | ------ |
| 40 | S Authorization + scheme: `SSWS <v>` | YYYYYY | ------ | - | ------ | - | ------ | ------ |
| 41 | S pwd: `pwd=<v>` | YYYYYY | ------ | - | ------ | - | ------ | ------ |
| 42 | S pwd: `PWD: <v>` | YYYYYY | ------ | - | ------ | - | ------ | ------ |
| 43 | S pwd: `--pwd=<v>` | YYYYYY | ------ | - | ------ | - | ------ | ------ |
| 44 | S credentials: `credentials=<v>` | YYYYYY | FFF-FF | generic-api-key | ------ | - | ------ | ------ |
| 45 | S credentials: `"credentials": "<v>"` | YYNNNN | FF---- | generic-api-key | ------ | - | ------ | ------ |
| 46 | S sk-: `sk- + 24 hex (no provider marker)` | YYYYYY | ------ | - | ------ | - | ------ | ------ |
| 47 | S sk-: `OpenAI legacy sk- + 20 + T3BlbkFJ + 20` | YYYYYY | FFF-FF | openai-api-key | FFFFFF | np.openai.1 | ------ | ------ |
| 48 | S sk-: `OpenAI sk-proj- 74 + T3BlbkFJ + 74` | YYYYYY | FFF-FF | openai-api-key | FFFFFF | np.openai.1 | ------ | ------ |
| 49 | S sk-: `Anthropic sk-ant-api03- 93 + AA` | YYYYYY | FFF-FF | anthropic-api-key | FFFFFF | np.anthropic.1,np.generic.2 | ------ | ------ |
| 50 | S gh: `ghp_ + 36` | YYYYYY | FFFFFF | github-pat | FFFFFF | np.github.1 | ------ | ------ |
| 51 | S gh: `gho_ + 36` | YYYYYY | FFFFFF | github-oauth | FFFFFF | np.github.2 | ------ | ------ |
| 52 | S gh: `ghs_ + 36` | YYYYYY | FFFFFF | github-app-token | FFFFFF | np.github.3 | ------ | ------ |
| 53 | S gh: `ghr_ + 36` | YYYYYY | FFFFFF | github-refresh-token | ------ | - | ------ | ------ |
| 54 | S gh: `github_pat_ + 82` | YYYYYY | FFFFFF | github-fine-grained-pat | FFFFFF | np.github.7 | ------ | ------ |
| 55 | S AIza: `AIza + 35` | YYYYYY | FFF-FF | gcp-api-key | FFFFFF | np.google.8 | ------ | ------ |
| 56 | S xox: `xoxb-` | YYYYYY | FFFFFF | slack-bot-token | FFFFFF | np.slack.2 | ------ | ------ |
| 57 | S bridge link: `https://<name>.trycloudflare.com/?t=<v>` | YYYYYY | ------ | - | ------ | - | ------ | ------ |
| 58 | S opaque run: `48 url-safe characters` | YYYYYY | ------ | - | ------ | - | ------ | ------ |
| 59 | ctl AWS: `aws_access_key_id = AKIA + 16` | NNNNNN | FFFFFF | aws-access-token | ------ | - | FFFFFF | ------ |
| 60 | ctl AWS: `aws_secret_access_key = 40 base64` | YYYYYY | FFF-FF | generic-api-key | FFFFFF | np.aws.2 | ------ | ------ |
| 61 | P bridge host no http(s): `wss://<v>.trycloudflare.com` | NYYYNY | ------ | - | ------ | - | ------ | ------ |
| 62 | P Bearer tail: `Bearer <8+>~<v>` | NYYYNY | ------ | - | ------ | - | ------ | ------ |
| 63 | P Basic behind escaped quotes: `{\"Authorization\": \"Basic <v>\"}` | NYYYNY | ------ | - | ------ | - | ------ | ------ |
| 64 | P R1 escaped-quote: `password=\"<v>\"` | NYYNNY | ------ | - | ------ | - | ------ | ------ |
| 65 | P R1 escaped-quote: `DB_PASS=\"<v>\"` | NYYYNY | ------ | - | ------ | - | ------ | ------ |
| 66 | P R1 escaped-quote: `api_key=\\\"<v>\\\"` | NYYNNY | ------ | - | ------ | - | ------ | ------ |
| 67 | P URL userinfo: `https://admin:<v>@db.example.com/x` | NYYYNY | ------ | - | FFFFFF | kingfisher.credentials.1,kingfisher.uri.1 | ------ | F---F- |
| 68 | P URL userinfo: `postgres://app:<v>@10.0.0.5:5432/db` | NYYYNY | ------ | - | FFFFFF | np.postgres.1 | ------ | F---F- |
| 69 | P URL userinfo: `mysql://root:<v>@h.example/x` | NYYYNY | ------ | - | ------ | - | ------ | ------ |
| 70 | P bearer any case: `authorization: bearer <v>` | YYYYYY | ------ | - | FFFFFF | np.http.2 | ------ | ------ |
| 71 | P bearer any case: `curl -H 'authorization: bearer <v>' https://x.example` | YYYYYY | FFFFFF | curl-auth-header | FFFFFF | np.http.2 | ------ | ------ |
| 72 | P bearer any case: `the bearer <v> works` | NYYYNY | ------ | - | ------ | - | ------ | ------ |
| 73 | P curl -u: `curl -u admin:<v> https://api.example.com` | NYYYNY | FFFFFF | curl-auth-user | FFFFFF | kingfisher.curl.1 | F---F- | F---F- |
| 74 | P curl -u: `curl --user 'svc:<v>' https://x.example` | NYYYNY | FFFFFF | curl-auth-user | FFFFFF | kingfisher.curl.1 | F---F- | F---F- |
| 75 | P *_PASS: `DB_PASS=<v>` | NYYYNY | ------ | - | ------ | - | ------ | ------ |
| 76 | P *_PASS: `SMTP_PASS='<v>'` | NYYYNY | ------ | - | ------ | - | ------ | ------ |
| 77 | P *_PASS: `PASS = <v>` | NYYYNY | ------ | - | ------ | - | ------ | ------ |
| 78 | P URL userinfo token: `https://<v>@github.com/org/repo.git` | NYYYNY | ------ | - | ------ | - | ------ | ------ |

(i) Aggregate (pasted from table_i.md):
| view | values | orig shows | PIN hid | gl F orig | gl T1 | gl T2 | ti-cli F | ti-cli T1 | ti-lib F | ti-lib T1 | PIN missed | gl finds on PIN out (F/m) | A1 gl | ti-cli finds on PIN out (F/m) | A1 ti-cli | A1 ti-lib |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dig | 98 | 98 | 80 | 52 | 52 | 52 | 39 | 39 | 40 | 40 | 18 | 3/0 | 83 | 4/0 | 84 | 85 |
| txt | 98 | 98 | 96 | 52 | 52 | 52 | 39 | 39 | 40 | 40 | 2 | 1/0 | 97 | 0/0 | 96 | 97 |
| call | 98 | 98 | 95 | 49 | 49 | 49 | 39 | 38 | 40 | 39 | 3 | 1/0 | 96 | 0/0 | 95 | 96 |
| call2 | 98 | 98 | 93 | 29 | 29 | 29 | 35 | 35 | 36 | 36 | 5 | 1/0 | 94 | 0/0 | 93 | 94 |
| pdig | 98 | 98 | 77 | 49 | 49 | 49 | 39 | 38 | 40 | 39 | 21 | 3/0 | 80 | 4/0 | 81 | 82 |
| ptxt | 98 | 98 | 95 | 49 | 49 | 49 | 39 | 38 | 40 | 39 | 3 | 1/0 | 96 | 0/0 | 95 | 96 |

(ii) F1's cases (VERIFY-SCRUB2-report.md:159-190; escape_named.py's SHAPES x CTX; each value is "7" + 14 alphanumerics + "9"). 48 values. ti-lib equals ti-cli. The first 8 columns list dig/call.
| shape | context | PIN hid | gl orig | ti-cli orig | gl@PIN | ti@PIN | A1 gl | A1 ti-cli |
|---|---|---|---|---|---|---|---|---|
| pwd= | line start | Y/N | -/- | -/- | -/- | -/- | Y/N | Y/N |
| pwd= | after a tab | Y/N | -/- | -/- | -/- | -/- | Y/N | Y/N |
| pwd= | JSON doc: escaped quotes | Y/N | -/- | -/- | -/- | -/- | Y/N | Y/N |
| pwd= | pasted JSON line, literal \n | N/N | -/- | -/- | -/- | -/- | N/N | N/N |
| pwd= | plain (control) | Y/Y | -/- | -/- | -/- | -/- | Y/Y | Y/Y |
| pwd= | after é | Y/Y | -/- | -/- | -/- | -/- | Y/Y | Y/Y |
| pwd= | after の | Y/Y | -/- | -/- | -/- | -/- | Y/Y | Y/Y |
| pwd= | before é | Y/Y | -/- | -/- | -/- | -/- | Y/Y | Y/Y |
| credentials= | line start | Y/N | F/F | -/- | -/F | -/- | Y/Y | Y/N |
| credentials= | after a tab | Y/N | F/F | -/- | -/F | -/- | Y/Y | Y/N |
| credentials= | JSON doc: escaped quotes | Y/N | F/- | -/- | -/- | -/- | Y/N | Y/N |
| credentials= | pasted JSON line, literal \n | N/N | F/- | -/- | F/- | -/- | Y/N | N/N |
| credentials= | plain (control) | Y/Y | F/F | -/- | -/- | -/- | Y/Y | Y/Y |
| credentials= | after é | Y/Y | F/F | -/- | -/- | -/- | Y/Y | Y/Y |
| credentials= | after の | Y/Y | F/F | -/- | -/- | -/- | Y/Y | Y/Y |
| credentials= | before é | Y/Y | -/- | -/- | -/- | -/- | Y/Y | Y/Y |
| Cookie: | line start | Y/N | -/- | -/- | -/- | -/- | Y/N | Y/N |
| Cookie: | after a tab | Y/N | -/- | -/- | -/- | -/- | Y/N | Y/N |
| Cookie: | JSON doc: escaped quotes | Y/N | -/- | -/- | -/- | -/- | Y/N | Y/N |
| Cookie: | pasted JSON line, literal \n | N/N | -/- | -/- | -/- | -/- | N/N | N/N |
| Cookie: | plain (control) | Y/Y | -/- | -/- | -/- | -/- | Y/Y | Y/Y |
| Cookie: | after é | N/N | -/- | -/- | -/- | -/- | N/N | N/N |
| Cookie: | after の | N/N | -/- | -/- | -/- | -/- | N/N | N/N |
| Cookie: | before é | Y/Y | -/- | -/- | -/- | -/- | Y/Y | Y/Y |
| Authorization: Token | line start | Y/Y | -/- | -/- | -/- | -/- | Y/Y | Y/Y |
| Authorization: Token | after a tab | Y/Y | -/- | -/- | -/- | -/- | Y/Y | Y/Y |
| Authorization: Token | JSON doc: escaped quotes | Y/N | -/- | -/- | -/- | -/- | Y/N | Y/N |
| Authorization: Token | pasted JSON line, literal \n | Y/Y | -/- | -/- | -/- | -/- | Y/Y | Y/Y |
| Authorization: Token | plain / after é / after の / before é (4 rows) | Y/Y | -/- | -/- | -/- | -/- | Y/Y | Y/Y |
| passphrase= (control) | all 8 contexts | Y/Y | -/- | -/- | -/- | -/- | Y/Y | Y/Y |
| password= (control) | line start, after a tab, plain, after é, after の | Y/Y | F/F | -/- | -/- | -/- | Y/Y | Y/Y |
| password= (control) | JSON doc: escaped quotes | Y/Y | F/- | F/- | -/- | -/- | Y/Y | Y/Y |
| password= (control) | pasted JSON line, literal \n | Y/Y | F/- | -/- | -/- | -/- | Y/Y | Y/Y |
| password= (control) | before é | Y/Y | -/- | -/- | -/- | -/- | Y/Y | Y/Y |

(ii) Aggregate (pasted):
| view | values | orig shows | PIN hid | gl F | gl T1 | gl T2 | ti-cli F | ti-cli T1 | ti-lib F | ti-lib T1 | PIN missed | gl on PIN out (F/m) | A1 gl | ti on PIN out (F/m) | A1 ti-cli | A1 ti-lib |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dig | 48 | 48 | 43 | 14 | 14 | 14 | 1 | 1 | 1 | 1 | 5 | 1/0 | 44 | 0/0 | 43 | 43 |
| txt | 48 | 48 | 43 | 14 | 14 | 14 | 1 | 1 | 1 | 1 | 5 | 1/0 | 44 | 0/0 | 43 | 43 |
| call | 48 | 48 | 33 | 10 | 10 | 10 | 0 | 0 | 0 | 0 | 15 | 2/0 | 35 | 0/0 | 33 | 33 |
| call2 | 48 | 48 | 29 | 10 | 10 | 10 | 0 | 0 | 0 | 0 | 19 | 4/0 | 33 | 0/0 | 29 | 29 |
| pdig | 48 | 48 | 27 | 10 | 10 | 10 | 0 | 0 | 0 | 0 | 21 | 4/0 | 31 | 0/0 | 27 | 27 |
| ptxt | 48 | 48 | 29 | 10 | 10 | 10 | 0 | 0 | 0 | 0 | 19 | 4/0 | 33 | 0/0 | 29 | 29 |
My PIN column for the "target" cells matches VR0's F1 table (VERIFY-SCRUB2-report.md:159-190). VR0's "target" was cdbc1b8, which is today's PIN.

(iii) Red items r2, r3 and r4. Parametrize lists and value makers come from the red files themselves. 39 values. ti-lib equals ti-cli.
| # | red group: item | red view | PIN hid on red view | PIN (6) | gl (6) | ti-cli (6) | gl@PIN | ti@PIN | rules (orig, any view) |
|---|---|---|---|---|---|---|---|---|---|
| 1-11 | r2 N1 decoded: pwd=, PWD: and credentials= with pair8, pairs10 and oddrun9; pwd= with tab8 and group8 | dig | Y (all 11) | YYYYYY (all 11) | ------ | ------ | ------ | ------ | - |
| 12-13 | r2 N1 canonical: `--pwd= + pair`, `credentials= + pair` | call1 | Y | YYYYYY | ------ | ------ | ------ | ------ | - |
| 14 | r2 N2: `{\"Cookie\": \"sid=<v>; pwd='<v>'\"}` | dig+txt1 | Y / txt1 Y | YYYYYY | ------ | ------ | ------ | ------ | - |
| 15 | r2 N2: `my_cookie: session=<v>; db_pwd="<v>"` | dig+txt1 | Y / txt1 Y | YYNNNN | ------ | ------ | ------ | ------ | - |
| 16 | r2 N2: `my_cookie: sid=<v>; credentials="<v>"` | dig+txt1 | Y / txt1 Y | YYNNNN | ------ | ------ | ------ | ------ | - |
| 17 | r3 N2R canonical: `export DB_PASSWORD="<v>"` | call | Y | YYYYNY | ------ | FF---- | ------ | ------ | np.generic.5 |
| 18 | r3 N2R canonical: `token="<v>"` | call | Y | YYYYNY | ------ | ------ | ------ | ------ | - |
| 19 | r3 N2R canonical: `api_key="<v>"` | call | Y | YYYYNY | ------ | ------ | ------ | ------ | - |
| 20 | r3 N2R canonical: `AGENT_TOKEN="<v>"` | call | Y | YYYYNY | ------ | ------ | ------ | ------ | - |
| 21 | r3 N2R canonical: `SMTP_PASS='<v>'` | call | Y | NYYYNY | ------ | ------ | ------ | ------ | - |
| 22 | r3 N2R decoded: `my_cookie: sid=<v>; DB_PASS="<v>"` | txt | Y | NYYYNY | ------ | ------ | ------ | ------ | - |
| 23 | r3 N2R decoded: `my_cookie: sid=<v>; curl -u "admin:<v>" https://zq.example` | txt | Y | NYYYNY | FF---- | FF---- | F----- | F----- | curl-auth-user, kingfisher.curl.1 |
| 24 | r3 N2R decoded: `x\rPWD: sid=<v>SMTP_PASS='<v>'` | txt | Y | NYYYNY | ------ | ------ | ------ | ------ | - |
| 25 | r3 N2R decoded: `my_cookie: sid=<v>; password=\"<v>\"` | txt | Y | NYYNNY | ------ | ------ | ------ | ------ | - |
| 26 | r3 N2R canonical: `x\tpwd=sid=<v>⏎DB_PASSWORD="<v>"` | call | Y | YYYYNY | ------ | FF---- | ------ | ------ | np.generic.5 |
| 27 | r3 N2R canonical: `y\rcredentials = sid=<v>⏎token="<v>"` | call | Y | YYYYNY | ------ | ------ | ------ | ------ | - |
| 28 | r4 R4V-1 canonical: `export credentials=ab⏎Bearer k1a2b3c4d5e6f/DB_PASS=\"<v>\"` | call | Y | NNYYNY | ------ | ------ | ------ | ------ | - |
| 29 | r4 R4V-1 canonical: `[auth] credentials=q1⏎Authorization: \"Basic dXNlcjpwYXNzQxtoken=\"<v>\"` | call | Y | NNYNNY | ------ | ------ | ------ | ------ | - |
| 30 | r4 R4V-1 canonical: `credentials=zz⏎bearer k1a2b3c4d59~curl -u a:<v> https://zq.example` | call | Y | NNYYNY | FFFFFF | FFFFFF | F---F- | F---F- | curl-auth-user, kingfisher.curl.1 |
| 31 | r4 R4V-1 canonical: `credentials=U⏎abcBearer k1qF5UwwJ7Lpcs/token=\"<v>\" next` | call | Y | NNYNNY | ------ | ------ | ------ | ------ | - |
| 32 | r4 R4V-1 canonical: `credentials=bT⏎Bearer khEPDGj0IKFUUP/https://u:<v>@h.example` | call | Y | NNYYNY | ------ | FFFFFF | ------ | F---F- | kingfisher.credentials.1, kingfisher.uri.1 |
| 33 | r4 R4V-1 decoded: `credentials=Z\tBearer k1a2b3c4d5e6f+X_PASS = <v>` | txt | Y | NYYYNY | ------ | ------ | ------ | ------ | - |
| 34 | r4 R4V-1 decoded: `set credentials=y\rtoken=\"k1a2b3c4d5;DB_PASS = <v>` | txt | Y | NYYYNY | ------ | ------ | ------ | ------ | - |
| 35 | r4 R4V-1 decoded: `'credentials':'qcro7h\rabcBearer kFMIgtUHJ76U2+X_PASS = <v>'` | txt | Y | NYYYNY | ------ | ------ | ------ | ------ | - |
| 36 | r4 R4V-1 decoded: `credentials=pfyXX\rx9y8z7w6Bearer kfl9ugaiT5LN2~curl -u "a:<v>"` | txt | Y | NYYYNY | ------ | FF---- | ------ | F----- | kingfisher.curl.1 |
| 37 | r4 R4V-1 decoded: `credentials=lP\tx9y8z7w6Authorization: \"Basic kyCcooZO4/cN1/bearer <v>\"` | txt | Y | NYYYNY | ------ | ------ | ------ | ------ | - |
| 38 | r4 R4V-1 control: `export credentials=abcdefgh⏎Bearer k1a2b3c4d5e6f/DB_PASS=\"<v>\"` | call | Y | NNYYNY | ------ | ------ | ------ | ------ | - |
| 39 | r4 R4V-1 control: `credentials=Zabcdefgh\tBearer k1a2b3c4d5e6f+X_PASS = <v>` | txt | Y | NYYYNY | ------ | ------ | ------ | ------ | - |
(The literal fillers in these rows come from the committed red files' parametrize lists. They are fixtures, not values.)

(iii) Aggregate (pasted):
| view | values | orig shows | PIN hid | gl F | gl T1 | gl T2 | ti-cli F | ti-cli T1 | ti-lib F | ti-lib T1 | PIN missed | gl on PIN out (F/m) | A1 gl | ti on PIN out (F/m) | A1 ti-cli | A1 ti-lib |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dig | 39 | 39 | 22 | 2 | 2 | 2 | 6 | 6 | 6 | 6 | 17 | 2/0 | 24 | 4/0 | 26 | 26 |
| txt | 39 | 39 | 33 | 2 | 2 | 2 | 6 | 6 | 6 | 6 | 6 | 0/0 | 33 | 0/0 | 33 | 33 |
| call | 39 | 39 | 37 | 1 | 1 | 1 | 2 | 2 | 2 | 2 | 2 | 0/0 | 37 | 0/0 | 37 | 37 |
| call2 | 39 | 39 | 34 | 1 | 1 | 1 | 2 | 2 | 2 | 2 | 5 | 0/0 | 34 | 0/0 | 34 | 34 |
| pdig | 39 | 39 | 14 | 1 | 1 | 1 | 2 | 2 | 2 | 2 | 25 | 1/0 | 15 | 2/0 | 16 | 16 |
| ptxt | 39 | 39 | 37 | 1 | 1 | 1 | 2 | 2 | 2 | 2 | 2 | 0/0 | 37 | 0/0 | 37 | 37 |
| call1 | 2 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0/0 | 2 | 0/0 | 2 | 2 |
| txt1 | 3 | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0/0 | 3 | 0/0 | 3 | 3 |

B2-edge: input-handling probes (fake ghp_ + 36 alnum; drivers $S/drv/b2_edge.py, b2_stdin_boundary.py and b2_nul.py; outputs under $S/runs/b2edge and $S/runs/b2nul). Each cell says whether the tool found the value.
| case | gl stdin | gl dir <file> | gl DetectString | ti scan <file> | ti ScanString |
|---|---|---|---|---|---|
| G1 control, token line alone | found (rc 1) | found | found | found | found |
| G2 text starts "MZ\n" | missed, rc 0, DBG "skipping binary file mime_type=application/vnd.microsoft.portable-executable" | missed (same) | found | found | found |
| G3 text starts "%PDF-1.4\n" | missed, rc 0 (application/pdf) | missed | found | found | found |
| G4 text starts "{\rtf1\n" | missed, rc 0 (application/rtf) | missed | found | found | found |
| G5 "MZ" on line 2 | found | found | found | found | found |
| G6 one line: 125,000 x, then "MZ token <v>" | found | missed, rc 0 (DBG skipping binary) | found | found | found |
| G6c control: "AB" in place of "MZ" | found | found | found | found | found |
| G7 one line: token straddles byte 125,000 | found | missed, rc 0, no log line | found | found | found |
| G7c control: token ends before 125,000 | found | found | found | found | found |
| N0 control, no NUL | found | n/a | found | found | found |
| N1 NUL at byte 5 | found | n/a | found | missed: "Scanned 0 B from 0 blobs", rc 0 | found |
| N2 NUL at byte 9,000 | found | n/a | found | found | found |
Stdin boundary sweep: a single line of "x" filler, the token at a swept offset, 3 runs per offset. gitleaks stdin missed 3 of 3 at every start offset from 90,500 to 90,533 (step 3). Offsets 90,536 to 90,542, 65,500 to 65,542 and 124,980 to 125,004 had 0 misses. 90,536 = 65,536 (the first pipe read in this setup) + 25,000 (the peek). Other writers or timings may cut elsewhere: UNSURE.

B3. Timing: each tool on each timing row, 60 s cap per process
Command: `( cd $S/runs/b3 && netless env PYTHONDONTWRITEBYTECODE=1 python3 $S/drv/b3_timing.py $S/runs/b3 <f7|b1|extra> 3 [family] )`, 4 foreground calls between 05:25Z and 05:41Z.
- Families. F7 uses the first SCRUB2 verifier's generators (scratchpad/vscrub2/timing.py, sha256 prefix bd2cdc46), n = 250, 500, 1000 and 2000. B1 uses VR1's bs_timing.py texts, n = 4000 to 32000. "extra" is `curl x ` * n; it is outside the brief's rows.
- Method. REP = 3, each rep its own process, 60 s subprocess cap. Cells show the median in seconds. CLI cells are process wall time. Library cells time only the in-process call: DetectString; ScanString; or Match + DrainTimedOut for ti-instr. PIN cells run scrub or scrub_payload in a child process, timing the call only.
- No cell hit TIMEOUT. Titus warning counts were 0 on every F7 and B1 row. Rows: $S/runs/b3/b3_{f7,b1,extra}.jsonl.
| family | n | chars | gl-cli | gl-re2-cli | ti-cli | gl-lib | gl-re2-lib | ti-instr | ti-lib | pin-scrub | pin-payload | titus warn (cli/instr) | load after |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dashes | 250 | 7500 | 0.047 | 0.429 | 0.078 | 0.0006 | 0.002 | 0.018 | 0.022 | 0.457 | 0.487 | 0/0 | 2.65 |
| dashes | 500 | 15000 | 0.097 | 0.497 | 0.080 | 0.001 | 0.003 | 0.015 | 0.021 | 1.671 | 1.731 | 0/0 | 2.51 |
| dashes | 1000 | 30000 | 0.047 | 0.482 | 0.105 | 0.002 | 0.006 | 0.037 | 0.028 | 6.778 | 6.639 | 0/0 | 2.93 |
| dashes | 2000 | 60000 | 0.054 | 0.481 | 0.100 | 0.004 | 0.011 | 0.041 | 0.045 | 26.164 | 25.815 | 0/0 | 2.39 |
| dash-run + 1 BEGIN | 250 | 7526 | 0.086 | 0.502 | 0.102 | 0.016 | 0.003 | 0.025 | 0.035 | 0.464 | 0.436 | 0/0 | 2.81 |
| dash-run + 1 BEGIN | 500 | 15026 | 0.070 | 0.469 | 0.093 | 0.019 | 0.004 | 0.019 | 0.025 | 1.763 | 1.716 | 0/0 | 3.08 |
| dash-run + 1 BEGIN | 1000 | 30026 | 0.086 | 0.515 | 0.097 | 0.036 | 0.006 | 0.024 | 0.038 | 6.703 | 6.813 | 0/0 | 3.57 |
| dash-run + 1 BEGIN | 2000 | 60026 | 0.127 | 0.483 | 0.124 | 0.056 | 0.014 | 0.062 | 0.083 | 27.000 | 27.974 | 0/0 | 3.89 |
| pem4-no-END x n | 250 | 7500 | 0.071 | 0.547 | 0.115 | 0.009 | 0.0005 | 0.023 | 0.032 | 0.058 | 0.059 | 0/0 | 4.32 |
| pem4-no-END x n | 500 | 15000 | 0.066 | 0.454 | 0.090 | 0.013 | 0.0006 | 0.026 | 0.037 | 0.207 | 0.230 | 0/0 | 4.27 |
| pem4-no-END x n | 1000 | 30000 | 0.107 | 0.500 | 0.198 | 0.022 | 0.0009 | 0.063 | 0.086 | 0.872 | 0.849 | 0/0 | 4.52 |
| pem4-no-END x n | 2000 | 60000 | 0.076 | 0.473 | 0.161 | 0.027 | 0.001 | 0.082 | 0.175 | 3.277 | 3.538 | 0/0 | 5.32 |
| pem3-spaced-no-END | 250 | 6500 | 0.067 | 0.492 | 0.094 | 0.008 | 0.0004 | 0.018 | 0.023 | 0.010 | 0.012 | 0/0 | 5.21 |
| pem3-spaced-no-END | 500 | 13000 | 0.065 | 0.479 | 0.109 | 0.009 | 0.0006 | 0.019 | 0.027 | 0.044 | 0.041 | 0/0 | 5.60 |
| pem3-spaced-no-END | 1000 | 26000 | 0.073 | 0.452 | 0.106 | 0.011 | 0.0009 | 0.026 | 0.042 | 0.139 | 0.183 | 0/0 | 5.87 |
| pem3-spaced-no-END | 2000 | 52000 | 0.077 | 0.543 | 0.127 | 0.024 | 0.001 | 0.093 | 0.167 | 0.738 | 0.725 | 0/0 | 6.25 |
| pem5-no-END x n | 250 | 8000 | 0.056 (62 findings) | 0.437 | 0.086 | 0.010 | 0.003 | 0.023 | 0.033 | 0.0002 | 0.0003 | 0/0 | 5.91 |
| pem5-no-END x n | 500 | 16000 | 0.066 (125) | 0.422 | 0.076 | 0.015 | 0.004 | 0.023 | 0.035 | 0.0004 | 0.0004 | 0/0 | 5.68 |
| pem5-no-END x n | 1000 | 32000 | 0.082 (250) | 0.476 | 0.120 | 0.030 | 0.007 | 0.029 | 0.038 | 0.0006 | 0.0007 | 0/0 | 5.68 |
| pem5-no-END x n | 2000 | 64000 | 0.111 (500) | 0.481 | 0.160 | 0.059 | 0.011 | 0.064 | 0.101 | 0.001 | 0.001 | 0/0 | 5.62 |
| pem4 + wrong END x n | 250 | 15000 | 0.058 | 0.478 | 0.070 | 0.007 | 0.0009 | 0.011 | 0.019 | 0.154 | 0.161 | 0/0 | 5.06 |
| pem4 + wrong END x n | 500 | 30000 | 0.055 | 0.436 | 0.076 | 0.014 | 0.001 | 0.022 | 0.031 | 0.646 | 0.673 | 0/0 | 4.73 |
| pem4 + wrong END x n | 1000 | 60000 | 0.064 | 0.428 | 0.100 | 0.033 | 0.001 | 0.043 | 0.062 | 2.582 | 2.660 | 0/0 | 3.67 |
| pem4 + wrong END x n | 2000 | 120000 | 0.128 | 0.503 | 0.158 | 0.060 | 0.003 | 0.089 | 0.137 | 9.742 | 9.823 | 0/0 | 2.49 |
| pwd+bs | 4000 | 4005 | 0.044 | 0.445 | 0.064 | 0.0006 | 0.0002 | 0.004 | 0.005 | 0.0007 | 0.0009 | 0/0 | 2.23 |
| pwd+bs | 8000 | 8005 | 0.056 | 0.465 | 0.065 | 0.001 | 0.0004 | 0.009 | 0.009 | 0.001 | 0.001 | 0/0 | 2.23 |
| pwd+bs | 16000 | 16005 | 0.046 | 0.442 | 0.082 | 0.002 | 0.0003 | 0.008 | 0.009 | 0.002 | 0.003 | 0/0 | 2.29 |
| pwd+bs | 32000 | 32005 | 0.050 | 0.492 | 0.097 | 0.007 | 0.0004 | 0.016 | 0.026 | 0.004 | 0.004 | 0/0 | 2.27 |
| cred+bs | 4000 | 4013 | 0.068 | 0.500 | 0.082 | 0.002 | 0.0003 | 0.005 | 0.006 | 0.0007 | 0.0008 | 0/0 | 2.33 |
| cred+bs | 8000 | 8013 | 0.060 | 0.510 | 0.081 | 0.004 | 0.0003 | 0.012 | 0.010 | 0.001 | 0.001 | 0/0 | 2.30 |
| cred+bs | 16000 | 16013 | 0.054 | 0.433 | 0.080 | 0.007 | 0.0006 | 0.006 | 0.008 | 0.004 | 0.003 | 0/0 | 2.28 |
| cred+bs | 32000 | 32013 | 0.056 | 0.468 | 0.078 | 0.010 | 0.0006 | 0.009 | 0.010 | 0.005 | 0.005 | 0/0 | 2.28 |
| cookie+bs | 4000 | 4008 | 0.044 | 0.446 | 0.062 | 0.0006 | 0.0002 | 0.004 | 0.006 | 0.002 | 0.003 | 0/0 | 2.17 |
| cookie+bs | 8000 | 8008 | 0.049 | 0.427 | 0.081 | 0.002 | 0.0002 | 0.007 | 0.008 | 0.003 | 0.006 | 0/0 | 2.08 |
| cookie+bs | 16000 | 16008 | 0.043 | 0.435 | 0.068 | 0.002 | 0.0003 | 0.005 | 0.006 | 0.007 | 0.012 | 0/0 | 1.99 |
| cookie+bs | 32000 | 32008 | 0.046 | 0.407 | 0.082 | 0.006 | 0.0004 | 0.011 | 0.010 | 0.012 | 0.024 | 0/0 | 1.91 |
| cookie=+bs | 4000 | 4010 | 0.045 | 0.430 | 0.069 | 0.0008 | 0.0002 | 0.004 | 0.005 | 0.0007 | 0.0008 | 0/0 | 1.91 |
| cookie=+bs | 8000 | 8010 | 0.048 | 0.472 | 0.069 | 0.001 | 0.0003 | 0.008 | 0.010 | 0.001 | 0.001 | 0/0 | 1.84 |
| cookie=+bs | 16000 | 16010 | 0.048 | 0.422 | 0.083 | 0.002 | 0.0003 | 0.005 | 0.006 | 0.002 | 0.002 | 0/0 | 1.77 |
| cookie=+bs | 32000 | 32010 | 0.048 | 0.453 | 0.071 | 0.005 | 0.0004 | 0.009 | 0.010 | 0.005 | 0.005 | 0/0 | 1.79 |
| EXTRA curl heads, one line | 1000 | 7000 | 0.049 | 0.459 | 0.403 | 0.003 | 0.0004 | 0.297 | 0.351 | 0.003 | 0.035 | 0/0 | 1.72 |
| EXTRA curl heads, one line | 2000 | 14000 | 0.059 | 0.497 | 0.693 | 0.005 | 0.0005 | 0.735 | 0.748 | 0.005 | 0.058 | 0/0 | 2.43 |
| EXTRA curl heads, one line | 4000 | 28000 | 0.083 | 0.528 | 2.978 | 0.014 | 0.0009 | 3.008 | 3.006 | 0.012 | 0.146 | 0/0 | 4.11 |
| EXTRA curl heads, one line | 8000 | 56000 | 0.060 | 0.438 | 23.847 | 0.019 | 0.002 | 5.015 (+ drain 17.49) | 5.016 | 0.024 | 0.344 | 2/2 | 3.42 |
Notes on the timing grid:
- gl-re2-cli's floor of about 0.3 s is start-up: `gitleaks-re2 version` takes 0.298 s (B4).
- The pem5 findings are gitleaks private-key matches spanning heads on filler that holds no key body. gl-re2 and both libraries report the same counts.
- The PIN's own F7 numbers: 26.16 s at 60,000 dashes, x3.9 per doubling. VR0 reported "over 20 s at 60,000" in its "target" column (VERIFY-SCRUB2-report.md:260). VR0's target was cdbc1b8, which is today's PIN (report :27, :30). VR0's "PIN" column (0.014 s) is 4b3b699, the exporter before SCRUB2, sha256 2136062e.
- A probe before the grid, at the largest sizes, 1 rep, load 3.38 to 2.92: PIN scrub on "curl heads" n=8000 took 0.023 s and scrub_payload 0.313 s. $S/runs/b3pinprobe.

B3 titus timeouts, retries and drops at DEFAULT settings (5 s timeout)
Each case plants a fake curl credential `curl -u <user>:<token_urlsafe(12)> https://example.invalid/x` after or before `curl x ` * n. Drivers are $S/drv/b3_drop.py, b3_dedup.py and b3_serve.py, each process with a 200 s cap; this is a demonstration, not a brief row. Outputs: $S/runs/b3drop/{single,blacklist}.jsonl, $S/runs/b3dedup and $S/runs/b3serve. Load 1.4 to 5.0.
| case (chars) | gitleaks stdin | titus scan (CLI) | titus instr (Match + Drain) | titus NewScanner().ScanString | titus serve | PIN scrub / scrub_payload hid |
|---|---|---|---|---|---|---|
| E1 planted line alone (57) | found, curl-auth-user, 0.048 s, rc 1 | found, kingfisher.curl.1, 0.062 s, rc 0 | found, first pass | found | found (0.002 s) | N / Y |
| E2 heads 8000, then planted (56,058) | found, 0.074 s | found via retry: 23.82 s, 2 timeout warnings (curl.1, curl.2), rc 0, "1/1 new matches" | first pass 0 matches (5.013 s); drain 17.749 s recovered 1 | MISSED: 5.025 s, err nil, no warning | MISSED: 5.032 s, success true, 2 stderr warnings | N / Y |
| E2b planted, then heads 8000 (56,058) | found | found, 2 matches for the 1 planted value, 23.62 s, 2 warnings | first pass 1 + retried 1 | found (5.036 s) | not run | N / Y |
| E3 heads 16000, then planted (112,058) | found, 0.079 s | MISSED: 65.11 s, 4 timeout warnings (2 first pass + 2 retry), "0/0 new matches", rc 0 | MISSED: 5.02 s + drain 60.03 s, 4 warnings | MISSED: 5.058 s, silent | not run | N / Y |
| E4 dir of 4 files, each heads 8000 + own planted line, all user "admin" (224,232 B) | 4/4 found | 1/4 found: 40.35 s, rc 0; 8 timeout lines plus "[warn] rule kingfisher.curl.1 disabled after 3 timeouts ..." and the same for curl.2; "1/1 new matches" | one process: 2/4 (texts 1-2 recovered by a per-text drain; text 3 hit the 3rd timeout, disabled; text 4 timed out at 5.01 s, not retried); 55.14 s | one process: 0/4, about 5.0 s each, silent | not run | not run |
| D1 2 files, same user | n/a | 1/2 found; 4 timeouts, 0 disabled; 41.64 s; "1/1 new matches" | | | | |
| D2 2 files, distinct users | n/a | 2/2 found; 4 timeouts; 42.44 s | | | | |
| D3 4 files, distinct users | n/a | 2/4 found; 8 timeouts, 2 disabled; 42.43 s | | | | |
Exact titus stderr in E3, pasted: "[warn] rule kingfisher.curl.1 regex timeout on blob 81496a987681b5a072caa64fc4bcfdb76f6c3d7a (skipping rule for this blob)" x2 and the same for curl.2 x2, then "Scanned 112058 B from 1 blobs in 65 second (1723 B/s); 0/0 new matches".

B3 extra sweep, outside the brief's rows. All 31 of VR0's hostile families at n=2000, imported read-only from scratchpad/vscrub2/timing.py, each tool one process with a 60 s cap. Command: `netless python3 $S/drv/b3_sweep.py $S/runs/b3sweep 0 15` and `... 16 30`. Load 1.6 to 1.8.
- No TIMEOUT anywhere.
- gitleaks: 0.044 to 0.117 s CLI, at most 0.084 s library. Findings: pem5 500; otherwise 0.
- ti-cli: 0.069 to 0.184 s, no timeout warnings. It found 1 match on the filler "sk-a...é".
- ti-lib (NewScanner, 539 rules) on "a- x n" (60,000 chars): 5.074 s, 0 matches, silent. Re-run as `titus-lib -mode instr -rules all`, the warnings name np.shopify.1 twice (first pass and retry), with drain 30.01 s. np.shopify.1 is "Shopify Domain", in the np.assets ruleset and not in the CLI default (rulesets/np.assets.yml:31). Its pattern is `(?x) \b ((?:[a-zA-Z0-9-]+\.)* [a-zA-Z0-9-]+ \.myshopify\.com) \b` (rules/shopify.yml:10-15).
- The PIN's times for these 31 families on the same file are VR0's "target" column (VERIFY-SCRUB2-report.md:256-266). Not re-run.

B4. Per-call cost and batch shapes
Method: 100 texts of about 10 KB each (10,001 to 10,097 chars, median 10,038.5). Each text has tool-call JSON lines, prose from a fixed word list, and 7 fakes: sk-, Bearer, ghp_, AKIA id, AWS secret, password= and a PEM block. `netless python3 $S/drv/b4_cost.py $S/runs/b4`, at 05:56:41 to 05:57:15Z, load 1.73 to 3.07. Results: $S/runs/b4/b4.json.
| shape | tool | per call: median (min / p90 / max) | other |
|---|---|---|---|
| process floor (10 runs) | gitleaks version | 0.0068 s (0.0047 / 0.0086 / 0.0091) | |
| | gitleaks-re2 version | 0.298 s (0.258 / 0.319 / 0.324) | |
| | titus version | 0.0140 s (0.0119 / 0.0178 / 0.0183) | |
| one process per 10 KB text (20 runs) | gitleaks stdin | 0.0554 s (0.0463 / 0.0666 / 0.0813) | 6 findings per text |
| | gitleaks-re2 stdin | 0.484 s (0.372 / 0.523 / 0.542) | 6 per text |
| | titus scan <file> --output :memory: | 0.0858 s (0.0714 / 0.0932 / 0.0953) | 7 per text |
| library, one process, 100 calls | gitleaks DetectString (stdlib) | 0.00885 s (0.00676 / 0.0105 / 0.0177) | init 47.9 ms; process 0.992 s; 5-6 per text |
| | gitleaks DetectString (re2) | 0.00195 s (0.00125 / 0.0039 / 0.0157) | init 150.3 ms; process 0.719 s |
| | titus NewScanner().ScanString (539 rules) | 0.0176 s (0.0129 / 0.0246 / 0.0345) | init 43.7 ms; process 1.942 s; 8 per text |
| | titus Match + DrainTimedOut (498 rules) | 0.0124 s (0.0097 / 0.0174 / 0.0273) | init 8.5 ms; process 1.415 s; 7 per text |
| stream, one process | `titus serve` NDJSON over stdin/stdout, 100 sequential "scan" requests | 0.0186 s latency (0.0138 / 0.0254 / 0.0438) | "ready" after 0.064 s; total 2.058 s; 8 per text; banner on stderr |
| many files, one process (3 runs) | gitleaks dir <100 files> | 0.362 s total (0.361 / - / 0.388) | 591 findings, rc 1 |
| | gitleaks-re2 dir | 0.648 s (0.596 / - / 0.676) | 591 |
| | titus scan <dir of 100> | 1.260 s (1.053 / - / 1.355) | 700 matches, rc 0 |
| one stdin, 100 texts joined by "\n\n" (1,004,368 B, 3 runs) | gitleaks stdin | 1.017 s (0.993 / - / 1.057) | 591 findings; mapping back to a text is by line number only |
| the PIN, one Python process | import | 0.0094 s | |
| | scrub | 0.0034 s (0.0032 / 0.0043 / 0.0050) | |
| | scrub_payload | 0.0076 s (0.0059 / 0.0106 / 0.0113) | |
titus has no stdin mode for `scan`; its streaming shape is `serve`.

======================================================================
CLAIMS VERSUS CODE OR MEASUREMENT (both sides recorded, none resolved)
======================================================================
1. D-116 (docs/08_DECISION_LOG.md:127) says titus has "487 rules"; so does its README.md:9, :30. Built-in count: 539. The default ruleset lists 507 ids, `titus scan` loads 498, and NewScanner and serve load 539. SOLID
2. D-116 says "a timed-out match is retried once with a longer timeout". Code: only the CLI drains (scan.go:434, 461-462). The library (titus.go) and serve (pkg/scanner/core.go) never retry. Measured: E2 ti-lib and serve both missed the value. SOLID
3. D-116 says "a rule that times out three times in a scan is skipped for the rest of it"; titus's own warning says "skipping remaining blobs" (regexp_portable.go:369-370). Code: the count gates only the retry queue (:349-385), and the match loops ignore it. Measured: E4's 4th blob still ran 5 s and warned. SOLID
4. D-116 says "live validation and scoring are opt-in network features". Code and measurement: that holds for validation and dynamic scoring. Separately, the default --accessibility auto does a git exec and, for a GitHub/GitLab/Bitbucket remote, an API call. Measured: DNS attempts to 8.8.8.8 and 8.8.4.4 under netless. SOLID
5. D-116 says gitleaks uses "Go's standard RE2 engine by default". Code: `go build` without tags gives stdlib. The project's release config builds with tag gore2regex (.goreleaser.yml:18-19). SOLID
6. titus comments say the default timeout is "500ms" (regexp_portable.go:86; vectorscan.go:61). Code sets 5 s (:80, :91-92; vectorscan.go:152). Measured: 5.0 s. SOLID
7. titus crossrule.go:38-40 says Deduplicate takes "all matches from a single blob". DrainTimedOut passes all retried blobs to it (dedup_matcher.go:40-46). Measured: D1 dropped 1 of 2. SOLID
8. The titus timeout warning says "(skipping rule for this blob)". In the CLI the retry pass later recovered the match (E2). SOLID
9. gitleaks sources/common.go:16 comment says "10kb"; the value is 25 * 1_000. SOLID
10. D-116 says titus is "a Go library that returns spans"; types.Match carries byte offsets, which is consistent. gitleaks DetectString returns line/column, not byte offsets (report/finding.go:14-55). SOLID

======================================================================
NOT MEASURED (and why)
======================================================================
- The titus vectorscan (Hyperscan) build, the default `make build`. It needs cgo plus a system libhs, and the brief barred a system install. Only its code was read (vectorscan.go: hybrid, regexp2 fallback, the same 5 s value).
- The titus retry-queue cap of 500. No input reached it; each rule enqueues at most 2 jobs before the blacklist.
- titus --validate, --score-scope, enum, analyze, the git/Docker/S3/Asana/GDrive targets, and serve's validate and scan_git requests; gitleaks git and detect modes. Barred by rule (network or exec); code read only.
- gitleaks decoding (--max-decode-depth) on encoded fake values. Not probed. B2 used 5 in both the CLI and the library harness.
- Memory (RSS) of any tool, including titus's never-drained retry queue (it holds content bytes) in library or serve use. /usr/bin/time is absent and no other probe was run.
- Timing on an idle box. It was not possible: 4 CPUs shared with live lanes, load 1.5 to 6.3. Each cell is a median of 3 reps; there is no separate noise-floor run.
- gitleaks-re2 CLI over the B2 texts. Not run; the re2 library equals the stdlib library on all 1,142 texts.
- Real transcripts, and the exposure of any shape in them. Barred: no transcript read.
- Per-file git dates for the third-party files. Depth-1 clones.
- The gitleaks stdin chunk boundaries under other writers or pipe timings, and offsets outside the three swept windows.
- The titus UTF-16 path (enum/utf16.go) and any titus inline-ignore syntax. Not probed.
- A forced short-timeout run (-timeout 1ms). Not run: the default-timeout cases E2 to E4 and D1 to D3 exercised the warning, retry success, retry failure, blacklist and cross-blob dedup branches.
- strace did not show the creation syscall for datastore.db (the openat filter). Its creation is shown by the file itself, 192,512 bytes.

Scratch drivers (for re-running): $S/drv/{b2_gen.py, b2_run.py, b2_eval.py, b2_tables.py, b2_edge.py, b2_stdin_boundary.py, b2_nul.py, b3_timing.py, b3_show.py, b3_pinprobe.py, b3_drop.py, b3_dedup.py, b3_serve.py, b3_sweep.py, b4_cost.py}.
