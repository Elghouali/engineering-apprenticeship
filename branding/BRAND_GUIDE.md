# Engineering Apprenticeship — Brand guide (v0.1)

> **DRAFT / PRE-RELEASE.** This is a practical working identity, not a trademark clearance, a legal name change, a finished educational release, or permission to imply that official certifications or placements are offered.

## Brand architecture

- **Public working name:** Engineering Apprenticeship
- **Short reference:** the Academy (use only after first mention)
- **Category:** GitHub-native engineering apprenticeship / hands-on engineering learning project
- **Tagline:** **Learn by fixing what breaks.**
- **Founder attribution:** Founded and built by [Elghouali](https://github.com/Elghouali).
- **Current availability:** public development preview; not yet ready for independent learners.

**One-line pitch:** A GitHub-native engineering academy where learners investigate realistic incidents, repair broken systems, and prove technical decisions through code reviews and automated tests.

**Promise:** hands-on practice with real tools and realistic, synthetic business scenarios — *not* guaranteed jobs, certification, production experience, or a finished course catalog.

## The distinction

**Not:** a conventional course portal, a library of finished tutorial answers, or a website with videos and quizzes.

**Instead:** a fictional engineering employer issuing evolving incidents; learners use GitHub Issues, forks, branches, PRs, Actions, evidence and reviews to demonstrate their reasoning.

**Four verbs:** Explain → Build → Recover → Defend.

**Primary audiences:** aspiring Data Engineers and Cloud/Platform Engineers; secondary audiences: instructors, reviewers, maintainers and open-source contributors.

## Voice and tone

- Precise, approachable, technically credible; avoid hype about revolutionary outcomes.
- Speak as builders: incident, contract, failure, root cause, recovery, evidence, trade-off.
- Explain what has run in CI and what remains a prototype.
- Say **public pre-release** until the release gate is signed off.
- Do not use **open source** as a license claim while a license is unapproved; say **public repository**.
- Do not claim learners have independently completed the curriculum before acceptance trials.

## Visual system

**Concept:** two angular paths converging at a summit. The metaphor is engineering progress through failure and review, not a conventional graduation cap or generic code icon.

| Token | Hex | Role |
| --- | --- | --- |
| Midnight | `#081220` | Main dark background |
| Blue | `#2688FF` | Primary action and path |
| Cyan | `#22C3EE` | Technical emphasis |
| Ice | `#EAF4FF` | High-contrast title |
| Mist | `#BCCBE1` | Supporting text |
| Green | `#10B981` | Verified success (not decorative status) |
| Amber | `#F59E0B` | Warnings/pre-release |
| Purple | `#885CF6` | Occasional highlight |

Typography: **Inter** where available; fallback **Segoe UI**, **Arial**, generic sans-serif. Code samples remain monospace. Do not bundle or redistribute fonts.

### Assets

- [Square mark](assets/ea-mark.svg) — avatar, favicon concept, compact branding
- [README banner](assets/ea-banner.svg) — wide brand header

These SVG files are editable source graphics. An illustrated concept board may be shared separately, but the committed SVG files are the canonical version in the repository.

### Usage

- Keep clear space around the symbol equal to at least half the inner path width.
- Do not distort or recolor the blue gradient without reviewing contrast.
- Use the symbol on Midnight for the dark variant; test any light variant for readability.
- Never use a platform's logo in a way that implies endorsement.
- When using the banner, show **public pre-release** prominently in nearby copy.

## Founder-led communications

LinkedIn headline suggestion:

> Founder of Engineering Apprenticeship | Building a GitHub-Native Engineering Academy | Big Data & Cloud Engineering

Profile description:

> Engineering student building Engineering Apprenticeship, a public pre-release GitHub-native learning project for realistic Data and Cloud engineering incidents, CI, PR reviews and end-to-end systems.

**Founder launch decision (2026-11-23):** **Hold founder-led promotional posts and the LinkedIn announcement until v1.0 has completed its release gates.** Do not schedule or publish a pre-release announcement. The public GitHub development repository remains visible, but we are not actively advertising its launch.

At v1.0, the founder's announcement should explain the unique workflow, show independently validated engineering evidence, link to the actual release and invite feedback. See [the held announcement draft](FOUNDER_ANNOUNCEMENT.md).

## Brand/governance gates before launch

- [ ] Founder approves final public name and brand direction.
- [ ] Check trademarks, relevant domains and handles in intended markets; web-search nonmatches are not clearance.
- [ ] Decide and approve repository/content licenses.
- [ ] Confirm visuals and marketing claims match the learner-validated experience.
- [ ] Add a social-preview PNG through GitHub repository settings if desired (GitHub may not render an SVG preview there).
- [ ] Launch only after [public release checklist](../docs/PUBLIC_LAUNCH.md) passes.
- [ ] Confirm founder approval for the final v1.0 LinkedIn announcement before publishing.

**Current name decision:** retain the existing repository/product working name; avoid prematurely renaming repositories, links and docs during pre-release.
