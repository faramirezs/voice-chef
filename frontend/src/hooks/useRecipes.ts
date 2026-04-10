import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/api/axios';
import type { PaginatedResponse, Recipe } from '@/types/recipe';

const RECIPES_KEY = 'recipes';

export function useRecipes(filters?: { status?: string; offset?: number; limit?: number }) {
  return useQuery({
    queryKey: [RECIPES_KEY, filters],
    queryFn: async () => {
      const { data } = await api.get<PaginatedResponse<Recipe>>('/recipes', { params: filters });
      return data;
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
