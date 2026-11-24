# Changes

One folder per change to the strategy, named `<nnn>-<slug>`, for example `001-defend-crystal`. The course workflow writes them; you read and approve what is in them.

| File | What it holds |
|---|---|
| `intent.md` | What the change is for and how you will see that it works |
| `design.md` | How the change will work, when the workflow asks for a design |
| `plan.md` | The small tasks of the change, each with its test |
| `verify.md` | The checks that were run after the build, and what they showed |

Start a change in Claude Code with `/sdlc:intent` and your idea, for example `/sdlc:intent defend my crystal when the enemy is within 5 squares`.
