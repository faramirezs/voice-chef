import axios from "axios";
// Imports Axios — a library for making HTTP requests (instead of using fetch directly).

export const api = axios.create({
  baseURL: "/api",
  headers: {
    "Content-Type": "application/json",
  },
});
