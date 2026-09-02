# UI/UX skill pack provenance (#265 front-end build prep, vendored 2026-07-02)

Extracted from the human's starred list (https://github.com/stars/Pxls21/lists/claude-code-skills-plugins,
278 repos swept) — the web-app-relevant UI/UX skills only, vendored into `.claude/skills/` so every
build session has them regardless of container recycling. All upstreams permissively licensed; each
skill dir is copied verbatim from a shallow clone of the revision current on 2026-07-02.

| Skills (dirs here) | Upstream | License |
|---|---|---|
| web-design-guidelines, react-best-practices | vercel-labs/agent-skills | MIT |
| gsap-core/-react/-timeline/-scrolltrigger/-utils/-frameworks | greensock/gsap-skills (official) | MIT |
| platform-web-design (the `web` skill only) | ehmo/platform-design-skills | MIT |
| impeccable (incl. its live-browser/measure scripts) | pbakaus/impeccable | Apache-2.0 |
| a11y-audit, apply-aesthetic, design-code, design-component, design-qa, design-review, design-tokens, prototype, redesign, ux-writing, performance | plugin87/ux-ui-agent-skills | MIT |
| taste-skill, minimalist-skill, soft-skill, brutalist-skill, output-skill | Leonxlnx/taste-skill | MIT |
| design, design-system, ui-styling, brand | nextlevelbuilder/ui-ux-pro-max-skill | MIT |
| building-ai-chat, creating-dashboards, visualizing-data, implementing-realtime-sync, designing-layouts, theming-components, assembling-components, implementing-navigation, providing-feedback, guiding-users | ancoleman/ai-design-components (frontend subset of 75) | MIT |
| design-md-spec (spec.md + PHILOSOPHY.md + README; SKILL.md wrapper is ours) | google-labs-code/design.md | Apache-2.0 |

Deliberately NOT vendored: alchaincyf/huashu-design (self-described unsuitable for production web
apps; HTML-prototype/slides focus), CloudAI-X/threejs-skills (no 3D in v1), yetone/native-feel-skill
(desktop), imagegen/figma/banner/slides variants (off-scope), backend/devops subsets of
ai-design-components. Security skim done: no exfil/hostile patterns; impeccable's `scripts/` are
local headless-Chromium render/contrast/live-iteration tools.

App-shaped repos from the same list worth BORROWING FROM (not skills — RP-40 OQ-4 inputs):
siteboon/claudecodeui, The-Vibe-Company/companion (web+mobile UI for CC/Codex), winfunc/opcode,
d-kimuson/claude-code-viewer, graykode/abtop (token/session monitor TUI).
