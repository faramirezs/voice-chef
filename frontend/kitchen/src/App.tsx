import { useEffect, useState } from "react";
import {
  getCurrentUser,
  redirectToOfficeLogin,
  tryKitchenLogin,
} from "@/lib/auth";
import { HudCanvas } from "@/components/layout/HudCanvas";

export default function App() {
  const [authed, setAuthed] = useState<boolean | null>(null);

  useEffect(() => {
    (async () => {
      let user = await getCurrentUser();
      if (!user && (await tryKitchenLogin())) {
        user = await getCurrentUser();
      }
      if (!user) {
        redirectToOfficeLogin();
        return;
      }
      setAuthed(true);
    })();
  }, []);

  if (authed === null) {
    return (
      <div className="h-screen w-screen flex items-center justify-center bg-background text-text">
        Checking authentication...
      </div>
    );
  }

  return <HudCanvas />;
}
