/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_AGENT_URL: string;
  readonly VITE_AGENT_DEBUG_STREAM?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
