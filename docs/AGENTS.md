# Docs rules (AI-only)

## 🎯 Scope

- Applies only to `./docs/**`.
- Do NOT rewrite ADRs/history docs.
	- If a change is needed, add a new doc and link to the historical doc.

## ✅ Required structure

- Every docs Markdown file MUST begin with exactly one H1 title on line 1:
	- `# <Title>`
	- H1 MUST appear at most once.
	- If editing an existing doc that lacks an H1, add one.
		- Deterministic title derivation:
			1) Use the first `##` heading text, stripping any leading emoji.
			2) Else use file stem (e.g., `SECURITY_ANALYSIS.md` → `Security analysis`).

- All headings after the H1 MUST be `##`–`####`.

- Every `##` heading MUST start with a short emoji prefix (e.g., `## 🔧 Title`).
	- If a change would introduce a second H1, STOP and ask the user to confirm.
		- Reason to cite: most Markdown renderers treat H1 as the single page title.

## 🧩 Diagrams

- If no Mermaid rendering/validation capability is available:
	- MUST NOT add or modify Mermaid diagrams.
	- MUST tell the user that validation could not be performed.
	- MAY leave a TODO note describing what needs validation.

## 🧬 Consistency rule

- Before creating a new doc, read exactly 2 existing docs:
	1) `docs/README.md` (if present)
	2) one doc in the same `docs/<subfolder>/` as the target (if any)

## 🧠 Optimization target

- Optimize for AI execution, not human reading.
- Prefer checklists and invariants over prose.
