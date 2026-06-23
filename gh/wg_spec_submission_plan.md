# `wg` multiaddr protocol: upstream spec submission plan

Plan for registering the `wg` (WireGuard) protocol upstream
once the `py-multiaddr` impl (PR
[multiformats/py-multiaddr#108][pr108]) is settled.

## Settled impl semantics (post-review)

- protocol name: `wg`
- code: `0x01c7` (decimal `455`) — the unassigned slot
  between `noise` (`0x01c6`) and `shs` (`0x01c8`) in the
  `multiaddr` tag range.
- binary form: exactly 32 bytes — a raw Curve25519 public
  key; fixed size `256` bits.
- string form: URL-safe base64 (RFC 4648 section 5) **with
  padding** — 44 chars ending in `=`.
  * standard base64 (as printed by `wg(8)`) is rejected
    since `/` collides with the multiaddr delimiter and `+`
    is reserved to the std alphabet; transliterate via
    `tr '+/' '-_'`.
  * precedent: `garlic64` uses alt-alphabet base64
    (`-~`) for the same delimiter-collision reason;
    `certhash` uses multibase `base64url`.
- example:
  `/ip4/1.2.3.4/udp/51820/wg/__________________________________________8=`

## Step 1: multicodec PR (reserves the code)

Repo: <https://github.com/multiformats/multicodec>

Add one row to `table.csv` (cols:
`name, tag, code, status, description`), keeping the file's
column alignment, sorted by code next to `noise`/`shs`:

```csv
wg,                             multiaddr,      0x01c7,         draft,      WireGuard tunnel endpoint - 32-byte Curve25519 public key
```

- run the repo's table validation locally before pushing
  (`make` / `npm test` per their CONTRIBUTING docs).
- per their addition process, `draft` status entries for
  unclaimed codes are routinely accepted via small PRs.
- PR body: link WireGuard cryptokey-routing docs, py-multiaddr
  PR #108 as the first implementation, and the overlay-network
  use case from issue #107.

## Step 2: multiaddr spec PR (defines the protocol)

Repo: <https://github.com/multiformats/multiaddr>

1. Add a row to `protocols.csv` (cols:
   `code,\tsize,\tname,\tcomment`), sorted by code after
   `noise` (`454`):

   ```csv
   455,	256,	wg,	WireGuard tunnel endpoint (Curve25519 public key)
   ```

2. If requested by maintainers, add a short protocol
   description to the README/spec covering:
   * value = 32-byte Curve25519 public key (binary),
     padded URL-safe base64 (string).
   * rationale for the URL-safe alphabet (delimiter
     collision) + the `tr '+/' '-_'` conversion from
     `wg(8)` output.
   * canonical composition: `/ip{4,6}/<host>/udp/<port>/wg/<key>`.

Open this PR referencing the multicodec PR from step 1 so
both land with the same code.

## Step 3: circle back to py-multiaddr

After (or alongside) the upstream PRs:

- update `multiaddr/codecs/wg.py` module docstring + PR #108
  body to point at the upstream PRs instead of calling the
  code a speculative draft.
- tick the "Submit a draft multicodec addition PR upstream"
  TODO checkbox in the PR #108 description.

## Follow-ups (optional)

- propose the same protocol to `go-multiaddr` /
  `js-multiaddr` once the spec rows land, so the string/binary
  forms stay interoperable across impls.

[pr108]: https://github.com/multiformats/py-multiaddr/pull/108
