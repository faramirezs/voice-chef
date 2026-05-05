import { api } from './axios';

export interface RecipePictureResponse {
  photo_url: string;
}

export const getRecipePicture = async (recipeId: string) => {
  const { data } = await api.get(`/recipe_images/${recipeId}`);
  return data;
};

export const uploadRecipePicture = (recipeId: string, file: File) => {
  const formData = new FormData();
  formData.append("file", file);

  return api.put<RecipePictureResponse>(`/recipe_images/?recipe_id=${recipeId}`, formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
};

export const deleteRecipePicture = (recipeId: string) => {
  return api.delete(`/recipe_images/${recipeId}`);
};