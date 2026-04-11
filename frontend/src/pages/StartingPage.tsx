import { NavLink } from "react-router-dom"
import recipeImage from "@/assets/voice-chef-recipe.jpg"
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
          className="group relative z-0 flex h-full min-h-0 flex-col items-center justify-center overflow-hidden rounded-lg border p-6 text-center transition-all duration-300 ease-out hover:z-10 hover:-mx-2 md:hover:-mx-3 hover:scale-y-[1.04]"
        >
          <div
            className="absolute inset-0 bg-cover bg-center bg-no-repeat transition-transform duration-500 ease-out group-hover:scale-110"
            style={{ backgroundImage: `linear-gradient(rgb(0 0 0 / 45%), rgb(0 0 0 / 45%)), url(${recipeImage})` }}
          />
          <div className="absolute inset-0 bg-black/10 transition-colors duration-300 group-hover:bg-black/5" />
          <div className="relative z-10">
          <h2 className="text-3xl font-semibold text-white">Recipes</h2>
          <p className="mt-2 text-lg text-white/90">View and manage your recipes.</p>
          </div>
        </NavLink>
        <NavLink
          to="/menu-planner"
          className="group relative z-0 flex h-full min-h-0 flex-col items-center justify-center overflow-hidden rounded-lg border p-6 text-center transition-all duration-300 ease-out hover:z-10 hover:-mx-2 md:hover:-mx-3 hover:scale-y-[1.04]"
        >
          <div
            className="absolute inset-0 bg-cover bg-center bg-no-repeat transition-transform duration-500 ease-out group-hover:scale-110"
            style={{ backgroundImage: `linear-gradient(rgb(0 0 0 / 45%), rgb(0 0 0 / 45%)), url(${personImage})` }}
          />
          <div className="absolute inset-0 bg-black/10 transition-colors duration-300 group-hover:bg-black/5" />
          <div className="relative z-10">
          <h2 className="text-3xl font-semibold text-white">Menu planner</h2>
          <p className="mt-2 text-lg text-white/90">Plan your weekly menu.</p>
          </div>
        </NavLink>
        <NavLink
          to="/ai-assistant"
          className="group relative z-0 flex h-full min-h-0 flex-col items-center justify-center overflow-hidden rounded-lg border p-6 text-center transition-all duration-300 ease-out hover:z-10 hover:-mx-2 md:hover:-mx-3 hover:scale-y-[1.04]"
        >
          <div
            className="absolute inset-0 bg-cover bg-center bg-no-repeat transition-transform duration-500 ease-out group-hover:scale-110"
            style={{ backgroundImage: `linear-gradient(rgb(0 0 0 / 45%), rgb(0 0 0 / 45%)), url(${aiImage})` }}
          />
          <div className="absolute inset-0 bg-black/10 transition-colors duration-300 group-hover:bg-black/5" />
          <div className="relative z-10">
          <h2 className="text-3xl font-semibold text-white">AI Assistant</h2>
          <p className="mt-2 text-lg text-white/90">Get help with ideas and prep.</p>
          </div>
        </NavLink>
      </div>
    </div>
  );
}
