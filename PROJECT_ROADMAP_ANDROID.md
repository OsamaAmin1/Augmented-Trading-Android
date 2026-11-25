# Augmented Trading — V1.19 project roadmap (2026-11-25)

Scope revision to V1.16, per user direction: move Phase 18 (AI Training & Decision Support) from V1 to V2. Preserve milestone IDs, the 35 strategy definitions and all 80 capability IDs and definitions. V1.17 adds candidate historical replay and extended synthetic path viewing; the Phase 18 deferral remains unchanged. V1.19 adds persistent Academy, descriptive progress evidence, and a 45-work-item implementation inventory. Formal capability integration remains open pending recovery of the locked register.

V1: offline education, historical research, deterministic analysis, simulation, backtesting and mathematical optimization. Existing synthetic learning datasets (10.10), rule-based Strategy Assistant (05), and assessment controls remain in scope; no learned-model fitting or AI-generated investment decisions required. V2: model training and validation, AI decision support, live connectivity and possible broker execution, contingent on data rights, verified access and approvals.

Initial implementation count: V1 17/19 (89.5%); Phase 19 partially implemented and not counted complete; V2 0/11; overall 17/30 (56.7%). These counts are not acceptance or production readiness. Phase 18 starts in V2 using offline data before any live AI deployment; phase 25 remains the separate real-time integration milestone.

## V1 — Offline analytical platform

| Phase | Milestone | Status / acceptance gap |
|---|---|---|
| 01 | Investor Personality Framework | Locked |
| 02 | Synthetic Investor Personas | 5,000 locked |
| 03 | Strategy Reference Engine | 35 strategies locked |
| 04 | Progressive Assessment | V4.1 locked |
| 05 | Strategy Assistant | Initial prototype |
| 06 | Trading Academy | Prototype; persistent competency integration pending |
| 07 | Scenario Simulator | Initial prototype |
| 08 | Continuous Investor Profile | Prototype; behavioral inference pending |
| 09 | Unified Application | Initial prototype |
| 10 | EGX Historical Data Platform | Warehouse and synthetic Market World implemented; complete real EGX/global prices, disclosures, macro, liquidity, calendars, corporate-action and rights verification outstanding |
| 11 | Persistent Investor Intelligence | Local encrypted workspace; security audit, behavioral integration and Windows test pending |
| 12 | Fundamental Analysis | Implemented; limited issuer coverage |
| 13 | Technical Analysis | Implemented; long real histories, timeframes and calibration pending |
| 14 | Market Intelligence | Implemented rule-based evidence; actual sentiment and impact calibration pending |
| 15 | Strategy Backtesting | 11/35 rule prototypes, 660 D5 runs; 24 strategies and actual historical validation pending |
| 16 | Operations Research Optimization | MILP with CVaR, 48 D5 runs; forecast calibration, verified 20-day backtest, profile linkage, multi-asset expansion and dynamic execution constraints pending |
| 17 | Historical Market Replay | Initial implementation: 51 paired ADIB/EGX30 dates, 20-interval candidate paper OR experiment, as-of news and macro, 20/60/120-step D5 path viewer. Strict verified gate remains closed; full actual calendars, corporate actions, rights, cross-source price reconciliation and international price alignment outstanding. |
| 19 | Approved Capability Integration | PARTIAL: 45 independent implementation work items audited (24 implemented, 14 partial, 2 blocked, 5 deferred). Persistent Academy and descriptive progress integrated. Exact 80 original definitions unavailable; 71 known ID slots recorded without fabricated definitions. Formal mapping and remaining V1 integration gaps open. |
| 20 | V1 Acceptance | Validate offline rule-based analysis, replay, backtesting and OR, data rights, security, browser/Windows, usability and regression; empirical claims require independent evidence. Trained AI is not a V1 acceptance requirement. |

## V2 — AI and live augmented trading

| Phase | Milestone | Status / acceptance gap |
|---|---|---|
| 18 | AI Training & Decision Support | Moved to V2. Train on development only after data rights and quality approval; independent empirical evaluation, calibrated uncertainty, rule-based safety gates and human authorization. Offline validation precedes live use. |
| 21 | Live EGX data | Deferred; verify free access, license and availability |
| 22 | Thndr connection | Deferred; MCP first if available/free, wrapper second, screenshots last |
| 23 | Portfolio synchronization | Deferred; user authorization, reconciliation and read-only first |
| 24 | Real-time intelligence | Deferred |
| 25 | Real-time AI | Deferred; depends on phase 18 validated models, live data and explicit safety/authorization controls. |
| 26 | Live optimization | Deferred; calibrated forecasts, risk and costs |
| 27 | Augmented interface | Deferred |
| 28 | Execution | Deferred; broker permissions, explicit user confirmation and regulatory requirements |
| 29 | Live risk controls | Deferred |
| 30 | V2 acceptance | Deferred; no real funds until validated and authorized |

## Next release sequence

19 (recover original register and close scoped gaps) → 20 → V2 (18, 21–30, subject to dependencies). Actual historical acquisition and verification remain open. Phase 19 must document deferred capabilities explicitly; no blanket acceptance claim.

## Android delivery track (V1, added after Phase 19)

| ID | Work item | Current status |
|---|---|---|
| AND-01 | Android Studio project and complete bundled V1.19 runtime | Source port prepared; no APK built |
| AND-02 | Embedded SQLite market warehouse and private persistent investor storage | Source implemented, host checks passed; Android storage validation pending |
| AND-03 | English / Arabic localization and RTL | Initial 622-entry label dictionary; untranslated original evidence and dynamic content pending |
| AND-04 | Contextual bilingual tool / strategy / metric / algorithm information | Initial 135 entries, all 35 strategies; comprehensive UI coverage review pending |
| AND-05 | Embedded OR MILP compatibility | Host enumeration and solver parity checks passed; Android dependency and performance tests pending |
| AND-06 | Android build and install | BLOCKED in current container; Gradle CI supplied, APK not compiled |
| AND-07 | Physical phone and tablet acceptance | Pending actual Android build, dependency review, offline execution, export, storage, Arabic QA, security review |
| AND-08 | V1 final acceptance | Pending original 80-capability recovery, data rights/validation, existing phase 19 gaps and Android acceptance |

No existing milestone IDs or locked definitions have been modified. Phase 18 (AI training and decision support) remains in V2 with live EGX and Thndr integration. Android is a delivery track, not a new completed milestone; V1 remains 17/19 initially implemented, with phase 19 partial and phase 20 open.
