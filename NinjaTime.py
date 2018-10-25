#!/usr/bin/env python3
# Evan Wilde (c) 2018

import argparse
import os
import sys
import re
import json

# File contains all information for as long as the build directory has
# been used.

# File format
# ninja log v5
# start     end     re-stat     Target      hash

# The order is defined by the time that the process finished running.
# We can use the time that a process ended to determine where a new
# build starts -- This makes one fatal assumption, that the first file
# compiled by Ninja in the second build doesn't take longer than the
# first one

# e.g.
# Build 1:
# | ---- t1 ---- |
#    | -------- t2 ------ |
#
# Build 2:
# | ------------ t3 ---------- |
#
# Running on this assumption, t1, t2, and t3 will be grouped in the same
# build, which is wrong, but I don't know if there is a better way given
# the information we have.
# I'm not sure how Ninja handles incomplete targets either. It may
# output them, it may not.

ninja_log_pat = "#[\t ]+ninja[\t ]+log[\t ]+v(\d)"
ninja_log_expr = re.compile(ninja_log_pat)


#############
#  Classes  #
#############


class MakePathAbsolute(argparse.Action):
    """
    Convert file paths to absolute filepaths
    """
    def __call__(self, parser, args, values, option_string=None):
        setattr(args, self.dest, os.path.abspath(values))


class VersionError(Exception):
    """
    Raise when we're trying to open the wrong log version
    """
    def __init__(self, version_good, version):
        self.good_version = version_good
        self.bad_version = version

    def __str__(self):
        return f"Attempting to open invalid log file version expected {self.good_version}, opened {self.bad_version}"


class Target:
    """
    Single line read from the log file

    I track some parts of the file:
    - Start time
    - End time
    - Targets
    - Target hash

    I don't track
    - re-stat
    """
    def __init__(self, start, end, name, target_hash):
        self.start = int(start)
        self.end = int(end)
        self.name = name
        self.hash = target_hash
        self.thread = None

    @property
    def period(self):
        return self.end - self.start

    def __eq__(self, other):
        return self.name == other.name and self.hash == other.hash

    def __hash__(self):
        # The return of hash() must be an integer
        # otherwise I would just use the computed hash
        return hash(self.hash)

    def __contains__(self, other):
        # if our start is between their start and end
        # | ------- |
        #    | ---...
        # Or if our end is between their start and end
        # | --------- |
        # ...--- |
        return self.start > other.start and self.start < other.end or \
                self.end > other.start and self.end < other.end

    def __repr__(self):
        return f"(Target[{self.thread}] {self.name}: {self.start}: {self.period}s)"


class Build:
    """
    The ninja log contains multiple builds.
    This class is used to track each build.
    """
    def __init__(self):
        self.targets = []

    def __iter__(self):
        self._current = 0
        return self

    def __next__(self):
        if self._current < len(self.targets):
            x = self.targets[self._current]
            self._current += 1
            return x
        raise StopIteration

    def __contains__(self, target):
        """
        Checks if a target is in a build
        """
        if type(target) == Target:
            for t in self.targets:
                if t.name == target.name:
                    return True
        return False

    def add_target(self, target):
        self.targets.append(target)


######################
#  Helper Functions  #
######################


def check_version(line):
    """
    Check that the version number is accepted
    """

    # Skip early
    if line and line[0] != '#':
        return None

    match = ninja_log_expr.match(line)
    if not match:
        return None

    version = int(match.groups()[0])
    allowed_versions = [5]

    # FIXME: VersionError should take a list of accepted versions
    if version not in allowed_versions:
        closest = min(allowed_versions, key=lambda x: abs(x-version))
        raise VersionError(closest, version)
    return version


def need_new_build(current_build, new_target):
    """
    Returns true if we need a new build, false if not

    If the current build is empty, we definitely do not need a new
    build.

    If we've already seen a target name in the build, then the new
    target is from a different build.

    If the ending time of the new target is earlier than the latest
    target in the current build, then the new target is also from a
    different build.
    """
    if not current_build.targets:
        return False
    if new_target in current_build:
        return True
    return new_target.end < current_build.targets[-1].end


def assign_threads(build):
    """
    Figures out the threading situation for each target.
    This is basically a line-sweep problem, sorting the targets in the
    build by the start time, then seeing where targets are overlapping.

    This returns a Build object with the thread assigned correctly in
    the Target objects
    """
    targets = sorted(build.targets, key=lambda t: t.start)

    # This tracks each thread, containing the ending time for the
    # current job in each thread. There must be at least one thread.
    threads = [0]
    for target in targets:
        for thread, end_time in enumerate(threads):
            if end_time <= target.start:
                target.thread = thread
                threads[thread] = target.end
                break
        # Need an additional thread to schedule this target at the given
        # time
        if target.thread is None:
            target.thread = len(threads)
            threads.append(target.end)
    return build


def read_log(fname):
    """
    Runs through the log file, parsing out the runtimes for the targets

    Returns a list of builds, containing the targets built in that run.
    """
    with open(fname, 'r') as f:
        # Find the log version
        # Consume until we have a version or we crash
        version = None
        while version is None:
            line = f.readline()
            try:
                version = check_version(line)
            except VersionError as e:
                print(e, file=sys.stderr)
                exit(1)

        # We have verified that the version is good, lets go through the
        # log file
        builds = [Build()]
        for line in f:
            current_build = builds[-1]
            # Skip empty lines and comments
            if line == '' or line[0] == '#':
                continue
            start, end, _, tname, thash = line.rstrip().split('\t')
            new_target = Target(start, end, tname, thash)

            if need_new_build(current_build, new_target):
                current_build = Build()
                builds.append(current_build)

            # If the end time of a target is before the end of the last
            # one in the build, we are in a new build

            current_build.add_target(new_target)
        return builds


def target_to_dict(target, pid):
    return {'name': target.name,
            'cat': 'targets',
            'ph': 'X',
            'ts': target.start * 1000,
            'dur': target.period * 1000,
            'pid': pid,
            'tid': target.thread,
            'args': {}}


##################
#  Main Program  #
##################


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("build", type=str,
                    help="Ninja build root directory",
                    action=MakePathAbsolute)
    ap.add_argument('-o', '--output', type=str, help="Output file name")
    args = ap.parse_args()

    if not args.output:
        args.output = sys.stdout
    else:
        args.output = open(args.output, 'w')

    # Looking for the log file
    # If we're given a log file, assume that it's a ninja log
    # If we're given a directory, look for the ninja log
    if os.path.isdir(args.build):
        args.build = os.path.abspath(args.build + '/.ninja_log')

    if not os.path.isfile(args.build):
        print(f"Error: {args.build} does not exist", file=sys.stderr)
        exit(1)

    for pid, build in enumerate(read_log(args.build)):
        assign_threads(build)

    # convert the target to a dictionary for each target in each build
    targets = [target_to_dict(target, pid)
               for pid, build in enumerate(read_log(args.build))
               for target in assign_threads(build)]
    print(json.dumps(targets), file=args.output)

    if args.output is not sys.stdout:
        args.output.close()


if __name__ == "__main__":
    main()
