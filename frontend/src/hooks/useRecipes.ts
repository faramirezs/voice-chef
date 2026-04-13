import {
  keepPreviousData,
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query';
import { api } from '@/api/axios';
import type { PaginatedResponse, Recipe } from '@/types/recipe';

const RECIPES_KEY = 'recipes';

export function useRecipes(filters?: {
  status?: string;
  name?: string;
  offset?: number;
  limit?: number;
}) {
  return useQuery({
    queryKey: [RECIPES_KEY, filters],
    placeholderData: keepPreviousData,
    queryFn: async () => {
      const { data } = await api.get<PaginatedResponse<Recipe>>('/recipes', { params: filters });
      return data;
    },
  });
}

export function useAllRecipes(pageSize = 100) {
  return useQuery({
    queryKey: [RECIPES_KEY, 'all', pageSize],
    queryFn: async () => {
      const safePageSize = Math.min(Math.max(pageSize, 1), 100);
      const allRecipes: Recipe[] = [];
      let offset = 0;
      let total = 0;

      do {
        const { data } = await api.get<PaginatedResponse<Recipe>>('/recipes', {
          params: { offset, limit: safePageSize },
        });

        allRecipes.push(...data.items);
        total = data.meta.total;
        offset += data.meta.limit;

        if (data.items.length === 0) {
          break;
        }
      } while (allRecipes.length < total);

      return allRecipes;
    },
  });
}

export function useRecipe(id: string) {
  return useQuery({
    queryKey: [RECIPES_KEY, id],
    queryFn: async () => {
      const { data } = await api.get<Recipe>(`/recipes/${id}`);
      return data;
    },
    enabled: !!id,
  });
}

export function useCreateRecipe() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (recipe: Partial<Recipe>) => {
      const { data } = await api.post<Recipe>('/recipes', recipe);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [RECIPES_KEY] });
    },
  });
}

export function useUpdateRecipe() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, ...updates }: Partial<Recipe> & { id: string }) => {
      const { data } = await api.put<Recipe>(`/recipes/${id}`, updates);
      return data;
    },
    onSuccess: (updatedRecipe) => {
      queryClient.setQueryData([RECIPES_KEY, updatedRecipe.id], updatedRecipe);
      queryClient.invalidateQueries({
        queryKey: [RECIPES_KEY],
        predicate: (query) => typeof query.queryKey[1] === 'object',
      });
    },
  });
}
