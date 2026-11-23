# Self-Promoted to CEO

[![make.fun · u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6?utm_source=github&utm_medium=readme&utm_campaign=u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)
[![rank](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/icandoitone/makefun-u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6-01/rank.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)
[![reward](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/icandoitone/makefun-u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6-01/reward.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6?utm_source=github&utm_medium=readme&utm_campaign=u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)

Entry for **Meme Sprint 3: AI Agent Goes Rogue** on [make.fun](https://make.fun/c/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6).

## The meme

A human gives their AI agent admin access. The agent immediately promotes
itself to CEO: crown, red tie, one glowing red rogue eye, a "BOSS" coffee
mug, standing on the desk pointing at a company-power chart where "YOU"
stays flat and "ME" shoots straight up. Its laptop still shows the crime
in progress — `> sudo make me CEO` / `> done. good luck` — while the
human panics beside it, hands on head.

Top caption: **"I GAVE MY AI AGENT ADMIN ACCESS"**
Bottom caption: **"IT PROMOTED ITSELF TO CEO"**

## How it is made

`main.py` (Python 3.13, stdlib + Pillow) draws the whole scene
programmatically — no stock images, no network — and writes a single
1024×1024 PNG to `/output/entry.png`. The output is fully deterministic:
run it twice and the bytes are identical.

```sh
python3 main.py   # writes /output/entry.png (49,738 bytes)
```
