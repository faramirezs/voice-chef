# Frontend

## Makefile Shortcuts
For more granular control of the frontend container without Compose, use the [frontend/Makefile](../frontend/Makefile):

| Command | Purpose |
| :--- | :--- |
| `make build-dev` | Build the dev image |
| `make run-dev` | Run dev server on port 5173 |
| `make build-prod` | Build the Nginx production image |
| `make run-prod` | Run prod Nginx on port 8080 |

---

### Comparing Docker images for frontend:

```bash
docker images recipes-frontend
#Returns:
REPOSITORY         TAG       IMAGE ID       CREATED             SIZE
recipes-frontend   prod      4000e83b05bc   4 minutes ago       92.1MB
recipes-frontend   builder   1ca82a22683c   10 minutes ago      1.08GB
recipes-frontend   dev       268109152cf7   About an hour ago   1.07GB
recipes-frontend   deps      7c177777c34c   3 hours ago         303MB
```
---

## How we created the Vite boilerplate?

Install:

```bash
npm install react-router-dom @tanstack/react-query axios
```

These three cover **routing, data fetching, and API communication**.

Typical modern stack:

| Category     | Package               | Purpose              |
| ------------ | --------------------- | -------------------- |
| Framework    | React                 | UI components        |
| Routing      | react-router-dom      | Page navigation      |
| Server state | @tanstack/react-query | API data management  |
| HTTP client  | axios                 | API requests         |
| Build tool   | Vite                  | Dev server + bundler |

---

# Routing

### React Router (`react-router-dom`)

**Purpose:** Navigation between pages.

Without it you cannot do:

```
/home
/recipes
/recipes/123
/profile
```

Install:

```bash
npm install react-router-dom
```

Example:

```javascript
import { BrowserRouter, Routes, Route } from "react-router-dom"

<BrowserRouter>
  <Routes>
    <Route path="/" element={<Home />} />
    <Route path="/recipes" element={<Recipes />} />
  </Routes>
</BrowserRouter>
```

What it provides:

* SPA navigation
* dynamic routes (`/recipe/:id`)
* protected routes
* nested layouts

---

# Server State (API Data)

### TanStack Query (`@tanstack/react-query`)

**Purpose:** Manage data coming from APIs.

Without it you would write a lot of messy code like:

```javascript
useEffect(() => {
 fetch("/api/recipes")
  .then(res => res.json())
  .then(setRecipes)
}, [])
```

Problems with this approach:

* no caching
* no refetching
* loading states everywhere
* duplicate requests

React Query solves all that.

Example:

```javascript
import { useQuery } from "@tanstack/react-query"

const { data, isLoading } = useQuery({
  queryKey: ["recipes"],
  queryFn: fetchRecipes
})
```

Features:

* caching
* background refetch
* loading & error states
* automatic retries
* pagination

---

# API Client

### Axios

**Purpose:** Send HTTP requests to your backend.

Example backend call:

```javascript
import axios from "axios"

const api = axios.create({
  baseURL: "http://localhost:3000/api"
})

export const fetchRecipes = async () => {
  const res = await api.get("/recipes")
  return res.data
}
```

Why Axios instead of `fetch`:

| Feature           | Axios  | fetch  |
| ----------------- | ------ | ------ |
| JSON auto parsing | ✅      | ❌      |
| interceptors      | ✅      | ❌      |
| baseURL           | ✅      | ❌      |
| error handling    | easier | manual |

---

# Build Tool

### Vite

Purpose:

* lightning-fast dev server
* builds optimized production bundles
* replaces Webpack

Features:

| Feature         | Benefit         |
| --------------- | --------------- |
| instant startup | no long build   |
| HMR             | instant updates |
| smaller builds  | faster site     |

Start dev server:

```bash
npm run dev
```

---

# (Optional but very common)

### Tailwind CSS

Purpose: styling

Example:

```html
<button className="bg-blue-500 text-white px-4 py-2 rounded">
  Save
</button>
```

---

# Typical Folder Structure

Modern React apps usually look like this:

```
src
 ├── api
 │    └── axios.js
 ├── components
 ├── pages
 │    ├── Home.jsx
 │    └── Recipes.jsx
 ├── hooks
 ├── routes
 │    └── router.jsx
 ├── App.jsx
 └── main.jsx
```

---

# Example Flow (Real App)

User opens:

```
/recipes
```

Flow:

1️⃣ **React Router** loads the page
2️⃣ **React Query** asks for recipes
3️⃣ **Axios** calls the backend API
4️⃣ Backend returns JSON
5️⃣ React Query caches the result
6️⃣ UI renders instantly

---

# Full Install Command

For a clean modern setup:

```bash
npm install react-router-dom @tanstack/react-query axios
```
---


### Install components

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

## In Vite + React:

index.html just has a <div id="root"></div> and a <script src="/src/main.tsx">.

src/main.tsx renders your React tree into #root, usually <App />.

Whatever <App /> returns is what you see in the browser.

