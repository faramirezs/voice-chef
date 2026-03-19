// NOTE: MP. Test axios for API requestAnimationFrame

import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default apiClient;

interface TablesResponse {
  tables: string[];
}

// Function to retrieve a list of tables
export const fetchDbTables = async (): Promise<TablesResponse> => {
  try {
    const response = await apiClient.get<TablesResponse>('/tables');
    return response.data;
  } catch (error) {
    console.error('Error fetching DB tables:', error);
    // Return an empty array if an error occurs
    return { tables: [] };
  }
};
