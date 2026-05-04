import { api } from './axios';

export interface RecipePhotoResponse {
  photo_url: string;
}

export const getRecipePhoto = async (recipeId: string) => {
  const { data } = await api.get<RecipePhotoResponse>(`/recipe_image/${recipeId}`);
  return data;
};

export const uploadRecipePhoto = (recipeId: string, file: File) => {
  const formData = new FormData();
  formData.append("file", file);

  return api.put<RecipePhotoResponse>(`/recipe_image/?recipe_id=${recipeId}`, formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
};

export const deleteRecipePhoto = (recipeId: string) => {
  return api.delete(`/recipe_image/${recipeId}`);
};