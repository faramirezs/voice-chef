import {
  keepPreviousData,
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query';
import { api } from '@/api/axios';
import { uploadRecipePhoto } from '@/api/recipePhotos';
import type { PaginatedResponse, Recipe } from '@/types/recipe';

const RECIPES_KEY = 'recipe';

export function useRecipes(filters?: {
  status?: string;
  name?: string;
  search?: string;
  sort_by?: string;
  offset?: number;
  limit?: number;
}) {
  return useQuery({
    queryKey: [RECIPES_KEY, filters],
    placeholderData: keepPreviousData,
    queryFn: async () => {
      const { data } = await api.get<PaginatedResponse<Recipe>>('/recipes', {
        params: filters,
      });
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
    retry: (failureCount, error: any) => {
      // Don't retry if it's a 401; the interceptor is handling it
      if (error.response?.status === 401) return false;
      return failureCount < 3; // Otherwise, retry 3 times
    }
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
      const { data } = await api.patch<Recipe>(`/recipes/${id}`, updates);
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

export function useDeleteRecipe() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const { data } = await api.delete<Recipe>(`/recipes/${id}`);
      return data;
    },
    onSuccess: (deletedRecipe) => {
      queryClient.removeQueries({ queryKey: [RECIPES_KEY, deletedRecipe.id] });
      queryClient.invalidateQueries({ queryKey: [RECIPES_KEY] });
    },
  });
}

export function useUploadRecipePhoto() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, file }: { id: string; file: File }) => {
      const { data } = await uploadRecipePhoto(id, file);
      return { id, photoUrl: data.photo_url as string };
    },
    onSuccess: ({ id, photoUrl }) => {
      queryClient.setQueryData([RECIPES_KEY, 'photo', id], photoUrl);
      queryClient.invalidateQueries({ queryKey: [RECIPES_KEY, id] });
      queryClient.invalidateQueries({ queryKey: [RECIPES_KEY] });
    },
  });
}
