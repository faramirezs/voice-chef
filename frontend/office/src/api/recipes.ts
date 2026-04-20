// This file defines API helper functions that wrap the Axios instance and add type safety + convenience.

import { api } from './axios';
import type { PaginatedResponse, Recipe } from '@/types/recipe';

export const getRecipes = (params?: { status?: string; offset?: number; limit?: number }) =>
  api.get<PaginatedResponse<Recipe>>('/recipes', { params });

export const getRecipe = (id: string) => api.get<Recipe>(`/recipes/${id}`);
