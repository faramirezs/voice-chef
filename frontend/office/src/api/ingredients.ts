import { api } from './axios';
import type { IngredientAutocompleteItem } from '@/types/ingredients';


export const ingredientsAutocomplete = (query: string, limit: number = 10) =>
  api.get<IngredientAutocompleteItem[]>('/ingredients/autocomplete', {
    params: {
      query,
      limit,
    },
  });