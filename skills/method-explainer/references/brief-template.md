# Brief template: delegating a method explainer to a subagent

Fill in every `{...}` and delete the notes in square brackets. The subagent knows only what is written here, so state the reader, the code and the walkthrough concretely. Save the filled brief in the explainer's folder (`briefs/<date>_original-brief.md`) and tell the subagent to read it from there, so the record of what was asked stays beside the work.

**Before you write it**, run the example once yourself (a minute's work) and put the main numbers in the walkthrough as values to check against. In the first test the subagent turned them, and the paper's published values, into assertions in its data script, so its computation was checked against two independent sources before anything was drawn.

**How to run the subagent.** Use the model with the longest context you have, at the highest effort: omit the Agent tool's `model` parameter so the subagent inherits the session's model, unless you know the override keeps the long context. In the first test, a subagent started with `model: opus` ran out of context after about 40 minutes (reading the code alone filled most of a 200,000-token window), and a second one, on the session's 1M-context model, finished the work in an hour and about 760,000 tokens. Expect one to two hours. If the subagent ends without a report, everything is in its folder (`spec.md`, `checks/`, the artifact URL in the spec), and its last messages are in its transcript, `~/.claude/projects/<project>/<session>/subagents/agent-<id>.jsonl`; in the first test the report was recovered from there. A report can also be delivered to the parent session instead of to you; if one hasn't arrived within a few minutes, say so rather than wait.

Two sections did most of the work in the original brief. "The walkthrough to cover" told the subagent the level of detail wanted, step by step, with the real numbers, and "Source of truth" told it to trust the code over that walkthrough. Keep both.

---

Hello, and thank you. Please take your time and do this properly; {person} asked for your best work.

**Who and why.** {Who the reader is: their field, what they already know (the paper's vocabulary? the library's API?), and what they don't (this code).} {What they want: to understand how {code} computes {thing}, for example, so that phrases like "{phrase from the code or paper}" map onto a picture.} {Where it may go later, such as to the code's authors, so it must be correct and readable on its own.} Make one explainer figure that shows every step below at the level of detail given, traced on one real example, with the explanation on a page beside it.

**Use the method-explainer skill** (`better-figures:method-explainer`: invoke it, or read its `SKILL.md` and `references/`). It says how to pin the code, compute the example, write the spec, draw with the figures skill's kit, check, and publish. This brief gives the content; the skill gives the process.

**Source of truth.**
- The code: {repository} at {path}, commit {hash} ({date}). Read {the entry points and modules, by file} in full, following every function the example passes through. {Any project instructions to read first, such as AGENTS.md or CLAUDE.md.}
- Run it with {the project's environment command}. {The configuration to use, for example the defaults at this commit, and any published version to compare against.}
- Terms: {the paper, glossary or terminology skill, naming the documents in it that matter for this figure}. Use its terms; never coin new ones. Where the code and the paper name a thing differently, use the paper's term in the image and give the code's name on the page. [A domain skill's full reading list may be written for prose answers and be far too long for a figure; in the first test, a glossary, one wiki page and the two papers that define the method were enough. Name them.]
- Where this brief, the docs or the paper disagree with the code, the code wins. List every disagreement, with file and line, in `spec.md` and in your report.
- Leave the repository alone: don't edit, commit, check out, stash or push anything in it.

**The running example.** {Either: "Use {example}, which {the paper's figure / the docs' worked example / a collaborator's figure} also uses, so the two can be read together." Or: "Choose one: small enough to compute in seconds and draw whole, big enough that every step below does something. Say why you chose it."}

**The walkthrough to cover**, as I understand it; verify each item in the code and don't trust this list:
- **{Step name}.** {What goes in, what is computed, what comes out, with the real sizes and the numbers from your own run of the example.}
- **{Step name}.** {...}
- [Give every step you want drawn, at the level of detail you want. A step you leave out will probably not be drawn; a step you describe in one vague clause will be drawn vaguely.]

**Level of detail.** Give each step the space its explanation needs, not the space its importance to the results would suggest. {Anything that must be set apart, for example what the method reads against what only builds its input, or what is trained against what is fixed.}

**Where things go.**
- Files: {folder} (`spec.md`, the figure's HTML and its PNG render, `page.html`, `data/` with the scripts behind every number, `checks/` with the fresh reader's reply).
- Publish the page privately with the Artifact tool (icon "diagram"), as the skill's step 9 says, and record its URL in `spec.md`. Scratch files go in a folder named for this explainer inside the scratchpad, which other agents share. {Any index or README line to add.}
- Keep the work in files, as the skill says: bring `spec.md` up to date after each step, and write each disagreement with the code into it when you find it.
- Git: {"commit nothing", or the repository, commit message style, which paths to stage, and the attribution lines}.
- Compute: {the machine's limits: what may run here, what goes to the scheduler and how, where scratch goes}.
- Don't send the figure or message anyone; {person} decides who sees it.

**The fresh reader.** Run one round as the skill says, and save the reader's reply unedited in `checks/fresh-reader-1.md`; I will read it.

**Report**, as your final message only:
- the artifact URL and the folder;
- the commit you drew, and the configuration;
- every place the code differed from the walkthrough above;
- what the fresh reader found and what you changed;
- anything you were unsure of, especially terms and numbers.
- [When testing the skill: where the method-explainer skill was unclear, missing something or wrong.]

Pushing back is welcome. If part of this brief seems wrong, or a different example or scope would make a clearly better figure, say so in your report rather than forcing it.
