// This file defines API helper functions that wrap the Axios instance and add type safety + convenience.

import { api } from './axios';
import type { PaginatedResponse, Recipe, RecipeWrite } from '@/types/recipe';

export const getRecipes = (params?: { status?: string; offset?: number; limit?: number }) =>
  api.get<PaginatedResponse<Recipe>>('/recipes', { params });

export const getRecipe = (id: string) => 
  api.get<Recipe>(`/recipes/${id}`);

export const createRecipe = (recipe: RecipeWrite) => 
  api.post<Recipe>('/recipes', recipe);

// TO DO: mpeshko
// export const updateRecipe = (id: string, updates: Partial<Recipe>) => 
//   api.patch<Recipe>(`/recipes/${id}`, updates);

export const deleteRecipe = (id: string) => 
  api.delete<Recipe>(`/recipes/${id}`);
