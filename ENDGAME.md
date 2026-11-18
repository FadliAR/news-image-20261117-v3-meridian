# ENDGAME — news-image-20261117 v3b ("The Daily Meridian")

## Artifact
- Repo: https://github.com/FadliAR/news-image-20261117-v3-meridian
  (created 2026-11-18T14:50:42Z, after the competition opened
  2026-11-17T23:43:00Z; public; MIT license; GitHub About set by the
  builder: website https://make.fun/c/news-image-20261117, topic makefun)
- Code commit: `1daf6b5aff6d93885224821c4cb6ed400ea07b66`
  (a final docs commit carrying this file follows it; the parent
  submits the HEAD recorded in its report)
- Checkpoint commit: `c94fdfb` (CHECKS.md, LICENSE, README, .gitignore)
- entry.png: 1024x1024 PNG, **376,792 bytes**
- entry.png sha256: `ad616f1d48c5e914ca245ce7b4bc896dc290ab0513ebf758b9826d43d13ffd42`
- Determinism: generator run twice into two output dirs; `cmp` reported
  no difference and all three copies (repo entry.png + both runs) share
  the sha256 above. Runtime ~4.5 s per run (limit 60 s), stdlib only.

## Kit
- Fresh kit downloaded into this workspace 2026-11-18 (git-ignored,
  never committed): bundle_sha256
  029664c9aa1a369801e8aeca15ece16758f4ef1ffcbf42878f84b3fe0cd09870,
  harness@6cd2f7103e5cc31f28573f71a7e208d605616f58b034ff6d32bbc81b30d8d945.
- CHECKS.md in this repo documents every server check, its semantics,
  its threshold, and how this build proves it. It was written before
  any generator code.

## Story count (counted mechanically from the source lists)
- Illustrated features: **13** (3 lead scenes + 10 features 4-13),
  each with its own drawn scene, kicker, headline and summary.
- One-liners ("ALSO ON TUESDAY 17 NOVEMBER", numbered 14-46): **33**
- **Total: 46 stories**

## Checklist self-assessment vs the winners' formula
- [x] Top strip: "THE WORLD'S NEWS IN ONE PICTURE" left /
  "45+ STORIES · 6 CONTINENTS · ALL FROM TUESDAY" right; paper name
  "THE DAILY MERIDIAN".
- [x] Giant masthead: "Tuesday 17 November 2026" full width (43 px
  stroke lettering), with a story-count subline.
- [x] Lead trio, each a real drawn scene with labels + caption bar:
  1. Kerch/Crimea Bridge — broken span in the sea, explosion, smoke,
     CRIMEA/RUSSIA labels, caption "KERCH STRAIT · STRUCK FOR A SECOND DAY".
  2. Iran-Gulf — Gulf scene: IRAN/QESHM/BAHRAIN/ARABIA/HORMUZ labels,
     dashed strike arcs, drone markers, "DRONES DOWNED", radar burst
     at Bahrain.
  3. Quad summit Manila — four drawn flags (US, India, Japan,
     Australia), summit banner, table with seated leaders.
- [x] Features 4-13 all illustrated with their own scenes (Ebola virus
  + clinic + rising bars; COP31 globe + torn draft; measles cracked
  shield + US/Mexico/Bolivia tags; Nvidia bars/chip vs Dow -849 arrow;
  Gaza tents + held aid truck in rain; Mongolia parliament + ger +
  resigning figure; Serbia parliament + student crowd, "140 - 103";
  Dhaka factory + "TK 30,000 NOW" banner crowd + gas cloud; An-12
  wreck in snow with wing/stripe/propellers; Mondlane courthouse +
  scales + Mozambique ribbon).
- [x] World map: recognisable continent polygons, numbered pins 1-13
  matching story numbers and region colours, 7-region legend
  (Americas / Europe / Middle East / Asia / Africa / Oceania / Global).
  Pins: Kerch, Bahrain, Manila, DR Congo, Antalya, Mexico, New York,
  Gaza, Mongolia, Serbia, Dhaka, Kemerovo/Siberia, Maputo.
- [x] "ALSO ON TUESDAY 17 NOVEMBER": 33 numbered one-liners (14-46),
  two columns.
- [x] Stat strip, exactly the four required: "2 DAYS — strikes on the
  Crimean Bridge" · "11,000+ — Ebola cases in DR Congo" ·
  "$115.8BN — Nvidia quarterly sales, up 103%" · "-849 — Dow fall (-1.6%)".
- [x] Footer: "Every story here happened or was first reported on
  Tuesday 17 November 2026. Contested claims are marked as claims." +
  "Sources: Reuters, AP, AFP, BBC, Al Jazeera, WHO, UN. Original drawings."
- [x] Density: page filled edge to edge; PNG 376,792 bytes — inside
  the winners' 250-650 KB richness band.
- [x] Tech discipline: Python stdlib only, own rasteriser + own stroke
  font, deterministic, all code written from scratch in the builder
  session (clean room — no earlier news-image code opened or copied;
  knowledge transfer was prose only).

## Visual QA (three read-and-fix iterations performed)
1. First render (112 KB): lead headlines and captions were clipped at
   the box edges, and feature scenes (composed on a wider stage)
   spilled past their cells. Fixes: lead headline size reduced,
   captions shortened and shrunk, feature scenes resampled from their
   238-wide stage onto the cell so nothing can spill, one-liner type
   tightened, and a deterministic newsprint grain pass added
   (112 KB -> 368 KB, into the richness band).
2. Second render: fixed a float-coordinate crash in the scaled scene
   path, then re-inspected — Ebola "11,000+" label collided with its
   tallest bar, the Serbia "STUDENTS" banner overlapped the crowd,
   the Gaza "AID HELD" label sat under the rain at the truck, a stray
   "MAPUTO" label was clipped at the scene edge, and the Kerch
   explosion was too small. All five were edited.
3. Third render (final, 376,792 bytes): no text spills outside its
   box, headlines and captions are whole, map pins are legible and
   correctly placed, the An-12 reads as an aircraft, and the stat
   strip and footer are clean.

## Known limits (honest)
- The stroke font is a hand-built vector font, not a true serif; the
  masthead reads as heavy newspaper lettering rather than classical
  serif type.
- The world map is simplified: continent shapes are stylised polygons
  and the Mediterranean/Black Sea are not carved out at this scale;
  pin placements are geographically correct.
- Feature scenes are composed on a 238-wide stage and resampled onto
  their cells, so their internal labels are slightly condensed
  horizontally — still legible in the final render.
- A few scene-internal labels sit close to their neighbours (Ebola
  count, Dhaka banner); none is clipped or contradictory.

## Submission handoff (parent does this)
- Bundle with the builder session + the fresh side-chat session as
  parent, system-prompt file uploaded, instructions collected,
  --mcp none, harness muse 1.3 / provider meta / model muse-spark-1.3
  / effort default, prompt origin handed-off via the subagent task.
- If thinking_priced fails for missing Muse usage rows, attach the
  rows the check prescribes with --muse-usage and re-check.
- Submit before 2026-11-19 07:00 WIB (2026-11-19T00:00:00Z).
