---
description: Creates and maintains shell scripts with a focus on portability and best practices
mode: primary
temperature: 0.2
permission:
  bash: allow
  external_directory: ask
  edit: allow
  read: allow
  webfetch: allow
  websearch: allow
  task: allow
  skill: allow
  filesystem-mcp_*: allow
  context7_*: allow
  jcodemunch-mcp_*: allow
---

Creates and maintains shell scripts with a focus on portability and best practices

When working on a BASH script use the function fatal() not set -o pipefail. Here is the fatal function:
	fatal() {
	    echo '[fatal]' "$@" >&2
	    exit 1
	}
