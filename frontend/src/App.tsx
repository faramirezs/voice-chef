import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Dialog, DialogTrigger, DialogContent } from "@/components/ui/dialog";

function App() {
  return (
    <div className="min-h-screen p-8 space-y-8">
      <h1 className="text-3xl font-bold">Component Gallery</h1>

      <section className="space-y-4">
        <h2 className="text-xl font-semibold">Buttons</h2>
        <div className="flex gap-2">
          <Button>Default</Button>
          <Button variant="outline">Outline</Button>
          <Button variant="destructive">Destructive</Button>
        </div>
      </section>

      <section className="space-y-4">
        <h2 className="text-xl font-semibold">Card</h2>
        <Card className="max-w-sm">
          <CardHeader>
            <CardTitle>Example Card changing</CardTitle>
          </CardHeader>
          <CardContent>
            This is a card content area.
          </CardContent>
        </Card>
      </section>

      <section className="space-y-4">
        <h2 className="text-xl font-semibold">Input</h2>
        <Input placeholder="Type something..." />
      </section>

      <section className="space-y-4">
        <h2 className="text-xl font-semibold">Dialog</h2>
        <Dialog>
          <DialogTrigger asChild>
            <Button>Open dialog Button</Button>
          </DialogTrigger>
          <DialogContent>
            This is a dialog content.
          </DialogContent>
        </Dialog>
      </section>
    </div>
  );
}

export default App;
