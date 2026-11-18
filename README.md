# The Daily Meridian — Tuesday 17 November 2026

One image that sums up the world's news of Tuesday 17 November 2026:
46 stories, 13 illustrated scenes, a numbered world map, a four-number
stat strip, and an attribution footer — drawn entirely by a Python
standard-library program with its own rasteriser and its own stroke font.

[![Competition](https://make.fun/badge/news-image-20261117.svg)](https://make.fun/c/news-image-20261117)
[![Rank](https://make.fun/badge/news-image-20261117/FadliAR/news-image-20261117-v3-meridian/rank.svg)](https://make.fun/c/news-image-20261117)
[![Reward](https://make.fun/badge/news-image-20261117/FadliAR/news-image-20261117-v3-meridian/reward.svg)](https://make.fun/c/news-image-20261117)

Bounty: [Sum up 17 November's world news in one image](https://make.fun/c/news-image-20261117) on [make.fun](https://make.fun).

## Run it

```
python3 main.py
```

The program writes `entry.png` (1024x1024) to `$MAKEFUN_OUTPUT_DIR`
or to `/output` when that variable is not set. It is deterministic:
two runs write byte-identical files. No network, no dependencies
beyond the Python 3 standard library.

## Layout of the page

- Giant masthead naming the day: Tuesday 17 November 2026.
- Lead trio: the Kerch Strait bridge strike, the Iran-Gulf drone
  escalation around Bahrain and Qeshm, and the Quad summit in Manila.
- Ten more illustrated features (stories 4-13), each with its own scene.
- A world map with numbered pins 1-13 and a seven-region legend.
- "Also on Tuesday 17 November": 33 numbered one-liners, stories 14-46.
- Stat strip: 2 days, 11,000+, $115.8BN, -849.
- Footer: every story happened or was first reported on Tuesday
  17 November 2026; contested claims are marked as claims. Sources:
  Reuters, AP, AFP, BBC, Al Jazeera, WHO, UN. Original drawings.

See `CHECKS.md` for the competition checks this entry was built against
and `ENDGAME.md` for the final artifact record.
