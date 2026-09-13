# python-telegram-bot/python-telegram-bot — HTTPXodus migration

## Branch
- Branch: `httpxodus/httpx2-migration` on the fork `ProgrammerPlus1998/python-telegram-bot`
- Remote push status: **pushed to `https://github.com/ProgrammerPlus1998/python-telegram-bot`** (remote tip = local HEAD)
- Commits on branch (1): `0775a55` — `refactor: migrate httpx to httpx2 with dual import`
- PR: **not opened** (per HTTPXodus charter — human opens after review)

> **Note on local duplicates:** a second attempt at the same migration produced a local-only commit `be2cb62` (cleaner — no `HTTPXodus:` comments, no `# type: ignore[no-redef]` cruft) but the remote branch already carried the equivalent migration. Per the global no-force-push rule, the local duplicate was reset to match the remote rather than force-pushed; the resulting state is one migration commit on the remote branch, ready for the human to review.

## Issue / takeover context
- The PTB maintainer BjoernPetersen already opened the canonical issue for this: **[#5258 "Consider replacing httpx with httpx2"](https://github.com/python-telegram-bot/python-telegram-bot/issues/5258)** (2026-06-05, labels `🛠 breaking` / `🛠 refactor`).
- Existing comments on #5258:
  - `harshil21` (2026-06-09): "We are aware of httpx's situation, and are considering different networking backends. We'll have another issue covering this soon."
  - `Kludex` (2026-08-02): linked https://httpx2.pydantic.dev/migration/
- HTTPXodus takeover comment: **[#5258 (comment 5523003311)](https://github.com/python-telegram-bot/python-telegram-bot/issues/5258#issuecomment-5523003311)** — data point to accelerate the next step, no new issue opened.
- Search: `gh api "search/issues?q=repo:python-telegram-bot/python-telegram-bot+httpx2"` → `total_count=1` (issue #5258 itself). Zero PRs.

## File changes (8 files, +35/-8 on local duplicate, +36/-8 on remote)

| File | Change |
|---|---|
| `pyproject.toml` | Added `"httpx2 >= 2.12.0; python_version >= '3.10'"` alongside `"httpx >=0.27,<0.29"` |
| `src/telegram/request/_httpxrequest.py` | Dual import: `try: import httpx2 as httpx; except ModuleNotFoundError: import httpx` (with `# type: ignore[no-redef]` for the no-redef lint rule) |
| `src/telegram/ext/_applicationbuilder.py` | Same dual import for the `httpx.Proxy` / `httpx.URL` type annotations on `Builder.proxy()` and `Builder.get_updates_proxy()` |
| `tests/auxil/networking.py` | `from httpx2 import AsyncClient, AsyncHTTPTransport, Response` (with `httpx` fallback) |
| `tests/ext/test_applicationbuilder.py` | Dual import — `httpx.Limits` / `httpx.Timeout` assertions need to match the SUT |
| `tests/request/test_request.py` | Dual import + `from httpx2 import AsyncHTTPTransport` fallback for the `http_version=2` test |
| `tests/test_bot.py` | Dual import — used for `monkeypatch.setattr(httpx.AsyncClient, ...)` and `httpx.HTTPError` side-effects |
| `tests/test_official/scraper.py` | Dual import — used for scraping the Bot API docs |

## Test results

### Tests touching the migration (all green)

```
tests/request/test_request.py            59 passed, 1 skipped, 5 xfailed
tests/ext/test_applicationbuilder.py     170 passed, 1 skipped
tests/ext/test_updater.py  (non-online)  72 passed, 2 skipped
```

### Broader offline + WithoutRequest run

```
4128 passed, 19 skipped, 1995 deselected, 15 xfailed, 2 xpassed in 455.70s (0:07:35)
```

### `ruff check` and `ruff format --check` on modified files
- `ruff check`: All checks passed
- `ruff format --check`: 7 files already formatted

### Pre-existing flaky test (NOT caused by this migration)

`TestBotWithoutRequest::test_get_me_and_properties` is **flaky on the unmodified master** too — verified by `git stash` + repeat runs:

```
=== Main run 1 ===  1 passed
=== Main run 2 ===  1 failed (assertionError on first_name)
=== Main run 3 ===  1 failed
=== Main 4 ===      1 passed
=== Main 5 ===      1 failed
```

Root cause: this test instantiates a non-Pytest `ExtBot(offline_bot.token).get_me()` and the local env doesn't have the `BOTS` GitHub Actions secret, so the fallback bot tokens (`579694714:...` etc.) get looked up against the real Telegram API; sometimes the API replies with a different bot's info (e.g. "HACKER FROG"). The `_disallow_requests_in_without_request_tests` autouse fixture that would catch this is only active in `GITHUB_ACTIONS`. Not in scope for the migration.

## Manual dual-import verification

```python
$ python3 -c "from telegram.request._httpxrequest import httpx as h; print(h.__name__, h.__file__)"
httpx2 /Users/cls/github/httpxodus-worktrees/ptb/.venv/lib/python3.12/site-packages/httpx2/__init__.py
```

The SUT's `httpx` name resolves to `httpx2` when httpx2 is installed (which it is in the test env).

## Why Option A (dual import) for this project

- **PTB is a published library** with a very large user surface — one of the most-installed Telegram bot frameworks (~30k★). A hard switch would force every user on Python 3.10+ to install `httpx2` and would break user code that type-annotates against `httpx.Proxy` / `httpx.URL` (or constructs an `httpx.AsyncClient` and passes it through `get_updates_client`).
- **`requires-python = ">=3.10"`** is already a non-issue for httpx2 (which also requires 3.10+). The marker `python_version >= '3.10'` on the new dep is documentation, not constraint.
- **The public API does leak httpx types** — `Builder.proxy()`'s `str | httpx.Proxy | httpx.URL` annotation, `HTTPXRequest`'s `proxy` constructor arg, `get_updates_client`'s documented `httpx.AsyncClient` return type. With Option A, when httpx2 is installed, the resolved annotation flips to `httpx2.Proxy | httpx2.URL` — runtime duck-typing is fine, but the type-level mismatch is real and worth a changelog line. This is the same trade-off every dual-imported library makes.
- **`python-telegram-bot[http2]` and `[socks]` extras** stay valid — `httpx2` ships the same `[http2]` and `[socks]` extras. The two extras blocks would need a parallel `httpx2[http2]` / `httpx2[socks]` entry if maintainers want the new optional dep to honor the same flags when httpx2 is selected at runtime; left as a maintainer call for now.
- **The "different networking backends" angle @harshil21 raised is orthogonal** — Option A is a drop-in compatibility layer, not a commitment to httpx2 forever. If aiohttp or a custom transport ends up being the long-term plan, the dual-import shim is a small reversible step in that direction.

## One caveat called out in the takeover comment

httpx2 verifies TLS against the **OS trust store** instead of the bundled `certifi`. PTB users span a wide range of deployment environments (containers, corporate proxies, custom CA bundles), so this is a real behaviour change worth a line in the changelog. The takeover comment on #5258 flags it explicitly so it doesn't sneak up on the maintainer.

## Suggested next step

Open a draft PR at:
`https://github.com/ProgrammerPlus1998/python-telegram-bot/pull/new/httpxodus/httpx2-migration`

The body should reference `Closes #5258` (or `Refs #5258` if the maintainer prefers to keep the issue open until the PR merges). PTB doesn't auto-close PRs on missing-issue links (no PR gate like mem0's), but the established etiquette is to keep the linked issue and the PR coherent.

## Iron-rule compliance
- No `Co-Authored-By:` or AI署名 on the commit. Verified by `git log -1 --format='%B' | grep -iE 'co-authored|claude|anthropic|AI'`.
- No new issue opened; takeover comment on existing #5258 only.
- No PR opened.
- No force-push to remote (local duplicate commit was reset to match remote rather than force-pushed).
- All network commands used `HTTPS_PROXY=http://127.0.0.1:7890`.
