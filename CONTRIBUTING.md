# Contributing to Hades

Thank you for your interest in contributing. This document outlines the process and expectations.

---

## Philosophy First

Before contributing code, understand the project's core constraints:

1. **AST over Regex** — Structural truth via compiler APIs
2. **Refusal over hallucination** — "No output" is valid
3. **Narrow scope** — v1 is TS/JS only
4. **Provenance is law** — Every claim must be anchored

If your contribution conflicts with these principles, it will not be accepted regardless of technical merit.

---

## Getting Started

```bash
# Clone the repository
git clone https://github.com/Lostenergydrink/Hades.git
cd Hades

# Install dependencies
npm install

# Run tests
npm test

# Build
npm run build
```

---

## Development Workflow

### Branch Naming

- `feature/short-description` — New functionality
- `fix/short-description` — Bug fixes
- `docs/short-description` — Documentation only
- `refactor/short-description` — Code restructuring without behavior change

### Commit Messages

Follow conventional commits:

```
type(scope): description

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

Examples:
```
feat(hecate): add arrow function extraction
fix(eris): handle empty node array in contradiction check
docs(readme): clarify v1 constraints
```

---

## Code Standards

### TypeScript

- Strict mode enabled (`"strict": true`)
- No `any` unless absolutely necessary (and documented why)
- Prefer `readonly` for interface properties
- Use non-null assertions (`!`) only when bounds are provably guaranteed

### Testing

- All new functionality requires tests
- Use `vitest` for unit tests
- Test files live alongside source: `foo.ts` → `foo.test.ts`
- Aim for behavior coverage, not line coverage

### Linting & Formatting

```bash
npm run lint     # Check for issues
npm run format   # Auto-format with Prettier
```

These run in CI. PRs with lint errors will not be merged.

---

## Pull Request Process

1. **Check the roadmap** — Is your change in scope for the current version?
2. **Open an issue first** for non-trivial changes
3. **Write tests** before or alongside implementation
4. **Update documentation** if behavior changes
5. **Keep PRs focused** — One concern per PR

### PR Template

Your PR description should include:

- **What**: Brief description of the change
- **Why**: Motivation or issue reference
- **How**: High-level approach (if non-obvious)
- **Testing**: How you verified the change works

---

## Scope Changes

Proposing changes to the roadmap or non-negotiable constraints requires:

1. An issue labeled `scope-change`
2. Clear justification against the guiding principles
3. Maintainer approval before any implementation work

Do not submit PRs for out-of-scope features without prior discussion.

---

## Reporting Issues

### Bug Reports

Include:
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment (Node version, OS)
- Relevant code/input if applicable

### Feature Requests

Include:
- Use case description
- How it aligns with project philosophy
- Which roadmap version it targets

---

## Code of Conduct

Be respectful. Assume good intent. Focus on the work.

This project values:
- Technical rigor over politeness theater
- Direct feedback over vague approval
- Working code over impressive proposals

---

## Questions?

Open an issue with the `question` label.
