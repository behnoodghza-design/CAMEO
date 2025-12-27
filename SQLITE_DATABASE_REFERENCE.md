# CAMEO Chemicals SQLite Database Reference
**Complete Technical Documentation**  
Version: 3.1.0 | Import Date: 2024-05-16  
Document Status: Comprehensive Reference

---

## Table of Contents
1. [Overview](#overview)
2. [Connection & Configuration](#connection--configuration)
3. [Database Architecture](#database-architecture)
4. [Core Tables](#core-tables)
5. [Mapping Tables](#mapping-tables)
6. [Reference Data Tables](#reference-data-tables)
7. [Relationships & Data Model](#relationships--data-model)
8. [Query Patterns & Examples](#query-patterns--examples)
9. [Performance Considerations](#performance-considerations)
10. [Best Practices](#best-practices)

---

## Overview

### Database Purpose
The `cameo.sqlite` database contains comprehensive hazardous chemical data for emergency response, including:
- 5,094 chemical records with physical properties, hazards, and response guidance
- 80 reactive groups for compatibility prediction
- Exposure limits (AEGL, ERPG, PAC)
- Regulatory data (CFATS, LOL, CERCLA)
- UN/NA identification and ERG guides

### Key Statistics
- **Chemicals**: 5,094 records
- **CAS Mappings**: 4,942 entries
- **UN/NA Mappings**: 3,850 entries
- **Reactive Groups**: 80 groups
- **Reactivity Rules**: 2,346 pair rules
- **AEGL Values**: 259 chemicals
- **ERPG Values**: 143 chemicals
- **PAC Values**: 1,774 chemicals

---

## Connection & Configuration

### MCP Configuration
```json
{
  "sqlite": {
    "command": "docker",
    "args": [
      "run", "-i", "--rm",
      "-v", "C:/Users/aminh/OneDrive/Desktop/CAMEO/CAMEO/data:/data",
      "mcp/sqlite",
      "--db-path", "/data/cameo.sqlite"
    ]
  }
}
```

### Database Location
- **Path**: `data/cameo.sqlite`
- **Size**: ~33.3 MB
- **Access**: Read-only (static reference data)

---

## Database Architecture

### Table Categories

#### 1. Core Chemical Data
- `chemicals` — Master chemical records (5,094)
- `chemical_search` — Search-optimized index (5,094)

#### 2. Identity Mappings
- `chemical_cas` — CAS number mappings (4,942)
- `chemical_unna` — UN/NA number mappings (3,850)
- `chemical_icsc` — ICSC identifiers

#### 3. Exposure Limits
- `aegls` — Acute Exposure Guideline Levels (259)
- `erpgs` — Emergency Response Planning Guidelines (143)
- `pacs` — Protective Action Criteria (1,774)

#### 4. Reactivity System
- `reacts` — Reactive group definitions (80)
- `reactivity` — Group-pair compatibility rules (2,346)
- `mm_reactivity_hazard` — Hazard category links (4,178)
- `hazards` — Hazard categories (12)

#### 5. Regulatory Data
- `lol` — List of Lists (1,709)
- `cfats` — CFATS chemicals (325)
- `dupont` — DuPont data (719)
- `aloha` — ALOHA-compatible chemicals

#### 6. Emergency Response
- `unnas` — UN/NA records (2,371)
- `erg_guides` — ERG guide numbers (64)
- `unna_cfr49s` — CFR 49 hazard classifications
- `unna_waterreactions` — Water reaction data
- `unna_actiondistances` — Isolation distances
- `unna_table3` — Protective action distances

#### 7. Many-to-Many Junctions
- `mm_chemical_react` — Chemicals ↔ Reactive groups (9,231)
- `mm_chemical_hc` — Chemicals ↔ Hazard codes (3,193)
- `mm_chemical_lol` — Chemicals ↔ LOL entries
- `mm_chemical_cfats` — Chemicals ↔ CFATS entries
- `mm_chemical_aegl` — Chemicals ↔ AEGL entries
- `mm_unna_erg_guide` — UN/NA ↔ ERG guides

#### 8. Metadata
- `info` — Database version & import date (1)
- `sources` — Data source annotations
- `notes` — Reference notes

---

## Core Tables

### `chemicals` (5,094 records)
**Purpose**: Master chemical data with comprehensive properties and response guidance.

**Schema**:
```
id                  INTEGER (PK)
name                VARCHAR        -- Primary chemical name
description         TEXT           -- Brief description

-- Hazard & Response
health_haz          TEXT
first_aid           TEXT
fire_haz            TEXT
fire_fight          TEXT
non_fire_resp       TEXT
prot_clothing       TEXT
air_water_reactions TEXT
chemical_profile    TEXT
special_hazards     TEXT
isolation           TEXT

-- NFPA Diamond
nfpa_source         VARCHAR
nfpa_note           VARCHAR
nfpa_flam           INTEGER        -- 0-4
nfpa_health         INTEGER        -- 0-4
nfpa_react          INTEGER        -- 0-4
nfpa_special        TEXT           -- W, OX, etc.

-- Physical Properties (each has: source, note, value, range, unit/temp fields)
fp_*                               -- Flash Point
lel_*                              -- Lower Explosive Limit
uel_*                              -- Upper Explosive Limit
ai_*                               -- Autoignition Temperature
mp_*                               -- Melting Point
vp_*                               -- Vapor Pressure
vd_*                               -- Vapor Density
sg_*                               -- Specific Gravity
bp_*                               -- Boiling Point
molwgt_*                           -- Molecular Weight
idlh_*                             -- IDLH (Immediately Dangerous to Life/Health)
solblty_*                          -- Solubility
ion_*                              -- Ionization Potential

-- Identifiers & Lists
niosh               VARCHAR
niosh_file          VARCHAR
synonyms            TEXT           -- JSON/delimited list
chris_codes         TEXT
dot_labels          TEXT
formulas            TEXT
incompatible_absorbents TEXT

-- Flags
response_guide_for_chemical_warfare_agent  INTEGER
psm                 TEXT
```

**Sample Data**:
```
id=2,   name='ACETAL'
id=8,   name='ACETONE'
id=10,  name='ACETONE OILS'
```

---

### `chemical_search` (5,094 records)
**Purpose**: Fast search index with regulatory flags and location data.

**Schema**:
```
id                   INTEGER (PK)

-- Regulatory Flags
is_aloha             BOOLEAN
is_dupont            BOOLEAN
is_cfats             BOOLEAN
is_icsc              BOOLEAN
is_ehs_tpq           BOOLEAN
is_ehs_rq            BOOLEAN
is_cercla_rq         BOOLEAN
is_section_313_notes BOOLEAN
is_caa_rq            BOOLEAN

-- Regulatory Text
regulatory_names     TEXT
rcra_codes           TEXT

-- Location Data
loc_title            VARCHAR
loc_value            FLOAT
loc_unit             VARCHAR
```

**Usage**: Use for filtering chemicals by regulatory status or full-text search (if FTS5 enabled).

---

### `reacts` (80 records)
**Purpose**: Reactive group definitions for compatibility prediction.

**Schema**:
```
id              INTEGER (PK)
name            VARCHAR        -- e.g., "Acids, Strong Non-oxidizing"
special         BOOLEAN        -- Special handling flag
description     TEXT
flammability    TEXT
reactivity      TEXT
toxicity        TEXT
characteristics TEXT
examples        TEXT           -- Example chemicals in this group
```

**Sample Data**:
```
id=1, name='Acids, Strong Non-oxidizing'
id=2, name='Acids, Strong Oxidizing'
id=3, name='Acids, Carboxylic'
id=4, name='Alcohols and Polyols'
id=5, name='Aldehydes'
```

---

### `reactivity` (2,346 records)
**Purpose**: Defines compatibility and hazards when two reactive groups interact.

**Schema**:
```
react1                INTEGER (PK part)  -- Reactive group 1 ID
react2                INTEGER (PK part)  -- Reactive group 2 ID
gas_products          TEXT               -- Gases produced
pair_compatibility    TEXT               -- Compatibility assessment
hazards_documentation TEXT               -- Detailed hazard description
```

**Usage**: Look up `(react1, react2)` to get interaction hazards. Combine with `mm_reactivity_hazard` for hazard categories.

---

### `hazards` (12 records)
**Purpose**: Hazard category definitions.

**Schema**:
```
id       VARCHAR (PK)  -- C, E, F, G, NR, R1-R4, T, UR, X
name     VARCHAR       -- Full hazard description
phrases  TEXT          -- Short phrase
```

**Complete List**:
```
C   - Reaction products may be corrosive (Corrosive)
E   - Reaction products may be explosive or sensitive to shock or friction (Explosive)
F   - Reaction products may be flammable (Flammable)
G   - Reaction liberates gaseous products and may cause pressurization (Generates gas)
NR  - No known hazardous reaction
R1  - Exothermic reaction at ambient temperatures (Generates heat)
R2  - Reaction products may be unstable above ambient temperatures (Unstable when heated)
R3  - Reaction may be particularly intense, violent, or explosive (Intense or explosive reaction)
R4  - Polymerization reaction may become intense and may cause pressurization (Polymerization hazard)
T   - Reaction products may be toxic (Toxic)
UR  - May be hazardous but unknown (Potentially hazardous)
X   - Possible exposure to radiation (Radiation)
```

---

### `aegls` (259 records)
**Purpose**: Acute Exposure Guideline Levels for various exposure durations.

**Schema**:
```
id                INTEGER (PK)
cas_id            VARCHAR
csv_id            VARCHAR
name              VARCHAR
name_note         VARCHAR
source            VARCHAR
unit              VARCHAR
footnotes         TEXT
status            VARCHAR

-- AEGL-1 (Discomfort/irritation)
aegl1_10min_value FLOAT
aegl1_10min_note  VARCHAR
aegl1_30min_value FLOAT
aegl1_30min_note  VARCHAR
aegl1_60min_value FLOAT
aegl1_60min_note  VARCHAR
aegl1_4hr_value   FLOAT
aegl1_4hr_note    VARCHAR
aegl1_8hr_value   FLOAT
aegl1_8hr_note    VARCHAR

-- AEGL-2 (Irreversible/serious effects)
aegl2_10min_value FLOAT
aegl2_10min_note  VARCHAR
... (similar pattern)

-- AEGL-3 (Life-threatening effects)
aegl3_10min_value FLOAT
aegl3_10min_note  VARCHAR
... (similar pattern)
```

---

### `erpgs` (143 records)
**Purpose**: Emergency Response Planning Guidelines.

**Schema**:
```
id            INTEGER (PK)
cas_id        VARCHAR
csv_id        VARCHAR
name          VARCHAR
name_note     VARCHAR
source        VARCHAR
unit          VARCHAR
lel_value_ppm FLOAT

erpg1_value   FLOAT        -- Mild, reversible effects
erpg1_note    VARCHAR
erpg2_value   FLOAT        -- Irreversible/serious effects
erpg2_note    VARCHAR
erpg3_value   FLOAT        -- Life-threatening effects
erpg3_note    VARCHAR
```

---

### `pacs` (1,774 records)
**Purpose**: Protective Action Criteria for exposure planning.

**Schema**:
```
id            INTEGER (PK)
cas_id        VARCHAR
csv_id        VARCHAR
name          VARCHAR
source        VARCHAR
unit          VARCHAR
lel_value_ppm FLOAT

pac1_value    FLOAT        -- Mild/transient effects
pac1_note     VARCHAR
pac2_value    FLOAT        -- Irreversible/escape impaired
pac2_note     VARCHAR
pac3_value    FLOAT        -- Life-threatening effects
pac3_note     VARCHAR
```

---

## Mapping Tables

### `chemical_cas` (4,942 records)
**Purpose**: Maps chemicals to CAS Registry Numbers.

**Schema**:
```
chem_id     INTEGER (PK)   -- FK to chemicals.id
cas_id      VARCHAR (PK)   -- CAS number (format: XXXXX-XX-X)
cas_nodash  VARCHAR        -- CAS without dashes
sort        INTEGER        -- Sort order (for multiple CAS per chemical)
annotation  VARCHAR        -- Notes/qualifiers
```

**Usage**: Join `chemicals.id = chemical_cas.chem_id` to get CAS numbers.

---

### `chemical_unna` (3,850 records)
**Purpose**: Maps chemicals to UN/NA identification numbers.

**Schema**:
```
chem_id     INTEGER (PK)   -- FK to chemicals.id
unna_id     INTEGER (PK)   -- FK to unnas.id
sort        INTEGER
annotation  VARCHAR
```

---

### `mm_chemical_react` (9,231 records)
**Purpose**: Maps chemicals to their assigned reactive groups.

**Schema**:
```
chem_id   INTEGER   -- FK to chemicals.id
react_id  INTEGER   -- FK to reacts.id
```

**Usage**: A chemical can belong to multiple reactive groups. Use this to resolve chemical → groups for reactivity checking.

---

### `mm_reactivity_hazard` (4,178 records)
**Purpose**: Links reactive group pairs to hazard categories.

**Schema**:
```
react1     INTEGER   -- FK to reacts.id
react2     INTEGER   -- FK to reacts.id
hazard_id  VARCHAR   -- FK to hazards.id (C, E, F, G, etc.)
```

**Usage**: After looking up `reactivity(react1, react2)`, use this table to get all hazard categories (multiple rows possible per pair).

---

### Other Mapping Tables
- `mm_chemical_hc` (3,193) — Chemicals ↔ Hazard codes
- `mm_chemical_lol` — Chemicals ↔ LOL entries
- `mm_chemical_cfats` — Chemicals ↔ CFATS entries
- `mm_chemical_aegl` — Chemicals ↔ AEGL entries
- `mm_unna_erg_guide` — UN/NA ↔ ERG guide numbers

---

## Reference Data Tables

### `unnas` (2,371 records)
**Purpose**: UN/NA identification records.

**Schema**:
```
id          INTEGER (PK)
faux        BOOLEAN        -- Pseudo/synthetic entry
active      BOOLEAN        -- Currently in use
polimerize  BOOLEAN        -- Polymerization risk
synonyms    TEXT
materials   TEXT           -- Associated materials
```

---

### `erg_guides` (64 records)
**Purpose**: Emergency Response Guidebook guide numbers.

**Schema**:
```
id        INTEGER (PK)
title_en  VARCHAR        -- English title
title_es  VARCHAR        -- Spanish title
title_fr  VARCHAR        -- French title
```

---

### `unna_cfr49s` (varies)
**Purpose**: 49 CFR 172.101 Hazardous Materials Table data.

**Schema**:
```
id            INTEGER (PK)
unna_id       INTEGER       -- FK to unnas.id
name          TEXT
unna_type     VARCHAR       -- UN or NA
hazard_class  VARCHAR       -- DOT hazard class
labels        TEXT          -- DOT labels required
notes         TEXT
provision     TEXT          -- Special provisions
packing_group VARCHAR       -- I, II, III
```

---

### `unna_waterreactions`
**Purpose**: Water reactivity data for UN/NA materials.

**Schema**:
```
id          INTEGER (PK)
unna_id     INTEGER
gas_name    VARCHAR        -- Gas produced
gas_formula VARCHAR
```

---

### `unna_actiondistances`
**Purpose**: Initial isolation and protective action distances.

**Schema**:
```
id                        INTEGER (PK)
unna_id                   INTEGER
name                      VARCHAR
small_isolate_feet        VARCHAR
small_protect_day_miles   VARCHAR
small_protect_night_miles VARCHAR
large_isolate_feet        VARCHAR
large_protect_day_miles   VARCHAR
large_protect_night_miles VARCHAR
```

---

### `unna_table3`
**Purpose**: Water-reactive materials protective action distances (ERG Table 3).

**Schema**:
```
id                    INTEGER (PK)
unna_id               INTEGER
sort                  INTEGER
title                 VARCHAR
container             VARCHAR
isolate_feet          VARCHAR
day_low_miles         VARCHAR
day_moderate_miles    VARCHAR
day_high_miles        VARCHAR
night_low_miles       VARCHAR
night_moderate_miles  VARCHAR
night_high_miles      VARCHAR
```

---

### `lol` (1,709 records)
**Purpose**: Consolidated "List of Lists" for regulated chemicals.

**Schema**:
```
id                   INTEGER (PK)
name                 VARCHAR
name_footnote_key    VARCHAR
name_with_footnote   VARCHAR
cas_313code          VARCHAR
ehs_tpq              VARCHAR        -- Threshold Planning Quantity
ehs_rq               VARCHAR        -- Reportable Quantity
cercla_rq            VARCHAR        -- CERCLA RQ
section_313_notes    VARCHAR
rcra_code            VARCHAR
caa_rq               VARCHAR        -- Clean Air Act RQ
```

---

### `cfats` (325 records)
**Purpose**: Chemical Facility Anti-Terrorism Standards data.

**Schema**:
```
id                 INTEGER (PK)
cas_id             VARCHAR
name               VARCHAR
synonyms           VARCHAR
release_min_conc   VARCHAR        -- Release hazard
release_stq        VARCHAR        -- Screening Threshold Quantity
release_security   VARCHAR
theft_min_conc     VARCHAR        -- Theft/diversion hazard
theft_stq          VARCHAR
theft_security     VARCHAR
sabotage_min_conc  VARCHAR        -- Sabotage hazard
sabotage_stq       VARCHAR
sabotage_security  VARCHAR
```

---

### `dupont` (719 records)
**Purpose**: DuPont chemical compatibility/hazard data.

**Schema**:
```
id       INTEGER (PK)
cas_id   VARCHAR
chemical VARCHAR
state    VARCHAR
qs       VARCHAR
qc       VARCHAR
sl       VARCHAR
c3       VARCHAR
tf       VARCHAR
tp       VARCHAR
rc       VARCHAR
tk       VARCHAR
rf       VARCHAR
```

---

### `aloha`
**Purpose**: Maps CAS numbers to ALOHA-compatible chemical names.

**Schema**:
```
cas_id      VARCHAR (PK)
aloha_name  VARCHAR
```

---

### Metadata Tables

#### `info` (1 record)
```
version      VARCHAR (PK)   -- "3.1.0"
import_date  DATETIME       -- "2024-05-16 18:54:53.623600"
```

#### `sources`
```
source    VARCHAR (PK)
symbol    VARCHAR (PK)
fieldname VARCHAR
sort      INTEGER
note      VARCHAR
```

#### `notes`
```
id      VARCHAR (PK)
source  VARCHAR
```

---

## Relationships & Data Model

### Entity-Relationship Overview

```
chemicals (1) ──┬─→ (N) chemical_cas → cas_id
                ├─→ (N) chemical_unna → unnas
                ├─→ (N) mm_chemical_react → reacts
                ├─→ (N) mm_chemical_hc
                ├─→ (N) mm_chemical_lol → lol
                ├─→ (N) mm_chemical_cfats → cfats
                └─→ (N) mm_chemical_aegl → aegls

reacts (1) ──→ (N) mm_chemical_react ──→ (1) chemicals
           └─→ (N) reactivity (react1, react2)
                  └─→ (N) mm_reactivity_hazard → hazards

unnas (1) ──┬─→ (N) chemical_unna
            ├─→ (N) mm_unna_erg_guide → erg_guides
            ├─→ (N) unna_cfr49s
            ├─→ (N) unna_waterreactions
            ├─→ (N) unna_actiondistances
            └─→ (N) unna_table3

aegls, erpgs, pacs ──→ cas_id (join via chemical_cas)
```

### Key Relationships

1. **Chemical Identity**
   - `chemicals.id` is the primary key
   - Join `chemical_cas` for CAS numbers
   - Join `chemical_unna` for UN/NA numbers

2. **Reactivity Prediction**
   - `chemicals` → `mm_chemical_react` → `reacts` (get all groups for a chemical)
   - For each pair of groups: `reactivity(react1, react2)`
   - Get hazards: `mm_reactivity_hazard` → `hazards`

3. **Exposure Limits**
   - Link via CAS: `chemical_cas.cas_id` = `aegls.cas_id`
   - Similarly for `erpgs` and `pacs`

4. **Regulatory Data**
   - Use `mm_chemical_lol`, `mm_chemical_cfats` junction tables
   - Or search `chemical_search` flags

5. **Emergency Response**
   - `chemical_unna` → `unnas` → `mm_unna_erg_guide` → `erg_guides`
   - `unnas` → `unna_actiondistances` for isolation zones

---

## Query Patterns & Examples

### 1. Search Chemical by Name
```sql
-- Simple search
SELECT id, name, description
FROM chemicals
WHERE name LIKE '%ACETONE%'
ORDER BY name;

-- With CAS numbers
SELECT c.id, c.name, cc.cas_id
FROM chemicals c
LEFT JOIN chemical_cas cc ON c.id = cc.chem_id
WHERE c.name LIKE '%ACETONE%'
ORDER BY cc.sort;
```

### 2. Search by CAS Number
```sql
SELECT c.id, c.name, cc.cas_id
FROM chemicals c
INNER JOIN chemical_cas cc ON c.id = cc.chem_id
WHERE cc.cas_id = '67-64-1'  -- Acetone
   OR cc.cas_nodash = '67641';
```

### 3. Search by UN Number
```sql
SELECT c.id, c.name, u.id AS unna_id
FROM chemicals c
INNER JOIN chemical_unna cu ON c.id = cu.chem_id
INNER JOIN unnas u ON cu.unna_id = u.id
WHERE u.id = 1090;  -- Example UN1090
```

### 4. Get Chemical Detail (Full Record)
```sql
SELECT *
FROM chemicals
WHERE id = 8;  -- ACETONE
```

### 5. Get All CAS Numbers for a Chemical
```sql
SELECT cas_id, sort, annotation
FROM chemical_cas
WHERE chem_id = 8
ORDER BY sort;
```

### 6. Get Reactive Groups for a Chemical
```sql
SELECT r.id, r.name, r.description
FROM mm_chemical_react mcr
INNER JOIN reacts r ON mcr.react_id = r.id
WHERE mcr.chem_id = 8
ORDER BY r.name;
```

### 7. Check Reactivity Between Two Groups
```sql
-- Get compatibility info
SELECT react1, react2, pair_compatibility, gas_products, hazards_documentation
FROM reactivity
WHERE (react1 = 1 AND react2 = 5)
   OR (react1 = 5 AND react2 = 1);

-- Get hazard categories
SELECT h.id, h.name, h.phrases
FROM mm_reactivity_hazard mrh
INNER JOIN hazards h ON mrh.hazard_id = h.id
WHERE (mrh.react1 = 1 AND mrh.react2 = 5)
   OR (mrh.react1 = 5 AND mrh.react2 = 1);
```

### 8. Multi-Chemical Reactivity Check
```sql
-- Step 1: Get all reactive groups for chemicals 8, 10, 15
WITH chem_groups AS (
  SELECT mcr.chem_id, r.id AS react_id, r.name AS react_name
  FROM mm_chemical_react mcr
  INNER JOIN reacts r ON mcr.react_id = r.id
  WHERE mcr.chem_id IN (8, 10, 15)
)
-- Step 2: Generate all pairs and look up reactivity
SELECT
  cg1.chem_id AS chem1,
  cg2.chem_id AS chem2,
  cg1.react_name AS group1,
  cg2.react_name AS group2,
  rx.pair_compatibility,
  rx.gas_products
FROM chem_groups cg1
CROSS JOIN chem_groups cg2
LEFT JOIN reactivity rx
  ON (cg1.react_id = rx.react1 AND cg2.react_id = rx.react2)
  OR (cg1.react_id = rx.react2 AND cg2.react_id = rx.react1)
WHERE cg1.chem_id < cg2.chem_id
ORDER BY cg1.chem_id, cg2.chem_id;
```

### 9. Get AEGL Values
```sql
SELECT name, unit, 
       aegl1_10min_value, aegl1_30min_value, aegl1_60min_value,
       aegl2_10min_value, aegl2_30min_value, aegl2_60min_value,
       aegl3_10min_value, aegl3_30min_value, aegl3_60min_value
FROM aegls
WHERE cas_id = '67-64-1';  -- Join via chemical_cas if starting from chem_id
```

### 10. Get ERPG Values
```sql
SELECT name, unit, erpg1_value, erpg2_value, erpg3_value
FROM erpgs
WHERE cas_id = '67-64-1';
```

### 11. Get PAC Values
```sql
SELECT name, unit, pac1_value, pac2_value, pac3_value
FROM pacs
WHERE cas_id = '67-64-1';
```

### 12. Get ERG Guide Number
```sql
SELECT eg.id, eg.title_en
FROM chemicals c
INNER JOIN chemical_unna cu ON c.id = cu.chem_id
INNER JOIN mm_unna_erg_guide meg ON cu.unna_id = meg.unna_id
INNER JOIN erg_guides eg ON meg.erg_guide_id = eg.id
WHERE c.id = 8;
```

### 13. Get Isolation Distances
```sql
SELECT ua.name,
       ua.small_isolate_feet,
       ua.small_protect_day_miles,
       ua.large_protect_night_miles
FROM chemicals c
INNER JOIN chemical_unna cu ON c.id = cu.chem_id
INNER JOIN unna_actiondistances ua ON cu.unna_id = ua.unna_id
WHERE c.id = 8;
```

### 14. Filter Chemicals by Regulatory Status
```sql
-- CFATS chemicals only
SELECT c.id, c.name
FROM chemicals c
INNER JOIN chemical_search cs ON c.id = cs.id
WHERE cs.is_cfats = 1;

-- Multiple flags
SELECT c.id, c.name
FROM chemicals c
INNER JOIN chemical_search cs ON c.id = cs.id
WHERE cs.is_aloha = 1
  AND cs.is_dupont = 1;
```

### 15. Get NFPA Diamond
```sql
SELECT name,
       nfpa_health,
       nfpa_flam,
       nfpa_react,
       nfpa_special,
       nfpa_source
FROM chemicals
WHERE id = 8;
```

### 16. Get Physical Properties
```sql
SELECT name,
       fp_value AS flash_point_f,
       bp_value AS boiling_point_f,
       mp_value AS melting_point_f,
       molwgt_value AS molecular_weight,
       sg_value AS specific_gravity,
       vp_value AS vapor_pressure,
       solblty_value AS solubility
FROM chemicals
WHERE id = 8;
```

### 17. Database Integrity Check
```sql
-- Verify version
SELECT version, import_date FROM info;

-- Check record counts
SELECT 'chemicals' AS tbl, COUNT(*) AS cnt FROM chemicals
UNION ALL
SELECT 'reacts', COUNT(*) FROM reacts
UNION ALL
SELECT 'reactivity', COUNT(*) FROM reactivity
UNION ALL
SELECT 'hazards', COUNT(*) FROM hazards;
```

### 18. Get All Hazard Categories
```sql
SELECT id, name, phrases
FROM hazards
ORDER BY id;
```

---

## Performance Considerations

### Indexing Strategy
- **Primary Keys**: All tables have PKs auto-indexed
- **Foreign Keys**: Junction tables should have indexes on both FK columns
- **Search Fields**: `chemicals.name`, `chemical_cas.cas_id`, `chemical_unna.unna_id` should be indexed
- **FTS (Full-Text Search)**: Verify if `chemical_search` uses FTS5 for fast text search

### Query Optimization Tips
1. **Use Specific Columns**: Avoid `SELECT *` in production; list only needed columns
2. **Index Lookups**: Search by `id`, `cas_id`, or indexed fields first
3. **Join Order**: Start with most selective table (usually `chemicals` by id)
4. **Batch Operations**: Use `IN (...)` for multiple IDs instead of loops
5. **Limit Results**: Always use `LIMIT` for exploratory queries

### Memory & Cache
- Database size: ~33 MB → fits easily in memory
- Use connection pooling if possible
- Consider read-only mode (`PRAGMA query_only = ON`) for safety

---

## Best Practices

### For Development

#### 1. Always Start with Validation
```sql
-- Ensure database is loaded
SELECT version FROM info;
```

#### 2. Use Consistent ID Resolution
```sql
-- CAS → Chemical ID
WITH chem_from_cas AS (
  SELECT chem_id FROM chemical_cas WHERE cas_id = '67-64-1'
)
SELECT c.* FROM chemicals c
WHERE c.id = (SELECT chem_id FROM chem_from_cas);
```

#### 3. Handle Multiple Mappings
```sql
-- A chemical may have multiple CAS numbers
-- Always ORDER BY sort and handle as array in application layer
SELECT cas_id FROM chemical_cas WHERE chem_id = 8 ORDER BY sort;
```

#### 4. Reactivity Workflow
```
User Input: [chem_id1, chem_id2, ...]
  ↓
Resolve to reactive groups: mm_chemical_react
  ↓
Generate all unique group pairs
  ↓
For each pair: Look up reactivity + mm_reactivity_hazard
  ↓
Aggregate hazards and present compatibility matrix
```

#### 5. Exposure Limit Fallback
```
Try AEGL → if null, try ERPG → if null, try PAC → if null, show "No data"
```

#### 6. Defensive NULL Handling
```sql
-- Many fields are nullable; use COALESCE or check in application
SELECT COALESCE(nfpa_health, -1) AS health_rating FROM chemicals WHERE id = 8;
```

### For Production

#### 1. Read-Only Access
- Mount database as read-only
- Use separate `user.db` for favorites/history/settings

#### 2. Error Handling
- Catch "no such table" → database not loaded
- Catch "database locked" → connection issue
- Validate all user inputs (CAS format, UN number range)

#### 3. Data Integrity
- On startup: verify `info.version = '3.1.0'`
- Periodically: check critical table counts > 0

#### 4. User Experience
- Cache frequently accessed data (e.g., hazard categories)
- Pre-load reactive groups on app start
- Use async queries for large JOINs

#### 5. Future Updates
- Keep `chemicals.db` separate from `user.db`
- Update strategy: backup user.db → replace chemicals.db → restore user.db
- Version check: compare `info.version` before migration

---

## Appendix

### Complete Table List with Row Counts
```
info                    1
sources                 (varies)
notes                   (varies)
erg_guides              64
unnas                   2,371
unna_cfr49s             (varies)
unna_waterreactions     (varies)
unna_actiondistances    (varies)
unna_table3             (varies)
mm_unna_erg_guide       (varies)
reacts                  80
hazards                 12
reactivity              2,346
mm_reactivity_hazard    4,178
chemicals               5,094
chemical_search         5,094
chemical_cas            4,942
chemical_unna           3,850
chemical_icsc           (varies)
mm_chemical_react       9,231
mm_chemical_hc          3,193
mm_chemical_lol         (varies)
mm_chemical_cfats       (varies)
mm_chemical_aegl        (varies)
aegls                   259
erpgs                   143
pacs                    1,774
lol                     1,709
cfats                   325
dupont                  719
aloha                   (varies)
```

### Schema Export Command
```bash
# To generate full DDL schema:
sqlite3 cameo.sqlite .schema > schema.sql
```

### Useful Pragmas
```sql
PRAGMA table_info(chemicals);         -- Show column details
PRAGMA foreign_key_list(chemical_cas); -- Show FKs
PRAGMA index_list(chemicals);          -- Show indexes
PRAGMA integrity_check;                -- Verify DB integrity
```

---

**Document Version**: 1.0  
**Last Updated**: December 27, 2025  
**Maintained By**: CAMEO Project Team
