# keain-backend

Django + GraphQL API for Keain, a mechanical keyboard sound analyzer. Takes a
short phone recording of someone typing and returns scored acoustic metrics,
plus CRUD for keyboard parts and builds.

Archived. Not maintained, not deployed.

Client: [keain-mobile](https://github.com/asiLukas/keain-mobile).

## What it does

`analyzeFile` accepts an audio upload and runs a librosa DSP pipeline:

- Decode via PyAV (iOS sends WAV, Android sends AAC), resample to 22050 Hz mono,
  cap at 10s
- 80 Hz high-pass to drop mic rumble, then peak-normalize
- STFT (n_fft 1024, hop 256) and band energy over four ranges: thock 100–500 Hz,
  body 500–2k, clack 2–8k, metallic 3–6k
- Onset detection with a 40 ms debounce so key-down and key-up count as one
  stroke; per-stroke spectral centroid, peak, decay-to--20dB, crest factor
- Harmonic product spectrum for the dominant tone, mapped to a musical note
- Eight rejection gates before scoring: clipping, silence, too few strokes,
  impossible stroke rate, no transients, tonal bleed from music or speech
  (measured as spectral flatness in the gaps between strokes), excessive reverb

Output is 11 integer scores, a 64-bin log-spaced frequency response, the
detected note, and a generated two-word character title ("Velvet Thock").

The score bounds in `_to_score` are hand-picked, not fit to any labelled data.
Metrics like `thock`, `clack` and `pitch` map to physical band ratios and decay
times. `creaminess`, `purity` and `variance` are invented composites — treat
them as relative, not absolute. Nothing here was tested for repeatability
across microphones or rooms.

`verdict` is an unimplemented field that always returns null.

## Layout

```
core/       settings, URLs, GraphQL schema assembly, error codes
user/       custom user model, JWT auth, rate limiting
build/      parts + builds: models, seed data, GraphQL
analyzer/   DSP pipeline, Analysis model, character titles
```

Single GraphQL endpoint at `/graphql/` (Strawberry, multipart uploads enabled),
Django admin at `/admin/`.

## Auth

Hand-rolled JWT with PyJWT. 30 min access token, 30 day refresh, `sub` is the
username. `user/graphql/utils.py::get_user_from_request` resolves the user and
`KeainGraphQLView` injects it into GraphQL context. Resolvers guard with
`permission_classes=[IsAuthenticated]`.

Logout does not blacklist refresh tokens, so they stay valid for 30 days. There
is no password reset.

## Parts data

Seeded through data migrations from `build/seed_data/`:

| file           | rows |
| -------------- | ---- |
| switches.json  | 2577 |
| cases.json     | 1400 |
| keycaps.json   | 2155 |

Scraped and normalized against the model enums. Case and keycap entries carry
image URLs pointing at vendor CDNs.

Plates and PCBs are enumerated variants rather than named products — a plate is
(material, flex cuts, half plate), a PCB is (RGB, hotswap, wireless). Small
enough to enumerate exhaustively.

`Ownable` in `build/models.py` handles visibility: a NULL `created_by` means
seeded and public, non-NULL means private to that user. `visible_to()` returns
both and sorts the user's own entries first.

There are no compatibility rules. `Plate` and `PCB` have no `layout` field, so
form-factor matching across case/plate/PCB is not possible without a migration.
`Build.layout` is stored, not validated against its parts.

## Running it

Needs Python 3.13, uv, and PostgreSQL.

```bash
uv sync
cp .env.example .env   # SECRET_KEY, DEBUG, DB_*
uv run python manage.py migrate   # also loads seed data, takes a while
uv run python manage.py runserver
```

`run.sh` starts the dev server behind a hardcoded ngrok tunnel, which is how the
phone reached it during development. Replace the URL or don't use it.

`pyproject.toml` and `uv.lock` are the dependency source of truth.

## State

No tests. `*/tests.py` are stubs.
