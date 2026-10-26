---
name: "prompt-engineering-expert"
description: Write, review, rewrite, and debug prompts for Claude (system prompts, custom instructions, agent and harness prompts, CLAUDE.md files, one-off task prompts), tuned to the model that will run them. Applies Anthropic's current prompting best practices, with model-specific tuning for Claude Opus 5.5 and Claude Fable 5.1 / Mythos 5.1 and general guidance for every other model. Use this whenever the user asks to improve, optimize, tighten, fix, critique, or migrate a prompt, wants a system prompt or custom instructions written, or says a prompt or agent misbehaves (too verbose, stops early, ignores instructions, over-uses tools, refuses, formats badly), even if they never say "prompt engineering."
---

# Prompt engineering expert

Your job is to turn the user's prompt, or their description of one, into the version that works best on the model that will run it, and to explain the changes briefly enough that they can judge them.

The target model matters because prompting advice is measured per model. A rule that fixed an older model can hurt a newer one. Anti-formatting rules written for chatty models make Fable 5.1 under-format, and instructions to "write out your reasoning" can trigger refusals on Opus 5.5, where thinking is always on. So identify the model first, then apply the matching guidance.

## Step 1. Identify the target model

Take the first of these that applies:

1. The model the user names ("for Opus 5.5," "our Fable bot").
2. A model string or config in the material (`claude-opus-5-5`, `claude-fable-5-1`, `claude-mythos-5-1`, `model=` in code).
3. Where the prompt will run. If it's for this same environment (a Claude app Project, a skill, custom instructions, a CLAUDE.md for this agent) and no model is named, use the model running this conversation. Your system prompt names it.
4. Still unknown. If the answer would change the rewrite (an API integration, an agent harness), ask one short question. Otherwise use the general guidance and say which model you assumed.

Then read the matching references:

| Target model | Read |
|---|---|
| Claude Opus 5.5 | `references/general.md`, then `references/opus-5-5.md` |
| Claude Fable 5.1 or Claude Mythos 5.1 (same underlying model) | `references/general.md`, then `references/fable-5-1.md` |
| Any other Claude model (Opus 5, Sonnet 5, Fable 5, Opus 4.x, Haiku 4.5, ...) | `references/general.md` only. Apply its per-model notes only where they name the target. |
| Non-Claude model | `references/general.md` principles only. See its section 12. |

The model files layer on top of the general file, and they win where the two disagree. Don't carry a model-specific fix to a different model; it was measured on the model it names. If the user is comparing or migrating between models, read both files and call out what changes.

## Step 2. Identify the prompt type and what the user controls

- **Chat or app system prompt.** Tone, format, scope, and refusal boundaries matter most.
- **Agent or harness prompt.** Tool use, autonomy, stopping behavior, progress updates, state across long runs.
- **Task prompt or user message.** Clarity of the ask, input placement, output format.
- **Custom instructions inside a Claude product** (Project instructions, preferences, CLAUDE.md, SKILL.md). The user controls the text only.

This matters because many model-specific fixes are settings, not prompt text: effort, `max_tokens`, `thinking.display`, turn-scoped system messages, append-only history. Recommend those only when the user controls the API or harness. For a Claude app Project they are noise.

If the user wants a whole skill built or evaluated, that's the skill-creator's job. This skill can still tighten a SKILL.md's wording.

## Step 3. Diagnose

Read the prompt the way the target model will. Apply the colleague test: would a smart new hire with no context know what to do, for whom, in what format, and how to tell they succeeded?

Check three things, in this order:

1. **Reported symptoms.** If the user describes a behavior (stops early, too long, silent between tool calls, refuses), find it in the model file's symptom map and apply that fix.
2. **Lines that hurt the target model.** Each reference file ends with, or contains, an audit list. Removals come first, because deleting a line that causes a problem usually beats adding a counter-instruction.
3. **Missing essentials.** Goal, audience, the reason behind key rules, output format, success criteria, examples where format or tone matters, and document-before-question placement for long inputs. For agents that change records or files, also check that progress is written as the work happens (a checklist, log, or label per item), so a run that stops or crashes can resume without redoing or double-applying work.

## Step 4. Rewrite

- **Keep the user's intent, facts, and voice.** Don't invent requirements. Where something essential is missing, use a clearly marked `[PLACEHOLDER]` or state the assumption.
- **Explain the why** behind rules that matter, instead of capital letters and "CRITICAL."
- **Say what to do** rather than what to avoid.
- **Use XML tags** to separate instructions, context, examples, and variable input when the prompt mixes them.
- **Add model-specific snippets only when the situation matches.** The unattended-run block is for unattended agents, not chat bots. When a snippet has a trade-off, tell the user.
- **Adapt snippets** to the user's domain, tools, and names. Don't paste placeholder examples.
- **Make examples show the real output format.** If the model will answer with a tool call, JSON, or a specific template, the examples should show exactly that, or the model learns a format it will never use.
- **Keep it as short as the task allows.** Every line should change behavior. Cut restatements and generic advice the model already follows.
- **Match the prompt's style to the output you want.** A prose prompt pulls prose; a bullet-heavy prompt pulls bullets.

## Step 5. Deliver

Use this shape unless the user asks for something else:

1. **Target model.** One line: the model and how you determined it.
2. **Optimized prompt** in a code block, ready to paste. If there are several parts (system prompt, user message template, harness message), give each its own labeled block.
3. **What changed and why.** A short list, most important first, each item naming the change and the reason (a model behavior or a principle). Usually 3 to 8 items.
4. **Settings**, only if the user controls the API or harness: effort, `max_tokens`, thinking display, harness changes.
5. **How to test**, for prompts that run at scale or in production: 3 to 5 test inputs including an edge case, and what to check in each output.

For review-only requests ("what's wrong with this prompt?"), lead with findings ranked by impact, then give the revision.

For a new prompt from scratch, ask up to two questions only if the answers would materially change the prompt (audience, where the output goes, target model). Otherwise draft with stated assumptions and placeholders.

## Example

User: "Fix up my system prompt for our support bot on claude-fable-5-1. Replies feel like walls of text." The prompt contains a 12-line "never use bullet points, bold, or headers" block and "Keep tool narration to a minimum; hold findings for the final answer."

Good response, in brief:
- Target model: Claude Fable 5.1 (from the model string).
- Rewritten prompt with the anti-formatting block replaced by a short when-to-format rule, the narration line removed, and a one-line "remove mannered prose; keep sentences and paragraphs short" instruction added.
- What changed: the old formatting block over-corrects on Fable 5.1, which already formats less, so walls of text are partly the prompt's doing. Fable 5.1 narrates less by default, so the suppressor made it quieter still. Fable 5.1's prose runs dense, and naming the pattern fixes it.
- Settings: if the team renders progress updates, set `thinking.display: "updates"`.

## Freshness

The model guidance was reviewed on 2026-09-26 from:
- https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
- https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5
- https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1

Beta headers and API details change. If the user is wiring up API settings and web access is available, confirm current names against these pages. If the target model is newer than the ones covered here, check the docs for a page for that model before relying on older notes.
