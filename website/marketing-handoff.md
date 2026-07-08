# Website IA Handoff — for Marketing

**Prepared:** 2026-07-07 · **For:** morning handoff · **Scope:** akka.io navigation + URL structure (mega-menu)

A running list of site changes to implement. New canonical URL structure below; current URLs are from the live header module.

---

## 1. URL structure changes

| # | Item | Current URL | New URL | Notes |
|---|------|-------------|---------|-------|
| 1 | **Platform** page | `akka.io/platform-intro` | `akka.io/offerings/platform` | Establishes the `/offerings/` parent. |
| 2 | **Akka Specify** page | `doc.akka.io/sdk/spec-driven-development.html` | `akka.io/offerings/specify` | New marketing page; will host the **new Akka Specify presentation**. Moves Specify from docs onto the marketing site alongside Platform. |
| 3 | **Customer stories** | `akka.io/customer-stories` (index + scattered) | `akka.io/customers/<customer-name>` | One page per customer under `/customers/`. (17 stories.) |
| 4 | **Battlecards** | not yet on site | `akka.io/compare/<competitor-name>` | One page per competitor under `/compare/`. (14 cards.) |

## 2. Remove from the site / menu

| Item | Current URL | Action |
|------|-------------|--------|
| **Discord** | `discord.com/invite/QZc652rgtf` | Remove |
| **Benchmarks** | `akka.io/akka-performance-benchmark` | Remove |
| **Demos** | `akka.io/blog?tag=demo` | Remove — content getting dated |

## 3. Move to `doc.akka.io` (relocate off the marketing site)

These product pages move under the docs subdomain:

| Item | Current URL |
|------|-------------|
| Akka Agents | `akka.io/akka-agents` |
| Akka Orchestration | `akka.io/akka-orchestration` |
| Akka Memory | `akka.io/akka-memory` |
| Akka Streaming | `akka.io/akka-streaming` |
| Akka Automated Operations | `akka.io/automated-operations` |
| How Akka works | `akka.io/how-akka-works` |

---

## Notes / recommendations (not yet instructed — flag for sign-off)

- **301 redirects:** every moved page (rows 1–3 and section 3) should 301 from its old URL to the new one, to preserve existing link equity and avoid broken inbound links.
- **Canonical, not duplicate:** for pages relocating to `doc.akka.io`, keep a single canonical copy — don't leave the old `akka.io/*` page live alongside it.
- **Mega-menu impact:** these changes reshape the header menu — the PLATFORM column slims to Platform / Specify / How-it-works-level items, the product pages leave for docs, and `/customers/` + `/compare/` become the homes for the customer-story and battlecard content we plan to surface in the menu.
