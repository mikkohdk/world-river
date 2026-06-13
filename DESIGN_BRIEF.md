# World River — Design Brief

For the designer creating the **ad** and **tutorial**. This explains what the
product is, who it's for, how it should feel, the visual language already in
place, and what's coming so nothing in the creative over-promises.

Live site: **https://mikkohdk.github.io/world-river/** (open it — the product is the best reference).

---

## 1. The one-liner

**World River lets you read the world's news from each country's own domestic
sources — Australia from Australian outlets, Japan from Japanese, Brazil from
Brazilian — instead of through your local media's filter.**

## 2. The problem it solves (the "aha")

Your national news tells you about the world *through its own lens*. You hear
about Japan only when it matters to your country, framed for your country.

World River flips that: every country reports on **itself, in its own voice**,
and you read them side by side. The test we hold every source to: *a UK source
shows UK news, not the UK's take on America.* You get the world first-hand.

> Concrete example for the ad: a typical app shows you "BBC: US strikes Iran."
> World River shows you what Britain is actually talking about today — and what
> Japan, Kenya, and Argentina are talking about, each in their own words.

## 3. Who it's for

Globally curious people; expats and immigrants; journalists and analysts;
anyone tired of parochial, second-hand, rage-optimized news. Calm, literate,
internationally-minded readers.

## 4. Tone & personality

- **Calm, quiet, confident.** A "quiet reading room," not a trading floor.
- Anti-noise, anti-rage, anti-clickbait. No urgency tricks, no red badges.
- Curious, worldly, a little intellectual. Trustworthy and unhurried.
- **Explicitly NOT** a busy headline aggregator (we studied Ampparit and went
  the opposite direction on density).

## 5. Visual language already in the product (please stay consistent)

| Token | Value | Use |
|---|---|---|
| Background | `#faf9f7` | warm off-white, paper-like |
| Ink (text) | `#1d1d1f` | near-black headlines |
| Meta | `#9a958c` | muted warm grey (source, time, labels) |
| Inset | `#6f6a62` | standfirst/summary text |
| Hairline | `#eceae5` | thin dividers |
| Accent | `#3a6ea5` | one restrained blue — links, "new" dot, pins |

- **Type:** clean system sans (no fancy display faces). Headline is the hero
  (~19px), everything else recedes into quiet grey.
- **Wordmark:** "WORLD RIVER" set in **uppercase, wide letter-spacing, small,
  grey** — understated, not a loud logo.
- **Layout:** one single centered column (~720px), generous whitespace,
  hairline dividers, chronological top-to-bottom flow (the "river").
- **No flag emoji.** Deliberate choice — flags read as toylike and don't render
  on Windows. We use **country names**. Please don't reintroduce flags.
- **Metaphor:** a *river* of headlines — continuous, flowing, fed by many
  tributaries (countries). Lean into water/flow/source imagery if useful, but
  keep it subtle and elegant, never literal-clipart.

## 6. What's LIVE today (safe to show in the tutorial/ad)

- **The river:** one calm column, newest first, every country in its own voice.
- **True world mix:** round-robin ordering means no single outlet dominates —
  you see one headline per country before any repeats.
- **Insets:** a one-line standfirst under each headline for context.
- **Local time:** each item timestamped in *your* timezone; "updated HH:MM" shows freshness.
- **One menu (hamburger):** the single entry point to everything —
  - **Search** + **collapsible continents** to pick countries (multi-select).
  - **Pin** favorite countries with a ★.
  - **Mute words** to hide topics you're sick of (e.g. "world cup").
- **Read-dimming:** headlines you've clicked fade, so only new stuff stands out.
- **"New since last visit" dots** in the accent blue.
- **Always links out** to the original publisher — we aggregate, we don't reprint.
- **Private by default:** personalization is stored only in your browser. **No
  account, no signup, no cookies, no tracking.**
- **Free, instant, any device.** A website — nothing to install. Auto-refreshes
  every 30 minutes.

**Coverage:** **42 countries** across all six continents, ~47 English-language
domestic news sources — including ones rarely in Western feeds (e.g. Russia,
Iran, China, Ukraine, Nigeria, Vietnam, Fiji), each heard in its own voice.

## 7. What's COMING (roadmap — frame as "coming soon," do NOT present as live)

- **Trending across borders:** see the *same* story through many countries'
  eyes at once — the signature future feature, very on-brand.
- **Smart suggestions:** "trending globally," "popular with readers like you,"
  "big in your region." (Needs accounts — later.)
- **Personalization that learns:** the river gradually surfaces what you
  actually read more of, quiets what you skip.
- **Accounts + sync:** optional login so your countries, pins, and mutes follow
  you across devices (today they live per-browser).
- **More coverage:** continually adding countries and sources; the roster is
  designed to grow.
- **Feedback loop:** readers will be able to flag stale/broken sources and
  suggest outlets to add.

## 8. Keywords & phrases to lean on

`go to the source` · `the world in its own words` · `unfiltered` ·
`first-hand, not second-hand` · `42 countries, one calm river` ·
`hear it from there` · `no algorithm, no rage, no noise` ·
`private by design` · `every country, its own voice` · `read past your borders`

## 9. Candidate taglines (for the copywriter to refine)

- *The world, in its own words.*
- *Skip the middleman. Read the source.*
- *Hear about Japan from Japan.*
- *Your news tells you about the world. We let the world speak for itself.*
- *A calm river of news, straight from the source.*

## 10. Design guardrails (please avoid)

- ❌ Flags, busy grids, loud colors, breaking-news red, countdowns/urgency.
- ❌ "AI summarizes the news for you" framing — we link to real sources, we
  don't rewrite them.
- ❌ Promising accounts/AI/personalization as if live (see §7).
- ✅ Keep it calm, editorial, spacious, honest.

## 11. Suggested tutorial flow (~30s)

1. Open to the calm river — many countries, newest first.
2. "Every country, in its own words." (show 3–4 different-country headlines)
3. Open the menu → pick a few countries (e.g. France, Brazil, Kenya).
4. Pin a favorite ★; mute a word you're tired of.
5. Tap a headline → it opens the original local source.
6. Close on: *the world, in its own words — free, private, no account.*
