#!/usr/bin/env bash

# The first environment containing a concrete hash owns its modulefile.
# Keep this order: downstream environments must not rewrite parent modules.
set -uo pipefail

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
environments=(arc-core-stacks arc-aocc-stacks r-stacks bioinformatics paraview py-stacks)
parents=()
failed=()

for environment in "${environments[@]}"; do
    echo "Refreshing modules owned by ${environment}"
    if ! python3 "$script_dir/refresh-owned-modules.py" --apply \
        "$environment" "${parents[@]}"; then
        failed+=("$environment")
    fi
    parents+=("$environment")
done

if ((${#failed[@]})); then
    printf 'Module refresh failed: %s\n' "${failed[@]}" >&2
    exit 1
fi
