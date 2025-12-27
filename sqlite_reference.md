## SQLite Reference – CAMEO (cameo.sqlite)

### Connection
- Location: `data/cameo.sqlite`
- MCP config: uses Docker image `mcp/sqlite` with `--db-path /data/cameo.sqlite` and mount `C:/Users/aminh/OneDrive/Desktop/CAMEO/CAMEO/data:/data`.
- Current snapshot: `info` table shows `version=3.1.0`, `import_date=2024-05-16`.

### Table inventory (selected, with row counts)
- `chemicals` (~5,094) — master chemical records.
- `chemical_search` (~5,094) — search-optimized entries (likely FTS).
- `chemical_cas` (~4,942) — CAS mappings; pk `(chem_id, cas_id)`.
- `chemical_unna` (~3,850) — UN/NA mappings; pk `(chem_id, unna_id)`.
- `chemical_icsc`, `chemical_lol`, `chemical_cfats`, `chemical_aegl`, `mm_chemical_*` — additional mappings to reference sets.
- `mm_chemical_react` (~9,231) — junction: chemicals → reactive groups.
- `mm_chemical_hc` (~3,193) — junction: chemicals → hazard codes.
- `reacts` (80) — reactive group definitions.
- `reactivity` (2,346) — reactive-group pair rules (compatibility + gas products + doc).
- `mm_reactivity_hazard` (4,178) — links reactive-group pairs to hazard categories.
- `hazards` (5) — hazard categories (e.g., Corrosive, Explosive, Flammable, Generates gas, NR).
- Exposure limits: `aegls` (~5,094 rows for many chemicals), `erpgs` (~5,094).
- Guides/regs: `erg_guides`, `unnas`, `unna_*` (CFR, water reactions, action distances, table3), `dupont`, `aloha`, `cfats`, `lol`.
- Text/meta: `notes`, `sources`, `info`.

### Key schemas (abbreviated)
- `chemicals`  
  - `id` (PK), `name`, `description`, hazard/response fields (`health_haz`, `fire_haz`, `non_fire_resp`, `first_aid`, `special_hazards`, `isolation`, etc.), NFPA (`nfpa_*`), physical props (`fp_*`, `lel_*`, `uel_*`, `ai_*`, `mp_*`, `vp_*`, `vd_*`, `sg_*`, `bp_*`, `molwgt_*`, `solblty_*`, `ion_*`), identifiers (`niosh`, `niosh_file`), lists (`synonyms`, `chris_codes`, `dot_labels`, `formulas`, `incompatible_absorbents`), flags (`response_guide_for_chemical_warfare_agent`, `psm`).
- `chemical_search`  
  - `id` (PK), flags `is_aloha`, `is_dupont`, `is_cfats`, `is_icsc`, `is_ehs_tpq`, `is_ehs_rq`, `is_cercla_rq`, `is_section_313_notes`, `is_caa_rq`, plus text fields `regulatory_names`, `rcra_codes`, location fields (`loc_title`, `loc_value`, `loc_unit`).
- `chemical_cas`  
  - PK `(chem_id, cas_id)`; also `cas_nodash`, `sort`, `annotation`.
- `chemical_unna`  
  - PK `(chem_id, unna_id)`; `sort`, `annotation`.
- `hazards`  
  - `id`, `name`, `phrases`.
- `reacts`  
  - `id`, `name`, `special` (bool), `description`, `flammability`, `reactivity`, `toxicity`, `characteristics`, `examples`.
- `reactivity`  
  - PK `(react1, react2)`; `pair_compatibility`, `gas_products`, `hazards_documentation`.
- `mm_reactivity_hazard`  
  - `(react1, react2, hazard_id)` — links reactive-group pairs to hazard categories.
- `mm_chemical_react`  
  - `(chem_id, react_id)` — maps chemicals to reactive groups (used by reactivity engine).
- `mm_chemical_hc`  
  - `(chem_id, react_id)` — maps chemicals to hazard codes (HC).
- `aegls`  
  - `id` (PK), `cas_id`, `csv_id`, `name`, `source`, `unit`, footnotes/status, AEGL1/2/3 values for 10min, 30min, 60min, 4hr, 8hr (value + note).
- `erpgs`  
  - `id` (PK), `cas_id`, `csv_id`, `name`, `source`, `unit`, `lel_value_ppm`, ERPG1/2/3 values + notes.

### Relationships & usage
- Chemical identity: `chemicals.id` is the hub.
- Identifiers: join `chemical_cas` (CAS), `chemical_unna` (UN/NA), other `chemical_*` mapping tables for regulatory datasets.
- Search: `chemical_search` used for fast lookups; likely FTS-enabled (validate in code); contains flags/regs for filtering.
- Reactivity:
  - Map a chemical to reactive groups via `mm_chemical_react`.
  - Evaluate group-pair rules from `reactivity` and hazard categories via `mm_reactivity_hazard` + `hazards`.
  - Reactive group metadata from `reacts`.
- Exposure limits: `aegls`, `erpgs` join on CAS/CSV ids; use `chemical_cas` to link from `chemicals`.
- Favorites/user data (future): should live in separate `user.db` (not bundled here).

### Query patterns (suggested)
- Search by name/CAS/UN: use FTS on `chemical_search` (or indexed columns) → get `chem_id` → fetch `chemicals`.
- Chemical detail: fetch `chemicals` by id; join `chemical_cas`, `chemical_unna`, exposure (`aegls`, `erpgs`), reactive groups (`mm_chemical_react` → `reacts`), hazard codes (`mm_chemical_hc`).
- Reactivity check (pairwise/multi):
  1) Resolve each chem → groups via `mm_chemical_react`.
  2) Generate group pairs; look up `reactivity` + `mm_reactivity_hazard` → `hazards`.
  3) Present `pair_compatibility`/`gas_products` plus hazard labels.
- Integrity: validate `info` version/date on startup; ensure row counts >0 for `chemicals`, `reacts`, `reactivity`.

### Notes / gaps to confirm in code
- Whether `chemical_search` uses FTS5 (inspect DB pragmas or DDL in build scripts).
- Any triggers or indexes (not listed here) — inspect if query plans need tuning.
- `user.db` schema not present yet; design favorites/history/settings there.

---

## Full table schemas (column : type [, PK])

- `info` — `version: VARCHAR (PK)`, `import_date: DATETIME`
- `sources` — `source: VARCHAR (PK)`, `symbol: VARCHAR (PK)`, `fieldname: VARCHAR`, `sort: INTEGER`, `note: VARCHAR`
- `notes` — `id: VARCHAR (PK)`, `source: VARCHAR`
- `erg_guides` — `id: INTEGER (PK)`, `title_en: VARCHAR`, `title_es: VARCHAR`, `title_fr: VARCHAR`
- `unnas` — `id: INTEGER (PK)`, `faux: BOOLEAN`, `active: BOOLEAN`, `polimerize: BOOLEAN`, `synonyms: TEXT`, `materials: TEXT`
- `unna_cfr49s` — `id: INTEGER (PK)`, `unna_id: INTEGER`, `name: TEXT`, `unna_type: VARCHAR`, `hazard_class: VARCHAR`, `labels: TEXT`, `notes: TEXT`, `provision: TEXT`, `packing_group: VARCHAR`
- `unna_waterreactions` — `id: INTEGER (PK)`, `unna_id: INTEGER`, `gas_name: VARCHAR`, `gas_formula: VARCHAR`
- `unna_actiondistances` — `id: INTEGER (PK)`, `unna_id: INTEGER`, `name: VARCHAR`, `small_isolate_feet: VARCHAR`, `small_protect_day_miles: VARCHAR`, `small_protect_night_miles: VARCHAR`, `large_isolate_feet: VARCHAR`, `large_protect_day_miles: VARCHAR`, `large_protect_night_miles: VARCHAR`
- `unna_table3` — `id: INTEGER (PK)`, `unna_id: INTEGER`, `sort: INTEGER`, `title: VARCHAR`, `container: VARCHAR`, `isolate_feet: VARCHAR`, `day_low_miles: VARCHAR`, `day_moderate_miles: VARCHAR`, `day_high_miles: VARCHAR`, `night_low_miles: VARCHAR`, `night_moderate_miles: VARCHAR`, `night_high_miles: VARCHAR`
- `mm_unna_erg_guide` — `unna_id: INTEGER`, `erg_guide_id: INTEGER`
- `erg_guides` (mapped above)
- `hazards` — `id: INTEGER (PK)`, `name: VARCHAR`, `phrases: TEXT`
- `reacts` — `id: INTEGER (PK)`, `name: VARCHAR`, `special: BOOLEAN`, `description: TEXT`, `flammability: TEXT`, `reactivity: TEXT`, `toxicity: TEXT`, `characteristics: TEXT`, `examples: TEXT`
- `reactivity` — `react1: INTEGER (PK part)`, `react2: INTEGER (PK part)`, `gas_products: TEXT`, `pair_compatibility: TEXT`, `hazards_documentation: TEXT`
- `mm_reactivity_hazard` — `react1: INTEGER`, `react2: INTEGER`, `hazard_id: VARCHAR`
- `chemicals` — (very wide) `id: INTEGER (PK)`, `name: VARCHAR`, `description: TEXT`, `health_haz: TEXT`, `first_aid: TEXT`, `fire_haz: TEXT`, `fire_fight: TEXT`, `non_fire_resp: TEXT`, `prot_clothing: TEXT`, `air_water_reactions: TEXT`, `chemical_profile: TEXT`, `special_hazards: TEXT`, `isolation: TEXT`, `niosh: VARCHAR`, `niosh_file: VARCHAR`, `nfpa_source: VARCHAR`, `nfpa_note: VARCHAR`, `nfpa_flam: INTEGER`, `nfpa_health: INTEGER`, `nfpa_react: INTEGER`, `nfpa_special: TEXT`, `fp_source: VARCHAR`, `fp_note: VARCHAR`, `fp_value: FLOAT`, `fp_range: VARCHAR`, `lel_source: VARCHAR`, `lel_note: VARCHAR`, `lel_value: FLOAT`, `lel_range: VARCHAR`, `lel_unit: VARCHAR`, `uel_source: VARCHAR`, `uel_note: VARCHAR`, `uel_value: FLOAT`, `uel_range: VARCHAR`, `uel_unit: VARCHAR`, `ai_source: VARCHAR`, `ai_note: VARCHAR`, `ai_value: FLOAT`, `ai_range: VARCHAR`, `mp_source: VARCHAR`, `mp_note: VARCHAR`, `mp_value: FLOAT`, `mp_range: VARCHAR`, `vp_source: VARCHAR`, `vp_note: VARCHAR`, `vp_value: FLOAT`, `vp_range: VARCHAR`, `vp_value_tempDegF: FLOAT`, `vp_range_tempDegF: VARCHAR`, `vp_unit: VARCHAR`, `vd_source: VARCHAR`, `vd_note: VARCHAR`, `vd_value: FLOAT`, `vd_range: VARCHAR`, `vd_value_tempDegF: FLOAT`, `vd_range_tempDegF: VARCHAR`, `sg_source: VARCHAR`, `sg_note: VARCHAR`, `sg_value: FLOAT`, `sg_range: VARCHAR`, `sg_value_tempDegF: FLOAT`, `sg_range_tempDegF: VARCHAR`, `bp_source: VARCHAR`, `bp_note: VARCHAR`, `bp_value: FLOAT`, `bp_range: VARCHAR`, `bp_value_presMMHG: FLOAT`, `bp_range_presMMHG: VARCHAR`, `molwgt_source: VARCHAR`, `molwgt_note: VARCHAR`, `molwgt_value: FLOAT`, `molwgt_range: VARCHAR`, `idlh_source: VARCHAR`, `idlh_note: VARCHAR`, `idlh_value: FLOAT`, `idlh_unit: VARCHAR`, `solblty_source: VARCHAR`, `solblty_note: VARCHAR`, `solblty_value: FLOAT`, `solblty_range: VARCHAR`, `solblty_unit: VARCHAR`, `ion_source: VARCHAR`, `ion_note: VARCHAR`, `ion_value: FLOAT`, `response_guide_for_chemical_warfare_agent: INTEGER`, `synonyms: TEXT`, `chris_codes: TEXT`, `dot_labels: TEXT`, `formulas: TEXT`, `incompatible_absorbents: TEXT`, `psm: TEXT`
- `chemical_search` — `id: INTEGER (PK)`, `is_aloha: BOOLEAN`, `is_dupont: BOOLEAN`, `is_cfats: BOOLEAN`, `is_icsc: BOOLEAN`, `is_ehs_tpq: BOOLEAN`, `is_ehs_rq: BOOLEAN`, `is_cercla_rq: BOOLEAN`, `is_section_313_notes: BOOLEAN`, `is_caa_rq: BOOLEAN`, `regulatory_names: TEXT`, `rcra_codes: TEXT`, `loc_title: VARCHAR`, `loc_value: FLOAT`, `loc_unit: VARCHAR`
- `chemical_cas` — `chem_id: INTEGER (PK)`, `cas_id: VARCHAR (PK)`, `cas_nodash: VARCHAR`, `sort: INTEGER`, `annotation: VARCHAR`
- `chemical_unna` — `chem_id: INTEGER (PK)`, `unna_id: INTEGER (PK)`, `sort: INTEGER`, `annotation: VARCHAR`
- `chemical_icsc` — `id: INTEGER (PK)`, `cas_id: VARCHAR`, `name: VARCHAR`, `synonyms: VARCHAR`, `release_min_conc: VARCHAR`, `release_stq: VARCHAR`, `release_security: VARCHAR`, `theft_min_conc: VARCHAR`, `theft_stq: VARCHAR`, `theft_security: VARCHAR`, `sabotage_min_conc: VARCHAR`, `sabotage_stq: VARCHAR`, `sabotage_security: VARCHAR`
- `chemical_lol` — `id: INTEGER (PK)`, `name: VARCHAR`, `name_footnote_key: VARCHAR`, `name_with_footnote: VARCHAR`, `cas_313code: VARCHAR`, `ehs_tpq: VARCHAR`, `ehs_rq: VARCHAR`, `cercla_rq: VARCHAR`, `section_313_notes: VARCHAR`, `rcra_code: VARCHAR`, `caa_rq: VARCHAR`
- `chemical_cfats` — `id: INTEGER (PK)`, `cas_id: VARCHAR`, `name: VARCHAR`, `synonyms: VARCHAR`, `release_min_conc: VARCHAR`, `release_stq: VARCHAR`, `release_security: VARCHAR`, `theft_min_conc: VARCHAR`, `theft_stq: VARCHAR`, `theft_security: VARCHAR`, `sabotage_min_conc: VARCHAR`, `sabotage_stq: VARCHAR`, `sabotage_security: VARCHAR`
- `chemical_aegl` — `cas_id: VARCHAR (PK)`, `aloha_name: VARCHAR`
- `dupont` — `id: INTEGER (PK)`, `cas_id: VARCHAR`, `chemical: VARCHAR`, `state: VARCHAR`, `qs: VARCHAR`, `qc: VARCHAR`, `sl: VARCHAR`, `c3: VARCHAR`, `tf: VARCHAR`, `tp: VARCHAR`, `rc: VARCHAR`, `tk: VARCHAR`, `rf: VARCHAR`
- `aloha` — `cas_id: VARCHAR (PK)`, `aloha_name: VARCHAR`
- `lol` — `id: INTEGER (PK)`, `name: VARCHAR`, `name_footnote_key: VARCHAR`, `name_with_footnote: VARCHAR`, `cas_313code: VARCHAR`, `ehs_tpq: VARCHAR`, `ehs_rq: VARCHAR`, `cercla_rq: VARCHAR`, `section_313_notes: VARCHAR`, `rcra_code: VARCHAR`, `caa_rq: VARCHAR`
- `cfats` — `id: INTEGER (PK)`, `cas_id: VARCHAR`, `name: VARCHAR`, `synonyms: VARCHAR`, `release_min_conc: VARCHAR`, `release_stq: VARCHAR`, `release_security: VARCHAR`, `theft_min_conc: VARCHAR`, `theft_stq: VARCHAR`, `theft_security: VARCHAR`, `sabotage_min_conc: VARCHAR`, `sabotage_stq: VARCHAR`, `sabotage_security: VARCHAR`
- `aegls` — `id: INTEGER (PK)`, `cas_id: VARCHAR`, `csv_id: VARCHAR`, `name: VARCHAR`, `name_note: VARCHAR`, `source: VARCHAR`, `unit: VARCHAR`, `footnotes: TEXT`, `status: VARCHAR`, `aegl1_10min_value: FLOAT`, `aegl1_10min_note: VARCHAR`, `aegl1_30min_value: FLOAT`, `aegl1_30min_note: VARCHAR`, `aegl1_60min_value: FLOAT`, `aegl1_60min_note: VARCHAR`, `aegl1_4hr_value: FLOAT`, `aegl1_4hr_note: VARCHAR`, `aegl1_8hr_value: FLOAT`, `aegl1_8hr_note: VARCHAR`, `aegl2_10min_value: FLOAT`, `aegl2_10min_note: VARCHAR`, `aegl2_30min_value: FLOAT`, `aegl2_30min_note: VARCHAR`, `aegl2_60min_value: FLOAT`, `aegl2_60min_note: VARCHAR`, `aegl2_4hr_value: FLOAT`, `aegl2_4hr_note: VARCHAR`, `aegl2_8hr_value: FLOAT`, `aegl2_8hr_note: VARCHAR`, `aegl3_10min_value: FLOAT`, `aegl3_10min_note: VARCHAR`, `aegl3_30min_value: FLOAT`, `aegl3_30min_note: VARCHAR`, `aegl3_60min_value: FLOAT`, `aegl3_60min_note: VARCHAR`, `aegl3_4hr_value: FLOAT`, `aegl3_4hr_note: VARCHAR`, `aegl3_8hr_value: FLOAT`, `aegl3_8hr_note: VARCHAR`
- `erpgs` — `id: INTEGER (PK)`, `cas_id: VARCHAR`, `csv_id: VARCHAR`, `name: VARCHAR`, `name_note: VARCHAR`, `source: VARCHAR`, `unit: VARCHAR`, `lel_value_ppm: FLOAT`, `erpg1_value: FLOAT`, `erpg1_note: VARCHAR`, `erpg2_value: FLOAT`, `erpg2_note: VARCHAR`, `erpg3_value: FLOAT`, `erpg3_note: VARCHAR`
- `pacs` — `id: INTEGER (PK)`, `cas_id: VARCHAR`, `csv_id: VARCHAR`, `name: VARCHAR`, `source: VARCHAR`, `unit: VARCHAR`, `lel_value_ppm: FLOAT`, `pac1_value: FLOAT`, `pac1_note: VARCHAR`, `pac2_value: FLOAT`, `pac2_note: VARCHAR`, `pac3_value: FLOAT`, `pac3_note: VARCHAR`
- `mm_chemical_react` — `chem_id: INTEGER`, `react_id: INTEGER`
- `mm_chemical_hc` — `chem_id: INTEGER`, `react_id: INTEGER`
- `mm_chemical_lol` — `chem_id: INTEGER`, `lol_id: INTEGER`
- `mm_chemical_cfats` — `chem_id: INTEGER`, `cfats_id: INTEGER`
- `mm_chemical_aegl` — `chem_id: INTEGER`, `aegl_id: INTEGER`
