# Adding an Integration to pyhall-examples

## Structure

Each integration lives in its own folder under the language it's written in:

```
python/<integration-name>/
  README.md              — what it does, how to install, env vars
  <implementation>.py    — the integration code
  test_<name>.py         — tests (optional but encouraged)

typescript/<integration-name>/
  README.md
  <implementation>.ts
```

## Requirements for a new integration

1. Must use `pyhall-wcp` (Python) or `@pyhall/core` (TypeScript) as the WCP layer
2. Must not contain secrets or hardcoded credentials
3. README must document: purpose, setup, required env vars, usage example
4. Must be Apache 2.0 compatible

## Examples

- See `python/discord/` for a complete integration with README, implementation, and tests
- See `python/workers/hello_worker/` for a minimal worker example
