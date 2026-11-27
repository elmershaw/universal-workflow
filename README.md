# Universal Workflow

Universal Workflow is a skills plugin for Codex and Claude Code. Use the five stages together for a project, or invoke one with the context you already have. The same workflow works for software, analysis, writing, and operations.

| Skill | What it hands off |
| --- | --- |
| `research` | A brief with primary evidence, sources, and open questions |
| `grill-with-docs` | Confirmed decisions, scope, constraints, and success criteria |
| `implement` | The deliverable, verification results, and any unresolved gaps |
| `review` | Independent findings and a readiness verdict against the brief and applicable standards |
| `retro` | Improvements for the next run, each with a way to tell whether it helped |

## Install from a local checkout

Run the commands from this repository's root.

**Codex**

```sh
codex plugin marketplace add "$PWD"
codex plugin add universal-workflow@universal-workflow
```

**Claude Code**

```sh
claude plugin marketplace add "$PWD"
claude plugin install universal-workflow@universal-workflow
```

## Install from GitHub

After the repository is pushed, replace `OWNER/REPO` with its GitHub slug.

**Codex**

```sh
codex plugin marketplace add OWNER/REPO
codex plugin add universal-workflow@universal-workflow
```

**Claude Code**

```sh
claude plugin marketplace add OWNER/REPO
claude plugin install universal-workflow@universal-workflow
```

## Use the skills

In Codex, start a new session and type `$` to select a skill from Universal Workflow. In Claude Code, start a new session and type `/universal-workflow:` to select a skill, such as `/universal-workflow:review`.

Give each stage the relevant output from the previous one. For example, give `review` the agreed brief and the finished deliverable, then give `retro` the review report and what happened when the work was used.

Research can be selected automatically. Invoke the other four stages explicitly. The plugin supplies skill instructions and needs no plugin-specific setup.

Both clients load the same skill files from `plugins/universal-workflow/skills/`.
