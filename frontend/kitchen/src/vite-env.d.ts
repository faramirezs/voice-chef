/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_AGENT_URL: string;
  readonly VITE_OFFICE_URL?: string;
  readonly VITE_AGENT_DEBUG_STREAM?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

interface AppRuntimeConfig {
  officeUrl?: string;
  kitchenEmail?: string;
  kitchenPassword?: string;
}

interface Window {
  __APP_CONFIG__?: AppRuntimeConfig;
}
