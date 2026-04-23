import { NavLink } from "react-router-dom"
import { RecipeImagePlaceholder } from "@/components/recipes/RecipeImagePlaceholder"
import personImage from "@/assets/voice-chef-person.jpg"
import aiImage from "@/assets/voice-chef-ai.jpg"

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
          className="group relative flex h-full min-h-0 flex-col items-center justify-center overflow-hidden rounded-lg border p-6 text-center transition-transform duration-300 ease-out hover:scale-[1.02]"
        >
          <RecipeImagePlaceholder title="Recipes" className="pointer-events-none absolute inset-0 rounded-none border-0" />
          <div className="pointer-events-none absolute inset-0 bg-black/35 opacity-80 transition-opacity duration-300 group-hover:opacity-100" />
          <div className="relative z-10">
          <h2 className="text-3xl font-semibold text-white">Recipes</h2>
          <p className="mt-2 text-lg text-white/90">View and manage your recipes.</p>
          </div>
        </NavLink>
        <NavLink
          to="/menu-planner"
          className="group relative flex h-full min-h-0 flex-col items-center justify-center overflow-hidden rounded-lg border p-6 text-center transition-transform duration-300 ease-out hover:scale-[1.02]"
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
        <NavLink
          to="/ai-assistant"
          className="group relative flex h-full min-h-0 flex-col items-center justify-center overflow-hidden rounded-lg border p-6 text-center transition-transform duration-300 ease-out hover:scale-[1.02]"
        >
          <div
            className="pointer-events-none absolute inset-0 bg-cover bg-center bg-no-repeat transition-[filter] duration-300 ease-out"
            style={{ backgroundImage: `url(${aiImage})` }}
          />
          <div className="pointer-events-none absolute inset-0 bg-black/35 opacity-100 transition-opacity duration-300 group-hover:opacity-100" />
          <div className="relative z-10">
          <h2 className="text-3xl font-semibold text-white">AI Assistant</h2>
          <p className="mt-2 text-lg text-white/90">Get help with ideas and prep.</p>
          </div>
        </NavLink>
      </div>
    </div>
  );
}
