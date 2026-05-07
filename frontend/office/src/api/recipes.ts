// This file defines API helper functions that wrap the Axios instance and add type safety + convenience.

import { api } from './axios';
import type {
  PaginatedResponse, 
  RecipeSummary,
  RecipeDetail, 
  RecipeWrite } from '@/types/recipe';

export const getRecipes = (params?: { status?: string; offset?: number; limit?: number }) =>
  api.get<PaginatedResponse<RecipeSummary>>('/recipes', { params });

export const getRecipe = (id: string) => 
  api.get<RecipeDetail>(`/recipes/${id}`);

export const createRecipe = (recipe: RecipeWrite) => 
  api.post<RecipeDetail>('/recipes', recipe);

// TO DO: mpeshko
export const updateRecipe = (id: string, updates: Partial<RecipeDetail>) => 
  api.patch<RecipeDetail>(`/recipes/${id}`, updates);

export const deleteRecipe = (id: string) => 
  api.delete<void>(`/recipes/${id}`);
