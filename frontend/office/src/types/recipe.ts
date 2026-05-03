export interface Recipe {
  id: string;
  name: string;
  status: string;
  photo_url: string | null;
  created_at: string;
  updated_at: string;
  tenant_id: string | null;
  created_by: string | null;
  description: string | null;
  description_short: string | null;
  instructions: string | null;
  notes: string | null;
  notes_instructions: string | null;
  serving_recommendation: string | null;
  side_dishes: string | null;
  storage_text: string | null;
  origin_fish: string | null;
  origin_location: string | null;
  devices: string | null;
  utensils: string | null;
  packaging: string | null;
  packaging_material: string | null;
  ingredient_list_custom: string | null;
  allergene_source: string | null;
  yield_amount: number | null;
  reduction_factor: number | null;
  eigene_menge: number | null;
  net_weight: number | null;
  fill_weight: number | null;
  fill_quantity: number | null;
  drained_weight: number | null;
  total_weight: number | null;
  portion_weight: number | null;
  margin: number | null;
  nutri_score_veg_fruits: number | null;
  preference_nutri_value: number | null;
  yield_unit: string | null;
  recipe_number: string | null;
  batch_number: string | null;
  storage_temperature: string | null;
  labor_effort: string | null;
  nutri_score_category: string | null;
  unit_measure: string | null;
  unit_serving: string | null;
  portion_by_weight: boolean;
  mise_en_place_display: boolean;
  is_component: boolean;
  production_date: string | null;
  use_by_date: string | null;
  expiry_date: string | null;
}

export interface PaginatedResponse<T> {
  items: T[];
  meta: {
    limit: number;
    offset: number;
    total: number;
  };
}

export interface Ingredient {
  id: string;
  name: string;
  source?: string | null;
  default_unit?: string | null;
  is_custom?: boolean;
  created_at?: string;
  updated_at?: string;
  [key: string]: unknown;
}
