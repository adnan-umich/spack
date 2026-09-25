#!/usr/bin/env python3
import argparse
import os
import shlex
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("environment")
parser.add_argument("parents", nargs="*")
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()

spack = os.environ.get("SPACK_COMMAND", "spack")


def hashes(environment):
    result = subprocess.run(
        [spack, "-e", environment, "find", "--format", "{hash}", "--no-groups"],
        check=True,
        capture_output=True,
        text=True,
    )
    return set(result.stdout.split())


downstream = hashes(args.environment)
inherited = set()
for parent in args.parents:
    inherited.update(hashes(parent))

owned = sorted(downstream - inherited)

print(f"Skipping {len(downstream & inherited)} parent-owned specs.")
print(f"Refreshing {len(owned)} candidates before module exclusions.")

# An empty constraint list would refresh the entire environment.
if not owned:
    raise SystemExit(0)

# Batch requests to stay below command-line size limits.
for start in range(0, len(owned), 100):
    command = [
        spack,
        "-e",
        args.environment,
        "module",
        "lmod",
        "refresh",
        "-y",
        *("/" + h for h in owned[start : start + 100]),
    ]
    if args.apply:
        subprocess.run(command, check=True)
    else:
        print(shlex.join(command))
