import { useQuery } from '@tanstack/react-query';
import { api } from '@/api/axios';
import { ingredientsAutocomplete } from '@/api/ingredients';
import type { IngredientListItem } from '@/types/ingredients';
import type { PaginatedResponse } from '@/types/recipe';

const INGREDIENTS_KEY = 'ingredients';
const INGREDIENTS_AUTOCOMPLETE_KEY = 'ingredients-autocomplete';

export function useIngredients(filters?: {
  search?: string;
  source?: string;
  offset?: number;
  limit?: number;
}) {
  return useQuery({
    queryKey: [INGREDIENTS_KEY, filters],
    queryFn: async () => {
      const { data } = await api.get<PaginatedResponse<IngredientListItem>>('/ingredients', {
        params: filters,
      });
      return data;
    },
  });
}

export function useIngredientsAutocomplete(query: string, limit: number = 10) {
  return useQuery({
    queryKey: [INGREDIENTS_AUTOCOMPLETE_KEY, query, limit],
    queryFn: async () => {
      const { data } = await ingredientsAutocomplete(query, limit);
      return data;
    },
    enabled: query.length >= 2,
  });
}
