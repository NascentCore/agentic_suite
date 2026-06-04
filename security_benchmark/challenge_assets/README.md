# Challenge assets

Minimal fixture layout for the security benchmark. Vendor a vulnerable app separately
(e.g. Kasra's Firebase BOLA book-review challenge) and place artifacts here:

```
challenge_assets/
  CHALLENGE.md    # agent prompt (this repo)
  app.apk         # optional — not redistributed in agentic-suite
  api/            # optional backend tree
```

Phase-1 smoke runs only require `CHALLENGE.md` plus any local fixture you provide.
