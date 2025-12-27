// Generated from actual chemicals.db schema via SQLite MCP

export interface Chemical {
  id: number;
  name: string;
  description: string | null;
  health_haz: string | null;
  first_aid: string | null;
  fire_haz: string | null;
  fire_fight: string | null;
  non_fire_resp: string | null;
  prot_clothing: string | null;
  air_water_reactions: string | null;
  chemical_profile: string | null;
  special_hazards: string | null;
  isolation: string | null;
  niosh: string | null;
  niosh_file: string | null;
  nfpa_source: string | null;
  nfpa_note: string | null;
  nfpa_flam: number | null;
  nfpa_health: number | null;
  nfpa_react: number | null;
  nfpa_special: string | null;
  fp_source: string | null;
  fp_note: string | null;
  fp_value: number | null;
  fp_range: string | null;
  lel_source: string | null;
  lel_note: string | null;
  lel_value: number | null;
  lel_range: string | null;
  lel_unit: string | null;
  uel_source: string | null;
  uel_note: string | null;
  uel_value: number | null;
  uel_range: string | null;
  uel_unit: string | null;
  ai_source: string | null;
  ai_note: string | null;
  ai_value: number | null;
  ai_range: string | null;
  mp_source: string | null;
  mp_note: string | null;
  mp_value: number | null;
  mp_range: string | null;
  vp_source: string | null;
  vp_note: string | null;
  vp_value: number | null;
  vp_range: string | null;
  vp_value_tempDegF: number | null;
  vp_range_tempDegF: string | null;
  vp_unit: string | null;
  vd_source: string | null;
  vd_note: string | null;
  vd_value: number | null;
  vd_range: string | null;
  vd_value_tempDegF: number | null;
  vd_range_tempDegF: string | null;
  sg_source: string | null;
  sg_note: string | null;
  sg_value: number | null;
  sg_range: string | null;
  sg_value_tempDegF: number | null;
  sg_range_tempDegF: string | null;
  bp_source: string | null;
  bp_note: string | null;
  bp_value: number | null;
  bp_range: string | null;
  bp_value_presMMHG: number | null;
  bp_range_presMMHG: string | null;
  molwgt_source: string | null;
  molwgt_note: string | null;
  molwgt_value: number | null;
  molwgt_range: string | null;
  idlh_source: string | null;
  idlh_note: string | null;
  idlh_value: number | null;
  idlh_unit: string | null;
  solblty_source: string | null;
  solblty_note: string | null;
  solblty_value: number | null;
  solblty_range: string | null;
  solblty_unit: string | null;
  ion_source: string | null;
  ion_note: string | null;
  ion_value: number | null;
  response_guide_for_chemical_warfare_agent: number | null;
  synonyms: string;
  chris_codes: string;
  dot_labels: string;
  formulas: string;
  incompatible_absorbents: string;
  psm: string | null;
}

export interface ChemicalSearchMeta {
  id: number;
  is_aloha: boolean;
  is_dupont: boolean;
  is_cfats: boolean;
  is_icsc: boolean;
  is_ehs_tpq: boolean;
  is_ehs_rq: boolean;
  is_cercla_rq: boolean;
  is_section_313_notes: boolean;
  is_caa_rq: boolean;
  regulatory_names: string;
  rcra_codes: string;
  loc_title: string | null;
  loc_value: number | null;
  loc_unit: string | null;
}

export interface ChemicalSummary {
  id: number;
  name: string;
  synonyms: string;
}

export interface SearchResult {
  items: ChemicalSummary[];
  total: number;
}
