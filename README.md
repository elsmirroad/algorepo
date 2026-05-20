# Algorepo (α)

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](CONTRIBUTING.md)

Algorepo is a CLI utility that scaffolds, organizes, and locally tests your algorithmic solutions — giving you a structured personal repository you control entirely.

![Algorepo Demo](./assets/demo.gif)

## Table of Contents
- [The Idea](#the-idea)
- [How it Works](#how-it-works)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [A Note on Test Runners](#a-note-on-test-runners)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

## The Idea
Solving DSA problems consistently is one of the most reliable ways to prepare for technical interviews. The harder part is building a habit and having something to show for it.

Algorepo's premise is simple: your solutions should live in your Git repository, structured the way you want, runnable from your terminal. LeetCode and CodeWars have their own tooling — sync integrations, notes, browser extensions. Algorepo is for those who prefer a local-first workflow: write in your editor, run tests in your terminal, commit to your own repo, and let the history speak for itself.

A well-maintained solutions repository is also something a potential employer can actually read — real code, organized and annotated the way you think.

## How it Works
Pass a problem URL and Algorepo fetches the statement, extracts the function signature, and opens a ready-to-edit file in your editor:

```bash
❯ algorepo [https://leetcode.com/problems/zigzag-conversion/description/](https://leetcode.com/problems/zigzag-conversion/description/)
6. Zigzag Conversion [Medium]
Python3
/Users/you/Solutions/LeetCode/6. Zigzag Conversion.py
```

The generated file looks like this:

```python
from lc import *
# ================================================
# 6. Zigzag Conversion
# https://leetcode.com/problems/zigzag-conversion/
# ================================================

class Solution:
    def convert(self, s: str, numRows: int) -> str:
        pass

test("""
Example 1:
Input: s = "PAYPALISHIRING", numRows = 3
Output: "PAHNAPLSIIGYIR"
Example 2:
Input: s = "PAYPALISHIRING", numRows = 4
Output: "PINALSIGYAHRPI"
# [truncated for readability]
""")
```

Write your solution, then test it with one command:

```bash
❯ algorepo test "6. Zigzag Conversion.py"
PASSED Test 1: args "PAYPALISHIRING", 3 result "PAHNAPLSIIGYIR" expected "PAHNAPLSIIGYIR"
PASSED Test 2: args "PAYPALISHIRING", 4 result "PINALSIGYAHRPI" expected "PINALSIGYAHRPI"
```

No compiler setup, no boilerplate `main()`, no copy-pasting.

## Features
- **Multi-platform** — LeetCode and CodeWars.
- **10 language runners** — C, C++, C#, Go, Java, JavaScript, Kotlin, Python, Rust, TypeScript. (more to come..)
- **Smart scaffolding** — function signature, type hints, and full problem statement extracted automatically.
- **Flexible language selection** — use your configured default priority list or override per problem with `--lang`.
- **Editor integration** — opens the new file in any editor (`vim`, `nvim`, `nano`, `code`, `notepad`…).
- **Local test runner** — isolated execution, data passed via JSON marshaling.
- **Share-ready** — consistent structure, ready to be shared after each session..

## Prerequisites
- **Python**: 3.10+
- **Supported environments**: Linux, macOS, Windows (WSL recommended).

## Installation

**Recommended (Global / CLI-wide):**
```bash
# Via uv (fastest)
uv tool install algorepo

# Via pipx (industry standard for CLIs)
pipx install algorepo
```

**Development / Local:**
```bash
# Clone and install dependencies
git clone https://github.com/elsmirroad/algorepo.git
cd algorepo
uv sync
```

## Quick Start

### 1. Configure
On the first run, Algorepo creates a `config.yaml`. Edit it to set your solutions directory, preferred language, and editor:

```yaml
general:
  # The directory where your solutions will be saved
  solutions_dir: ~/Solutions

  # Custom templates directory (Optional)
  # If not set, uses ~/.config/algorepo/templates
  # templates_dir: ~/.config/algorepo/templates

  # Priority list: if Python3 isn't available for a problem, it falls back to C++
  language_priority:
    - Python3
    - C++
  
  editor: vim         # nano | vim | nvim | notepad | code | ...
  open_editor: true

  # LeetCode Authentication (RECOMMENDED)
  # Without these tokens, Cloudflare protection may block requests (403 Forbidden).
  # Required to bypass 403 on Premium problems and some public ones.
  # How to get them: Browser DevTools -> Application -> Cookies
  leetcode_session: ""
  leetcode_csrf_token: ""
```

### 2. Download a problem
```bash
# Shortest form — uses your default language priority
algorepo https://leetcode.com/problems/two-sum/

# Explicit subcommand
algorepo download https://leetcode.com/problems/two-sum/

# Override language for this specific problem
algorepo download https://leetcode.com/problems/two-sum/ --lang Java
```

### 3. Solve and test
Algorepo automatically finds the file in your `solutions_dir` by its name and extension.

```bash
algorepo test "1. Two Sum.py"

# Test a problem from a specific platform
algorepo test "Two Sum" --platform leetcode
```

### 4. Review your solutions
```bash
❯ algorepo list
SOLUTIONS:

LeetCode
    1. Two Sum.py
    6. Zigzag Conversion.py

# Filter by platform
algorepo list --platform codewars
```

## A Note on Test Runners
⚠️ The runner system was designed with AI assistance and covers the common cases well. Complex or unusual data structures — certain tree variants, custom graph formats — may need manual test case adjustments.

If you find a bug or want to make a runner more idiomatic for your language, contributions are very welcome. See [Contributing](#contributing).

## Roadmap
Roughly in priority order:

- [ ] HackerRank, CodeRun, Codeforces support — third major platform.
- [ ] Interactive CLI — search and select problems in the terminal via `questionary`.
- [ ] Stats engine — generate a `STATS.md` with activity graphs and progress over time.

## Contributing
If you're experienced in one of the supported languages and see a way to improve its runner — that's the highest-value contribution right now. Issues and PRs are open.

Please check [CONTRIBUTING.md](CONTRIBUTING.md) for local setup instructions and architectural guidelines. 

## License
MIT © 2026.

