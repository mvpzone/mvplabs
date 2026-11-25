# mvplabs

Hands-on labs and reusable recipes for cloud-native security and agentic AI. Each lab is a self-contained, runnable demonstration of one idea — small enough to read, big enough to learn from.

## Labs

| Lab | What it shows |
|-----|---------------|
| [Lab_4_1_AgentSpace_Security](labs/Lab_4_1_AgentSpace_Security/) | AgentSpace deployment security (in progress) |
| [Lab_6_1_Model_Armor](labs/Lab_6_1_Model_Armor/) | Prompt injection defenses and guardrails with Model Armor |
| [Lab_8_1_ADK_Observer](labs/Lab_8_1_ADK_Observer/) | Observability for Google ADK agents — notebook + SQL for inspecting agent behavior |

Workshop labs live under [`labs/`](labs/). Writing a new one? Start from the template in [`example/`](example/) (README + notebook + reset script).

## Codelabs

[`codelab/`](codelab/) — the code behind the step-by-step codelabs on [devnull.fyi/labs](https://devnull.fyi/labs/): each folder runs on a laptop, most with the broken and the fixed version side by side.

| Codelab | What it shows |
|---------|---------------|
| [agent-inner-loop](codelab/agent-inner-loop/) | [Your Agent's Inner Loop](https://devnull.fyi/labs/your-agents-inner-loop/): an ADK agent from an empty folder to Cloud Run — local tool, stdio MCP server, hermetic tests, own service account |
| [envoy-ext-proc-logger](codelab/envoy-ext-proc-logger/) | [Envoy and a Stub ext_proc](https://devnull.fyi/labs/envoy-and-a-stub-ext-proc-that-logs-every-request/): one log line per request, then one rule in observe or enforce mode |
| [ext-proc-full-duplex](codelab/ext-proc-full-duplex/) | [The Reply That Deleted Every Body](https://devnull.fyi/labs/the-reply-that-deleted-every-body/): a full-duplex ext_proc stub that "changes nothing" breaks every body |
| [blocked-event-loop](codelab/blocked-event-loop/) | [Blocking the Loop Is a Liveness Bug](https://devnull.fyi/labs/blocking-the-loop-is-a-liveness-bug/): a sync call inside `async def` starves the health check |
| [one-record-per-request](codelab/one-record-per-request/) | [One Record per Request, Reconciled](https://devnull.fyi/labs/one-record-per-request-reconciled/): a decision taken on the body never sees a request without one |

## Katas

[`kata/`](kata/) — single-lesson exercises: one bug, one fix, one test. Walkthroughs on [devnull.fyi/labs](https://devnull.fyi/labs/).

| Kata | Lesson |
|------|--------|
| [strict-mocks](kata/strict-mocks/) | A mock that answers anything proves only that your code asked |
| [hermetic-suite](kata/hermetic-suite/) | A suite that degrades cleanly on `OSError` still fails hermeticity unless the harness tracks every outbound destination |
| [decision-router](kata/decision-router/) | A model that must choose will always choose: act only above a confidence threshold, otherwise fall back |

## ADK Recipes

[`recipes/`](recipes/) — self-contained [Google ADK](https://adk.dev) agent recipes. Each recipe is a single folder you can run locally or deploy to Google Cloud.

| Recipe | Tools |
|--------|-------|
| [hello](recipes/hello/) | Time-telling agent (local tool) |
| [search](recipes/search/) | Grounded research with `google_search` |
| [maps](recipes/maps/) | Places, weather, routes via Maps MCP |
| [registry](recipes/registry/) | Discover and invoke registered agents |
| [bigquery](recipes/bigquery/) | Query datasets via BigQuery MCP |
| [gcs](recipes/gcs/) | List buckets and read objects |
| [mcp](recipes/mcp/) | Custom MCP server on Cloud Run |

See [recipes/README.md](recipes/README.md) for prerequisites and quick start.

## Agent skills

[`skills/`](skills/) — reusable [agent skills](https://agentskills.io/specification) for Claude Code and compatible agent CLIs; copy a folder into a `skills/` directory your agent reads.

| Skill | What it does |
|-------|--------------|
| [llm-council](skills/llm-council/) | Put a hard question to several independent sub-agents, have them rank each other's answers anonymously, then synthesise one verdict that keeps the disagreements visible |

## Why this exists

Three reasons:

- **Showing beats telling.** The labs are the proof. Frameworks describe the problem; runnable code demonstrates the answer.
- **Sharing what works.** Patterns I've used in real deployments, distilled into the smallest reproducible form.
- **A place to tinker.** New tools, new threats, new ideas — this is the bench.

## Contributing

PRs welcome. See [`CONTRIBUTING.md`](CONTRIBUTING.md). Code of Conduct applies.
