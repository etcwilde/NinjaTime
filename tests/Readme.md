# Tests

These are just simple tests to see that we're generating something sane.

There are a few things that should be tested here.

- Single-process compilation (e.g. `ninja -j 1`)
- Multi-process compilation (e.g. `ninja`)
- Single-process, Multi-builds compilation
- Multi-process,  Multi-builds, all full builds
- Single-process, Multi-builds, partial builds
- Multi-process,  Multi-builds, partial builds

This list grows in complexity.

## Processing Type

### Single-Process

This only runs a single target at a time, creating a nice linear
visualization.

### Multi-Process

Up to N targets may be running at a time, making a big mess of things.


## Builds

### Single-Build

The ninja logs can contain multiple builds, essentially containing all
of the information for every build from the time the build directory was
created. This is a simpler case where ninja has only been called once in
a build directory.


### Multi-Build

This is the opposite case, where ninja has been called multiple times in
a directory.

## Completion

### Completed

This is a build where ninja was allowed to finish.

### Incomplete

Ninja was not allowed to finish. In the case of multi-builds, this means
that the first build was canceled before it was allowed to finish. Then
ninja was called again, finishing the build.


# Test File List

- single_single_full.log: single process, single build, to completion
- multi_single_full.log: multi process, single build, to completion
- single_multi_full.log: single process, multi build, to completion
