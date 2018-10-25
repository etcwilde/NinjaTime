This little tool is designed to help shed some light on compile times of
targets in Ninja builds.

To use it, just point it at the directory where you call ninja from. It
will then attempt to reconstruct the history of your builds, outputting
JSON.

# Usage

```
Usage: NinjaTime.py INTPUT [-o|--output OUTPUT]
```

The `INPUT` is either a ninja log file, or the directory where ninja was
run. I currently only support log format version 5.

The output is a JSON file formatted in a way that chrome tracer can read
it. To use the file, open up chrome and navigate to `chrome://tracing`.
Click "Load" and select the generated JSON file.

# Contributing

Right now, I think that the best way is to fork the repository and make
pull requests.

# Authors

- Evan Wilde <etceterawilde@gmail.com>

# License

The project is under the BSD-3 license.

NinjaTime
Copyright © 2018 Evan Wilde
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.
3. Neither the name of the organization nor the
names of its contributors may be used to endorse or promote products
derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY Evan Wilde ''AS IS'' AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL Evan Wilde BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
