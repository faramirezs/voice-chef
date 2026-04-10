import { api } from './axios';

interface TablesResponse {
  defined_models: string[];
}

// Function to retrieve a list defined ORM models
export const fetchDbTables = async (): Promise<TablesResponse> => {
    const res = await api.get<TablesResponse>("/defined-models");
    return res.data;
}
