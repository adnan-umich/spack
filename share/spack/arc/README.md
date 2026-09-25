# ARC module refresh

`spack-env-refresh.sh` refreshes environments in ownership order. A concrete
hash belongs to the first environment containing it; later environments skip
that hash. In particular, `r-stacks` must not regenerate the OpenMPI and R
providers owned by `arc-core-stacks`.

The script uses `spack -e` explicitly and does not require shell activation.
Keep `refresh-owned-modules.py` beside it. The deployed copies are in
`/sw/spack`. Set `SPACK_COMMAND` to select a different Spack executable.

Preview one environment without writing modules:

```sh
python3 /sw/spack/refresh-owned-modules.py r-stacks arc-core-stacks arc-aocc-stacks
```

Refresh all environments while preserving ownership:

```sh
bash /sw/spack/spack-env-refresh.sh
```

## Multi-provider discovery

Lmod discovery aliases live in a separate `.spack-spider` tree directly under
the architecture root. Only spider mode adds directories from that tree to
MODULEPATH. Each alias is hard-hidden by its exact filename, using Lmod 8.8+
`hide{kind="hard"}` support. Spider follows these aliases to discover combined
R/MPI prerequisites, but they do not appear as provider variants or participate
in normal module loading.

Refreshing a provider migrates its old public aliases and removes stale aliases
and their generated hiding rules. Existing site modulerc settings are preserved.
Refresh all participating providers after upgrading the generator. Combined
application modules retain their normal paths.

Regression tests are in `spack/test/modules/lmod.py` and
`spack/test/modules/arc_refresh.py`. The Lmod integration tests use `LMOD_CMD`
and check spider output, both hierarchy orders, loading in both provider orders,
canonical provider filenames, and removal of combined paths on unload.
