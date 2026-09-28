# Gap statement review — actively stabilised model rocket (student group project)

*Date: 2026-09-17 · Audience assumed: student-conference reviewers (the expo audience is less demanding; the verdict uses the stricter standard) ·
Reviewer: Claude (Opus 5, via Claude Code) · Search bound: three altitudes (surveys, system papers, recent preprints) plus one citation hop per sub-claim, same-tier sweep of capstones/GitHub/hobbyist builds; "recent" cut-off 2025-03*

**Statement under review (verbatim):**

> Active stabilisation of vertical thrust is a stretch problem for student teams; commercial model rockets use passive fins and aren't designed for control experimentation.

## Verdict

**Defensible after narrowing** — confidence medium.

As written, the first half fails: thrust-vector-controlled model rockets have been flown repeatedly by hobbyists since 2019 [S7][S12], by an open-source project anyone can fork [S8], by a single high-school student with a documented 7° maximum deviation [S13], and a University of Leeds student team flew canard-based stabilisation of the vertical flight path in April 2024 and published it [S16]. A reviewer who knows the field will name BPS.space in the first sentence. What *does* hold, and holds with documented evidence, is narrower: university teams attempting solid-motor TVC typically reach static fire but not flight within a project year [S2][S9][S11][S15], the one commercial TVC kit that packaged the hard part (the flight software) was withdrawn in 2019 and the software is still not public [S7][S18], and the largest student competition's own rules state that active flight-control components are "generally unavailable as COTS to the amateur high-power rocketry community" [S17]. The second half of the statement is therefore defensible once "commercial" is qualified as *currently available* and *mainstream*, and the first half is defensible once "stretch" is replaced by the specific, falsifiable pattern the evidence shows.

| Test | Result | Why (one line, with [S#]) |
|---|---|---|
| 1 Falsifiable | partial | "Stretch problem" cannot be refuted by any paper; "commercial rockets aren't designed for control experimentation" can be (and Signal R2 nearly does [S7][S18]) |
| 2 Evidenced absence | partial | Strong documented evidence for the COTS/platform absence [S17 §7.5.2][S7]; the "stretch" claim rests on team reports that stalled at static fire [S2][S9][S11][S15], not on any survey |
| 3 Honestly scoped | fail | "Student teams" is unbounded: a high-school student [S13] and a university team [S16] have flown active stabilisation; the claim survives only for solid-motor TVC flown by a university team within a project year |
| 4 Significant | pass | A flown, documented, controller-exposed platform is exactly what the academic groups building electric TVC testbeds say the field lacks [S6][S5], and what the 2025 arXiv gimbal paper frames as its goal [S1] |
| 5 Not empty for a good reason | pass | The reasons are structural, not "impossible": the software is the hard part and is withheld [S7]; IREC forbids control actuation during boost, which channels student effort into post-boost canards and airbrakes rather than TVC [S17 §7.4.1]; first flights usually fail [S12][S14] |
| 6 Current | partial | Since 2025-03: a bench-tested "reproducible platform for STEM education" gimbal [S1] and a quadrotor-based TVC testbed [S5] — both aim at the same niche but neither is a flown, commercial model rocket, so the narrowed statement still stands |

## Glossary

| Term | Meaning here |
|---|---|
| Sub-claim | One atomic piece of the statement, "X has not been done under condition Y", that a single paper could refute |
| Documented absence | Evidence that something is missing: a survey table with the cell empty, a rule that says a component is unavailable, or a paper's own future-work sentence naming it |
| Not-found-by-search | Weaker: our logged queries surfaced nothing. Only as strong as the queries |
| Citation chaining | Walking a paper's reference list backwards and its "cited by" list forwards |
| Thrust vector control (TVC) | Steering a rocket by tilting the motor (gimbal) or deflecting its exhaust (jet vanes); only works while the motor burns |
| Canard / active fin control | Steering with movable aerodynamic surfaces; works whenever airspeed is high enough, including after burnout |
| Weather-cocking | The tendency of a finned rocket to turn into the wind, i.e. away from vertical — the disturbance active stabilisation must reject |
| Static fire / hold-down test | Firing the motor with the rocket clamped to a stand; tests the actuator and controller without flying |
| COTS | Commercial off-the-shelf: a component you can buy rather than build |

## Inputs and assumptions

| Slot | Value | Supplied or assumed |
|---|---|---|
| Field / sub-field | Amateur (model and high-power) rocketry; active flight control; thrust vector control | assumed from the statement |
| Vocabulary used for searching | "thrust vector control" / TVC, "gimbal", "jet vane", "active stabilisation", "attitude control", "canard", "active fin", "roll control", "model rocket", "amateur rocket", "high-power rocket", "sounding rocket", "student team", "capstone". The statement's own phrase "active stabilisation of vertical thrust" is non-standard: the method is *thrust vector control*, the goal is *vertical attitude hold* / rejecting *weather-cocking*. Searching with the statement's wording finds almost nothing; searching with the field's terms finds dozens of projects | assumed; stated here as a finding |
| Audience | Student-conference reviewers (stricter than the expo) | supplied (expo primary, student conference secondary) |
| Scope boundaries | Student group project; budget not a constraint; about 3 months to an expo, may continue after; "student teams" read as university teams unless the statement says otherwise; model-rocket scale (commercial solid motors, sub-high-power) | supplied (time, budget) / assumed (tier) |
| Seed papers / library | None supplied; seeds taken from the top-down pass: [S1][S2][S6][S7][S9][S16] | assumed |
| Already searched by the user | Nothing | supplied |
| "Recent" cut-off | 2025-03 (18 months) | assumed |

## Sub-claims

| ID | Sub-claim | Gap type | Top-down evidence | Bottom-up evidence | Status | Strongest counter-paper | Evidence strength |
|---|---|---|---|---|---|---|---|
| SC1 | Active stabilisation of a model rocket's attitude to keep the thrust vertical (by TVC or aerodynamic surfaces) has not been achieved by student teams — it is beyond their typical reach ("a stretch problem") | practical-knowledge / population | Academic groups do it in simulation [S3][S4] or on electric indoor testbeds [S5][S6]; a Leeds student team flew canard-based correction of deviation from vertical in April 2024 [S16]; university solid-motor TVC teams report static fires but no flight [S2][S9][S10][S11][S15] | Hobbyist model-rocket TVC flown routinely since 2019, with "over 40 successful flights" by one builder [S7][S12]; MIT-licensed flight code with a flight video, 63 stars, 14 forks [S8]; a high-school student flew TVC with 7° max deviation [S13]; a 2007 Cambridge undergraduate project flew and crashed on its maiden flight [S14] | partially closed | [S16] (student team, flown, vertical-attitude hold); [S13] (student, TVC, flown) | closed by [S16] and [S13] as written; documented absence only for the narrowed form "solid-motor TVC flown by a university team within a project year" [S2][S9][S11][S15] |
| SC2 | Commercially available model rockets rely on passive fin stabilisation; no actively stabilised model rocket is sold | evidence (market) | No survey covers the amateur market. The IREC 2025 design guide exempts flight-control systems from its COTS-redundancy rule "given that such components are generally unavailable as COTS to the amateur high-power rocketry community" [S17 §7.5.2] | BPS.space sold the Signal R2 TVC kit until 20 Nov 2019 [S18]; today it sells only the gimbal 3D files (US$35) and states the flight software "is not publicly available yet" [S7]; a search for currently sold active kits surfaced none (search log #26) | partially closed | [S7]/[S18] — a commercial TVC kit existed and was withdrawn | documented absence for "currently available" [S17 §7.5.2][S7]; the historical claim is closed by [S18] |
| SC3 | No commercial model-rocket platform is designed for control experimentation (controller exposed, instrumented, reusable by a student team) | methodological / platform | EPFL built an electric small-scale TVC rocket explicitly as "an inexpensive platform to explore guidance algorithms" [S6]; a 2026 quadrotor-based TVC testbed serves the same purpose indoors [S5]; a 2025 arXiv gimbal is framed as "a reproducible platform for STEM education and experimental aerospace research" but is bench-tested only [S1] | Open-source flight code exists and has flown [S8]; a 2022 UTA senior design built a TVC rocket "as an educational tool for avionics, embedded systems, and real time processing" [S15]; BPS.space's product withholds the software [S7] | partially closed | [S6] (academic, electric, flown, not a commercial model rocket); [S8] (open-source, hobbyist, flown) | not-found-by-search for a *commercial* model-rocket experimentation platform; documented absence via [S7] (software withheld) and [S1]'s own framing ("costly and technically inaccessible to students and hobbyists") |

## Top-down search

### SC1 — active stabilisation by student teams

**Surveys.** No survey or review of active control in amateur rocketry was found (search log #1, #35). The nearest thing to a field-level statement is the 2007 Cambridge project report, whose introduction says "the complexity and expense of the latter, coupled with the small size of hobby rockets, means that amateur actively-stabilised rockets have rarely been built in the past" [S14 §1 p.1] — true in 2007, and the strongest documented version of the statement's premise. Everything below shows how far it has eroded since.

**System papers.** The academic TVC literature at small scale is dominated by one Lisbon group, working in simulation on a solid-motor launcher with LQR/LQI and gain scheduling [S3][S4], and by two flown *electric* testbeds: EPFL's small-scale electric TVC rocket flown indoors and outdoors with MPC on embedded hardware [S6], and the 2026 QuadRocket, a rocket body on a quadrotor through a universal joint, validated in a motion-capture arena [S5]. Neither is a model rocket with a solid motor, but both exist precisely because the field wants a low-risk platform to test TVC controllers on.

At the university-team tier with solid motors, the pattern is consistent: Georgia Tech's Ramblin' Rocket Club published two 2025 AIAA student-conference papers on a jet-vane TVC rocket after "three static fires" with "a final static fire scheduled for future test" — no flight in the abstract [S9][S10]; College of Engineering Trivandrum simulated pitch-plane TVC in Simulink and ran hold-down tests [S2]; SFU Rocketry's TVC project is a ground test platform with completion expected early 2026 [S11]; UTA's 2022 senior design reached gimbal static testing with real motors [S15]. The one university flight found with TVC-class hardware is the 2007 Cambridge cold-gas project, which "rapidly veered away from the vertical and crashed" on its maiden flight after bench tests had already shown instability attributed to neglected cross-axis coupling [S14 §7.6 p.32, §8.1 p.35].

The strongest counter-example at this tier uses aerodynamic surfaces instead of TVC: the University of Leeds team's canard-based attitude stabilisation system, tuned with an LQR, whose abstract reports "a successful launch in April 2024 shows the effectiveness of the integrated attitude control system" against "attitude deviation from the vertical flight induced by wind" [S16]. That is a student team, actively stabilising the vertical flight path, flown, and published in an IFAC venue. If "active stabilisation of vertical thrust" means keeping the rocket vertical (rather than specifically vectoring the motor), SC1 as written is closed by this paper.

**Recent preprints (since 2025-03).** The arXiv API query returned three papers in total for TVC on model/small-scale/student rockets, only one since the cut-off: Singh's 2025 3D-printed servo gimbal, bench-tested to ±5° at 44.5 ms response, framed as showing "the feasibility of student-accessible thrust vector control systems" [S1]. QuadRocket [S5] is the only other 2025–26 item. Nothing since the cut-off reports a university team flying solid-motor TVC.

### SC2 — commercial model rockets are passively finned

No survey addresses the amateur market. The strongest top-down evidence is regulatory rather than academic: the IREC 2025 Design, Test & Evaluation Guide exempts flight-control electronics from its COTS-redundancy requirement "given that such components are generally unavailable as COTS to the amateur high-power rocketry community" [S17 §7.5.2]. The same document confines active control to "pitch and/or roll stability augmentation, or for aerodynamic braking" [§7.1.1], requires the vehicle to be "naturally stable without those controls" [§7.2.1], and requires control actuators to "remain in a neutral state" until boost has ended or max-Q or an altitude gate is passed [§7.4.1] — which excludes TVC from the largest student competition by construction, since TVC only acts during boost.

### SC3 — no platform designed for control experimentation

Top-down, the "platform" niche is being filled from the academic side with electric vehicles: EPFL's stated aim was "to provide an inexpensive platform to explore guidance algorithms and automatic landing for sounding rockets" [S6]; QuadRocket is "a low-cost, low-risk platform for validating advanced thrust-vector control strategies" [S5]. Both are counter-examples to the *spirit* of SC3 (a platform for control experimentation exists) but not its letter (neither is a commercial model rocket, and neither uses a solid motor). Singh's 2025 paper opens by stating the gap itself — "conventional implementations remain costly and technically inaccessible to students and hobbyists" — and offers a bench-tested gimbal as a "reproducible platform" [S1]; it has not flown.

## Bottom-up search

**Seeds:** [S1], [S2], [S6], [S7], [S9], [S16]

**Chaining.** Forward from Praveen et al. 2023 [S2]: 2 citing works on OpenAlex (not opened). Forward from the Lisbon simulation papers [S3][S4] leads to QuadRocket [S5], same authors — the group moved from simulation to an electric testbed. Backward from Wyatt 2007 [S14] confirms the premise was documented in 2007 (its refs [1], [2]; not chased). The arXiv API pass (search log #34) is a forward check that nothing newer than [S1] has appeared with these terms.

**Same-tier builds (hobbyist, high-school, capstone).**

- BPS.space: gimbal 3D files sold for US$35, designed for Estes F15/E9, Apogee F10/E6, AeroTech G8/G11 motors ("average thrust of 5–20 Newtons, and a flat thrust curve"), "developed over 3 years of iterative design with over 40 successful flights" — and: "nearly all of the complexity involved is in the flight software, which is not publicly available yet", "your first few tests will probably fail" [S7]. The Signal R2 kit that bundled the software was sold until 20 Nov 2019 [S18]. Joe Barnard's own account: "My first ten launches were failures. But the eleventh succeeded," after "four years of hard work, crashes, and iterative designs" [S12].
- tomkuttler/TVC-Rocket-Flight-Code: MIT-licensed, Teensy 4.1, two servos, state machine plus two PID loops, flight video in the README, 63 stars / 14 forks, presented as reusable after editing `Rocket.h` and `StateMachine.h` [S8].
- Timothy Cai, Canadian Science Fair Journal 2023: Arduino-based flight computer and TVC hardware; "Initial test flights and recent ground test data have indicated stable control with a maximum of 7° and 2.62° of deviation from the intended flight path respectively" [S13]. One high-school student.
- UTA senior design 2022: TVC gimbal rocket built "as an educational tool for avionics, embedded systems, and real time processing", eight sprints, static tests with real motors, flight not confirmed [S15].
- Santa Clara 2018 senior thesis: active control for a straight path to apogee, 6-DOF model-based design; method and flight outcome not stated in the abstract [S21].
- Other same-tier pages seen in results but not opened: Princeton Rocketry "Active Controls" TVC project [S30], Space Enterprise at Berkeley TVC page [S31], Georgia Tech GNC page claiming "first collegiate team to test jet vanes" in April 2024 [S32], NAU 2026 EE capstone on inducing and cancelling roll [S22], UW–River Falls team meeting a 2026 NASA WSGC requirement to roll 90° and back in flight [S26], Leeds Rocketry's canard-development report [S27], a university team's forum thread asking "movable fins or TVC?" [S20]. These show that *aerodynamic* active control (roll, canards, airbrakes) is now a routine student-competition task, while TVC remains the exception.

**Nearest neighbours' own statements of the gap:**

> "nearly all of the complexity involved is in the flight software, which is not publicly available yet" — [S7], product description

> "conventional implementations remain costly and technically inaccessible to students and hobbyists" — [S1], abstract

> "such components are generally unavailable as COTS to the amateur high-power rocketry community" — [S17], §7.5.2

> "the complexity and expense of the latter, coupled with the small size of hobby rockets, means that amateur actively-stabilised rockets have rarely been built in the past" — [S14], §1 p.1 (2007)

> "a final static fire scheduled for future test" — [S9], abstract (no flight yet, 2025)

**Map of what exists.** Four tiers, and the gap looks different in each:

| Tier | Solid-motor TVC flown? | Platform for experiments? |
|---|---|---|
| Academic research groups | No — simulation [S3][S4] or electric testbeds [S5][S6] | Yes, but electric and lab-bound [S5][S6] |
| University student teams | Not found; static fires only [S2][S9][S11][S15]; 2007 crash [S14]; canard stabilisation flown [S16] | Individual builds, not reusable platforms [S15] |
| Hobbyists and individual students | Yes, repeatedly [S7][S8][S12][S13] | Open-source code [S8]; commercial files with software withheld [S7] |
| Commercial kits | Signal R2, 2018–2019, withdrawn [S18] | Nothing currently sold with the controller exposed [S7][S17 §7.5.2] |

The empty region is the intersection: a *flown*, *solid-motor*, *documented*, *controller-exposed* model-rocket platform that a *university team* produced. The statement gestures at that region but claims two much larger ones.

## Reconciliation

- **Top-down says "the field does this"; bottom-up says "students do this too, but individually".** Both are right. The academic literature has flown TVC on electric testbeds [S5][S6] and the hobbyist tier has flown solid-motor TVC many times [S7][S8][S12][S13]. The only tier where the "stretch" reading survives is university teams with solid motors, and even there the evidence is *team reports that stopped at static fire* [S2][S9][S11][S15], not a survey. Resolution: narrow "student teams" to that tier and replace "stretch" with the observable pattern.
- **Top-down (regulatory) says COTS active control is unavailable [S17]; bottom-up says a commercial kit existed [S18].** Both are right at different dates. Resolution: qualify "commercial" as *currently available*, and cite the Signal R2 withdrawal as the reason the claim is true today rather than pretending it was always true.
- **The statement's vocabulary hides the counter-examples.** "Active stabilisation of vertical thrust" reads as TVC-only. If the project's goal is *keeping the rocket vertical*, the Leeds canard flight [S16] is a direct precedent and a fallback design; if the goal is specifically *thrust vectoring*, say so, and the Leeds paper becomes adjacent work rather than a counter-example. The rewrite below assumes TVC is the point.

## Rewritten statement

> Thrust-vector-controlled model rockets have been flown repeatedly by hobbyists and by individual students, and at least one university team has flown canard-based stabilisation of the vertical flight path; but university teams attempting solid-motor TVC typically reach static fire, not flight, within a project year. The flight software is the hard part, and the only commercial kit that packaged it (BPS.space Signal R2) was withdrawn in 2019, so mainstream commercial model rockets remain passively finned and there is no currently available, documented platform on which a student team can run attitude-control experiments with the controller exposed. This project builds and flies such a platform in one term.

**What changed and why:** "stretch problem for student teams" became the specific, falsifiable pattern the evidence shows (university teams stall at static fire), with the hobbyist and individual-student flights acknowledged rather than hidden; "commercial model rockets ... aren't designed for control experimentation" gained "currently available" and "documented, controller exposed", because a commercial TVC kit did exist and open-source code does exist — the absence is of a *supported, documented* platform, not of any platform at all.

## Implications for the project

Not part of the audit, but the evidence bears directly on a three-month plan:

- **The reason teams stall is known, and it is not the gimbal.** Every static-fire-only team built a working gimbal [S1][S2][S9][S15]; the flights fail on control and estimation [S14 §8.1][S12]. Start from flown open-source code [S8] rather than a blank controller, and treat the test stand as a two-week milestone, not the deliverable.
- **Motor choice decides whether control is even possible.** The commercial guidance is long-burn, flat-thrust motors at 5–20 N (Estes F15/E9, Apogee F10/E6, AeroTech G8/G11) [S7]; a short-burn motor leaves no time for the loop to act.
- **Expect the first flights to fail.** Ten failures before the first success for the most experienced builder in the tier [S12]; "your first few tests will probably fail" is on the product page [S7]. Schedule flight days early and often, and plan the expo demonstration around a test stand and flight data, not a single live flight.
- **Fallback with a precedent.** If TVC will not converge in time, canard-based vertical stabilisation has been flown and published by a student team on a comparable timescale [S16], and it also works after burnout.
- **Rules matter only if you compete.** IREC forbids control actuation during boost [S17 §7.4.1], so a TVC rocket cannot fly there; the expo and a student conference have no such constraint, but the paper should say why TVC rather than canards was chosen given that rule.

## What would flip it

- **The finding that would overturn this verdict:** a currently sold, documented model-rocket TVC kit whose control loop is exposed for modification — for example, if BPS.space's current AVA flight computer ships TVC support with editable control code, or if any vendor now sells what Signal R2 was. That would close SC2 and SC3 as narrowed. For SC1, a published university-team paper flying solid-motor TVC within one project term with released code would close the narrowed form.
- **Where it would most likely be found:** the BPS.space store and its AVA documentation (not opened — the product page fetched was the TVC files page only), GitHub searches for "AVA TVC", YouTube (where most hobbyist TVC flights are documented and which was not searched), and the Rocketry Forum threads that returned HTTP 403 [S19][S20].

## Search log

| # | Date | Tool / database | Query (verbatim) | Hits | Surfaced |
|---|---|---|---|---|---|
| 1 | 2026-09-17 | WebSearch | `thrust vector control model rocket student project review survey` | 9 links (no count) | [S1] [S2] [S4] [S5] [S34] [S35] |
| 2 | 2026-09-17 | WebFetch | `https://arxiv.org/abs/2509.00061` | page | [S1] read |
| 3 | 2026-09-17 | WebFetch | `https://ieeexplore.ieee.org/document/10425646/` | blocked (empty page) | — |
| 4 | 2026-09-17 | WebSearch | `"Thrust Vector Control of Solid Propellant Model Rocket" IEEE 2023` | 10 links | [S3] [S6]; IEEE 11360267 seen, not opened |
| 5 | 2026-09-17 | Semantic Scholar API | `paper/search?query=Thrust+Vector+Control+of+Solid+Propellant+Model+Rocket` | HTTP 429 | — |
| 6 | 2026-09-17 | OpenAlex API | `works?search=Thrust Vector Control of Solid Propellant Model Rocket` | 5 (1 relevant) | [S2] |
| 7 | 2026-09-17 | WebFetch | `https://arxiv.org/abs/2303.16983` | page | [S3] read |
| 8 | 2026-09-17 | WebFetch → OpenAlex | Springer article redirected to login; `works/https://doi.org/10.1007/s42496-023-00161-w` | 1 | [S4] |
| 9 | 2026-09-17 | WebFetch | `https://arxiv.org/abs/2607.02474` | page | [S5] read |
| 10 | 2026-09-17 | OpenAlex API | `works?search=Optimal Thrust Vector Control of an Electric Small-Scale Rocket Prototype` | 3 (1 relevant) | [S6] |
| 11 | 2026-09-17 | WebSearch | `BPS.space Signal thrust vector control kit model rocket discontinued AVA flight computer` | 9 links | [S7] [S18] [S19] |
| 12 | 2026-09-17 | WebFetch | `https://bps.space/products/thrust-vector-control` | page | [S7] read |
| 13 | 2026-09-17 | WebFetch | Rocketry Forum thread 182550 | HTTP 403 | [S19] not accessible |
| 14 | 2026-09-17 | WebSearch | `thrust vector control model rocket kit for sale 2025 flight computer hobbyist TVC mount` | 9 links | [S8] [S12] [S23] |
| 15 | 2026-09-17 | WebFetch | `https://github.com/tomkuttler/TVC-Rocket-Flight-Code` | README | [S8] read |
| 16 | 2026-09-17 | WebSearch | `university student team thrust vector controlled model rocket successful flight test capstone 2024 2025` | 9 links | [S9] [S10] [S20] [S30] [S31] |
| 17 | 2026-09-17 | WebFetch → OpenAlex | `arc.aiaa.org/doi/10.2514/6.2025-99339` gave HTTP 403; `works?filter=doi:10.2514/6.2025-99339|10.2514/6.2025-98332` | 2 | [S9] [S10] |
| 18 | 2026-09-17 | WebSearch | `student rocketry team thrust vector control rocket flew successfully video first flight 2024 OR 2025 OR 2026 TVC` | 9 links | [S11] [S26] [S32] [S33] |
| 19 | 2026-09-17 | WebFetch | `https://www.sfurocketry.com/completed-projects/tvc` | page | [S11] read |
| 20 | 2026-09-17 | WebFetch | `https://www.instructables.com/TVC-Model-Rocket/` | title only (JS page) | [S23] not accessible |
| 21 | 2026-09-17 | WebFetch | Make: article on thrust-vectored rockets | page | [S12] read |
| 22 | 2026-09-17 | WebSearch | `Tripoli NAR safety code active stabilization thrust vectoring allowed "guided" model rocket rule` | 9 links | [S22] [S28] |
| 23 | 2026-09-17 | WebFetch | `https://ceias.nau.edu/capstone/projects/EE/2026/RocketControl/` | TLS certificate error | [S22] not accessible |
| 24 | 2026-09-17 | WebSearch | `NAU capstone 2026 "Active Rocket Control System" ceias` | 9 links | [S13]; ASU thesis link (host does not resolve) |
| 25 | 2026-09-17 | WebFetch | `https://arxiv.org/abs/2304.13704` | page | [S13] read |
| 26 | 2026-09-17 | WebSearch | `buy actively stabilized model rocket kit gyro stabilized "model rocket" product 2025 2026 reaction wheel OR canard OR TVC kit educational` | 9 links; no currently sold active kit among them | [S14] [S15]; Hackaday.io project seen, not opened |
| 27 | 2026-09-17 | WebFetch + pypdf | `https://aeroconsystems.com/tips/Active_Stabilized_rocket_Wyatt.pdf` (52 pp, text extracted locally) | 1 | [S14] read: §1, §7.6, §8 |
| 28 | 2026-09-17 | WebFetch | `https://websites.uta.edu/cseseniordesign/2022/11/08/tvc-gimbal-rocket` | page | [S15] read |
| 29 | 2026-09-17 | WebFetch | `https://keep-24.lib.asu.edu/node/201409` | DNS failure | ASU roll-control thesis could not be located |
| 30 | 2026-09-17 | WebSearch | `"Servo-driven Fin-based Active Roll Control System for Model Rockets" ASU thesis` | 9 links | JKUAT active-fin paper, PSAS roll control, AIAA 2024-85779 seen, not opened |
| 31 | 2026-09-17 | WebSearch (multi-round) | `Spaceport America Cup IREC rules thrust vector control prohibited active control allowed roll airbrakes "thrust vectoring"` | ~45 links | [S17] |
| 32 | 2026-09-17 | WebFetch + pypdf | IREC 2025 Rules & Requirements v1.6 PDF | text had no active-control clauses (they live in the DTEG) | — |
| 33 | 2026-09-17 | curl + pypdf | IREC 2025 Design, Test & Evaluation Guide v1.1.6 PDF (58 pp) | 1 | [S17] §7.1–7.5 read verbatim |
| 34 | 2026-09-17 | arXiv API | `all:"thrust vector control" AND (all:"model rocket" OR all:"amateur rocket" OR all:"student" OR all:"small-scale")`, sorted by date | totalResults 3 | [S1] [S3] [S13]; nothing else since 2025-03 |
| 35 | 2026-09-17 | WebSearch | `review OR survey "active control" OR "active stabilization" amateur OR hobby OR "high-power" rockets literature canards airbrakes thrust vectoring student teams` | 9 links | [S16] [S21] [S27]; no survey found |
| 36 | 2026-09-17 | WebFetch | `https://scholarcommons.scu.edu/mech_senior/81/` | page | [S21] read |
| 37 | 2026-09-17 | OpenAlex API | `works?filter=doi:10.1016/j.ifacol.2024.08.041` (a guessed DOI — wrong) | 1, irrelevant | [S24] opened in error |
| 38 | 2026-09-17 | OpenAlex API | `works?search=Improved attitude stabilisation system augmented sounding rocket design integration verification launch` | 1 | [S16] |
| 39 | 2026-09-17 | OpenAlex API | `works/https://doi.org/10.1109/incoft60753.2023.10425646` | 1; cited_by_count 2 | [S2] abstract and citation count |

## Searches not run

- **Google Scholar with hit counts** — not reachable from the tools used; every "Hits" cell above is a link count from a general web search, not a database count. A Scholar pass with "cited by" chaining from [S6] and [S16] is the first thing to add.
- **YouTube** — the majority of hobbyist and student TVC flights are documented only as videos. This is the largest blind spot for SC1: the count of student-flown TVC rockets is certainly higher than the published record shows.
- **Rocketry Forum** (HTTP 403) and **Instructables** (JavaScript-only) — the same-tier community discussion, including the thread where a university team asks "movable fins or TVC?" [S20] and the thread on why Signal R2 was withdrawn [S19].
- **IEEE Xplore full text** — blocked; [S2] and IEEE 11360267 ("Design and Development of a Thrust Vector Control Model Rocket for High-Altitude Payload Delivery", seen in search log #4) were assessed from abstracts or not at all.
- **BPS.space's current AVA product and documentation** — only the TVC-files page was opened; whether AVA now ships TVC support with editable code is unchecked and is the single most likely flip (see above).
- **Second citation hop** in either direction; **Google Patents** beyond incidental hits; **non-English literature**; **thesis repositories** (ProQuest, university DSpace) beyond what web search surfaced; **other competition rulebooks** (EuRoC, Australian Universities Rocket Competition, NASA Student Launch) — only IREC was read.
- **The Tripoli Unified Safety Code v1.04 (2025)** was seen in results [S28] but not opened; the claim that active stabilisation is permitted rests on [S12] (2019) and the IREC text [S17], not on the Tripoli document itself.

## Sources consulted

| Key | Citation (authors, year, title, venue) | Link (DOI / URL) | Role | Depth read | Verified |
|---|---|---|---|---|---|
| S1 | E. Singh, 2025, "Design and Testing of a Low-Cost 3D-Printed Servo Gimbal for Thrust Vector Control in Model Rockets", arXiv preprint (submitted 2025-08-26; single author, no affiliation listed) | https://arxiv.org/abs/2509.00061 | recent preprint; documented statement of the gap; counter-example SC3 (bench only) | abstract | yes — abstract (quotes "costly and technically inaccessible", "reproducible platform"; bench-tested only) |
| S2 | A. Praveen, S. J. Anjith, A. Shiva, A. Mathews, M. Shaiju, S. Sreeja, 2023, "Thrust Vector Control of Solid Propellant Model Rocket", 2nd Int. Conf. on Futuristic Technologies (INCOFT), IEEE; College of Engineering Trivandrum | https://doi.org/10.1109/INCOFT60753.2023.10425646 | same-tier university build; supports narrowed SC1 (hold-down tests, no flight) | abstract | yes — abstract via OpenAlex ("hold-down tests were conducted"); IEEE full text blocked |
| S3 | P. dos Santos, P. Oliveira, 2024, "Thrust vector control and state estimation architecture for low-cost small-scale launchers", Acta Astronautica 222 (arXiv 2303.16983) | https://arxiv.org/abs/2303.16983 | academic baseline; simulation only | abstract | yes — abstract ("tested in simulation environment") |
| S4 | P. dos Santos, P. Oliveira, 2023, "ADCS Design for a Sounding Rocket with Thrust Vectoring", Aerotecnica Missili & Spazio 102(3):257–270 | https://doi.org/10.1007/s42496-023-00161-w | academic baseline; simulation only | abstract | spot-checked — abstract reconstructed from OpenAlex index; Springer page redirected to login |
| S5 | P. Santos, J. Reis, P. Oliveira, C. Silvestre, 2026, "QuadRocket: An Aerial Robotic Testbed for Adaptive Thrust-Vector Control of Rocket-Like Vehicles", arXiv preprint (submitted 2026-07-02) | https://arxiv.org/abs/2607.02474 | recent; counter-example SC3 (electric testbed, not a model rocket) | abstract | yes — abstract ("versatile testbed", motion-capture arena) |
| S6 | R. Linsen, P. Listov, A. de Lajarte, R. Schwan, C. N. Jones, 2022, "Optimal Thrust Vector Control of an Electric Small-Scale Rocket Prototype", IEEE ICRA 2022; EPFL | https://doi.org/10.1109/ICRA46639.2022.9811938 | counter-example SC3 (flown electric TVC platform "to explore guidance algorithms") | abstract | yes — abstract via OpenAlex; IEEE full text not opened |
| S7 | BPS.space (J. Barnard), n.d. (page current 2026-09-17), "Thrust Vector Control 3D Files", product page | https://bps.space/products/thrust-vector-control | nearest commercial neighbour; documented absence (software withheld); motor guidance | full text | yes — product description (US$35; motors listed; "not publicly available yet"; "over 40 successful flights"; "first few tests will probably fail") |
| S8 | T. Kuttler, n.d., "TVC-Rocket-Flight-Code: Closed loop thrust vector control software for model rocketry", GitHub repository, MIT licence | https://github.com/tomkuttler/TVC-Rocket-Flight-Code | same-tier open-source build; counter-example SC1/SC3 (flown, reusable) | full text | yes — README (Teensy 4.1, two PID loops, flight video, 63 stars / 14 forks); last-commit date not captured |
| S9 | P. Sathish, K. Bandi, A. Gujrathi, M. Hwang, S. Shailesh, M. Yore, T. Lee, A. Zangara, A. Yagnavajhala, C. Wang, 2025, "Structural Development, Analysis, and Testing of a Full Scale Jet Vane Thrust Vector Control Rocket for Active Stabilization", AIAA Regional Student Conferences; Georgia Tech Ramblin' Rocket Club | https://doi.org/10.2514/6.2025-99339 | same-tier university build; supports narrowed SC1 (static fires, no flight) | abstract | yes — abstract via OpenAlex ("three static fires", "final static fire scheduled for future test"); AIAA page HTTP 403 |
| S10 | R. Negandhi, S. Sheth, H. Sanchez, J. Meyers, 2025, "Aerodynamic Modeling for Thrust Vector Control Rocketry", AIAA Regional Student Conferences; Georgia Tech | https://doi.org/10.2514/6.2025-98332 | same-tier; companion to S9 (CFD only) | abstract | spot-checked — abstract via OpenAlex |
| S11 | SFU Rocketry, n.d. (page current 2026-09-17), "Thrust Vector Control", project page | https://www.sfurocketry.com/completed-projects/tvc | same-tier university build; supports narrowed SC1 (ground test platform, completion expected early 2026) | full text | yes — page text |
| S12 | J. Barnard, K. Hammond, 2019 (updated 2020), "Build Your Own Thrust Vectored Rockets for Vertical Landings Like SpaceX", Make: magazine | https://makezine.com/article/maker-news/build-your-own-thrust-vectored-rockets-for-vertical-landings-like-spacex/ | hobbyist-tier evidence of difficulty and of regulatory permissibility | full text | yes — article ("My first ten launches were failures. But the eleventh succeeded"; active control "not illegal") |
| S13 | T. Cai, 2023, "An Investigation into Active Control for Accessible Orbital Flight", Canadian Science Fair Journal (arXiv 2304.13704) | https://arxiv.org/abs/2304.13704 | counter-example SC1 (individual student, TVC, test flights) | abstract | yes — abstract ("maximum of 7° and 2.62° of deviation"; Arduino flight computer) |
| S14 | D. Wyatt, 2007, "An Actively Stabilised Model Rocket", fourth-year (IIB) undergraduate project report, University of Cambridge Engineering Dept., Group C 2006/07; hosted by Aerocon Systems | https://aeroconsystems.com/tips/Active_Stabilized_rocket_Wyatt.pdf | same-tier historical build; documented statement of the premise (2007); flown and crashed | full text | yes — §1 p.1 ("rarely been built in the past"), §7.6 p.32 (maiden flight 6 May 2007, Estes E9, "veered away from the vertical and crashed"), §8.1 p.35 (cost ~£1120; bench instability from cross-axis coupling) |
| S15 | D. Sherman, M. Noori, S. Guerrero, M. Balsomi, 2022, "TVC Gimbal Rocket" (Team WR140), UTA Computer Science & Engineering Senior Design | https://websites.uta.edu/cseseniordesign/2022/11/08/tvc-gimbal-rocket | same-tier capstone; "educational tool" framing; static tests, flight unconfirmed | full text | yes — page text |
| S16 | A. Posta, A. Monk, A. Durollet, O. Martin, S. Bruton, J. Kim, 2024, "Improved attitude stabilisation system augmented sounding rocket design, integration, Verification & launch", IFAC-PapersOnLine 58(16):175–180; University of Leeds | https://doi.org/10.1016/j.ifacol.2024.08.482 | strongest counter-example SC1 (student team, canards, LQR, successful launch April 2024, vertical-flight correction) | abstract | yes — abstract via OpenAlex ("A successful launch in April 2024 shows the effectiveness of the integrated attitude control system"); ScienceDirect full text not opened |
| S17 | Experimental Sounding Rocket Association, 2025, "IREC Design, Test, & Evaluation Guide", Revision 2025 V1.1.6, effective 2025-02-14 | https://www.soundingrocket.org/uploads/9/0/6/4/9064598/2025-irec_dteg_v1.1.6_02-14-25.pdf | documented absence (COTS active control unavailable); explains why student TVC is rare at competitions | full text | yes — §7.1.1, §7.1.2, §7.2.1, §7.2.2, §7.4.1, §7.5.2 read verbatim from extracted text |
| S18 | BPS.space, 2019-10-22, post on X announcing Signal R2 availability "until Nov 20, 2019" | https://x.com/bps_space/status/1186752713910030336 | evidence that a commercial TVC kit existed and was withdrawn | snippet only | no — seen in search-result snippet only; the post was not opened |
| S19 | Rocketry Forum thread, n.d., "Another Joe Bernard and Thrust Vectoring Question" | https://www.rocketryforum.com/threads/another-joe-bernard-and-thrust-vectoring-question.182550/ | could not locate the content (HTTP 403); would explain the Signal R2 withdrawal | not accessible | n/a |
| S20 | Rocketry Forum thread, n.d., "University team looking for advice: Movable fins or thrust vector control (TVC) for an active control system in a model rocket?" | https://www.rocketryforum.com/threads/university-team-looking-for-advice-movable-fins-or-thrust-vector-control-tvc-for-an-active-control-system-in-a-model-rocket-question.188779/ | same-tier signal that teams face this choice | snippet only | no — title only; forum blocks fetching |
| S21 | V. Avila Guerrero, A. Barranco, D. Conde, 2018, "Active Control Stabilization of High Power Rocket", Mechanical Engineering Senior Thesis, Santa Clara University | https://scholarcommons.scu.edu/mech_senior/81/ | same-tier capstone; method and flight outcome not stated in abstract | abstract | spot-checked — abstract on repository page |
| S22 | Northern Arizona University, 2026, "Active Rocket Control System", EE capstone project page | https://ceias.nau.edu/capstone/projects/EE/2026/RocketControl/ | same-tier; active roll control (induce and cancel roll) | snippet only | no — page fetch failed (TLS certificate); description from search snippet |
| S23 | Instructables, n.d., "TVC Model Rocket: 5 Steps" | https://www.instructables.com/TVC-Model-Rocket/ | hobbyist-tier build guide | not accessible | n/a |
| S24 | A. Guillén-López, A. Sánchez-Herguedas, M. Rodríguez, 2024, "Application of Digital Twin Technology for the Digitization of Railway Maintenance Services...", IFAC-PapersOnLine 58(8) | https://doi.org/10.1016/j.ifacol.2024.08.041 | read, not cited — opened by mistake through a guessed DOI; irrelevant | abstract | n/a |
| S26 | University of Wisconsin–River Falls, 2026-07, "Rockets' red glare: Falcon Rocketeers win NASA WSGC Collegiate Rocket Launch Competition", news release | https://www.uwrf.edu/newsroom/2026/07/rockets-red-glare-falcon-rocketeers-win-nasa-wsgc-collegiate-rocket-launch | same-tier; competition required active roll manoeuvre in flight | snippet only | no — search snippet only |
| S27 | Leeds Rocketry, 2024, "Development of an Active Control System for a Canard Controlled..." (report PDF) | https://leedsrocketry.co.uk/wp-content/uploads/2024/08/Canard-Control-Development.pdf | same-tier documentation behind S16 | snippet only | no — not opened |
| S28 | Tripoli Rocketry Association, 2025-03, "Unified Safety Code", Version 1.04 | http://www.4cornersrocketry.org/Tripoli_Unified_Safety_Code_1.04.pdf | regulatory context (thrust-to-weight below 3:1 only with active stability, per search summary) | snippet only | no — not opened |
| S30 | Princeton Rocketry, n.d., "Active Projects" (Active Controls / TVC team) | https://www.princetonrocketry.com/active-projects | same-tier university TVC project in progress | snippet only | no — search snippet only |
| S31 | Space Enterprise at Berkeley, n.d., "Thrust Vector Control" project page | https://www.berkeleyse.org/thrust-vector-control | same-tier university TVC project | snippet only | no — search snippet only |
| S32 | Georgia Tech Ramblin' Rocket Club, n.d., "GNC" team page | https://www.ramblinrocketclub.org/gnc | same-tier; claims first collegiate jet-vane test fire (April 2024), launch targeted Spring 2025 | snippet only | no — search snippet only |
| S33 | Imperial College London, 2024-10, "Imperial student rocketry team win international challenge" (ICLR, first European student liquid-engine TVC) | https://www.imperial.ac.uk/news/256154/imperial-student-rocketry-team-international-challenge/ | adjacent tier (liquid-engine hot-fire TVC, not a model rocket) | snippet only | no — search snippet only |
| S34 | "Thrust Vector Control (TVC) Using Gimbal Mechanism", 2024, IJIRSET (pay-to-publish tier) | https://www.ijirset.com/upload/2024/may/301_Thrust.pdf | existence evidence only; venue tier too weak for claims | snippet only | no — not opened |
| S35 | KSCST Student Project Programme, n.d., "Thrust Vector Control" (exhibition project report, India) | https://www.kscst.org.in/spp/46_series/46s_spp/02_Exhibition_Projects/208_46S_BE_3913.pdf | existence evidence of a same-tier student exhibition project | snippet only | no — not opened |
