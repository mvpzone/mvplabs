# llm-council

A skill that puts a hard question to a small council of independent sub-agents, has them rank each other's answers without knowing who wrote what, and then produces one verdict that keeps the disagreements visible instead of averaging them away.

## The method

Three stages, after [Andrej Karpathy's llm-council](https://github.com/karpathy/llm-council) (reviewed at commit `92e1fccb1bdcf1bab7221aa9ed90f9dc72529131`):

1. **Independent answers.** Every member gets the same neutral question and cannot see the others.
2. **Anonymous peer review.** Answers are shuffled and relabelled `Response A..N`. Each member critiques them, ranks them best to worst, and names what all of them missed.
3. **Chairman.** One synthesis: verdict, agreements, disagreements with the strongest case for each side, blind spots, confidence, and a single next step.

Differences from the original: it runs as a skill inside your agent session rather than a web app, uses no third-party API or key, caps calls and words, reports rank dispersion rather than only the mean, and fences member output as untrusted data.

## Install

Copy this folder into a skills directory your agent reads:

```bash
cp -R skills/llm-council ~/.claude/skills/          # all projects
# or
cp -R skills/llm-council <your-project>/.claude/skills/   # one project
```

It is manual-only (`disable-model-invocation: true`): the agent never starts a council on its own. Invoke it with `/llm-council`.

## Usage

```
/llm-council Should we split the ingest service into two deployables now, or after the schema stabilises? Constraints: two engineers, one on-call rotation, a release every two weeks.
```

The agent states the plan (members, models, call count), runs the stages, and reports in chat.

## Cost

A default council of 3 makes 3 + 3 + 1 = 7 calls (the chairman is your own session, so 6 extra). Use cheaper model families for members. Answers are capped at about 250 words, reviews at 150. Use it for decisions that matter, not lookups.

## Security notes

- Member and reviewer outputs are treated as untrusted data and wrapped in labelled fences in every later prompt, so an answer containing "ignore the above" or a command is evaluated, not obeyed.
- Members get no tools: they answer from the text you give them. The skill never runs a command, opens a URL, or edits a file because a member asked.
- No network calls and no API keys are needed; members are sub-agents you already run. Do not paste secrets or private files into the framed question.

## When not to use it

Factual lookups, anything with one right answer, creation tasks, or re-opening a decision your docs already settle.

## Prior art

Ideas only; no code or text copied.

- [karpathy/llm-council](https://github.com/karpathy/llm-council), `92e1fccb1bdcf1bab7221aa9ed90f9dc72529131`: the three-stage method.
- [aiwithremy/claude-skills-llm-council](https://github.com/aiwithremy/claude-skills-llm-council), `55ee36e89e0f3f780099ac50332fbb3ec8d14738`: council-as-a-skill packaging.
- [tenfoldmarc/llm-council-skill](https://github.com/tenfoldmarc/llm-council-skill), `0dc03275b0ddf542545da3a9684510fff31df353`: a second skill port.

## License

Apache-2.0, see [LICENSE](LICENSE).
