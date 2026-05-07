import { useEffect, useState } from "react";
import { getCurrentUser, redirectToOfficeLogin } from "@/lib/auth";
import { HudCanvas } from "@/components/layout/HudCanvas";

export default function App() {
  const [authed, setAuthed] = useState<boolean | null>(null);

  useEffect(() => {
    getCurrentUser().then((user) => {
      if (!user) {
        redirectToOfficeLogin();
      } else {
        setAuthed(true);
      }
    });
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
