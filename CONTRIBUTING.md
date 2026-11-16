# Contributing to openspective

Thanks for helping. openspective has one job: answer Perspective API requests well enough that clients can switch without noticing, using open models. Contributions that make it more compatible, more accurate in more languages, or easier to run are the most useful.

## Ways to help

- **Report a wrong score.** Use the "Wrong score" form. Scores from Perspective for the same text are especially useful while it still runs (until December 31, 2026).
- **Report a client that breaks.** If an app or library that worked with Perspective fails against openspective, that's a compatibility bug. Include the request and the error.
- **Add a migration guide** for a project that calls Perspective.
- **Fix something.** Issues labelled `good first issue` are scoped for a first PR.

## Development

You need Python 3.11 or newer and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/aryan-tah/openspective
cd openspective
uv sync
uv run ruff check && uv run mypy && uv run pytest
```

The default test run uses a small fake model, so it's fast and needs no downloads. `uv run pytest -m models` runs the real models (about 1.5 GB download the first time).

## Pull requests

- Keep each PR to one change. Small PRs get reviewed fast.
- Add or update tests. API behaviour changes need a test that pins the exact JSON.
- When openspective knowingly differs from Perspective, say so in the docs' compatibility page.
- Write commit messages in the [Conventional Commits](https://www.conventionalcommits.org/) style (`feat:`, `fix:`, `docs:`). The changelog is generated from them.

## Code of conduct

This project follows the [Code of Conduct](CODE_OF_CONDUCT.md). By taking part you agree to it.
