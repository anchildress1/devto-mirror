- Applies to `docs/**` except this file.
- Write `docs/*.md` for humans catching up: short prose with context. Instructions stay here; docs never address an AI reader.
- Update an existing doc before creating a new one. Cut anything that does not answer a reader's question.
- Do NOT rewrite ADRs or history docs (`docs/implementations/*`). If a change is needed, add a new doc and link to the historical one.

## Structure

- Line 1 is the only H1: `# <Title>`.
  - Missing H1 → use the first `##` heading text minus its emoji; else the file stem (`SECURITY_ANALYSIS.md` → `Security analysis`).
  - A change that would add a second H1 → STOP and ask the user (renderers treat H1 as the page title).
- Headings after the H1 are `##`–`####`.
- Every `##` heading starts with an emoji (`## 🔧 Title`).

## Diagrams

- Mermaid only, with `accTitle`/`accDescr` and `%%{init: {"theme": "default"}}%%`.
- Validate every added or modified diagram with a Mermaid validation tool.
- No validation tool available → do not add or modify the diagram; tell the user validation could not be performed.

## New docs

- Before creating one, read `docs/README.md` and one doc in the target `docs/<subfolder>/` (if any).
