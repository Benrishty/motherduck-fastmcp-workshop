# Exercise 4: Ask with elicitation

**Time:** 15 minutes

## The brief

When a neighborhood name is ambiguous, the tool asks the user instead of guessing.

San Francisco has 41 official neighborhoods, but people use about 120 names.
"Lower Nob Hill" is a real place, and it overlaps three official neighborhoods: Nob Hill, Tenderloin, and Western Addition.
If someone asks how many requests came from Lower Nob Hill, the right answer depends on what they mean.

## The tool

Add `count_in_neighborhood(name, boundary=None)`:

| Input | Behavior |
| --- | --- |
| An official neighborhood, such as `Mission` | Count its requests. Ask nothing. |
| A local name that overlaps one official neighborhood | Count the requests in that local area. Ask nothing. |
| A local name that overlaps several | Ask which part to count. Offer each official neighborhood it overlaps, plus `All of <name>`. Count the user's choice. |
| `boundary` given | Skip the question. `boundary` is one of the overlapped neighborhoods, or `all`. |
| The user declines | Return a short message that says nothing was counted. |
| An unknown name | Raise a `ToolError` that suggests the closest names. |

## How elicitation works here

The current MCP protocol has no long-lived connection for a server to push a question down.
Instead, the tool returns its question as the result.
The client shows a form, then calls the same tool again with the answer attached.
The second call can reach a different copy of your server, so the tool must save nothing between the two calls.

`sf311.kit` has the two helpers: return `ask_choice(...)` to ask, and call `read_choice(ctx, key)` to read the answer on the second call.
Your coding agent may know an older API, `ctx.elicit()`.
It fails on FastMCP Gateway, and `AGENTS.md` tells your agent not to use it.

## Steps

1. Ask your coding agent:

   ```text
   Read exercises/04-ask-with-elicitation.md and add count_in_neighborhood. Run tests/test_ex4.py until it passes, and keep the earlier tests passing.
   ```

2. Commit and push, then wait for `Live`.
3. In Claude Code, type `/mcp` and reconnect `sf-311`.

## Prove it

1. Ask: `How many 311 requests came from Lower Nob Hill?`
   Claude Code shows a form with the neighborhoods it overlaps.
   Pick one, and the agent reports the count.
2. Open **Logs**.
   You see two `count_in_neighborhood` rows for one question: the first returned the question, and the second returned the count.

Cursor and Claude Desktop may not show the form.
There, ask the agent to pass `boundary`, for example `boundary="Tenderloin"`, or run the tool from **Playground** in FastMCP Gateway.

## Tier 4

Your tool now knows local names, so ask the room server for the last tier:

```text
Get my tier 4 room challenge. My handle is <your-handle>.
```

These questions are about a local name that spans several official neighborhoods: how many requests it had in all, which official neighborhood holds the largest share, or how many fall inside one part.
If `count_in_neighborhood` cannot answer yours in one call, extend it, or add a tool beside it.

## Stretch goals

- Ask about `Duboce Triangle` or `Civic Center`, which each overlap three official neighborhoods.
- Make `search_requests` ask the same question when its `neighborhood` argument is a local name.

## If you fall behind

```bash
cp solutions/ex4/server.py server.py
git commit -am "Use the Exercise 4 solution" && git push
```
