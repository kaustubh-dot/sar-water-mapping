# Submission connections review

29 October 2026. Bounded independent audit of source commit
`a2a9e15fc4f21fbe2595bdc481b37142265ee1cf`. This review traces the supplied
first-100 recipe through acquisition, audit/splits, calibration, the single
notebook and submission instructions. It does not rerun experiments, choose
splits, tune parameters or reopen model selection.

**Decision: the reviewed development experiment remains separate and usable;
the supplied-subset submission is not connected end to end yet.** The earlier
development acceptance and the supplied-recipe documentation acceptance do not
close the new dataset or fresh-Colab gates. No new defect in the recorded
development scores is asserted here.

## Material wiring findings

### P1 — No executable notebook path consumes the supplied selection

Locations: [notebook](../notebooks/01_sar_water_mapping.ipynb), physical JSON
lines 28, 44 and 74; [development downloader](../scripts/prepare_development_data.py),
lines 95–118 and 137–141.

The notebook defaults to `DATA_SOURCE='upstream-development'`. Its acquisition
cell reads `reports/development_data_selection.json`, requires official
60/20/20 membership and installs the old training/held-out ROI files. None of
its ten code cells references `supplied_subset_selection.csv` or
`supplied_subset_recipe.json`. Changing to `organizer` accepts externally
prepared inventory/provenance but unconditionally raises before calibration.
The downloader's fresh-selection path also generates the old hash-ranked
60/20/20 selection. Therefore neither changing the data directory nor running
the existing defaults in a fresh Colab session executes the newly supplied
first-100 recipe. This is an unfinished integration, not a reason to bypass the
organizer guard.

Smallest correction: add one explicitly versioned supplied-recipe acquisition
path, reusing verified bounded object download and the existing scientific
adapter. Bind it to the committed ordered 100 IDs and source CSV hash, use a new
data/run directory, and connect its audited inventory, internal split CSV,
training ROIs and held-out ENL ROIs to the same notebook. Preserve the earlier
development profile and its artifacts. Keep original `upstream_split=train`
separate from newly frozen evaluation membership: copying upstream `train`
into the inventory's operative `split` column would supply no validation/test
partition (`src/sar_water/data.py`, lines 342–350). Do not remove the 60/20/20
guard from the development profile or relabel old result tables.

### P2 — Generic calibration inputs receive hardcoded development provenance

Locations: [calibrator](../scripts/calibrate_classical.py), lines 143–159,
172–179 and 194–198; [notebook calibration guard](../notebooks/01_sar_water_mapping.ipynb),
physical JSON line 74.

The CLI accepts manifest/splits/ROIs without an explicit source configuration.
It starts from `configs/experiment.json`, or conditionally uses the old
`configs/development.json` when the manifest hash matches. It then always sets
`status='upstream_development_subset_calibrated'` and records
`source='audited_supplied_development'`. It does not carry the supplied recipe's
selection hash, source CSV identity, internal-split provenance or prior-training
exposure into its frozen configuration. A valid new manual-label manifest can
therefore be calibrated through the CLI while receiving the wrong source
description. The notebook's deliberate organizer stop correctly prevents that
case in the notebook today; deleting only that stop would expose it.

Smallest correction: support an explicit audited source/provenance configuration
in the calibrator and bind its file hash into frozen calibration evidence.
Preserve the locked grids and all train/validation/test access protections.
Carry source identity, selection identity, split policy/limitations and the
22-patch exposure disclosure without allowing this input to override scientific
choices. Pass it from the supplied notebook path and verify the resulting
bindings before removing the stop for that supported path. Add focused checks
that development provenance stays development, supplied provenance stays
supplied, changed/missing source bindings fail, and calibration still opens no
held-out sources.

## Immediate documentation follow-ups

- [ROADMAP.md](../ROADMAP.md), lines 99–105, says to run the current fresh
  classical notebook before the newly supplied experiment. Its own earliest
  incomplete phase is now Phase 1 (line 38). Put the supplied audit/split and
  integration first, followed by the fresh supplied-profile Colab run. An
  optional old-development timing run must retain that identity and cannot
  certify the supplied workflow's time.
- [Final report](final_report.md), lines 14–20 and 165–168;
  [demo](demo_outline.md), lines 8–15 and 27–34;
  [data guide](../data/README.md), lines 3–6; and
  [reproduction guide](../docs/REPRODUCING.md), lines 3–6 and 18–23, have not
  incorporated the known recipe. Their development labels prevent their
  existing tables from becoming false supplied-subset claims, so this is not
  a newly discovered invalid-result finding. Before submission, add the same
  distinction already present in README: selection known, exact internal
  evaluation not yet run, only 22 IDs overlapping prior development and all
  previously trained. Link to the recipe audit and explicitly label the
  existing commands/tables/checkpoints as development reproduction.
- Once the final accepted implementation exists, pin the submitted notebook
  access link and executed `REPO_REF` to its reviewed full SHA. The current
  notebook line 28 and README line 22 use a moving branch. The notebook records
  the resolved executed SHA, which is useful evidence, but the final submission
  should identify the intended source as well. Keep the older GPU training SHA
  attached to its existing checkpoints.

## Execution gates that code or prose fixes cannot close

1. Download and independently audit all exact supplied pairs: units/bands,
   manual-label provenance, integrity, native geometry and independent validity.
   The committed selection contains 100 upstream training chips, all with
   `evaluation_split=unassigned`; it does not supply an internal holdout.
2. Freeze defensible internal event/scene/spatial membership before tuning.
   Group constraints take precedence over exact proportions. Establish new
   raw-training ROIs/looks and, for any learned comparison, new training
   normalization. Keep the earlier test-visible development choices/results
   unchanged.
3. Run the locked bounded calibration on the new validation partition, freeze
   its identities, then score its new held-out partition. Any learned result
   requires separate training and honest prior-exposure disclosure. The released
   development checkpoint is not an unseen-input baseline for the full new set.
4. Execute the connected supplied profile in an actual fresh Colab runtime with
   uncached documented access; retain setup, acquisition, audit, calibration,
   evaluation, figures, archive/hash and authoritative timing sidecar. The
   91.78-second cached Linux development smoke does not close this gate. Keep
   remote training and Colab classical/checkpoint/full-training timings distinct.
5. Update submission claims from those measured artifacts, then consider the
   final acceptance tag. No final readiness or sub-30-minute claim follows from
   this review.

## Verification performed for this review

Read AGENTS, README, ROADMAP, evaluation protocol, implementation lock and
reproduction guide, plus the supplied recipe/selection/review, downloader,
calibrator, data splitter, notebook, relevant provenance tests and submission
report/demo. Recomputed local selection facts without downloading imagery:
100 unique IDs at recipe positions 0–99; all upstream `train`; all internal
membership `unassigned`; Ghana 31, India 40, Mekong 18, Nigeria 10, Pakistan 1;
exactly 22 prior-development overlaps, all `train`. Selection SHA-256 matches
`9c4204b432254130a7dc7cc8e08705962b3a6eeab03824ea8fe76f9f8070b7b2`.
All ten notebook code cells parse, and none references the supplied selection
artifacts. Existing fixture tests were read as implementation evidence; no
scientific execution, model test or fresh Colab run was performed for this
documentation audit. Only this review file was added.

## Bounded fix re-review, 29 October 2026

**Accept the neutral provenance correction and the reviewed submission wording.
The false-upstream-identity defect in P2 is resolved. P1 and the supplied-source
integration/execution gates remain open.** This accepts a smaller truthful
metadata fix than the full source-config support originally proposed above;
it does not claim that support has been implemented.

The calibrator now sets `real_data.status='audited_manual_subset_calibrated'`
and result `source='audited_manual_subset'`. These labels describe what the
generic CLI actually verifies without asserting upstream-development or
organizer identity. The existing exact-manifest pending-config branch remains
unchanged, so its recorded source-specific fields are retained when applicable;
generic inputs do not gain `organizer_subset=true`. The remaining result status
`real_development_calibration_frozen` is a development-stage status rather than
an upstream or organizer identity claim.

The notebook still stops the unsupported organizer path before invoking the
calibrator. Its explanation now identifies the missing supplied-set
acquisition/split/provenance profile instead of pointing to the removed
hardcoded-upstream metadata. New opening text and organizer instructions state
that defaults reproduce the older 60/20/20 set. The report, demo and reproduction
guide now disclose the known different recipe and keep their commands/results
under development identity; the report explicitly discloses the 22 previously
trained IDs. Their supplied-set and fresh-Colab gates remain open.

Independent verification in this re-review:

- Executed the existing generic calibration fixture with the new assertions,
  and the new test that executes the actual organizer calibration cell and
  verifies zero subprocess calls before its stop: **2 passed in 2.28 seconds**.
  These are temporary synthetic fixtures, not supplied-data execution.
- Compared parsed syntax trees against HEAD: the calibrator differs only in the
  two intended metadata strings; notebook code differs only in the stop's
  explanation. Scientific search, counts, thresholds, masks and all other
  notebook execution logic are unchanged.
- Verified UTF-8 content and all 14 local link targets in the three updated
  Markdown documents. No links or scientific output files were replaced.

At the re-review snapshot, two non-scientific follow-ups still need attention:
`data/README.md` lines 3–6 retain the archive-absent introduction without the
known recipe, and ROADMAP lines 103–104 still put the old fresh-Colab run ahead
of the earliest incomplete supplied audit. `git diff --check` also reports
trailing whitespace at the two changed calibrator lines (149 and 172), caused
by their retained CRLF bytes under the current file treatment. The parent was
notified to correct formatting and run final repository checks. These do not
reopen the resolved provenance semantics or close any execution gate.

## Final audit-artifact re-review, 29 October 2026

**Accept the bounded fixes and audit artifacts for development publication.
The supplied-subset submission remains NOT READY.** No unresolved P1/P2 defect
remains in the neutral-label, guard-message and documentation corrections.
The unimplemented supplied profile (S1/P1), fresh uncached Colab verification
(S2/P1) and final publication step (S3) remain explicitly open; this acceptance
does not close them or authorize a final acceptance tag.

The remaining documentation follow-ups identified in the prior re-review are
now corrected. `data/README.md` describes the known first-100 recipe and its
unrun audit/internal split. ROADMAP orders supplied-profile audit/execution
before fresh Colab of that connected profile and explicitly states that
repeating the old development run does not verify the supplied submission.
README, the notebook, report, demo, reproduction guide and consolidated
`reports/submission_audit.md` retain the development/supplied distinction and
do not claim an unrun gate passed. Existing result tables remain unchanged.

Independently checked the current audit snapshot:

- `reports/submission_verification.json` parses and its
  `new_calibrator_sha256` matches the current file exactly:
  `bca808707f2ac0908bbef20d26bf04ceb5fc91bf7ba57bfddbad0e26202ab164`.
  Supplied-profile connection, internal split, supplied execution, fresh Colab
  and final-tag fields are all false, consistent with the NOT READY verdict.
- The calibrator's raw bytes match HEAD after exactly the two reviewed label
  replacements; original CRLF bytes are preserved. Parsed notebook code still
  differs only in cell 9's organizer-stop explanation; all ten code cells
  parse. No numerical/data-access statements or legacy results/configurations/
  checkpoint artifacts changed.
- The publication inventory contains 143 files, including 139 readable text
  files. All 119 local Markdown links resolve inside that publication set;
  no file exceeds 5 MB. These counts match the verification JSON.
- The parent-recorded final suite reports 111 passing tests in 40.09 seconds
  and the focused suite 11 passing tests in 4.87 seconds. This final artifact
  pass did not repeat those suites; the previous re-review independently ran
  the two focused calibration/guard fixtures recorded above.
- `git diff --check` exits successfully. The explicit
  `scripts/calibrate_classical.py -text whitespace=cr-at-eol` rule resolves the
  earlier CR-at-EOL diagnostic while retaining source-byte preservation.

This completes the review of the requested corrective audit change. Continue
with the recorded supplied-data/profile and actual Colab execution gates;
preserve prior negative findings and the original development evidence.
