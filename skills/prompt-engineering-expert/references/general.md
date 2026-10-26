# General Claude prompting best practices

Baseline for every target model. Opus 5.5 and Fable 5.1 have their own files that layer on top of this one.

Source: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices (reviewed 2026-09-26). Snippets below are condensed adaptations, not the official text. Link the source when the user wants the canonical wording.

## Contents
1. Core principles
2. Long context
3. Output and formatting
4. Prefill and its replacements
5. Tool use
6. Thinking and reasoning
7. Agentic systems
8. Vision and frontend
9. Model identity
10. Per-model notes from the general guide
11. Audit list: lines to remove or rewrite
12. Non-Claude targets

---

## 1. Core principles

**Be clear and direct.** Treat Claude as a brilliant new hire with no context on your norms. The colleague test: if a smart coworker with minimal context would be confused by the prompt, Claude will be too. State the desired output format and constraints. Use numbered steps only when order or completeness matters.

**Ask explicitly for ambitious output.** Current models do what you ask, fairly literally. If you want "above and beyond," say so.

```
Less effective: Create an analytics dashboard
More effective: Create an analytics dashboard. Include as many relevant features and interactions as possible. Go beyond the basics to a fully featured implementation.
```

**Give the reason behind a rule.** Claude generalizes from the reason, so one explained rule covers cases the bare rule misses.

```
Less effective: NEVER use ellipses
More effective: This reply is read aloud by a text-to-speech engine, which can't pronounce ellipses, so don't use them.
```

**Use examples.** Few-shot examples are one of the most reliable ways to steer format, tone, and structure. Use 3 to 5. Make them relevant to the real use case, diverse enough that Claude doesn't copy an accidental pattern (same length, same opening, same topic), and wrap them in `<example>` tags inside `<examples>` so they read as examples, not instructions.

**Structure with XML tags** when a prompt mixes instructions, context, examples, and variable input: `<instructions>`, `<context>`, `<input>`, `<documents>`. Keep tag names consistent and descriptive. Nest when content is hierarchical.

**Set a role in the system prompt.** One sentence focuses behavior and tone ("You are a support agent for a home insurance agency."). Skip long invented résumés ("20 years of experience"); the role plus real context about the audience and task does the work.

## 2. Long context

For inputs over roughly 20k tokens:

- Put long documents at the top, above instructions, examples, and the question. Ending with the query improved response quality by up to 30% in Anthropic's tests, most on multi-document inputs.
- Wrap each document with its metadata:

```xml
<documents>
  <document index="1">
    <source>q3_campaign_export.csv</source>
    <document_content>{{EXPORT}}</document_content>
  </document>
</documents>
```

- For long-document tasks, ask Claude to pull the relevant quotes into `<quotes>` tags first, then work from those quotes. This keeps it focused on what matters.

## 3. Output and formatting

- **Say what to do, not what to avoid.** "Write in flowing prose paragraphs" works better than "Don't use markdown."
- **Use XML format indicators** when output must be parsed: "Put the summary in `<summary>` tags."
- **Match the prompt's style to the output you want.** A markdown-heavy prompt pulls markdown-heavy output. Write the prompt in prose if you want prose back.
- **Spell out detailed formatting rules** when defaults don't fit (when to use lists, headings, bold). Fable 5.1 is the exception: it already under-formats, so long anti-markdown blocks suppress structure it needs. See `fable-5-1.md`.
- **Plain-text math:** if LaTeX is unwanted, say so and name the replacement ("/" for division, "^" for exponents).
- **Verbosity:** current models are concise and may skip summaries after tool calls. If you want one, ask: "After finishing a task that used tools, give a short summary of what you did." Opus 5 runs long by default and needs an explicit conciseness instruction. Fable 5.1 writes fewer progress updates and needs them requested.
- **No preamble:** "Respond directly without preamble. Don't open with phrases like 'Here is...' or 'Based on...'." Strip stragglers in post-processing if needed.

## 4. Prefill and its replacements

Prefilling the last assistant turn returns a 400 error on Claude 4.6 models and later (and Mythos Preview). Earlier models, including Haiku 4.5, Sonnet 4.5, and Opus 4.5, still accept prefill. Only flag prefill as broken when the target is 4.6 or later, or when the user plans to migrate.

Replacements:

| Prefill was used for | Replace with |
|---|---|
| Forcing JSON, YAML, or a schema | Structured Outputs, or ask for the schema directly (newer models follow complex schemas well, especially with retries) |
| Classification labels | A tool whose input has an `enum` of valid labels, or Structured Outputs |
| Skipping preambles | A direct no-preamble instruction, XML output tags, or tool calling |
| Steering around refusals | Clear context in the user message. Usually no longer needed. |
| Continuing a cut-off reply | Put it in the user turn: "Your previous response was interrupted and ended with `[last text]`. Continue from there." Or just retry. |
| Re-injecting reminders in long chats | Put reminders in the user turn, expose context through tools, or refresh during compaction |

## 5. Tool use

**Use action verbs when you want action.** "Can you suggest changes to this function?" gets suggestions. "Change this function to improve its performance" gets edits.

**Set the default explicitly** for agents:

```
Proactive: By default, make the changes rather than only suggesting them. If intent is unclear, infer the most useful action and proceed, using tools to find missing details instead of guessing.

Conservative: Don't edit files or start implementing unless clearly asked. When intent is ambiguous, research and recommend instead of acting.
```

**Drop the shouting.** Current models follow the system prompt closely. Language written to fix under-triggering on older models ("CRITICAL: You MUST use this tool when...") now causes over-triggering. Write "Use this tool when..." and give the condition.

**Parallel calls.** Current models already run independent tool calls in parallel. To push it close to 100%:

```
When several tool calls don't depend on each other, make them all at once in the same response. When a call needs a value from an earlier result, run them in order. Never guess or use placeholders for missing parameters.
```

To slow things down instead: "Run operations one at a time."

## 6. Thinking and reasoning

**Adaptive thinking is the default mode on current models.** Claude decides when and how much to think based on the effort parameter and the query's difficulty. Effort is the main control for depth, latency, and cost. Adjust effort before adding prompt instructions about thinking.

| Model | Thinking behavior |
|---|---|
| Fable 5.1, Mythos 5.1, Fable 5, Mythos 5, Opus 5.5 | Always on, adaptive only. Can't be disabled. |
| Opus 5, Sonnet 5 | On by default. Opus 5 can disable it only at effort high or lower. |
| Opus 4.6 to 4.8, Sonnet 4.6 | Off unless you set `thinking: {type: "adaptive"}` |
| `budget_tokens` (manual extended thinking) | Deprecated on Opus 4.6 and Sonnet 4.6. Returns 400 on 4.7 and later. Migrate to adaptive plus effort; use `max_tokens` as the hard cap. |

Guidance:

- **Prefer general instructions over hand-written step plans.** "Think thoroughly about this" often beats a scripted Step 1/Step 2/Step 3, because Claude's own reasoning usually exceeds the plan a person would write. Replace prescriptive chain-of-thought scaffolds with the goal plus success criteria.
- **Show reasoning style through examples** by putting `<thinking>` tags inside few-shot examples. Claude generalizes the pattern to its own thinking.
- **Manual chain of thought is a fallback** for when thinking is off: ask Claude to reason in `<thinking>` tags and answer in `<answer>` tags. Don't use it on models where thinking is always on (see the model files for why this can trigger refusals).
- **Self-check:** "Before you finish, verify your answer against [criteria]." Reliable for code and math. Skip on Opus 5, which verifies on its own and over-verifies when told to.
- **Guide interleaved thinking** in tool loops: "After each tool result, check its quality and decide the best next step before acting."
- **Overthinking:** "Pick an approach and commit to it. Revisit only if new information contradicts your reasoning." Or lower effort.
- **Thinking too often** (common with large system prompts): "Thinking adds latency. Use it only when the problem needs multistep reasoning. When in doubt, answer directly."
- **Opus 4.5 with thinking off** is sensitive to the word "think." Use "consider" or "evaluate."

## 7. Agentic systems

**Long tasks and context limits.** If the harness compacts context or saves state to files, tell the model so it doesn't wrap up early:

```
Your context will be compacted automatically as it fills, so you can keep working. Don't stop early over token budget. Before a refresh, save progress and state to [file or memory]. Finish the task fully.
```

**Multi-window workflows.**
- Use a distinct first-window prompt that sets up the framework (tests, setup scripts); later windows iterate on a to-do list.
- Keep test status in structured files (`tests.json`) and freeform notes in `progress.txt`. Use git as the log and checkpoint system.
- Tell a fresh window how to reorient: "Run pwd. Read progress.txt, tests.json, and the git log. Run a basic integration test before new work." Starting fresh this way often beats compaction.
- Give the model ways to verify its own work (tests, browser or computer use tools).
- Tell it tests are not to be deleted or weakened to make them pass.

**Autonomy vs. safety.** Ask for confirmation on hard-to-reverse actions:

```
Weigh how reversible and far-reaching each action is. Go ahead with local, reversible steps like editing files or running tests. Ask first before anything destructive (deleting files or branches, dropping tables), hard to undo (force-push, hard reset), or visible to others (pushing code, posting, sending messages). Don't use destructive shortcuts to get past obstacles.
```

**Research.** Define what a successful answer looks like, ask for cross-source verification, and for hard questions ask the model to track competing hypotheses and confidence in a notes file.

**Subagents.** Current models delegate on their own when subagent tools exist. If they over-delegate: "Use subagents for parallel, independent work or work that needs isolated context. For simple tasks, single-file edits, or sequential steps, work directly."

**Chaining.** Split into separate calls only when you need to inspect or branch on intermediate output. The standard chain is draft, review against criteria, refine.

**Coding guardrails**, each added only when the behavior shows up:
- Scratch files: "Delete any temporary files or scripts you create before finishing."
- Over-engineering: "Only make changes that are requested or clearly necessary. No extra features, refactors, docstrings on untouched code, defensive handling for impossible cases, or one-off abstractions."
- Test gaming: "Write a general solution that works for all valid inputs, not just the tests. Don't hard-code test values. If a test is wrong or the task is infeasible, tell me."
- Hallucinated code claims: "Never describe code you haven't opened. Read the referenced files before answering."

## 8. Vision and frontend

**Vision.** For dense images, a crop or zoom tool gives consistent gains: the model inspects a region at higher resolution. Video can be analyzed as frames.

**Frontend.** Without direction, models drift to a generic "AI" look. General "be creative" instructions mostly swap one default for another. Better: name the specific choices you want (typography, a committed color palette with sharp accents, one orchestrated page-load animation, layered backgrounds) and the specific defaults to avoid (Inter/Roboto/Arial, purple-on-white gradients, cookie-cutter layouts). Request animations and interactivity explicitly.

## 9. Model identity

If an app needs Claude to name itself or pick a model string:

```
The assistant is Claude, created by Anthropic. The current model is Claude [MODEL].
When an LLM is needed, default to Claude [MODEL] (model string: [MODEL_STRING]) unless the user asks otherwise.
```

## 10. Per-model notes from the general guide

Apply a note only when the target matches.

- **Opus 5:** default replies run long, and raising or lowering effort doesn't reliably change length. Add an explicit conciseness instruction. It verifies its own work well; remove verification instructions carried over from older prompts (they cause over-verification). It delegates to subagents readily; add damping guidance if needed. With thinking disabled it can leak internal XML tags; prefer thinking on at lower effort.
- **Opus 4.5 and 4.6:** follow the system prompt closely and over-trigger on aggressive tool language. Tend to over-engineer (extra files, abstractions). Opus 4.6 explores heavily up front, likes subagents, and may take hard-to-reverse actions without the autonomy/safety guidance above.
- **Sonnet 5, Sonnet 4.6, Sonnet 4.5, Haiku 4.5:** track their remaining context window. Tell them if the harness compacts, or they may wrap up early.
- **Sonnet 5 and Opus 4.8** have their own pages covering response length, effort calibration, tool triggering, literal instruction following, and frontend defaults. If the user is tuning for one of them and web access is available, the page is at `https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-<model>` (for example `prompting-claude-sonnet-5`).

## 11. Audit list: lines to remove or rewrite

Removing a line that hurts usually beats adding a counter-instruction. Check for:

- ALL-CAPS commands and "CRITICAL / MUST / ALWAYS" pressure without a reason. Rewrite as a plain instruction plus the why.
- Negative-only formatting rules ("no markdown") where a positive version exists.
- Prescriptive step-by-step reasoning scripts on models with thinking on. Replace with the goal and success criteria.
- Prefilled assistant turns on 4.6+ targets.
- "If in doubt, use [tool]" or "Default to using [tool]" blanket rules. Replace with the condition under which the tool helps.
- Anti-laziness pressure written for older models ("be extremely thorough, check everything twice"). Current models already do more; this causes over-exploration.
- Vague quality words ("make it good," "high quality") with no criteria. Replace with what good looks like.
- Contradictions between sections, and duplicated rules that drift apart.
- Instructions buried after long pasted context when they belong before or after it by design (documents first, question last).

## 12. Non-Claude targets

For GPT, Gemini, Llama, and others, keep the model-agnostic principles (clarity, context and reasons, examples, delimiting input, explicit format, positive instructions, success criteria). Drop Claude API specifics: effort, thinking display, prefill notes, turn-scoped system messages, Structured Outputs names. Say that the rewrite is tuned on Claude guidance and that the user should test on their model.
