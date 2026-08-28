# Plan: Complete KB-024 and KB-025

## Goal
Finish v4.0 release by completing documentation (KB-024) and verification/release prep (KB-025).

## Prerequisites
- All tests passing: ✅ (389 passed)
- Version bumped to 4.0.1: ✅ (already done)

## Phase 1: Documentation (KB-024)

### Task 1.1: Update README with mermaid support
- [ ] Add "Mermaid Diagram Support" section after HTML export
- [ ] Document `--mermaid`, `--no-mermaid`, `--mermaid-theme` CLI flags
- [ ] Explain bundled merman-cli binary (air-gapped operation)
- [ ] Add example showing mermaid export

### Task 1.2: Add troubleshooting section
- [ ] Document merman-cli binary not found scenarios
- [ ] Explain fallback behavior (diagrams as code blocks)
- [ ] List supported themes and how to use them

### Task 1.3: Update mdutil-specification.md
- [ ] Add CLI flags table for mermaid options
- [ ] Document bundled binary architecture
- [ ] Add mermaid theme configuration section

## Phase 2: Verification & Release Prep (KB-025)

### Task 2.1: Manual verification
- [ ] Test HTML export with mermaid diagram (actual render)
- [ ] Test `--no-mermaid` flag (diagrams as code blocks)
- [ ] Test `--mermaid-theme dark` (theme passthrough)
- [ ] Verify air-gapped: run with network blocked, confirm no network calls

### Task 2.2: Create release branch
- [ ] Create `feature/v4.0-release` branch from current state
- [ ] Move KB-024 to ready/in-progress
- [ ] Move KB-025 to ready/in-progress

### Task 2.3: Update release notes
- [ ] Create CHANGELOG.md or update README with v4.0 release notes
- [ ] List new features, CLI flags, bundled binary
- [ ] Note air-gapped operation

### Task 2.4: Create PR
- [ ] Push branch to origin
- [ ] Create PR from `feature/v4.0-release` to `main`
- [ ] Request review (if applicable)
- [ ] Merge after approval

## Order of Operations
1. Complete KB-024 (documentation updates)
2. Commit documentation changes
3. Complete KB-025 (verification + release prep)
4. Create PR and merge

## Branch Naming
`feature/v4.0-release`
