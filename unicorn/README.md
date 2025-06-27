# Unicorn

## Edgelist Format

10% base, others stream.

base:

```
{src} {dst} {src_type}:{dst_type}:{edge_type}:{logical_ts}
```

stream:

```
{src} {dst} {src_type}:{dst_type}:{edge_type}:{src_unseen}:{dst_unseen}:{logical_ts}
```

## Generate sketches

Make sure `bin/unicorn/main` has exec permission.

Then exec shell scripts under this dir, whose contents should be like this:

```bash
bin/unicorn/main filetype edgelist \
  base normal.txt \
  stream stream.txt \
  sketch sketch.txt \
  decay 500 lambda 0.02 batch 3000 chunkify 1 chunk_size 50
```
