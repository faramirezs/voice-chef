import { useQuery } from '@tanstack/react-query';
import { api } from '@/api/axios';
import type { Ingredient } from '@/types/recipe';

const INGREDIENTS_KEY = 'ingredients';

export function useIngredients(search?: string) {
  return useQuery({
    queryKey: [INGREDIENTS_KEY, search],
    queryFn: async () => {
      const { data } = await api.get<Ingredient[]>('/ingredients', {
        params: search ? { search } : undefined,
      });
      return data;
    },
  });
}
