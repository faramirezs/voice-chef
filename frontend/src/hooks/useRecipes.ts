import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/api/axios';
import type { Recipe } from '@/types/recipe';

const RECIPES_KEY = 'recipe';

export function useRecipes(filters?: { status?: string; skip?: number; limit?: number }) {
  return useQuery({
    queryKey: [RECIPES_KEY, filters],
    queryFn: async () => {
      const { data } = await api.get<Recipe[]>('/recipe/read_all', { params: filters });
      return data.items;
    },
  });
}

export function useRecipe(id: string) {
  return useQuery({
    queryKey: [RECIPES_KEY, id],
    queryFn: async () => {
      const { data } = await api.get<Recipe>(`/recipe/read/${id}`);
      return data;
    },
    enabled: !!id,
  });
}

export function useCreateRecipe() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (recipe: Partial<Recipe>) => {
      const { data } = await api.post<Recipe>('/recipe/create', recipe);
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
      const { data } = await api.patch<Recipe>(`/recipe/update/${id}`, updates);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [RECIPES_KEY] });
    },
  });
}
