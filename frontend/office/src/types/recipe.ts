// RecipeIngredientResponse
export interface RecipeIngredientResponse {
  id: string;
  ingredient_id:string;
  ingredient_name: string;
  ingredient_default_unit: string;
  quantity: string;
  unit: string;
  quantity_grams: string;
  preparation: string | null;
  sort_order: number;
  // NOTE: mpeshko - Do we need it? TO DO
  // [key: string]: unknown;
}

export interface Recipe {
  // RecipeSummary
  id: string;
  name: string;
  description: string | null;
  status: string;
  yield_mode: string;
  portion_size_grams: string | null;
  total_raw_weight_grams: string | null;
  total_cooked_weight_grams: string | null;
  portions_count_resolved: string | null;
  photo_url: string | null;
  created_at: string;
  updated_at: string;
  
  // export interface RecipeDetail extends RecipeSummary
  instructions: string | null;
  preparation_time_minutes: number | null;
  cooking_time_minutes: number | null;
  is_component: boolean;
  ingredients?: RecipeIngredientResponse[];
  
  // below: present in DB Shema, but not used
  // created_by: string | null;
  // yield_amount: number | null;
  // yield_unit: string | null;
  // reduction_factor: number | null;
  // recipe_number: string | null;
  // storage_temperature: string | null;
}

export interface PaginatedResponse<T> {
  items: T[];
  meta: {
    limit: number;
    offset: number;
    total: number;
  };
}

// RecipeIngredientResponse
export interface Ingredient {
  id: string;
  ingredient_id:string;
  ingredient_name: string;
  ingredient_default_unit: string;
  quantity: string;
  unit: string;
  quantity_grams: string;
  preparation: string | null;
  sort_order: number;
  
  // below: present in DB Shema, but not used
  // source?: string | null;
  // is_custom?: boolean;
  // created_at?: string;
  // updated_at?: string;

  // NOTE: mpeshko - Do we need it? TO DO
  // [key: string]: unknown;
}
