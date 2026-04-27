import { useQuery } from '@tanstack/react-query';
import { api } from '@/api/axios';
import type { Ingredient, PaginatedResponse } from '@/types/recipe';

const INGREDIENTS_KEY = 'ingredients';

export function useIngredients(filters?: {
  search?: string;
  source?: string;
  offset?: number;
  limit?: number;
}) {
  return useQuery({
    queryKey: [INGREDIENTS_KEY, filters],
    queryFn: async () => {
      const { data } = await api.get<PaginatedResponse<Ingredient>>('/ingredients', {
        params: filters,
      });
      return data;
    },
  });
}
