import { api } from "./axios";

export interface TablesResponse {
  tables: string[];
}

export const fetchDbTables = async (): Promise<TablesResponse> => {
  const res = await api.get<TablesResponse>("/tables");
  return res.data;
};