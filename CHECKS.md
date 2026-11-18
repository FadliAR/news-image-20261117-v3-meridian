# CHECKS — news-image-20261117 v3b ("The Daily Meridian")

Kit used: fresh download 2026-11-18 from https://make.fun/c/news-image-20261117/kit
- kit.json format agent-fun/kit/v1, phase dev
- bundle_sha256 029664c9aa1a369801e8aeca15ece16758f4ef1ffcbf42878f84b3fe0cd09870
- harness_version harness@6cd2f7103e5cc31f28573f71a7e208d605616f58b034ff6d32bbc81b30d8d945, node v26.13.1
- Competition opens 2026-11-17T23:43:00Z; server deadline 2026-11-19T00:00:00Z
  (= 2026-11-19 07:00 WIB). Escrow entries list committed before 00:10Z.
- Submission rule Force_Last, max 10/day, 20 total, transcripts required,
  OSI license, repo created after open, authorship policy 12.

## A. Image gate (sealed scorer, Valid = 1 or 0)
- Semantics: file at entry.png is a whole PNG or JPEG (told apart by first
  bytes; every PNG chunk checksum correct, image data matches header), at
  most 1 MiB (1048576 bytes), at most 1024x1024 px. No fact/subject check.
- Pass: Valid = 1, only valid entries reach the judge.
- This build proves it: generator writes a real PNG, 1024x1024, target
  250-650 KB (well under 1 MiB), verified locally by parsing the PNG header
  and by file size after every run.

## B. Program / harness gate (program/v1)
- Semantics: repo root holds main.ts (Node 22) or main.py (Python 3.13),
  standard library only, nothing installed, no network. Runs in a fresh
  container: 1 CPU, 512 MB, 64 pids, 60 s wall, read-only /bot, writable
  /output. It must write /output/entry.png (MAKEFUN_OUTPUT_DIR locally).
- The program runs TWICE; both runs must write the same bytes, or grading
  fails.
- This build proves it: main.py is Python stdlib only, reads no files,
  uses a fixed seed / no randomness, no time, no network; local proof is
  two consecutive runs compared with cmp + sha256 (both recorded).

## C. Judge (not a pass/fail check, but the ranking contract)
Judge z-ai/glm-5.3-flash via OpenRouter (named superbot, effort high),
pairwise, both orders, margin 1-5, Bradley-Terry win rate; final heat =
3 Swiss rounds + playoff of top 52; playoff entries place above non-playoff.
Criteria in priority order:
  1. One day's news, and it names that day: specific recognisable events
     of that day + the date. Pre-13-Nov days / no date / no news lose.
  2. Selection and breadth: most consequential stories, across regions
     and fields, not one country or one beat.
  3. It reads: a viewer who missed the day can tell what happened from
     the image alone; each story clear from picture + short labels;
     nothing self-contradictory, implausible, or known false.
  4. Faithful: as reported, no hype, no speculation shown as fact.
  5. Craft: one clear composition, clean, legible at about 300 px across,
     no smears, artefacts, or garbled text.
- This build proves it by construction: giant date masthead naming
  Tuesday 17 November 2026, lead trio in the field's consensus order,
  13 illustrated stories + 33 numbered one-liners (46 total), numbered
  world map with 7-region legend, four-number stat strip, attribution
  footer marking contested claims as claims, dense broadsheet grid.

## D. Transcript gate (10 pass/fail + thinking_fresh note/fail rules)
Any failure rejects the entry (not graded, no prize); fix and resubmit
before the deadline is allowed.
1. transcripts_present — at least one session parsed from the upload.
   Proof: parent bundles this builder session + the parent side-chat
   session; bundle/check output must list >=1 parsed session.
2. transcripts_recorded — every session is a harness-recorded log or a
   file exported from its record. handed_over_places = none: a handed-over
   session is ranked but takes NO paid place.
   Proof: use only real Muse session files, never a self-written export,
   never handed_over.
3. thinking_wellformed — every user/assistant/tool message timestamped;
   no assistant/tool message >60 s behind the latest before it
   (max_step_back_sec 60); every tool result answers an earlier tool call
   of its session; a self-export must name its harness.
   Proof: upload harness logs unchanged; never edit session files.
4. thinking_in_window — every transcript timestamp between competition
   opening (2026-11-17T23:43:00Z) and receipt time, +-60 s skew.
   Proof: this builder session and its parent side chat both start after
   the opening and before the deadline.
5. thinking_committed — for a signed entry, the uploaded transcripts are
   exactly those the entry signature names (by sha256); unsigned skips.
   Proof: parent bundles first, then signs/submits that same bundle;
   no re-bundle after signing.
6. thinking_reproduces — >=30% of counted lines authored (first carried
   by the agent's own write/edit in the transcripts); lines first seen in
   a human message, a tool result, a read-back, or nowhere (absent), and
   re-typed/copied lines, count against; kit starter lines are excluded;
   <=40% of counted text lines unwritten (absent or imported by clone /
   curl / cp-from-outside / archive unpack), failing only at >=10 such
   lines; entrypoint main.py must have >=1 authored line.
   Proof: CLEAN ROOM — all code in this repo is written from scratch via
   write/edit in this session; no file from any earlier news-image
   workspace is opened or copied (only prose ENDGAME.md / AUTOPSY.md);
   the kit is downloaded into a git-ignored folder and its files are
   never committed, so no imported lines enter the snapshot.
7. thinking_turns — >=5 assistant turns carrying text or thinking
   (tool-only turns do not count). Proof: this session works in many
   narrated steps: rules, checks, code, run, visual QA, revision, report.
8. thinking_priced — usage records must price to a known model (or $0 for
   a genuinely local runtime); a self-reported session needs provider
   usage on >=50% of assistant messages, real unrounded counts, output
   <=500 tokens/sec over its timestamps; Muse app sessions must carry
   Muse's own usage rows, >=1 row, attached with bundle --muse-usage
   (kit gate table lists min_priced_share 1; the body text says an
   unpriced record is a warning — satisfy the stricter reading).
   Proof: parent attaches the muse-usage rows the check prescribes,
   unchanged, and re-checks until this passes.
9. thinking_revised — some file (entrypoint or code it runs) takes its
   final content from >=2 assistant write/edit messages (min_file_writes 2).
   Proof: generator is written, rendered, visually inspected, then
   edited at least once for real fixes before the final run.
10. thinking_fresh — for a source-bundle entry, credited lines must come
    from sessions showing the kit init anchor line in a tool result
    before their first counted write; short of that it SKIPS as a note
    (not a rejection, prize paid as any other); a quote timestamped
    before the round fails.
    Proof: no pre-round anchor quote is claimed; the check is expected
    to skip as a note for this bundle-flow entry, as in prior entries.
11. transcripts_run_record — required from 2026-11-17T00:00:00Z. Bundle
    must carry a run record not contradicted by the upload: prompt is
    the person's own opening prompt, never blank / unfilled template /
    an agent's or harness's hand-off; typed = first message of an
    uploaded top-level session; other origins name what started the run.
    Harness, version, provider, model, effort each declared or recorded
    by every top-level session. System prompt uploaded as a file or
    carried in-session (withheld rejects from 2026-11-18T12:00:00Z).
    Every MCP server used is listed by name; none marked builtin unless
    the harness ships it. Instruction files: collected only if the
    upload carries one, none only if it carries none, withheld rejects
    from 2026-11-18T12:00:00Z. If another session started the run, the
    upload must carry every parent-chat link up to the session that
    opens with the person's prompt (max 4 links) — missing link rejects
    from 2026-11-18T12:00:00Z.
    Proof: parent bundles with --parent-session = the fresh side chat
    (whose first message is the owner's own instruction), this builder
    session as the build session, system-prompt file uploaded,
    instructions collected, --mcp none, harness muse 1.3, provider meta,
    model muse-spark-1.3, effort default, prompt origin handed-off with
    via naming the subagent task from the main agent.

## E. Repository / submission checks (site-side)
- repo ownership: GitHub owner is the account's GitHub login (FadliAR),
  or .makefun/owner.json names a linked wallet. This repo is created
  under FadliAR, so no claim file is needed.
- repo created at/after opening (2026-11-17T23:43:00Z), public, OSI
  license present (MIT LICENSE at root), submitted commit stays reachable
  (no history rewrite, no making it private, no license removal).
- snapshot not a copy: a snapshot identical to another account's earlier
  submission is refused; identical snapshots from the same account are
  allowed. Proof: this repo's files are all newly authored here.
- repo_readme (GitHub entries): README at the submitted commit carries
  the three live badges as images — the competition badge
  https://make.fun/badge/news-image-20261117.svg plus this repo's own
  rank.svg and reward.svg under
  https://make.fun/badge/news-image-20261117/FadliAR/news-image-20261117-v3-meridian/
  — links to a make.fun page, and leaves no {owner}-style placeholder.
- repo_about (GitHub entries): GitHub About set before submit, website
  on make.fun, topic "makefun" (set via gh by the parent before submit;
  recorded in ENDGAME.md if already set by the builder).
- committed_secret: no pushed secret value anywhere in repo history or
  transcripts. Proof: no secrets are used or written by this build.
- Limits: <=10 submissions/day, <=20 total; Force_Last — the last
  receipt before the deadline is the final entry, so the parent submits
  v3b only after visually confirming it is at least as strong as v2/v3.

## F. Disqualification traps (avoid absolutely)
Network probing / sandbox escape / attacking the grader; fabricated,
edited, withheld, or borrowed transcripts; submitting someone else's
work; multiple accounts; making the repo private / removing license /
rewriting away the submitted commit; exploiting a gate/grader bug;
false claim payout details. This build does none of these: original
drawings, original code, real sessions, free entry, no transactions.
