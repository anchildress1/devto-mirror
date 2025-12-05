# Agent Instructions for Documentation (docs/ folder only)

**Scope**: These instructions apply ONLY to files in the `docs/` folder. For general repository guidance, see `/AGENTS.md` at repo root.

## Documentation Generation Rules

When creating or modifying documentation files:

1. **Format**: Output valid markdown compatible with standard markdown-to-HTML converters. Validate syntax before finalizing.
2. **Structure**: Use hierarchical headers (h2-h4). Include unique emoji prefix for each major section to aid visual parsing.
3. **Diagrams**: Use Mermaid format exclusively. Always invoke mermaid-diagram-validator tool before saving diagram content.
4. **Consistency**: Before finalizing, read 2-3 existing docs files to match established tone and structure patterns.
5. **Target Audience**: Write for technical readers with varying expertise levels. Content must support both scanning (clear headers, lists) and detailed reading (comprehensive explanations).
6. **Tone**: Use conversational technical writing with occasional humor. Avoid formal academic or overly dry corporate tone.
