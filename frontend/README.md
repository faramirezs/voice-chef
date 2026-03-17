# React + TypeScript + Vite

## Getting Started

To run the project in development mode, execute this single command from the project root:

```bash
docker compose up --build
```

The application will then be available at [http://localhost:5173](http://localhost:5173).

For local development without Docker, you can install dependencies and run the dev server directly:

```bash
npm install
npm run dev
```

---

## Makefile Shortcuts
For more granular control of the frontend container without Compose, use the [frontend/Makefile](../frontend/Makefile):

| Command | Purpose |
| :--- | :--- |
| `make build-dev` | Build the dev image |
| `make run-dev` | Run dev server on port 5173 |
| `make build-prod` | Build the Nginx production image |
| `make run-prod` | Run prod Nginx on port 8080 |

---

## Working with shadcn/ui

This section is a "how-to" guide specifically for the `shadcn/ui` library.

`shadcn/ui` works differently from most UI libraries. Instead of installing a single package from `npm` and importing components from it, you use a command-line tool (`npx shadcn-ui@latest add ...`) to copy the source code of individual components (like `button`, `card`, `dialog`) directly into your project's src/components folder.

Example:

```bash
npx shadcn@latest add button
```

This generates:

```bash
src/components/ui/button.jsx
```

Suggested basic components:

```bash
npx shadcn@latest add button
npx shadcn@latest add card
npx shadcn@latest add input
npx shadcn@latest add dialog
```

---

## Advanced Configuration

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) (or [oxc](https://oxc.rs) when used in [rolldown-vite](https://vite.dev/guide/rolldown)) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

### React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

### Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...

      // Remove tseslint.configs.recommended and replace with this
      tseslint.configs.recommendedTypeChecked,
      // Alternatively, use this for stricter rules
      tseslint.configs.strictTypeChecked,
      // Optionally, add this for stylistic rules
      tseslint.configs.stylisticTypeChecked,

      // Other configs...
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

---

## Docker Image Reference

```bash
docker images recipes-frontend
#Returns:
REPOSITORY         TAG       IMAGE ID       CREATED             SIZE
recipes-frontend   prod      4000e83b05bc   4 minutes ago       92.1MB
recipes-frontend   builder   1ca82a22683c   10 minutes ago      1.08GB
recipes-frontend   dev       268109152cf7   About an hour ago   1.07GB
recipes-frontend   deps      7c177777c34c   3 hours ago         303MB
```
