import {
  keepPreviousData,
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query';
import { 
  getRecipes, 
  getRecipe, 
  createRecipe,
  updateRecipe,
  deleteRecipe } from '@/api/recipes';
import { uploadRecipePicture, deleteRecipePicture } from '@/api/recipePhotos';
import type { 
  RecipeSummary,
  RecipeDetail, 
  RecipeWrite } from '@/types/recipe';

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
      const { data } = await getRecipes(filters);
      return data;
    },
  });
}

export function useAllRecipes(pageSize = 100) {
  return useQuery({
    queryKey: [RECIPES_KEY, 'all', pageSize],
    queryFn: async () => {
      const safePageSize = Math.min(Math.max(pageSize, 1), 100);
      const allRecipes: RecipeSummary[] = [];
      let offset = 0;
      let total = 0;

      do {
        const { data } = await getRecipes({ offset, limit: safePageSize });

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

// The enabled flag is used here to provide granular control over when 
// the network request should fire.
// External Control: This is particularly useful during a deletion process: 
// once a recipe is deleted, you can set enabled to false to prevent TanStack Query 
// from automatically refetching a resource that no longer exists in the database.
export function useRecipe(id: string, options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: [RECIPES_KEY, id],
    queryFn: async () => {
      const { data } = await getRecipe(id);
      return data;
    },
    enabled: !!id && (options?.enabled ?? true),
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
    mutationFn: async (recipe: RecipeWrite) => {
      const { data } = await createRecipe(recipe);
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
    mutationFn: async ({ id, ...updates }: Partial<RecipeDetail> & { id: string }) => {
      //                 ↑ Destructuring: extract id separately
      //                      ↑ Rest of the fields (name, description, instructions, etc.)
      const { data } = await updateRecipe(id, updates);
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
      const { data } = await deleteRecipe(id);
      return data;
    },
    onSuccess: (_data, id) => { // The first argument is empty (_)
      queryClient.removeQueries({ queryKey: [RECIPES_KEY, id] });
      queryClient.invalidateQueries({ queryKey: [RECIPES_KEY], exact: true});
    },
  });
}

export function useUploadRecipePicture() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, file }: { id: string; file: File }) => {
      const { data } = await uploadRecipePicture(id, file);
      return { id, photoUrl: data.photo_url as string };
    },
    onSuccess: ({ id, photoUrl }) => {
      queryClient.setQueryData([RECIPES_KEY, 'photo', id], photoUrl);
      queryClient.invalidateQueries({ queryKey: [RECIPES_KEY, id] });
      queryClient.invalidateQueries({ queryKey: [RECIPES_KEY] });
    },
  });
}

export function useDeleteRecipePicture() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await deleteRecipePicture(id);
      return id;
    },
    onSuccess: (id) => {
      queryClient.invalidateQueries({ queryKey: [RECIPES_KEY, id] });
      queryClient.invalidateQueries({ queryKey: [RECIPES_KEY] });
    },
  });
}
