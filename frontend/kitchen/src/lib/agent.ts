import { HttpAgent } from "@ag-ui/client";

export const chefAgent = new HttpAgent({
  url: `${import.meta.env.VITE_AGENT_URL ?? "http://localhost:8001"}/`,
});
