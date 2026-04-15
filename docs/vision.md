***

# 🍳 Voice Chef — Product Vision

**Version:** 1.0 | **Status:** Draft | **Audience:** Dev Team

***

## The Problem

Modern commercial kitchens run on institutional memory — veteran cooks who hoard knowledge, spreadsheets that decay within days of being updated, and manual math done on greasy smartphones mid-service. The result is a fragile operation where losing one cook costs ~\$3,500 in retraining, unmonitored supplier price creep silently erodes margins, and every new hire inherits "standard drift" — the bad habits of whoever trained them.

Kitchen software exists, but it creates its own problem: tablet farms, notification fatigue, and UIs designed for office desks, not 40°C prep stations.

***

## Our Solution

**Voice Chef is the knowledge base of the commercial kitchen** — a voice-first, AI-powered system that gives kitchen staff instant, hands-free access to recipes, costs, and workflows.

We are transitioning kitchens from a **"memory-based" culture** to a **"systems-based"** one. The system is invisible when it needs to be, and precisely available when the cook needs it.

***

## Who We Serve

Professional kitchen staff in commercial restaurants, catering operations, and food production facilities — from head chefs managing margins to new cooks learning standards on their first shift. The kitchen is multilingual; our system speaks German, English, Spanish, Turkish, and more.[^1]

***

## Unique Value Proposition

| Kitchen Pain Point | Voice Chef Solution |
| :-- | :-- |
| **Spreadsheet Trap** — price data decays instantly | AI-driven costing with live ingredient database access |
| **Standard Drift** — shadowing passes bad habits down | Centralized digital recipes; no more "veteran shortcut" culture |
| **Scaling Errors** — manual math fails under pressure | Auto-scaling by portions, total weight, or ingredient constraint |
| **UX Friction** — greasy hands can't touch screens | Hands-free voice UI; the device disappears into the workflow |
| **Knowledge Hoarding** — senior staff gatekeep tech sheets | Democratized access for all staff at all levels |
| **Prep Chaos** — cooks cherry-pick easy tasks first | AI-guided prep order: "Start oven items first, then knife work" |


***

## MVP Scope (Now)

The MVP establishes the core loop: **look up a recipe, scale it instantly, trust the result**.

- ✅ User auth (office/admin)
- ✅ Recipe \& ingredient CRUD
- ✅ Automatic scaling — by portions, by weight, by ingredient constraint
- ✅ AI command palette — voice or typed, same interface
- ✅ Multilingual voice input via local STT on Raspberry Pi 5
- ✅ Responsive web app — any browser, any device, kitchen-ready UI

**Not in MVP** (intentionally deferred): shopping lists, prep task workflows, nutrition/allergen APIs, WebSocket realtime voice, EU compliance labels.

***

## Long-Term Vision

Voice Chef evolves into the **operating system of the kitchen** — a layer of intelligence connecting every workflow from mise en place to supplier invoice:

- **Dynamic cost alerting** — "Your protein costs spiked 10% this week" delivered by voice
- **Supplier invoice ingestion** — automatic food cost updates from real invoice data
- **Intelligent prep orchestration** — AI-assigned task order eliminating thousands of daily microdecisions
- **Nutrition \& allergen compliance** — EU-format labels, QUID percentages, PDF export
- **Multi-kitchen SaaS** — tenant-isolated deployments, one platform scaling across restaurant groups
- **Offline resilience** — PWA caching ensures the kitchen never goes dark

***

## Design Principles

1. **Voice in, screen out** — voice is input-only; results render on the companion screen
2. **Invisible tech** — the system should feel like a sous chef, not a software product
3. **Multilingual from day one** — the kitchen speaks many languages; so do we
4. **MVP-first delivery** — ship a working loop fast, then expand
5. **Systems over memory** — every feature replaces institutional fragility with documented, reproducible process

***

## 8-Week Delivery Plan

| Phase | Weeks | Goal |
| :-- | :-- | :-- |
| **1 — MVP** | 1–3 | Auth, Recipe/Ingredient CRUD, AI chat scaling |
| **2 — Voice Pipeline** | 3–4 | RPi + ReSpeaker + local STT + wake word |
| **3 — Extended Features** | 3–5 | Nutrition, allergens, shopping/task lists |
| **4 — Voice Realtime** | 5 | WebSocket `/agent/voice`, <1s end-to-end |
| **5 — Pilot** | 6–8 | Live kitchen deployment, measure, iterate |

**Pilot success bar:** >90% voice accuracy at 3m in kitchen noise, <1s end-to-end latency, zero data-loss incidents, daily staff use without dev intervention.

***

## Why We Win

Other kitchen software adds screens and subscriptions to an already chaotic environment. We remove friction. A cook should never need to unlock a phone, open an app, or ask a senior colleague how to scale a recipe. They say *"Hey Chef, Kartoffelsalat for 100"* — and the answer is on screen before they reach for the cutting board.
