# Modern React Stack (Minimal & Production Ready)

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

# 1️⃣ Routing

### 📦 React Router (`react-router-dom`)

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

# 2️⃣ Server State (API Data)

### 📦 TanStack Query (`@tanstack/react-query`)

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

Most **modern React apps use this**.

---

# 3️⃣ API Client

### 📦 Axios

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

Most backend teams prefer Axios.

---

# 4️⃣ Build Tool

### 📦 Vite

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

# 5️⃣ (Optional but very common)

### 📦 Tailwind CSS

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

# What Big React Apps Add Later

Large apps also include:

| Tool            | Purpose           |
| --------------- | ----------------- |
| Zustand         | global state      |
| React Hook Form | forms             |
| Zod             | schema validation |
| Framer Motion   | animations        |

---

✅ **The 3 packages you need right now**

```
react-router-dom
@tanstack/react-query
axios
```

---

# 1️⃣ Tailwind installation

Installing **Tailwind CSS** as a dev dependency is correct:

```bash
npm install -D @tailwindcss/vite
```


---

# 2️⃣ shadcn/ui is NOT installed like a normal package

**shadcn/ui** is **not a dependency** you install with npm.

This will fail or do nothing useful:

```bash
npm install @shadcn/ui ❌
```

Instead you use the **CLI tool**:

```bash
npx shadcn@latest init
```

This tool:

* configures Tailwind
* installs required dependencies
* creates a `components/ui` folder
* copies UI components into your project

Important: **shadcn does not ship a component library**.
It **copies the code into your project** so you own it.


---

### 3️⃣ Install components

Example:

```bash
npx shadcn@latest add button
```

This generates:

```
src/components/ui/button.jsx
```


Suggested basic components:

```bash
npx shadcn@latest add button
npx shadcn@latest add card
npx shadcn@latest add input
npx shadcn@latest add dialog
```


