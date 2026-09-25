# DATA-EXT: public datasets that could train or test the System 1 Jevs

STATUS: COMPLETE (started 2026-09-25 00:45Z). 54 datasets or corpora tabulated in 10 families (section 2), five read
deep (section 3), 8 empty searches listed (section 4), gaps named (section 5).
Read deep (section 3): G1 MAST-Data and E2 CVE-to-CWE Consensus (`ap.violates_row`), J1 HackerOne disclosed reports and
J2 Code4rena judged findings (`v1.finding_class`), A6 AIDev review verdicts (`v1.blocking`).
Lane: evidence-gatherer (EXPLORE), sandbox, Opus 5.5. Brief: `tasks/briefs/jev-laya/DATA-EXT-brief.md` (task #233).
Posture: read-only web research (WebSearch, WebFetch, Exa). No downloads beyond cards, READMEs and a few sample rows.
No verdicts: this file collects and tabulates. The coordinator ranks and decides.

## 0. Our three question types (read from the repo, 2026-09-25 00:45Z)

Source: `docs/research/findings/laya-ft-labels/2026-09-24-openjev/labels.jsonl` (1,788 rows) and its
`dataset-manifest.json`; the class-to-blocking rule from `tasks/briefs/laya/J1-3-brief.md:98`.

| id | options (verbatim from labels.jsonl) | rows in the teacher set | unit |
|---|---|---|---|
| `ap.violates_row` | `["false", "true"]` | 1616 | (incident or bug note, ONE registry row) pair; 16 candidates per entry (manifest `candidates_per_entry: 16`) |
| `v1.finding_class` | `["BLOCKER", "FOLLOW-UP", "INFO", "UNVERIFIED", "CONTRACT-DEFECT", "KNOWN"]` | 86 | one verification finding |
| `v1.blocking` | `["false", "true"]` | 86 | one verification finding |

- The J1-3 brief (line 98) sets `disposition` = `BLOCKING` for `BLOCKER`/`CONTRACT-DEFECT`, `NON-BLOCKING` otherwise.
- Class meanings used for the mappings below (read from `.claude/agents/adversarial-verifier.md:63-97`): `BLOCKER` = meets
  the whole blocking predicate (contract mapping, canonical reproduction through the production path, material effect,
  concrete discriminator, task ownership); a statically suspected issue is labelled "UNVERIFIED or FOLLOW-UP";
  `CONTRACT-DEFECT` = "a newly discovered exact-production-path defect that demonstrably falsifies evidence, corrupts
  state, loses data, or causes destructive unintended effects", returned for a contract amendment; `INFO` = a
  meaningful observation with no action. `KNOWN` has no definition in that file; in use it marks a finding already on
  record, e.g. "**KNOWN, seen again, not re-derived** (issue #41 ...)" at
  `tasks/briefs/continuity/VERIFY-AF-AP-127-R1-REPIN-a-R2-report.md:745`. `CONTRACT-INVALID` (the criterion itself is
  contradictory or impossible) is a gate recommendation, not one of the six classes.
- A registry row (`docs/INCIDENT-LOG.md`, 201 rows by the brief's premise) carries: id, mechanism in words, a greppable
  signature, the source incident, and a sweep status.

## 1. Legend

- SOLID = read on the dataset's own card, README, repository or paper in this session (URL given).
- UNSURE = not read on a primary page, or read only on a secondary page (a survey, a search snippet, an aggregator).
- Mapping kinds: EXACT (their label set can be renamed onto ours with no teacher), PROXY (a related label that needs a
  rule or a threshold), INPUT-ONLY (text of the right kind, but a teacher must label it for our question).

## 2. The evidence table

Every cell carries [S] (SOLID) or [U] (UNSURE). "Maps to" names our type and the mapping kind (EXACT, PROXY,
INPUT-ONLY). "Comm." = commercial use allowed under the stated license. Rows are grouped by the brief's families;
row ids (A1, B2, ...) are used in sections 3 to 6.

### 2.A Code-review comments with category, severity, usefulness or verdict labels

| id | name | URL (card or paper) | license; comm. | size; download | unit | label set | how labels were made | lang | format | maps to (kind: how) | quality problems the source reports |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A1 | CR-ESEM23 (Turzo, Faysal, Poddar, Sarker, Iqbal, Bosu; ESEM 2023) | https://arxiv.org/abs/2307.03852 ; data https://github.com/WSU-SEAL/CR-classification-ESEM23 | GPL-3.0 notice on the repo [S]; comm. yes under GPL copyleft terms [U: GPL on data is unusual] | 1,828 comments [S abstract]; download size not read [U] | one Gerrit review comment + its code context, OpenDev Nova [S] | 5 high-level categories "proposed by Turzo and Bosu" [S]; per the CRC-Py README the 5 are functional, refactoring, documentation, discussion, false positive [U: read on a derived dataset]; usefulness also present [U: aggregator https://huggingface.co/datasets/BranLiu/cr_taxonomy_dataset] | human, manual labeling [S abstract] | Python code (Nova), English text [U] | xlsx + csv + pkl [S README] | v1.finding_class PROXY: category (functional vs refactoring vs documentation vs discussion vs false positive) is a type label, not a disposition; v1.blocking PROXY: "functional" as the defect bucket | best model accuracy 59.3% (CodeBERT) [S abstract]; no agreement figure read [U] |
| A2 | CR usefulness, OpenDev Nova (Turzo & Bosu; EMSE 2023) | https://arxiv.org/abs/2302.11686 ; data https://github.com/WSU-SEAL/CR-usefulness-EMSE | not read (repo README is one line) [U] | 2,500 comments sampled from 300,304 Nova comments [S Exa extract of the paper] | one review comment [S] | 18 categories in 5 groups + useful / not useful per comment + survey usefulness scores per category [S paper extract] | human: two authors labeled each comment independently after reading the thread and code; usefulness rubric of Bosu et al. [S paper extract] | Python code, English [U] | not read [U] | v1.finding_class PROXY (18 categories incl. 'False positive'); v1.blocking PROXY (useful + 'Functional' group) | single project; "most CR comments are related to trivial issues", only ~19% functional [S paper extract] |
| A3 | CleanCodeReview (Petrova, Markov, Kachanov; 2024) | https://zenodo.org/records/13828619 | CC BY 4.0 [S]; comm. yes [S] | 10,045 comments [S]; 921.5 kB zip [S] | one review comment [S] | 16 classes (Style, Naming, Questioning, Response, Convention, Testing, Design, Refactoring, Functionality, Roadmap, Optimization, Error, Documentation, Support, Input/Output, Other) in 5 groups [S] | 4 open datasets merged + 3,200 comments manually marked by the authors [S]; the merge rule is not stated on the record [U] | English text; code languages not stated [U] | zip, JSONL per aggregator [U] | v1.finding_class PROXY: topic classes only; no severity or disposition label; v1.blocking INPUT-ONLY | not read [U] |
| A4 | CRC-Py (Icoz; 2025) | https://github.com/busraicoz/crc-py-dataset | MIT [S]; comm. yes [S] | 16,711 records per the README [S]; 13,726 per an aggregator [U] (discrepancy) | one GitHub PR review comment + diff hunk, top-100 Python repos [S] | 5 categories (functional, refactoring, documentation, discussion, false positive) + subcategories [S] | MODEL: "manual seed set + SVM-based multi-view classifier" assigns subcategories, mapped to categories [S]; seed size not stated [U] | Python, English [S] | 5 JSON files [S] | v1.finding_class PROXY (same 5 categories as A1); labels are classifier output, not human | seed size and classifier accuracy not stated [S absence on README] |
| A5 | CR Smell / human review-comment smells (Caglar, Gokirmak, Tuzun; arXiv 2604.23667, 2026-04-26) | https://arxiv.org/html/2604.23667v1 ; data https://doi.org/10.6084/m9.figshare.31073632 | CC BY-NC-ND 4.0 [S]; comm. NO [S] | 448 comments [S paper]; 439 per an aggregator [U] (discrepancy) | one review comment with diff hunk, drawn from A1's Nova set [S] | 9 labels: Incorrect, Toxic, Unrelated, Vague, Redundant, Praise, Question, Actionable, Clarification [S] | human: 2 annotators, kappa 0.56 before and 0.98 after reconciliation, third author adjudicated [S] | English [S] | CSV per aggregator [U] | v1.finding_class PROXY: Actionable vs Praise/Clarification (INFO-like) vs Question vs Incorrect (a false claim) | authors: labels are "a best-effort approximation of reviewer intent" [S]; initial kappa 0.56 [S] |
| A6 | AIDev (Li, Zhang, Hassan; 2025-2026) | https://huggingface.co/datasets/hao-li/AIDev ; paper https://arxiv.org/html/2602.09185v1 | card tag cc-by-4.0 [S]; card: each source repository keeps its own license, users must comply [S]; comm. yes for the CC BY layer, per-repo for content [U] | v4: 2,743,854 agent PRs, 327,477 repos [S]; `pr_reviews` 83.8k rows, `pr_review_comments` 81.7k rows (card viewer) [S]; v2 Zenodo files: pr_reviews.parquet 7.5 MB, pr_review_comments.parquet 14.7 MB [S https://zenodo.org/records/16919051] | a PR, a review (verdict), an inline review comment [S] | review `state` counts in v4 `pr_reviews` (83,816 rows): COMMENTED 58,693, APPROVED 19,445, CHANGES_REQUESTED 4,960, DISMISSED 718; `user_type` Bot 35,114, User 48,701 [S viewer statistics API]; PR state open/closed/merged [S]; `pr_task_type` Conventional-Commit purpose [S] | human GitHub actions (review verdicts, merges), plus bot reviewers (`user_type: Bot`) [S sample]; `pr_task_type` is MODEL ("auto-classification ... via LLMs") [S] | many programming languages; English text [U] | Parquet [S] | v1.blocking PROXY: a review with CHANGES_REQUESTED vs APPROVED; inline comments INPUT-ONLY for v1.finding_class | card: `pr_review_comments.parquet` "does not contain full data points, use `pr_review_comments_v2.parquet`" [S]; large patches missing from the API [S]; bot reviews mixed with human ones [S sample] |
| A7 | CodeReviewer, Diff Quality Estimation task (Li et al.; FSE 2022, Microsoft) | https://zenodo.org/records/6900648 ; paper https://arxiv.org/abs/2203.09095 | CC BY 4.0 on the Zenodo record [S]; comm. yes [S] | split sizes not read [U]; Diff_Quality_Estimation.zip 2.8 GB [S] | one diff hunk (old file + hunk) from GitHub PRs, 9 languages [S] | binary: the hunk received a review comment ("suspicious") or not ("correct") [S paper] | HEURISTIC, mined from later events: "All commented code changes are regarded as suspicious ... Other code changes without comments are labeled as correct"; un-commented hunks down-sampled to balance [S paper] | 9 programming languages, English comments [S] | JSONL [S README example] | v1.blocking PROXY (weak): "needs a comment" is not "blocks the merge"; the comment text itself is INPUT-ONLY for v1.finding_class | paper: "the dataset quality still varies, especially when it comes to review comments"; low-quality comments filtered by rules in an appendix [S]; A14 reports only 64% of sampled training comments are valid and cites 32% noise in the test set [S A14]; license conflict: Zenodo says CC BY 4.0 [S], the CRScore paper calls the test set Apache 2.0 [S A13] |
| A8 | CROP, Code Review Open Platform (Paixao, Krinke, Han, Harman; MSR 2018) | https://crop-repo.github.io/ ; data https://zenodo.org/records/3599150 | not read [U] | 11 systems, 50,959 reviews, 144,906 revisions on the site [S]; the paper says 8 systems, 48,975 reviews [S] | one Gerrit revision + its discussion file (commit message + reviewer comments) + code snapshots [S] | revision status (merged or abandoned) [S]; Gerrit votes appear only if present inside the comment messages [U] | mined from Gerrit (human reviewer actions) [S] | Java, JavaScript, Python, C++, Go [S] | CSV + text discussion files + git repos [S] | v1.blocking PROXY (abandoned vs merged at the review level); comments INPUT-ONLY | none read [U] |
| A9 | AACR-Bench (Alibaba; arXiv 2601.19494, 2026) | https://github.com/alibaba/aacr-bench ; paper https://arxiv.org/abs/2601.19494 ; data on HF `Alibaba-Aone/aacr-bench` [S repo] | Apache-2.0 [S]; comm. yes [S] | 200 PRs, 50 projects, 10 languages, 2,145 review comments [S] | one review comment on a PR with repository context [S] | category: Security, Defect, Maintainability, Performance; context level: diff / file / repository; flag for AI-generated comments [S] | MODEL + human: original GitHub comments "enhanced through LLM analysis", then multi-round expert validation by 80+ senior engineers [S] | 10 programming languages [S] | JSON [S] | v1.finding_class PROXY (category is a topic, no disposition); all comments are accepted issues, so no non-blocking negatives [U] | paper claim: raw PR comments are "noisy, incomplete ground truth" [U: search-engine summary of the abstract] |
| A10 | SWR-Bench (Zeng et al.; arXiv 2509.01494; Proc. ACM Softw. Eng., DOI 10.1145/3808144 per a search result [U]) | https://arxiv.org/abs/2509.01494 | CC BY 4.0 stated for the paper/package [S]; data URL: "an anonymous repository" at review time [S]; current data URL not read [U] | 1,000 PRs: 500 Change-PRs with issues, 500 Clean-PRs [S]; 1.90 change-actions per Change-PR [S] | one PR; ground truth = list of change-actions [S] | each change-action typed into 11 leaf types (Evolutionary: documentation, visual representation, structure; Functional: interface, logic, resource, check, support, larger defects) + description + commit SHA [S] | MODEL + human: LLM extraction from review timelines with 3-way majority vote, SZZ for missed issues, then manual verification by five graduate students, kappa 0.66 [S] | Python mostly [U] | not read [U] | v1.blocking PROXY at PR level: Change-PR vs Clean-PR; Functional vs Evolutionary change-action as a severity proxy | paper: SZZ precision/recall limits, annotation ambiguity, trivial changes filtered out, stratified sampling departs from the natural distribution [S] |
| A11 | CR-Bench and CR-Bench-Verified (Pereira, Sinha, Ghosh, Dutta, Nutanix; arXiv 2603.11078, 2026-03-10) | https://arxiv.org/html/2603.11078 | CC BY 4.0 (paper) [S]; data license not read [U] | 584 tasks; Verified subset 174 [S] | one PR derived from a SWE-bench instance, with the defect a review should catch [S] | tags for bug category, impact and severity [S]; value lists not read [U] | derived from SWE-bench; tag provenance not read [U] | Python [U] | not read [U] | v1.finding_class PROXY (severity/impact tags), v1.blocking PROXY (defect-focused: every task carries a real defect) | paper: review agents show "a low signal-to-noise ratio"; evaluation by LLM judge [S] |
| A12 | c-CRAB, Code Review Agent Benchmark (Zhang, Pan, Yusuf, Ruan, Shariffdeen, Roychoudhury; arXiv 2603.23448, 2026) | https://arxiv.org/abs/2603.23448 | CC BY 4.0 (paper) [S]; data license not read [U] | not read [U] | one PR with human reviews converted to tests [S abstract: "constructed from human reviews of pull requests"] | test-based pass/fail per review issue [U] | human reviews -> tests [U] | not read [U] | not read [U] | v1.blocking PROXY (a review issue that a test reproduces is close to "a contract break reproduced through the real path") [U] | tools together solve ~40% of tasks [S] |
| A13 | CRScore human annotations (Naik, Alenius, Fried, Rose; NAACL 2025) | https://aclanthology.org/2025.naacl-long.457/ ; code https://github.com/atharva-naik/CRScore | not read; the underlying CodeReviewer test set is Apache-2.0 per the paper [S] | 2.9k human-rated reviews; 5.7k (claim, review) pairs of which 1,948 positive; 1,231 claims coded correct / incorrect / unverifiable [S] | a review comment for a CodeReviewer diff (Python, Java, JavaScript) [S] | 1-5 Likert on conciseness, comprehensiveness, relevance; per-claim 1 correct / 0 incorrect / -1 unverifiable [S] | human: two trained annotators (co-authors); Cohen kappa 0.804 on claims; Krippendorff alpha 0.85-0.89 on dimensions [S] | Python, Java, JavaScript [S] | not read [U]; the paper said release was planned on acceptance [S] | v1.finding_class PROXY for UNVERIFIED: the claim codes "incorrect" vs "unverifiable (lack of evidence)" match our UNVERIFIED idea | release location of the annotations not confirmed [U] |
| A14 | Too Noisy To Learn, cleaned CodeReviewer (Liu, Lin, Thongtanunam; arXiv 2502.02757, 2025) | https://arxiv.org/html/2502.02757v2 ; package https://zenodo.org/records/13150598 | not read [U] | cleaned sets 25-66% smaller than the original (e.g. 117K vs 39K) [S] | one review comment [S] | valid vs noisy [S] | MODEL labels on the full set (LLM, precision 66-85% for valid); a human-annotated sample to measure them [S] | as A7 [S] | not read [U] | v1.finding_class PROXY: "noisy" (vague, clarification-only) is close to INFO | paper: only 64% of sampled CodeReviewer training comments are valid; Tufano et al. found 32% noise in its test set [S] |
| A15 | CRAVE (Turing Enterprises; Hugging Face) | https://huggingface.co/datasets/TuringEnterprises/CRAVE | MIT [S]; comm. yes [S] | 1,200 samples, 600 APPROVE + 600 REQUEST_CHANGES, 1,174 rows across train/validation/test; 24.3 MB [S] | one PR state (base/head commit pair) from 123 repos, with diff, patch, description [S] | `label` APPROVE / REQUEST_CHANGES + `explanation` text + `hint` [S first rows] | "Human reviewers" with "automated and manual" validation; PRs picked by undisclosed heuristic rules; who wrote `explanation` is not stated [S card]; the APPROVE explanations read "The commit was approved by the reviewer." [S first rows] | many; English [S] | HF parquet [U] | v1.blocking PROXY close to EXACT at PR-state level: REQUEST_CHANGES -> true, APPROVE -> false; the REQUEST_CHANGES `explanation` is a finding-like note (INPUT for v1.finding_class) | card: open-source only; "Human reviewers may have bias based on hidden context of the repositories" [S]; the same PR appears in both classes at different commits (row 0 and row 1 share PR 4127) [S] |
| A16 | github-codereview (HF user ronantakizawa) | https://huggingface.co/datasets/ronantakizawa/github-codereview | license tag "other", details not given [S]; source repos limited to permissive licenses per the card [S]; comm. unclear [U] | 356k rows (train 334k, validation 10.5k, test 11k), 653 MB [S card header]; the card text also says 167K+ positive triplets and 51K+ negatives [S] (the two counts do not add up; not reconciled) | one inline review comment with ~50 lines of code before and after the author's change, or a negative chunk labelled "No issues found." [S] | `comment_type` in {suggestion, question, nitpick, bug, refactor, style, security, performance, none}; `quality_score` 0.0-1.0; `is_negative` [S] | comment text is human (bots excluded) and kept only if the code changed after it (a mined acted-on signal) [S]; how `comment_type` and `quality_score` were made is not disclosed [S absence] | 37 programming languages [S] | Parquet on HF [U] | v1.finding_class PROXY: nitpick/style -> INFO or FOLLOW-UP, bug/security -> BLOCKER candidates, question -> no slot; `is_negative` is a no-finding class our set lacks | type and score provenance undisclosed [S]; row counts inconsistent on the card [S] |

### 2.B Issue and bug-report triage (severity, priority, type, blocking)

| id | name | URL (card or paper) | license; comm. | size; download | unit | label set | how labels were made | lang | format | maps to (kind: how) | quality problems the source reports |
|---|---|---|---|---|---|---|---|---|---|---|---|
| B1 | The Public Jira Dataset (Montgomery, Luders, Maalej; MSR 2022) | https://arxiv.org/abs/2201.08368 ; data https://zenodo.org/records/15393866 | CC BY 4.0 on the record [S]; comm. yes [S] | 16 Jiras, 1,822 projects, 2.7M issues, 32M changes, 9M comments, 1M issue links [S]; ~50 GB MongoDB dump [S paper] | one Jira issue with its full change history, comments and links [S] | Jira fields incl. `priority`, `issuetype`, `resolution`, `status`, `issuelinks` (a unified "Block" link type: "An issue cannot be resolved until another issue is resolved") [S paper]; the exact priority values per Jira instance not read [U] | mined from the trackers: human project members set the fields; link types unified by the authors' qualitative labelling (75 -> 30 types) [S] | English mostly [U] | MongoDB dump [S] | v1.blocking PROXY: priority "Blocker" where an instance uses it [U], or an outgoing Block link; v1.finding_class PROXY via `resolution` values (e.g. duplicate -> KNOWN, cannot-reproduce -> UNVERIFIED) [U: values not read] | NOT DOWNLOADABLE NOW: Zenodo v6 (2025-05-13) says "Data has been removed while anonymising the data"; "This version does not contain the data itself"; files "Restricted" [S] |
| B2 | Mozilla CORE issue report dataset (Lopez Duran; Zenodo 2024) | https://doi.org/10.5281/zenodo.14229871 | not read [U] | 522,355 bug reports [S] | one Bugzilla bug with comments and history [S] | Bugzilla fields: Severity, Priority, Resolution, Keywords, Flags, Blocks, Depends on, Whiteboard, Target Milestone, ... [S] | mined from Bugzilla (human triagers' fields) via the Issuex tool [S] | English [U] | not read [U] | v1.blocking PROXY via release-tracking/blocking flags or keywords [U: flag values not read]; v1.finding_class PROXY via Severity + Resolution | none stated on the record [U] |
| B3 | Eclipse issue report dataset (Zenodo 2024) | https://zenodo.org/records/15348468 | not read [U] | 9 projects; the per-project table sums to 302,378 issues (Platform 122,497; JDT 63,266; ...) [S table, sum computed here] | one Bugzilla bug [S] | same Bugzilla field set as B2 incl. Severity, Priority, Flags, Blocks [S] | mined from Bugzilla [S] | English [U] | not read [U] | as B2 | none stated [U] |
| B4 | bugbug labels (Mozilla) | https://github.com/mozilla/bugbug/tree/master/bugbug/labels | MPL-2.0 (repo) [S]; comm. yes [S] | files: bug_nobug.csv, defect_enhancement_task*.csv, regression_bug_nobug.csv, regressionrange.csv, str.csv, tracking.csv, annotateignore.csv [S]; tracking.csv read as 102 rows (4 True) and bug_nobug.csv as 600 rows by the fetch tool [U: counts may be truncated]; README: the defect set "contains 2110 bugs" [S] | a Bugzilla bug id only; text must be fetched from Bugzilla [S header `bug_id,tracking`] | `tracking` True/False; `is_bug` True/False; defect/enhancement/task; regression [S] | human: "manually collected labels" [S README]; other bugbug models use Bugzilla fields such as the `regression` keyword, which "isn't used consistently" [S] | English [U] | CSV [S] | v1.blocking PROXY (weak): `tracking` = release management wants to track the bug; ids need a Bugzilla join (outward API reads) | README: keyword-based labels are inconsistent [S] |
| B5 | "It's not a bug, it's a feature" reclassification (Herzig, Just, Zeller; ICSE 2013) | https://www.st.cs.uni-saarland.de/softevo/bugclassify/paper/icse2013-bugclassify.pdf ; data page http://www.st.cs.uni-saarland.de/softevo/bugclassify/ | not read [U] | 7,401 closed-and-fixed issue reports, 5 projects (HTTPClient, Jackrabbit, Lucene-Java, Rhino, Tomcat5) [S] | one issue report (ids; text re-fetched from the trackers per a later user of the data) [S Kochhar et al. PDF] | BUG, RFE, IMPR, DOC, REFAC, OTHER and more (11 categories) [S paper] | human: first author classified all 7,401 by a fixed rule set; second author re-inspected 3,093 candidates blind; 340 conflicts resolved jointly [S] | English, Java projects [S] | not read [U] | v1.finding_class PROXY (weak): the paper's rule "reports violations of JAVA contracts without causing failures" -> OTHER is close to a non-blocking finding; v1.blocking INPUT-ONLY | paper: 33.8% of BUG reports misclassified in the source trackers; misclassification ratios "a lower bound" [S] |
| B6 | Bug root-cause types (Catolino, Palomba, Zaidman, Ferrucci; JSS 2019) | https://arxiv.org/abs/1907.11031 | not read [U] | 1,280 sampled, 1,139 classified after 141 discarded [S] | one fixed-and-closed bug report (Mozilla, Apache, Eclipse; 119 projects) [S] | 9 types: Configuration, Network, Database, GUI, Performance, Permission/Deprecation, Security, Program Anomaly, Test Code [S] | human: iterative content analysis by the authors [S] | English [S] | online appendix, format not read [U] | ap.violates_row PROXY: (report, one root-cause type definition) -> yes/no over 9 rows | classifier F-measure 64% [S]; 123 of 1,280 were improvement proposals, not bugs [S] |
| B7 | NLBSE issue report classification ('23: 1.4M issues; '24: 3,000 issues) | https://github.com/nlbse2023/issue-report-classification ; https://github.com/nlbse2024/issue-report-classification | '23 repo AGPL-3.0 [S]; '24 repo "Other (NOASSERTION)" [S]; comm. unclear [U] | '23: 1,275,881 train + 142,320 test [S]; '24: 3,000 balanced (5 repos) [S] | one GitHub issue (title + body) [S] | '23: bug, feature, question, documentation; '24: bug, feature, question [S] | mined: maintainers' GitHub labels, synonyms mapped (Izadi et al.) [S] | English [S] | CSV [S] | INPUT-ONLY for our types (issue type, not severity or disposition) | '24 paper: "Variability in labeling rationale of the dataset was the main item of critique in previous editions" [S] |
| B8 | Blocking-bug prediction corpora (Garcia & Shihab MSR 2014; Chen et al. 2022) | https://dl.acm.org/doi/10.1145/2597073.2597099 ; https://doi.org/10.53106/160792642022092305018 | not read [U] | Chen et al.: 129,178 reports from 7 trackers, 10,129 (7.84%) blocking [S] | one bug report (summary + description) [S] | blocking vs non-blocking [S] | mined: the Bugzilla "Blocks" field (Chromium: "Blocking") [S] | English [S] | not read [U] | v1.blocking PROXY with a SEMANTIC GAP: here "blocking" = one unfixed bug prevents fixing another, not "blocks a merge" [S definition] | Garcia & Shihab models reach F-measures of 15-42% [S abstract] |
| B9 | Prioritising GitHub Priority Labels (Caddy et al.; PROMISE 2024) | https://zenodo.org/records/10894272 ; paper https://arxiv.org/pdf/2405.10891 | CC BY 4.0 [S]; comm. yes [S] | one CSV of label names, 19.6 kB, from the 5,000 most-starred GitHub repos (June 2022) [S] | one repository label name (not an issue) [S] | priority-related labels "ranked and normalised into three values; 'High', 'Medium', and 'Low'" [S] | human: "manually categorized" [S] | English label names [S] | CSV + a helper script [S] | v1.blocking INPUT: a ready map from projects' own labels (P0, critical, blocker, ...) to High/Medium/Low, for mining issues that carry them; no issue text included | a label map only; issues must be fetched from GitHub [S] |

### 2.C Code smells and anti-patterns

| id | name | URL (card or paper) | license; comm. | size; download | unit | label set | how labels were made | lang | format | maps to (kind: how) | quality problems the source reports |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C1 | MLCQ, industry-relevant code smells (Madeyski & Lewowski; EASE 2020) | https://zenodo.org/records/3666840 ; paper https://madeyski.e-informatyka.pl/download/MadeyskiLewowski20EASE.pdf | CC BY 4.0 [S]; comm. yes [S] | 14,739 reviews of 4,770 code samples (8,040 class reviews, 6,699 function reviews) [S]; MLCQCodeSmellSamples.csv 7.5 MB, total 9.7 MB [S] | one (code sample, smell) review by one developer; code is a link + commit + line range, not inlined [S] | smell in {Blob, Data Class, Feature Envy, Long Method} x severity {critical, major, minor, none} [S] | human: 26 developers with professional experience, no smell definitions imposed ("to extract professional developers' contemporary understanding") [S] | Java [S] | CSV/XLSX; header `id,reviewer_id,sample_id,smell,severity,review_timestamp,type,code_name,repository,commit_hash,path,start_line,end_line,link,is_from_industry_relevant_project` [S https://zenodo.org/records/3590102] | ap.violates_row PROXY: (code sample, one smell row) -> severity; none = false, else true; severity also a PROXY for v1.finding_class weight | paper: first 2,175 samples drawn under a randomisation defect; 454 samples by reviewers who skipped the survey [S] |
| C2 | DACOS / DACOSX (Nandani, Saad, Sharma; MSR 2023) | https://zenodo.org/records/7570428 ; paper https://arxiv.org/abs/2303.08729 | not read [U] | DACOS: 10,267 annotations for 5,192 snippets from 86 annotators; DACOSX: 207,605 snippets [S] | one code snippet x one smell [S] | multifaceted abstraction, complex method, long parameter list: present / absent [S] | human for DACOS (two annotations per sample, TAGMAN web tool); HEURISTIC metric thresholds for DACOSX [S] | Java [U] | SQL tables (annotations, sample, metrics) [S] | ap.violates_row PROXY (snippet, smell row) -> yes/no | paper: two annotations per sample can contradict; plan to move to three [S] |

### 2.D Static-analysis warning actionability

| id | name | URL (card or paper) | license; comm. | size; download | unit | label set | how labels were made | lang | format | maps to (kind: how) | quality problems the source reports |
|---|---|---|---|---|---|---|---|---|---|---|---|
| D1 | The Technical Debt Dataset (Lenarduzzi, Saarimaki, Taibi; PROMISE 2019) | https://github.com/clowee/The-Technical-Debt-Dataset ; paper https://arxiv.org/abs/1908.00827 | CC BY-NC-SA 4.0 [S README]; comm. NO [S] | 1,840,217 SonarQube issues (Table 1 total), 33 Apache Java projects, 78K commits [S paper]; download size not read [U] | one SonarQube issue on one commit [S] | severity BLOCKER, CRITICAL, MAJOR, MINOR, INFO; type BUG / VULNERABILITY / CODE_SMELL (the README query uses TYPE='BUG' and 'VULNERABILITY') [S paper + README] | HEURISTIC: the tool's rule sets the severity; not a human judgment of the instance [S paper] | Java [S] | CSV + SQLite [S] | v1.finding_class PROXY: SonarQube names overlap ours (BLOCKER, INFO) but mean rule-level impact, not a verified finding; v1.blocking PROXY (BLOCKER/CRITICAL, which SonarQube says to review "immediately") | README: items "exported as reported by the tools. We did not excluded duplications nor filtered any technical debt issues" [S]; SonarQube claims zero false positives only for reliability/maintainability rules [S paper] |
| D2 | NASCAR, (Non-)Actionable Static Code Analysis Reports (Koszo, Aladics, Ferenc, Hegedus; arXiv 2511.10323, 2025-11-13) | https://zenodo.org/records/17079912 ; paper https://arxiv.org/html/2511.10323 | CC BY 4.0 [S]; comm. yes [S] | 1,227,763 records: 196,940 actionable (16%), 1,030,823 non-actionable (84%); deduplicated file 1,083,073 [S paper]; nascar.zip 447.9 MB + manual-eval xlsx 31.1 kB [S] | one static-analysis warning (Java, commits since 2022-01-01) [S] | actionable (A) vs non-actionable (NA) [S] | HEURISTIC from later commits: a parent-commit warning is actionable when a Java change touches its context and its message is gone from the changed part; non-actionable when it persists [S paper] | Java; tools PMD and SpotBugs in the released table (Checkstyle excluded) [S paper] | Parquet (`dataset.parquet`, `deduplicated.parquet`) + `files.zip` of sources [S paper] | v1.blocking PROXY (weak): "developers fixed it" vs "left it"; the rule id + message form a (row, instance) pair close to ap.violates_row's shape but the label answers "acted on", not "matches" | paper defines NA as "systematically not addressed, irrespective of the underlying reason" [S]; duplicates of NA kept only at last occurrence [S] |
| D3 | Actionable-warning benchmark after the Golden Features leak fix (Kang, Le, Lo; ICSE 2022) | https://arxiv.org/abs/2202.05982 | not read [U] | test revision warnings cut from 15,695 to 2,615 after dedup [U: from a search-engine summary, not the paper] | one FindBugs/SpotBugs warning [U] | actionable vs unactionable [U] | HEURISTIC (warning closed in a later revision) then partly manual in the paper [U] | Java [U] | not read [U] | v1.blocking PROXY (weak) | the paper's point: data leakage + duplication inflated prior results [U: search-engine summary] |
| D4 | "New Real-World Dataset" of SonarQube warnings (Hegedus & Ferenc; IEEE Access 2022) | https://doi.org/10.1109/access.2022.3176865 ; package https://doi.org/10.5281/zenodo.5885653 | not read [U] | 224,484 warnings of 160 SonarQube rule types from 9,958 Java projects: 47,015 true positive, 177,469 false positive [S paper] | one SonarQube warning with its code context [S] | true positive (fixed) vs false positive (explicitly ignored) [S] | mined developer ACTIONS: a commit that removes the warning = true positive; a `//NOSONAR` comment placed by developers = false positive [S] | Java [S] | replication package, format not read [U] | v1.finding_class PROXY: an explicit suppression is an owner's "no action" decision (INFO-like), a fix is an acted-on finding; v1.blocking PROXY (weak) | rule types with only one class were dropped (337,438 found, 224,484 kept) [S]; a NOSONAR line can carry several warnings, all counted as false positives [S] |

### 2.E Vulnerability and CWE classification

| id | name | URL (card or paper) | license; comm. | size; download | unit | label set | how labels were made | lang | format | maps to (kind: how) | quality problems the source reports |
|---|---|---|---|---|---|---|---|---|---|---|---|
| E1 | CTIBench, task CTI-RCM (Alam, Bhusal et al.; arXiv 2406.07599) | https://huggingface.co/datasets/AI4Sec/cti-bench ; repo https://github.com/xashru/cti-bench | CC BY-NC-SA 4.0 [S card]; comm. NO [S] | CTI-RCM 1,000 rows + CTI-RCM-2021 1,000 rows [S repo README] | one CVE description [S] | one CWE id (`GT`) [S sample row: CVE-2024-23848 -> CWE-416] | taken from NVD's CWE mapping [U: implied by the NVD URL column, not stated on the card] | English [S] | TSV [S] | ap.violates_row PROXY: (description, weakness catalogue) -> which row; a binary per-candidate form needs the CWE catalogue as the "rows" | small (1,000) [S] |
| E2 | CVE-to-CWE Consensus (exploitintel; Hugging Face, v3) | https://huggingface.co/datasets/exploitintel/cve-cwe-consensus | CC BY 4.0 [S]; comm. yes [S] | 71,640 examples: 50,074 / 11,052 / 10,514 [S]; 40 MB Parquet [S] | one CVE description [S] | 127 CWE types of View-1003, multi-label (about 14% multi) [S] | intersection of two official human sources: NVD analyst CWE and CNA-supplied CWE, rolled up to View-1003 [S] | English [S] | Parquet, chat `messages` format [S] | ap.violates_row PROXY: each (description, CWE row) pair gives a yes/no; negatives are the other View-1003 rows | card: recency-skewed (2023+); consensus drops ~67% of scanned CVEs where the sources disagree or give no CWE, so the set is "cleaner/easier"; roll-up discards child-CWE detail [S] |
| E3 | cve-to-cwe with ATT&CK (xamxte; Hugging Face) | https://huggingface.co/datasets/xamxte/cve-to-cwe | not read [U] | 205 CWE classes; row count not read [U] | one CVE description [S] | single CWE id (205 classes) + ATT&CK technique list (361) [S] | "Built from NVD with AI-assisted label refinement" [S] -> partly MODEL | English [S] | not read [U] | ap.violates_row PROXY (as E2) | card: single-label although "some vulnerabilities may involve multiple weakness types" [S] |

### 2.F CI-failure and flaky-test triage

| id | name | URL (card or paper) | license; comm. | size; download | unit | label set | how labels were made | lang | format | maps to (kind: how) | quality problems the source reports |
|---|---|---|---|---|---|---|---|---|---|---|---|
| F1 | IDoFT, International Dataset of Flaky Tests (Lam et al., UIUC; living dataset) | https://github.com/TestingResearchIllinois/idoft | no license shown on the repo page [S absence]; comm. unclear [U] | "2000+ flaky tests detected ... and 500+ flaky tests fixed" per the maintainer's page [S https://mir.cs.illinois.edu/winglam/software.html]; CSV sizes not read [U] | one flaky test at one commit (Java Maven, Java Gradle, Python) [S] | Category: OD, OD-Brit, OD-Vic, ID, ID-HtF, NIO, NOD, NDOD, NDOI, UD, OSD, TD, TZD; Status: blank, Opened, Accepted, InspiredAFix, DeveloperWontFix, DeveloperFixed, Deleted, Rejected, ... [S] | mixed: category from detection tools (iDFlakies, NonDex) and contributors; Status from the upstream developers' response to a fix PR [S] | Java, Python [S] | CSV (pr-data.csv, gr-data.csv, py-data.csv) [S] | v1.finding_class PROXY via Status: Rejected / DeveloperWontFix = a fix the owners judged unnecessary (INFO-like), Accepted = acted on; v1.blocking INPUT-ONLY | crowd-sourced; "Please use UD if you do not know the category" [S] |
| F2 | FlakeStorm (HF user ahenrij; authors not read) | https://huggingface.co/datasets/ahenrij/flakestorm | CC BY 4.0 [S]; comm. yes [S] | ~4,200 labeled GitLab CI job logs, 8 projects, 2016-2024, ~160 KB per log [S] | one failed CI job log [S] | 30 fine categories (e.g. flaky_test, dependency_installation_failure, container_oom_error, job_execution_timeout) + 5 GitLab coarse `failure_reason` values [S] | HEURISTIC: "the regex-based tool developed in this paper"; only jobs with an assignable intermittent category kept [S] | English logs [S] | Parquet/HF [U] | ap.violates_row PROXY: (log, one failure-category definition) -> yes/no over 30 rows; every row is an intermittent failure, so no negatives of the "real regression" kind | card: logs "have not been further sanitized beyond what GitLab exposes publicly" [S] |
| F3 | FlakeFlagger data (Alshammari et al.; venue not read [U]) | https://github.com/AlshammariA/FlakeFlagger (code); archive contents described at https://par.nsf.gov/biblio/10101224 (that page mixes the iDFlakies abstract with the FlakeFlagger archive text) | not read [U] | 24 projects, each test suite rerun 10,000 times [S] | one test [S] | flaky / not flaky (pass and fail observed on the same code), plus per-test features [S] | EXECUTION: 10,000 reruns [S] | Java [S] | CSV + build-log tarballs [S] | INPUT-ONLY / weak PROXY for v1.blocking ("a failure that is not a real defect") | the study found some flaky tests stay undetected even after 10,000 reruns [S] |
| F4 | Flaky builds in GitHub Actions (arXiv 2602.02307, 2026) | https://arxiv.org/html/2602.02307v1 ; site https://flaky-build.github.io/ | not read [U] | CI builds from 1,960 open-source Java projects [S]; labeled-set size not read [U] | one failed GitHub Actions job [S] | flaky vs non-flaky failure; 15 failure categories (flaky tests 64.99% of flaky failures; network 15.8%; ...) [S] | mined from later events: "If a failed job was rerun by developers and subsequently succeeded, we directly labeled ... flaky"; categories by regex patterns built iteratively by hand [S] | English logs [S] | not read [U] | v1.blocking PROXY: a non-flaky (deterministic) failure is closer to a reproduced break than a flaky one | paper: jobs rerun few times or never make "non-flaky" labels miss low-rate flakes (false negatives) [S] |
| F5 | logdx-ci (Hugging Face) | https://huggingface.co/datasets/eyuansu71/logdx-ci | not read [U] | 35 cases across 6 splits [S] | one GitHub Actions failure log + ground truth [S] | 8 failure categories (test_assertion, compile_error, type_error, lint_failure, dependency_install, docker_build, timeout_or_oom, multi_failure) + root-cause summary + flaky_or_transient flag [S] | MODEL + human: "AI-drafted + author-verified root cause" [S] | English logs [S] | JSONL + per-case files [S] | v1.finding_class INPUT-ONLY (too small to train; test-only size) | small (35) [S] |

### 2.G Agent trajectories with step or outcome labels

| id | name | URL (card or paper) | license; comm. | size; download | unit | label set | how labels were made | lang | format | maps to (kind: how) | quality problems the source reports |
|---|---|---|---|---|---|---|---|---|---|---|---|
| G1 | MAST-Data / MAD (Cemri et al., "Why Do Multi-Agent LLM Systems Fail?"; NeurIPS 2025 poster, https://neurips.cc/virtual/2025/poster/121528) | https://huggingface.co/datasets/mcemri/MAST-Data ; paper https://arxiv.org/abs/2503.13657 | CC BY 4.0 [S]; comm. yes [S]; no gating stated [S] | 1,642 traces (`MAD_full_dataset.json`) + 19 rows human set [S card]; paper says 21 human traces [S] (discrepancy) | one multi-agent execution trace (7 MAS frameworks, 8 benchmarks) [S] | 14 binary failure modes (1.1 Disobey Task Specification ... 3.3 Incorrect Verification), each 1 / 0 / null [S] | MODEL for the 1,642: "Annotations are produced by an LLM judge, not by human labelling" (o1; kappa 0.77 vs experts) [S]; taxonomy built by humans, IAA kappa 0.88 [S] | English traces [S] | JSON [S] | ap.violates_row EXACT in shape: (trace, one failure-mode definition) -> yes/no, 14 candidates per trace; the labels are LLM-made | human set uses different taxonomy revisions per round (18, 17, 17, 14 modes), "not comparable across rounds" [S]; authors do not claim the taxonomy is exhaustive [S] |
| G2 | TRAIL, Trace Reasoning and Agentic Issue Localization (Deshpande et al., Patronus AI; 2025) | https://huggingface.co/datasets/PatronusAI/TRAIL ; paper https://arxiv.org/abs/2505.08638 | MIT tag [S]; GATED: users agree not to reshare outside a gated repo and "must not use this dataset for training systems ... intended to automate human evaluation" [S]; comm. unclear; training use NO [S] | 148 traces (118 GAIA, 30 SWE-bench), 841 errors, 1,987 spans (575 with an error); 241 MB [S] | one error on one OpenTelemetry span of an agent trace [S] | error category from a 20+ type taxonomy (reasoning, planning/coordination, system execution) + impact Low / Medium / High + evidence + description [S] | human: four expert annotators, four review rounds; 5.63% (SWE) / 5.31% (GAIA) of spans changed in review [S] | English [S] | JSON [S] | ap.violates_row PROXY (span + taxonomy category); v1.finding_class PROXY via impact (High / Medium / Low); test-only by its terms | card: category imbalance, Output Generation errors ~42% [S]; text-only [S] |
| G3 | Who&When (Zhang et al.; ICML 2025) | https://huggingface.co/datasets/Kevin355/Who_and_When ; paper https://arxiv.org/abs/2505.00212 | not read [U] | 184 annotated failure tasks from 127 multi-agent systems [S paper] | one failure log (GAIA / AssistantBench queries) [S] | failure-responsible agent, decisive error step, natural-language reason [S] | human: three experts, three rounds (confident / uncertain split, consensus discussion, cross-validation) [S] | English [S] | JSON [U] | ap.violates_row INPUT-ONLY: the reason text is a mechanism note, but there is no fixed row set | best automated method: 53.5% agent-level, 14.2% step-level accuracy [S] |
| G4 | SWE-agent-trajectories (Nebius) | https://huggingface.co/datasets/nebius/SWE-agent-trajectories | CC BY 4.0 now (an older revision said MIT) [S]; card: model outputs fall under the Llama 3.1 license; per-repo licenses apply [S]; comm. yes with those conditions [U] | 80,036 trajectories (13,389 resolved, 66,647 not) [S]; download 1.11 GB, 5.63 GB on disk [S] | one full agent trajectory + final patch + test logs [S] | `target` bool (issue resolved), `exit_status` [S] | EXECUTION: the patch is run against the linked PR's tests [S] | English, Python repos [S] | Parquet [S] | v1.blocking PROXY (weak): a failing patch with its `eval_logs` is a reproduced break at patch level, not a finding-level label | "synthetic" tag; outcome label only, no step labels [S] |
| G5 | SWE-bench Verified human annotations (OpenAI with the SWE-bench authors; 2024) | https://openai.com/index/introducing-swe-bench-verified/ ; rubric https://cdn.openai.com/introducing-swe-bench-verified/swe-b-annotation-instructions.pdf | not read for the annotation zip [U] | 1,699 annotated samples, 3 annotators each, 93 developers [S] | one (issue, gold patch, test patch) sample [S] | underspecified 0-3, tests-false-negative 0-3, difficulty bucket, other-major-issues flag; free-text explanation (min 100 chars) asked per question [S rubric] | human: professional developers after onboarding tests; ensemble = max severity of 3 [S] | English, Python [S] | CSV `ensembled_annotations_public.csv` (zip name `swe-bench-annotation-results.zip` per a search summary [U]); header read from a copy in https://github.com/uw-swag/BouncerBench [S copy]: per-question score + `*_notes` text + `*_decided_by` + `filter_out` | v1.blocking PROXY: "labels 2 and 3 are severe and indicate that the sample ... should be discarded" is a keep/block decision; v1.finding_class PROXY via 0-3 severity; the released `underspecified_notes` / `false_negative_notes` / `other_notes` columns are finding-like notes [S copy] | OpenAI: the filter "is likely to be overzealous" (max-of-3 ensembling raises false removals) [S] |
| G6 | AgentErrorBench (Zhu et al., "Where LLM Agents Fail and How They Can Learn From Failures"; arXiv 2509.25370) | https://github.com/ulab-uiuc/AgentDebug ; paper https://arxiv.org/abs/2509.25370 | repo MIT [S]; data on Google Drive with no data license stated [S absence]; comm. unclear [U] | 200 failed trajectories: ALFWorld 100, GAIA 50, WebShop 50 [S] | one decision step of an agent trajectory [S] | 17 error types in 5 modules (memory, reflection, planning, action, system), e.g. constraint_ignorance, progress_misjudge, tool_execution_error; plus the minimal set of root-cause steps and feedback [S] | human: ten graduate-student annotators, step level, three pilot rounds [S] | English [S] | JSON on Google Drive [U] | ap.violates_row PROXY: (step or trajectory, one error-type row) -> yes/no over 17 rows | agreement figure not read [U]; non-SE environments (ALFWorld, WebShop) dominate [S] |
| G7 | MP-Bench, multi-perspective failure attribution (Adobe Research; arXiv 2603.25001) | https://huggingface.co/datasets/Yeonjun/MP-Bench ; raw data https://github.com/adobe-research/multi-agent-eval-bench/tree/main/MP-Bench | "adobe-research-license" tag [S]; comm. not read [U] | 295 files: manual 169, automatic 126 [S] | one step of a multi-agent trace [S] | per step: fail_annotation 0/1, fail_category, fail_reason, ideal_action [S]; category list not read [U] | human: three annotators, kept separate, consolidated later with an LLM summary [S] | English [U] | JSON, built by scripts from pointers to source logs [S] | ap.violates_row PROXY (step, fail_category); fail_reason is a mechanism note | viewer unavailable; data must be rebuilt locally from source logs [S] |

### 2.H Code-review preference, critique and judge datasets

| id | name | URL (card or paper) | license; comm. | size; download | unit | label set | how labels were made | lang | format | maps to (kind: how) | quality problems the source reports |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H1 | CodeCriticBench (m-a-p; arXiv 2502.16614, 2025) | https://huggingface.co/datasets/m-a-p/CodeCriticBench | not read on the card [U] | 4,300 samples (3,200 code generation, 1,100 code QA) [S] | one (question, answer) pair to critique [S] | Correct / Error; 10 per-dimension checklist scores; final score; difficulty Easy/Medium/Hard [S] | EXECUTION for code generation (all tests pass = Correct); human for code QA (3 of 20 volunteers per item, majority vote); checklist scores by 3 LLMs calibrated on 20% human ratings; difficulty from 12 LLMs' accuracy [S] | Python + others [U] | JSONL [S] | v1.blocking PROXY (weak): Correct / Error of an answer, not of a finding | code QA questions are LLM-generated (Qwen2.5-72B) from StackOverflow material [S] |
| H2 | CodeJudgeBench (2025) | https://huggingface.co/datasets/mattymchen/codejudgebench | Apache-2.0 [S]; comm. yes [S] | not read [U] | a (question, positive response, negative response) triple [S] | pairwise correct vs incorrect for codegen, coderepair, testgen [S] | EXECUTION (responses from several LLMs checked by tests) [U] | code [S] | HF parquet [U] | INPUT-ONLY: pairwise code correctness, no finding or registry row | not read [U] |

### 2.I Incident reports and postmortems (the input type of `ap.violates_row`)

| id | name | URL (card or paper) | license; comm. | size; download | unit | label set | how labels were made | lang | format | maps to (kind: how) | quality problems the source reports |
|---|---|---|---|---|---|---|---|---|---|---|---|
| I1 | VOID, Verica Open Incident Database | https://www.usenix.org/system/files/sre22amer_slides_nash.pdf ; https://www.thevoid.community/report-2024 | not read [U] | 1,856 public incident reports from 610 organizations, 2008 to March 2022 [S SREcon 2022 slides] | one public incident report (postmortem, status page, blog, talk, news) [S] | metadata: impact type tags, technologies, duration, report type, analysis format (Root Cause, Contributing Factors, ...) [S] | human curation from the report text; impact tags "do not represent a formal classification system" [S] | English [U] | web database; bulk export not confirmed [U] | ap.violates_row INPUT-ONLY: incident notes a teacher could pair with our registry rows | curators say impact tags are informal [S]; current bulk availability not confirmed [U] |
| I2 | postmortems.app, Postmortem Index | https://postmortems.app/about | not read [U] | 242 postmortems, 111 companies, 8 categories [S] | one public postmortem with a summary [S] | categories such as Automation, Cascading Failure, Config Change, Security, Cloud, Hardware [S] | human (maintainers and contributors), building on danluu/post-mortems [S] | English [S] | JSON read-only API under `/output/` [S] | ap.violates_row PROXY (8 coarse categories as rows) or INPUT-ONLY | small [S] |
| I3 | Post-mortems-Analysis, cloud incidents (IntelligentDDS) | https://github.com/IntelligentDDS/Post-mortems-Analysis | not read [U] | 354 public post-mortems from Azure, Google Cloud, AWS [S] | one post-mortem, raw and structured [S] | structured template fields (fault occurrence, detection, identification, mitigation) [S] | human structuring by the study's authors [S] | English [S] | repo files [S] | ap.violates_row INPUT-ONLY | not read [U] |
| I4 | Token Budgets, catalog of LLM-agent budget-overrun incidents (Khan; arXiv 2606.04056, 2026-06-02) | https://arxiv.org/html/2606.04056 ; artifact https://github.com/sajjadanwar0/token-budgets | paper CC BY 4.0 [S]; catalog CSV license not read [U] | 63 confirmed incidents from 21 agent frameworks (2023-2026) + 47 structural entries; N=113 rows in the four-class sample [S] | one incident backed by a quoted GitHub issue [S] | four-class scheme (validated) + an eight-cluster mechanism taxonomy (exploratory) [S] | human: two independent raters; kappa 0.837 on the four-class scheme (0.943 on the 79 rows both marked confirmed); only 0.44 on the eight-cluster assignment [S] | English [S] | CSV in the artifact [S] | ap.violates_row PROXY with the closest DOMAIN match found (agent-system incidents mapped to a mechanism catalogue), but tiny | author: the eight-way partition is "exploratory", agreement "moderate" (kappa 0.44) [S] |

### 2.J Security-report and audit-finding triage (added family: the closest public analogue of a judged finding)

| id | name | URL (card or paper) | license; comm. | size; download | unit | label set | how labels were made | lang | format | maps to (kind: how) | quality problems the source reports |
|---|---|---|---|---|---|---|---|---|---|---|---|
| J1 | HackerOne disclosed reports (HF org `Hacker0x01`, HackerOne's GitHub handle; org ownership not verified [U]; a mirror `elamaran619/hackerone_disclosed_reports`) | https://huggingface.co/datasets/Hacker0x01/hackerone_disclosed_reports ; state definitions https://docs.hackerone.com/en/articles/8475030-report-states | "made available under HackerOne's Terms of Service" [S]; comm. not stated [U] | official: 18.7 MB, row count not served (viewer "config-size" error) [S]; mirror: 10,094 rows [S mirror statistics] | one disclosed vulnerability report [S] | `substate`: resolved, informative, duplicate, not-applicable, spam; mirror counts 8,823 / 789 / 217 / 242 / 23 [S mirror]; `weakness` {id, name}; `original_report_id` for duplicates [S]; NO per-report severity column in the features (the scope's `max_severity` is asset-level) [S features list] | human: program triage teams and HackerOne triagers set the state [S docs] | English [S] | parquet/JSON on HF [U] | v1.finding_class PROXY close to EXACT for 3 of 6 classes: duplicate -> KNOWN, informative -> INFO, not-applicable -> UNVERIFIED-like; resolved -> BLOCKER or FOLLOW-UP (no severity to split them); `weakness` gives an ap.violates_row PROXY | disclosure bias: only disclosed reports; mirror: 2,504 of 10,094 rows have `visibility: no-content` (body withheld) [S mirror]; report text contains researcher names and handles [S sample] |
| J2 | Code4rena audit findings (per-contest GitHub repos `code-423n4/*-findings`, plus derived sets) | rules https://docs.code4rena.com/competitions/judging-criteria ; https://docs.code4rena.com/competitions/severity-categorization ; derived: https://zenodo.org/records/17571169 (C4Audit, CC BY 4.0), https://huggingface.co/datasets/xanoutas/solidity-security-findings (MIT tag), https://huggingface.co/datasets/leohachico/audit-findings-dataset ("license: other") | source repos: no dataset license read [U]; C4Audit CC BY 4.0 [S]; xanoutas MIT tag [S] but a third-party card warns contest-finding redistribution rights are "uncertain even when the dataset wrapper claims MIT" [S https://huggingface.co/datasets/samscrack/solidity-audit-cot] | C4Audit: 342 audits, reports zip 8.4 MB [S]; xanoutas: 18,869 rows per the card fetch, HIGH 4,418, MEDIUM 4,910 [S] (an Exa highlight said 9,359 [U], discrepancy); leohachico: 23,625 findings [S] | one warden submission (issue) or one published finding [S] | judge labels on the issue: `3 (High Risk)`, `2 (Med Risk)`, `QA (Quality Assurance)`, grades A/B/C, `sufficient quality report`, `duplicate`, sponsor `confirmed` / `disputed` / `acknowledged`, `disagree with severity` [S repo READMEs + sample issue]; validity "sufficient, insufficient, or low quality/spam" [S rules] | human: a judge decides validity, severity and duplicates, with sponsor input [S rules] | English + Solidity [S] | GitHub issues (source); JSON / Parquet (derived) [S] | v1.finding_class PROXY close to EXACT: High/Med -> BLOCKER, QA-Low -> FOLLOW-UP, informational -> INFO, duplicate or listed "known issues" -> KNOWN, "insufficient proof" -> UNVERIFIED [S rule texts]; v1.blocking PROXY (High/Med vs rest). Derived sets keep mostly the ACCEPTED findings, so the invalid / unsatisfactory / duplicate negatives live only in the source repos; Code4rena's own `findings.csv` holds "valid Code4rena findings" only [S https://docs.code4rena.com/awarding/awarding-process] | rules: a finding "may be factually true ... but ... may be deemed invalid"; leohachico card: inconsistent severity strings, 216 rows `Unknown`, 136 duplicate descriptions [S] |

## 3. The five closest fits (deep)

Selection rule used here (stated so the coordinator can re-rank): closeness of the UNIT (a note or finding, optionally
paired with one catalogue row) plus a label that maps onto one of our three label sets by a written rule, with the
label source stated. Two picks per the ranking-shaped question (`ap.violates_row`, `v1.finding_class`) and one for
`v1.blocking`. This is a selection for depth, not a recommendation. The rows that nearly made the list are named at the
end of this section.

### 3.1 G1 MAST-Data (multi-agent failure traces x 14 failure modes) -> `ap.violates_row`

Schema excerpt, verbatim from the card https://huggingface.co/datasets/mcemri/MAST-Data [S]:

```
| `mas_name` | string | AG2, MetaGPT, ChatDev, Magentic, AppWorld, HyperAgent, OpenManus |
| `llm_name` | string | GPT-4o, Claude, GPT-4o-mini, Qwen, CodeLlama |
| `benchmark_name` | string | ProgramDev, ProgramDev-v2, GSM, Olympiad, GAIA, MMLU, Test-C, SWE-Bench-Lite |
| `trace_id` | int | index within its config |
| `trace` | dict | `{key, index, trajectory}` |
| `mast_annotation` | dict | 14 codes →`1`,`0`, or`null` where the annotation is unavailable |
```

First 3 rows, as returned by the dataset viewer API
(https://datasets-server.huggingface.co/first-rows?dataset=mcemri/MAST-Data&config=default&split=train) [S, fields
summarised by the fetch tool; the annotation dict arrived truncated]:

```
row 0: mas_name "ChatDev", llm_name "GPT-4o", benchmark_name "ProgramDev", trace_id 0,
       trace.trajectory starts "[2025-31-03 19:09:41 INFO] **[Preprocessin",
       mast_annotation {"1.1":0,"1.2":0,"1.3":0,"1.4":0,"1.5":0,"2.1":0,"2.2":0,"2.3":0,"2.4":0,"2.5":0,"2.6":0,"3.1":0,"3. ...
row 1: same system, trace_id 1, trajectory starts "[2025-31-03 19:30:18 INFO] **[Preprocessin", annotation reported as all 0
row 2: same system, trace_id 2, trajectory starts "[2025-31-03 19:48:48 INFO] **[Preprocessin", annotation reported as all 0
```

The 14 codes (card [S]): 1.1 Disobey Task Specification, 1.2 Disobey Role Specification, 1.3 Step Repetition, 1.4 Loss
of Conversation History, 1.5 Unaware of Termination Conditions, 2.1 Conversation Reset, 2.2 Fail to Ask for
Clarification, 2.3 Task Derailment, 2.4 Information Withholding, 2.5 Ignored Other Agent's Input, 2.6 Reasoning-Action
Mismatch, 3.1 Premature Termination, 3.2 No or Incomplete Verification, 3.3 Incorrect Verification.

Mapping onto `ap.violates_row`:

| theirs | ours | kind |
|---|---|---|
| one trace | the incident or bug note | PROXY: their unit is a whole execution trace ("each averaging over 15,000 lines of text" for the 150 analysis traces [S paper]); ours is a short note (the teacher rows show `input_tokens` 880 for an `ap.violates_row` question [S labels.jsonl row 1]) |
| one failure-mode definition (14 per trace) | one registry row (16 candidates per entry) | EXACT in shape: one yes/no per (unit, row) pair, ranked within the unit |
| `1` | `true` | EXACT |
| `0` | `false` | EXACT |
| `null` | no mapping (drop the pair) | - |
| (none) | the row's greppable signature | UNMAPPED: MAST rows carry a one-sentence definition only, kept in the paper's "Appendix A: MAST Failure Categories: Deep Dive", not in the JSON; e.g. FM-3.2 "(partial) omission of proper checking or confirmation of task outcomes or system outputs", FM-1.3 "Unnecessary reiteration of previously completed steps in a process, potentially causing delays" [S https://arxiv.org/html/2503.13657v3] |

Label source: an LLM judge (o1) for all 1,642 traces, kappa 0.77 against experts [S]; human labels exist only for 19-21
traces and across four taxonomy revisions [S]. License CC BY 4.0, no gating stated [S]. Files: MAD_full_dataset.json
200 MB, MAD_human_labelled_dataset.json 2.66 MB [S tree page].

### 3.2 E2 CVE-to-CWE Consensus (vulnerability note x CWE catalogue row) -> `ap.violates_row`

First 3 rows, from the viewer API
(https://datasets-server.huggingface.co/first-rows?dataset=exploitintel/cve-cwe-consensus&config=default&split=train)
[S; long user texts cut at about 300 characters by the fetch tool]:

```
row 0: system "You are a vulnerability analyst. Given a CVE description, reply with only the CWE ID(s) it maps to, comma-separated."
       user "The Net::EasyTCP package before 0.15 for Perl always uses Perl's builtin rand(), which is not a strong random number generator, for cryptographic keys."
       assistant "CWE-338"
row 1: user "TCP firewalls could be circumvented by sending a SYN Packets with other flags (like e.g. RST flag) set, which was not correctly discarded by the Linux TCP stack..."
       assistant "CWE-287"
row 2: user "A vulnerability was found in Netegrity SiteMinder up to 4.5.1 and classified as critical. Affected by this issue is the file /siteminderagent/pwcgi/smpwservicescgi.exe of..."
       assistant "CWE-601"
```

Mapping onto `ap.violates_row`:

| theirs | ours | kind |
|---|---|---|
| CVE description | the note | PROXY (a vulnerability note, not a process incident) |
| one of 127 View-1003 CWE ids | one registry row | PROXY: the CWE row text (name, description) is not in the dataset; it must be joined from MITRE's catalogue [S card lists "MITRE CWE catalog (v4.20)" as a source]; CWE terms of use not read [U] |
| CWE id present in the label list | `true` | EXACT |
| any other View-1003 id | `false` | EXACT under a closed-world reading; the card warns the set drops CVEs where NVD and the CNA disagree [S] |
| multi-label rows (~14%) | several `true` rows in one entry | EXACT (our ranking already allows more than one hit per entry [U: not checked in our scorer]) |
| (none) | greppable signature | UNMAPPED |

Label source: the intersection of NVD analyst CWEs and CNA-supplied CWEs [S]. License CC BY 4.0 [S]. 71,640 rows, 40 MB
Parquet [S].

### 3.3 J1 HackerOne disclosed reports (report x triage outcome) -> `v1.finding_class`

First 3 rows, identical ids in the official viewer response and the mirror's viewer
(https://huggingface.co/datasets/elamaran619/hackerone_disclosed_reports/viewer) [S; nested `reporter`, `team`,
`structured_scope` columns left out here; text cut]:

```
id 411337 | "Forget password link not expiring after email change." | created 2018-09-19T05:13:33.396Z | substate resolved
  vulnerability_information: "I found a token miss configuration flaw in ..., When we reset password for a user a link is sent to
  the registered email address but incase it remain unused and email is updated by user from setting panel then too that old
  token [reset link] sent at old email address remains valid. ..." | has_bounty? true | weakness {"id": 124, "name": "Improper Authorization"} | original_report_id null
id 311805 | "Cross-origin resource sharing misconfig" | created 2018-02-02T21:19:34.071Z | substate duplicate
  vulnerability_information: "Description An HTML5 cross-origin resource sharing (CORS) policy controls whether and how content
  running on other domains can perform two-way interaction with the domain that publishes the policy. ..." | has_bounty? false
  | weakness {"id": 27, "name": "Improper Authentication - Generic"} | original_report_id 193559
id 385322 | "Open API For Username enumeration" | created 2018-07-23T07:32:50.020Z | substate not-applicable
  vulnerability_information: "We Can do username enumeration, Reproduce: 1. Go any wordpress site. #2.www.site.com/?author=1 ..."
  | has_bounty? false | weakness null | original_report_id null
```

State definitions, verbatim from https://docs.hackerone.com/en/articles/8475030-report-states [S]: Informative: "The
report contains valid information, but the information provided doesn't require action. This state is often used for
out-of-scope submissions or submissions against known issues disclosed on the program's security page, but it's also
often used to imply accepted risk." Duplicate: "This issue has already been reported or is otherwise previously known
by the customer team." Not Applicable: "The report doesn't contain a valid reproducible issue, and the security
implications have not been demonstrated."

Mapping onto `v1.finding_class` (and `v1.blocking`):

| theirs (`substate`) | ours | kind |
|---|---|---|
| duplicate (+ `original_report_id`) | KNOWN | EXACT in meaning ("previously known"); the pointer to the original also gives a pairing signal |
| informative | INFO | EXACT in meaning ("valid information ... doesn't require action"); HackerOne also uses it for known issues and accepted risk, so some rows are KNOWN or FOLLOW-UP in ours |
| not-applicable | UNVERIFIED | PROXY: "not ... reproducible ... not ... demonstrated" matches UNVERIFIED; it also absorbs outright false claims, for which our six classes have no slot |
| resolved | BLOCKER or FOLLOW-UP | PROXY: valid and fixed, but no per-report severity column exists to split the two [S features list]; `has_bounty?` is a weak stand-in [U] |
| spam | no mapping (drop) | - |
| (none) | CONTRACT-DEFECT | UNMAPPED |
| resolved-with-high-impact | `v1.blocking` true | PROXY only, severity missing |

Label source: human triage (program teams, HackerOne triagers) [S docs]. License: HackerOne's Terms of Service
[S]; commercial terms not read [U]. Mirror distribution: resolved 8,823, informative 789, not-applicable 242,
duplicate 217, spam 23 of 10,094 [S mirror]; 2,504 rows are `no-content` [S mirror].

### 3.4 J2 Code4rena judged findings (submission x judge verdict) -> `v1.finding_class` and `v1.blocking`

Schema excerpt, verbatim from the C4Audit record https://zenodo.org/records/17571169 (a CC BY 4.0 derivative holding
the published findings) [S]:

```
"issues": [ { "issue_id": "H-01", "title": "Exploitation of the receive Function to Steal Funds", "severity": "High",
"description": "...The WiseLending contract incorporates a reentrancy guard through its syncPool modifier, ...",
"vulnerable_code_links": [ "https://github.com/code-423n4/2024-02-wise-lending/blob/79186b243d85 53e66358c05497e5ccfd9488b5e2/contracts/WiseLending.sol#L49", ... ] }
```

Judge and sponsor label vocabulary, verbatim from a findings repo README
(https://github.com/code-423n4/2024-03-coinbase-findings) [S]: "`sponsor confirmed`, meaning: 'Yes, this is a problem and
we intend to fix it.'" / "`sponsor disputed`, meaning either: 'We cannot duplicate this issue' or 'We disagree that this
is an issue at all.'" / "`sponsor acknowledged`, meaning: 'Yes, technically the issue is correct, but we are not going to
resolve it for xyz reasons.'" / "All duplicates have been labeled `duplicate`, linked to a primary issue, and closed."
A judged QA issue carries the labels "bug, grade-b, QA (Quality Assurance), sufficient quality report,
edited-by-warden, Q-28" (https://github.com/code-423n4/2023-10-nextgen-findings/issues/174) [S]. Rules
(https://docs.code4rena.com/competitions/judging-criteria) [S]: "Judges assess each submissions' validity as
`sufficient`, `insufficient`, or `low quality/spam`"; "Findings from previous audit reports listed in the audit repo
`README` should generally be considered as known issues and therefore out of scope"; submission guidelines: "Insufficient
proof shall be defined as the judge needing to do additional research or coding in order to validate the claims made in
the submission."

Mapping onto `v1.finding_class` and `v1.blocking`:

| theirs | ours | kind |
|---|---|---|
| `3 (High Risk)`, `2 (Med Risk)`, valid | BLOCKER; `v1.blocking` true | PROXY: severity by asset impact, not by our blocking predicate |
| QA / Low (incl. "function incorrect as to spec" [S severity doc]) | FOLLOW-UP; `v1.blocking` false | PROXY; note the conflict: a spec deviation is Low there, while a severe spec-path defect is CONTRACT-DEFECT (blocking) here |
| informational ("Non-standard labels such as `R-` ..., `I-` ..., or `S-` ... will be considered informational" [S]) | INFO | EXACT in meaning |
| listed "known issues" (findings of previous audits named in the repo README; V12 tool findings "will be judged as known issues" [S https://docs.code4rena.com/competitions/submission-guidelines.md]) | KNOWN | EXACT in meaning |
| `duplicate` (same root cause as another submission) | KNOWN | PROXY: "already reported in the same contest", not "already on record before" |
| insufficient proof / `insufficient quality` / `unsatisfactory` | UNVERIFIED | PROXY: "insufficient" also covers low effort and overinflated severity [S rules] |
| `sponsor acknowledged` | FOLLOW-UP or KNOWN | PROXY |
| `sponsor disputed` | UNVERIFIED (cannot reproduce) or no slot (not an issue) | PROXY |
| (none) | CONTRACT-DEFECT | UNMAPPED |

Availability: the full label set lives only on the GitHub issues of each findings repo; the packaged derivatives read
here (C4Audit, xanoutas, leohachico) keep mostly the published or accepted findings with a severity string, so the
negative classes (duplicate, insufficient, disputed) are absent from them [S cards; U for completeness]. Code4rena's own `findings.csv` (with `contests.csv`, used to recompute awards) lists "valid Code4rena findings"
only [S https://docs.code4rena.com/awarding/awarding-process]; its columns, per a third-party README, are contest, handle,
finding, risk, score, pie, split, slice, award, awardCoin, awardUSD [U https://github.com/0237h/code4rena-stats]. The xanoutas
rows mix `confirmed_finding` and `slither_candidate` types with many null fields [S first rows].

### 3.5 A6 AIDev (inline review comment x its review verdict) -> `v1.blocking`

`pr_reviews` first 3 rows (viewer API, config `pr_reviews`) [S]:

```
id 3232618220 | pr_id 3424612595 | user_type User | state APPROVED  | submitted_at 2025-09-17T04:31:25Z | body null
id 3260239057 | pr_id 3447130697 | user_type Bot  | state COMMENTED | submitted_at 2025-09-24T00:57:44Z | body null   (user github-advanced-security[bot])
id 3095150493 | pr_id 3298817151 | user_type Bot  | state COMMENTED | submitted_at 2025-08-07T04:04:51Z | body "## Code Review\n\nThis pull request is a great step towards improving maintainability by refactoring..." (user gemini-code-assist[bot])
```

`pr_review_comments` columns (viewer API, config `pr_review_comments`) [S]: id, pull_request_review_id, user, user_type,
diff_hunk, path, position, original_position, commit_id, original_commit_id, body, pull_request_url, created_at,
updated_at, in_reply_to_id. First 3 comment bodies [S]: "Less sure about this bit!"; "```suggestion\n# Firebase
Functions Test (with jest) - Quickstart\n```\n\nThe library is called firebase-functions-test, so this title probably
should stay."; "If these are not in fact tests, then we would need to enable a hidden flag for the time being. Please
let me know."

Mapping onto `v1.blocking` (join `pr_review_comments.pull_request_review_id` = `pr_reviews.id`):

| theirs | ours | kind |
|---|---|---|
| comment in a review with `state` CHANGES_REQUESTED | `true` | PROXY: GitHub "request changes" blocks the merge when reviews are required, but a blocking review can also hold nit comments |
| comment in a review with `state` APPROVED | `false` | PROXY (an approving review can still carry "fix later" notes) |
| `state` COMMENTED (the bulk, incl. bots) | no mapping, or `false` by rule | - |
| bot reviewers (`user_type` Bot) | drop or keep as a separate stratum | - |
| comment text | INPUT for `v1.finding_class` (a teacher would label it) | INPUT-ONLY |

Class balance of the verdict [S viewer statistics API, config `pr_reviews`]: CHANGES_REQUESTED 4,960, APPROVED 19,445,
COMMENTED 58,693, DISMISSED 718 of 83,816 reviews; 35,114 reviews are by bots.

Caveats [S card]: `pr_review_comments.parquet` "does not contain full data points, use `pr_review_comments_v2.parquet`";
the v2 file is not served by the viewer (a first-rows request for it returned 404) [S]. Scale: 83.8k reviews and 81.7k
inline comments in v4 [S card]. License tag CC BY 4.0, per-repository licenses on content [S].

### 3.6 Rows that nearly made the list (one line each)

- A15 CRAVE: PR-level APPROVE / REQUEST_CHANGES with an explanation text; 1,200 rows, MIT; explanation authorship not
  stated [S].
- G5 SWE-bench Verified annotations: 3 humans per sample, 0-3 severity with "2 and 3 ... should be discarded", and notes
  columns. Header, verbatim from a copy in https://github.com/uw-swag/BouncerBench (data/ensembled_annotations_public.csv)
  [S copy]: `instance_id,underspecified,underspecified_notes,false_negative,false_negative_notes,other_major_issues,other_notes,difficulty,underspecified_decided_by,false_negative_decided_by,other_major_issues_decided_by,difficulty_decided_by,difficulty_ensemble_decision_procedure,filter_out`.
  The flagged object is a benchmark task whose own contract (issue text or tests) is defective, which in our vocabulary
  sits closer to the gate recommendation CONTRACT-INVALID than to a code finding.
- G2 TRAIL: human span-level errors with Low / Medium / High impact; gated, and its terms forbid training systems that
  "automate human evaluation" [S].
- C1 MLCQ: (code sample, smell) pairs with 4-level severity by 26 professional developers, CC BY 4.0 [S].
- A13 CRScore claims: correct / incorrect / unverifiable codes on review claims, kappa 0.804; release not confirmed [S/U].
- I4 Token Budgets: 63 agent incidents mapped to a mechanism catalogue by two raters; tiny [S].

## 4. Searches that found nothing relevant

Each line: the query as sent, the tool, and what came back. An empty result on a web search engine is a weak absence
(search coverage is not proven); it says only that these queries did not surface such a dataset.

| # | query (verbatim) | tool | result |
|---|---|---|---|
| N1 | `"conventional comments" dataset code review "(blocking)" "(non-blocking)" labeled comments` | WebSearch | no dataset; a dev.to blog on the Conventional Comments scheme and datasets already in the table (A1, A4, A5) |
| N2 | `dataset code review comments labeled blocking vs non-blocking merge "request changes" classification` | WebSearch | no dataset; GitLab docs, a vendor blog (propelcode.ai), a tool PR (malsabbagh/review-sensei #58), the SEKE 2017 taxonomy paper. (A15 CRAVE surfaced later under N5's query) |
| N3 | `release blocker bugs dataset Chromium "ReleaseBlock" OR "release-blocker" label prediction public dataset` | WebSearch | no packaged dataset; Chromium docs define the `ReleaseBlock` field (Dev / Beta / Stable) at https://chromium.googlesource.com/chromium/src/+/HEAD/docs/process/release_blockers.md |
| N4 | `Gerrit code review dataset "Code-Review" votes -2 -1 +1 +2 per patch set reviewer approvals mining MSR data showcase` | WebSearch | Gerrit documentation only; no dataset exposing per-patch-set votes surfaced (A8 CROP has revision status; votes inside its messages are unverified) |
| N5 | `huggingface dataset code review comments severity labels critical major minor nit` | WebSearch | no dataset with a critical / major / minor / nit scheme; found A15 CRAVE, CodeReviewQA, and a paper (arXiv 2608.21311) that extracts CodeRabbit headers "Refactor suggestion, Potential issue, and Nitpick, plus ... Verification" by rule, with no data URL on its abstract page |
| N6 | `dataset matching incident reports or bug reports to anti-pattern catalog entries labeled pairs` | WebSearch | no (incident, anti-pattern row) pair dataset; nearest were BugScope's memory-safety pattern categories (arXiv 2507.15671, not tabulated) and I4 |
| N7 | `dataset of code verification findings reproduced vs unverified labels LLM code review agent findings true positive false positive human validated 2026` | WebSearch | no dataset with a reproduced / unverified split; review benchmarks already tabulated (A10, A11, A12) and SWE-PRBench (named only) |
| N8 | survey extraction of https://arxiv.org/html/2602.13377 (code review benchmarks, 99 papers) asked for labeled datasets with URLs | WebFetch | the extraction reported "No datasets explicitly cite public availability or URLs" for its labeled-comment entries; UNVERIFIED absence (a summariser read of a long page) |

## 5. NOT-done (could not read, or read only in part)

- G2 TRAIL rows: gated behind an agreement ("not reshare ... outside of a gated or private repository"); no account was
  used, so no row was read. Everything in G2 comes from the card and the paper.
- B1 Public Jira Dataset: the current Zenodo version holds no data ("This version does not contain the data itself";
  files "Restricted"). No earlier version was searched for.
- J1 HackerOne official set: the viewer API returned `num_rows: 0` with a "config-size" error and HTTP 500 for
  statistics, so its row count and class counts are unknown; the counts in the table are the mirror's. HackerOne's
  Terms of Service text was not read.
- G5 SWE-bench Verified: https://openai.com/index/introducing-swe-bench-verified/ returned HTTP 403 to WebFetch and was
  read through Exa; the annotation zip was not downloaded; the CSV header and 3 rows were read from a third-party copy
  (uw-swag/BouncerBench). The row count printed by that fetch ("80+") looks truncated and is not used.
- G6 AgentErrorBench data (Google Drive) and the OpenReview page (browser check) were not opened.
- G7 MP-Bench raw files, I1 VOID bulk export, I3 structured post-mortems, I4 catalog CSV: not opened.
- A10 SWR-Bench, A11 CR-Bench, A12 c-CRAB: current data locations and data licenses not found.
- A13 CRScore: whether the 2.9k human annotations are in the GitHub repo was not confirmed.
- RevMate (arXiv 2411.07091): no replication package was found on its abstract page; its human accept / reject labels on
  LLM review comments were not located.
- G1 MAST: only four of the 14 Appendix A definitions were read (FM-1.1, 1.3, 3.2, 3.3).
- E2: the MITRE CWE catalogue terms of use were not read.
- Data licenses not read or not stated (from the license column): A2, A8, A10, A11, A12, A13, A14, B2, B3, B5, B6, B8,
  C2, D3, D4, E3, F3, F4, F5, G3, G5 (annotation zip), G6 (data), G7 (commercial terms), H1 (card), I1, I2, I3, I4 (CSV),
  J1 (ToS text), J2 (source repos). F1 shows no license on its repo page; A16 says only "other"; B7 '24 says
  "NOASSERTION".
- D3 Kang et al.: numbers come from a search-engine summary of the paper, not from the paper.
- A7 CodeReviewer split sizes not read.
- B4 bugbug label CSV row counts come from a fetch tool that may truncate long files.
- The first-rows responses for G1, J1 (official), A6 and A15 passed through WebFetch's summariser; field values match
  across two fetches where both exist (J1 ids), but the texts are not byte-exact.
- No file, archive or dataset beyond cards, READMEs and viewer samples was downloaded; `curl` was not used.

## 6. Adjacent observations (reported, not acted on)

- Leads named on pages read but not tabulated: CodAGE (a public dataset of coding-agent GitHub events used by arXiv
  2608.21311; 248,641 AI-attributed PRs receiving review per that abstract page); SWE-PRBench (2026); SeRe (security
  review comments, 6,729 per the BranLiu aggregator); ConfusionCR (Ebert et al.); ContextCRBench; CodeFuse-CR-Bench;
  CodeReviewQA; ToxiCR (19,651 comments per the arXiv 2602.13377 survey); Nutanix/codereview-dataset on Hugging Face;
  a bugbug notebook that reads a `ci_failures.json.zst` Taskcluster artifact with failure and fix commits
  (https://github.com/mozilla/bugbug/blob/master/notebooks/build_repair_create_dataset.ipynb).
- Preference-style code sets seen but not tabulated (their unit is code, not a review finding): Themis-CodePreference
  (350k+ pairs; commit-mined plus multi-LLM consensus; https://huggingface.co/datasets/project-themis/Themis-CodePreference),
  CRScore++ (DPO pairs scored by GPT-4o-mini; arXiv 2506.00296), CodePrefBench (1,364 tasks; amazon-science/llm-code-preference).
- More leads seen in search results, not opened: RevMate user study at Mozilla and Ubisoft (arXiv 2411.07091; 587 patch
  reviews, 8.1% / 7.2% of LLM-generated review comments accepted by reviewers; data release not found), BugHub (Zenodo
  10028953, 2,462,666 issue reports per a search summary), BugsRepo (119,585 Mozilla bug reports per a search summary),
  an Eclipse Bugzilla CSV on Hugging Face with P1-P5 priority and severity (88,682 reports per a search summary).
- The aggregator https://huggingface.co/datasets/BranLiu/cr_taxonomy_dataset re-packs 25 code-review sets into one
  JSONL schema (747,352 rows, 32.8 GB); it states no license, and its counts differ from two primary pages (A4, A5).
- Label provenance, examples per group (the table's "how labels were made" column is the full record). Human: A1, A2, A5, A6 (verdicts), A13, B5, B6, C1, C2, E2, G2, G3, G5, G6,
  G7, I4, J1, J2. Model or rule: A4 (SVM), A7 and D2 (mined events), A9 (LLM then experts), A14 (LLM), D1 (tool rule),
  E3 (AI-assisted), F2 (regex), G1 (o1 judge), H1 checklists (LLM calibrated on 20% human). Execution: G4, F3, H1
  (code generation part), H2.
- Terms that limit use for training or commercial work: non-commercial CC licenses on D1 and E1 (BY-NC-SA) and A5 (BY-NC-ND); TRAIL's
  no-training clause (G2); HackerOne's Terms of Service (J1); Llama 3.1 terms on G4's model outputs; per-repository
  licenses on A6 and G4 content.
- Personal data: J1 report texts and A6 comment rows carry researcher names, handles and site names; any use needs a
  PII pass (no values from them are copied here beyond the three truncated sample rows).
- Terminology collisions to keep in view when mapping: SonarQube's `BLOCKER` and `INFO` severities (D1) are rule-level
  impact, not verified findings; Bugzilla "blocking bugs" (B8) are dependency links, not merge blocks; Code4rena rates
  "function incorrect as to spec" as Low (QA), while our CONTRACT-DEFECT is blocking.
- Domain gap, recorded as a fact: none of the human-labelled sets found uses agent-process incident notes like ours as
  the unit; the nearest in domain are G1 and I4 (agent failures), and in label shape J1 and J2 (judged findings).
