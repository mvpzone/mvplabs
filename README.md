# mvplabs

Hands-on labs and reusable recipes for cloud-native security and agentic AI. Each lab is a self-contained, runnable demonstration of one idea — small enough to read, big enough to learn from.

## Labs

| Lab | What it shows |
|-----|---------------|
| [Lab_6_1_Model_Armor](Lab_6_1_Model_Armor/) | Prompt injection defenses and guardrails with Model Armor |
| [Lab_8_1_ADK_Observer](Lab_8_1_ADK_Observer/) | Observability for Google ADK agents — notebook + SQL for inspecting agent behavior |
| [Lab_4_1_AgentSpace_Security](Lab_4_1_AgentSpace_Security/) | AgentSpace deployment security (in progress) |

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

## Why this exists

Three reasons:

- **Showing beats telling.** The labs are the proof. Frameworks describe the problem; runnable code demonstrates the answer.
- **Sharing what works.** Patterns I've used in real deployments, distilled into the smallest reproducible form.
- **A place to tinker.** New tools, new threats, new ideas — this is the bench.

## Contributing

PRs welcome. See [`CONTRIBUTING.md`](CONTRIBUTING.md). Code of Conduct applies.
