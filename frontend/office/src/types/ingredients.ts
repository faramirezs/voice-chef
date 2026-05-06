export interface IngredientAutocompleteItem {
  id: string;
  name: string;
}

export interface IngredientListItem {
  id: string;
  name: string;
  source: string;
  default_unit: string | null;
  ingredient_type: string | null;
  bls_key: string | null;
  is_custom: boolean;
  parent_id: string | null;
  created_at: string;
  updated_at: string;
}