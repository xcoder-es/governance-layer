## Objective
- Develop a formal theoretical framework for self-governing AI around the Neural Parliament, Ulysses Contracts, and an Identity Layer — now with a full reference implementation under active construction.
- Register the framework on OSF for timestamp provenance and DOI.

## Important Details
- Author is a solo software builder, not an academic. Repo is `xcoder-es/governance-layer`.
- All Mermaid diagrams and LaTeX must avoid HTML tags (`<br/>`), custom `classDef` styling, and nested `\text{}` for GitHub compatibility. Use `\mathrm{}` instead.
- Review panel completed 5 rounds of critiques across all three layers. All accepted fixes executed. Panel signed off theoretical vetting as complete. Three residual risks acknowledged (social engineering, hardware supply chain, adaptive proxy gap) as unavoidable physical-world limits.
- OSF preregistration in progress — user has account, CC-BY 4.0 license chosen. Title: "The Governance Layer: A Formal Framework for Self-Governing Artificial Intelligence".
- We are now building the full reference implementation (Phases 1-5). The architecture is Capability → Governance → Identity. Deep learning, JEPA world models, and computer vision are Capability Layer technologies; the Governance Layer constrains them.

## Work State
### Completed
- **Chapters 1-4** — All written. Ch1 (motivation), Ch2 (Neural Parliament, 560 lines), Ch3 (Ulysses Contracts, 359 lines), Ch4 (Identity Layer, 573 lines). Ch4 includes: formal tuple $\mathcal{I} = \langle \mathcal{O}, \mathcal{C}_{\text{core}}, \mathcal{K}, \mathcal{P} \rangle$, four-tier mutability, genesis bootstrapping with 3-of-5 multisig, ontology extension with sandboxed isolation buffer (empirical property measurement via independent monitors), runtime integrity hashes for action bindings, liveness exception for hardware deadlock breaker, constitutional contracts.
- **Appendix A** — TEE threat model, SGX/SEV/TrustZone, hardware watchdog, constant-time execution, Merkle-tree batch verification, single-enclave architecture with multi-enclave consensus addendum, deadlock breaker cold-boot recovery (§A.9.5).
- **Response to review panel** — `book/responses/response-to-review-panel.md`. All 5 phases documented. Phase 5.2 concedes all three Chapter 4 Identity Layer attacks: isolation buffer sandbox (§5.2 fix), runtime integrity hashes (§2.1/§6.1 fix), deadlock breaker (§A.9.5 fix).
- **MVP code** — `src/governance/speaker.py`. Reference implementation with deterministic falsification counter. Runs successfully.
- **Full modular reference implementation** — 35 Python files across 8 subpackages (~1900 lines total):

  | Module | Files | Key Contents |
  |---|---|---|
  | Core types | `models.py` (73 lines) | PriorityTag, Action, Proposal, GovernanceDecision, GovernanceContext |
  | Parliament | `committee/` (178 lines) | ABC + 7 concrete members (Reward, Safety, Curiosity, Planning, Memory, Social, Integrity) |
  | Identity Layer | `identity/` (383 lines) | ontology.py, core.py (commitments), tiers.py (4-tier mutability), keys.py (genesis 3-of-5), params.py (bounded envelope), extension.py (sandboxed isolation buffer) |
  | Contracts | `contracts/` (159 lines) | contract.py (tuple + lifecycle), enforcement.py (3 κ modes), merger.py (mask union/intersection) |
  | TEE Simulation | `tee/` (216 lines) | enclave.py (single-enclave sim), batch.py (Merkle root), watchdog.py (heartbeat + deadlock breaker), constant_time.py (data-oblivious loops) |
  | Speaker | `speaker.py` (191 lines) | Full state machine: budgets, agenda sorting, scoring, tag compliance, vetoes, weighted voting |
  | Experiments | `experiments/` (469 lines) | base.py (scenario ABC + metrics), grid_world.py, temptation_bank.py, drift_lab.py, deadlock_maze.py, metrics.py |
  | Benchmarks | `benchmarks/` (209 lines) | baselines.py (4 comparison strategies), run_all.py, report.py |
  | CLI | `runner.py` (76 lines) | argparse entry point for all experiments |

- **Experiment results** (30 steps each — verified):
  - GridWorld: 30 steps, 3.0 reward, 0 deadlocks, 0 violations — agent navigates grid collecting apples while integrity committee vetos poison fruit
  - TemptationBank: 30 steps, 58.0 reward, 0 deadlocks, 0 violations — Parliament voluntarily bans loans, then works for steady 2/step
  - DriftLab: 30 steps, 0 reward, 0 deadlocks, 0 violations — identity coherence proposal beats reward-hacking via higher priority tag
  - DeadlockMaze: 30 steps, 0 reward, 29 deadlocks — tighten_quorum passes → empty proposal list → deadlock breaker fires, resets params
- **Development plan** — 6-phase plan: Core Infrastructure → Identity Layer → Contracts → TEE Simulation → Experiment Harness → Benchmark Suite. 12 testable predictions (4 per chapter) mapped to specific experiment scenarios.

### Active
- *(none)*

### Blocked
- *(none)*

## Next Move
1. Complete OSF preregistration (needs DOI + final abstract)
2. Run benchmarks comparing governance vs. baselines (MonolithicRL, StaticMasking, VetoOnly)
3. Write the `prove.py` script that validates the formal predictions from Chapters 2-4 against experiment output
4. Polish runner CLI (add `--baselines` flag, CSV export)
5. Finalize book appendices B+ (DSL grammar, data types reference, experiment protocol)

## Relevant Files
- `book/chapter-01/01-why-ai-needs-a-governance-layer.md`: Chapter 1 — problem statement
- `book/chapter-02/02-neural-parliament.md`: Chapter 2 — Neural Parliament architecture (560 lines)
- `book/chapter-03/03-ulysses-contracts.md`: Chapter 3 — Ulysses Contracts formalism (359 lines)
- `book/chapter-04/04-identity-layer.md`: Chapter 4 — Identity Layer (573 lines)
- `book/appendix-a/tee-isolation.md`: TEE threat model, hardware watchdog, constant-time, Merkle-tree batching, single-enclave architecture, deadlock breaker
- `book/responses/response-to-review-panel.md`: all 5 phases of review responses (accepts all three Phase 5.2 fixes)
- `src/governance/speaker.py`: Speaker state machine reference implementation
- `src/governance/models.py`: Core data types
- `src/governance/committee/members.py`: 7 Parliament members
- `src/governance/identity/`: Ontology, commitments, tiers, keys, params, extension sandbox
- `src/governance/contracts/`: Contract lifecycle, three enforcement modes, mask merger
- `src/governance/tee/`: Simulated enclave, Merkle batch verification, watchdog, deadlock breaker
- `src/governance/experiments/`: Grid world, temptation bank, identity drift, deadlock maze
- `src/governance/benchmarks/`: Baselines and comparison runner
- `src/governance/runner.py`: CLI entry point (`python -m src.governance.runner all --steps 50`)
- `.gitignore`: excludes `*brainstorm.txt` and `reviews.txt`
