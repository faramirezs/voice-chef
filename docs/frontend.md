# Frontend

This document describes the architecture and technology stack of the frontend application.

## Getting Started

To run the project in development mode, execute this single command:

```bash
docker compose up --build
```

The application will then be available at [http://localhost:5173](http://localhost:5173).

---

## 🛠️ Technology Stack

The core technologies used in this project are:

| Category     | Package               | Purpose              |
| ------------ | --------------------- | -------------------- |
| **Framework** | **React**            | UI components |
| **Routing** | **React Router** (react-router-dom) | Page navigation |
| **Server state** | **TanStack Query** (@tanstack/react-query) | API data management |
| **HTTP Client** | **Axios** | Sending HTTP requests to the backend |
| **Build Tool**| **Vite** | Fast dev server and project bundling |
| **UI Components** | **shadcn/ui** | Pre-built, styled, and accessible components |
| **Styling** | **Tailwind CSS** | A utility-first CSS framework for styling |

---

## 🏛️ Architecture Overview

### Routing (React Router)

**Purpose:** Navigation between pages in a Single Page Application (SPA).

It allows creating routes like `/home`, `/recipes`, and `/recipes/123`.

**Example:**
```javascript
import { BrowserRouter, Routes, Route } from "react-router-dom"

<BrowserRouter>
	<Routes>
		<Route path="/" element={<Home />} />
		<Route path="/recipes" element={<Recipes />} />
	</Routes>
</BrowserRouter>
```

### Server State Management (TanStack Query)

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

**Example:**
```javascript
import { useQuery } from "@tanstack/react-query"

const { data, isLoading } = useQuery({
	queryKey: ["recipes"],
	queryFn: fetchRecipes
})
```

### API Client (Axios)

**Purpose:** Send HTTP requests to your backend. We use Axios for its convenience compared to the native `fetch`.

**Example:**
```javascript
import axios from "axios"

const api = axios.create({
	baseURL: "http://localhost:8000/api" // URL of our FastAPI backend
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

### Build Tool (Vite)

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

### Tailwind CSS (Optional but very common)

**Purpose:** styling

**Example:**
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
 ├── api								# Axios setup and fetch functions
 │    └── axios.js
 ├── components					# UI components (buttons, cards)
 ├── pages							# Page components (Home, Recipes)
 │    ├── Home.jsx
 │    └── Recipes.jsx
 ├── hooks							# Custom hooks
 ├── routes							# Routing configuration
 │    └── router.jsx
 ├── App.jsx						# Main application component
 └── main.jsx						# Entry point where React is mounted to the DOM
```

---

### Example Flow (Real App)

When a user opens the `/recipes` page:

1.  **React Router** loads the page
2.  **React Query (TanStack)** initiates a request to fetch the recipes
3.  **Axios** sends a GET request to the backend
4.  The backend returns the data in JSON format
5.  React Query (TanStack) caches the result and provides it to the component
6.  The UI renders instantly

---

## Appendix: Boilerplate Creation Notes

This section documents the initial command used to add core dependencies after setting up the base Vite project.

**Install Command:**

```bash
npm install react-router-dom @tanstack/react-query axios
```

---
