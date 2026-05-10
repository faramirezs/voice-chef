import { NavLink } from "react-router-dom"
import recipeImage from "@/assets/voice-chef-recipe.jpg"
import personImage from "@/assets/voice-chef-person.jpg"
import aiImage from "@/assets/voice-chef-ai.jpg"

const KITCHEN_URL = import.meta.env.VITE_KITCHEN_URL || "http://localhost:8082"

export function StartingPage() {
  return (
    <div className="flex min-h-[calc(100svh-9rem)] flex-col gap-6">
      <div className="space-y-1">
        <h1 className="text-2xl font-semibold">Welcome, chef!</h1>
        <p className="text-muted-foreground">What would you like to do today?</p>
      </div>

      <div className="grid flex-1 gap-4 md:grid-cols-3">
        <NavLink
          to="/recipes"
          className="card-stagger-in group relative flex h-full min-h-0 flex-col items-center justify-center overflow-hidden rounded-lg border p-6 text-center transition-transform duration-300 ease-out hover:scale-[1.02]"
          style={{ animationDelay: "120ms" }}
        >
          <div
            className="pointer-events-none absolute inset-0 bg-cover bg-center bg-no-repeat transition-[filter] duration-300 ease-out"
            style={{ backgroundImage: `url(${recipeImage})` }}
          />
          <div className="pointer-events-none absolute inset-0 bg-black/35 opacity-80 transition-opacity duration-300 group-hover:opacity-100" />
          <div className="relative z-10">
          <h2 className="text-3xl font-semibold text-white">Recipes</h2>
          <p className="mt-2 text-lg text-white/90">View and manage your recipes.</p>
          </div>
        </NavLink>
        <NavLink
          to="/menu-planner"
          className="card-stagger-in group relative flex h-full min-h-0 flex-col items-center justify-center overflow-hidden rounded-lg border p-6 text-center transition-transform duration-300 ease-out hover:scale-[1.02]"
          style={{ animationDelay: "240ms" }}
        >
          <div
            className="pointer-events-none absolute inset-0 bg-cover bg-center bg-no-repeat transition-[filter] duration-300 ease-out"
            style={{ backgroundImage: `url(${personImage})` }}
          />
          <div className="pointer-events-none absolute inset-0 bg-black/35 opacity-80 transition-opacity duration-300 group-hover:opacity-100" />
          <div className="relative z-10">
          <h2 className="text-3xl font-semibold text-white">Menu planner</h2>
          <p className="mt-2 text-lg text-white/90">Plan your weekly menu.</p>
          </div>
        </NavLink>
        <a
          href={KITCHEN_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="card-stagger-in group relative flex h-full min-h-0 flex-col items-center justify-center overflow-hidden rounded-lg border p-6 text-center transition-transform duration-300 ease-out hover:scale-[1.02]"
          style={{ animationDelay: "360ms" }}
        >
          <div
            className="pointer-events-none absolute inset-0 bg-cover bg-center bg-no-repeat transition-[filter] duration-300 ease-out"
            style={{ backgroundImage: `url(${aiImage})` }}
          />
          <div className="pointer-events-none absolute inset-0 bg-black/35 opacity-100 transition-opacity duration-300 group-hover:opacity-100" />
          <div className="relative z-10">
          <h2 className="text-3xl font-semibold text-white">Ai Kitchen Display</h2>
          <p className="mt-2 text-lg text-white/90">Open the kitchen screen.</p>
          </div>
        </a>
      </div>
    </div>
  );
}
