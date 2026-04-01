import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { 
  Dialog, 
  DialogTrigger, 
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription
 } from "@/components/ui/dialog";

// Note: MP. Test for relative API paths with proxying
import { fetchDbTables } from './api/axios';
import { useState, useEffect } from 'react';

function App() {

  // State for storing the list of tables and the load status
  const [tables, setTables] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  // An effect that runs once when the component loads
  useEffect(() => {
    const getTables = async () => {
      setLoading(true);
      const data = await fetchDbTables();
      if (data && data.defined_models) {
        setTables(data.defined_models);
      }
      setLoading(false);
    };

    getTables();
  }, []);

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
            <DialogHeader>
              <DialogTitle>Are you sure?</DialogTitle>
              <DialogDescription>
                This action cannot be undone.
              </DialogDescription>
            </DialogHeader>
          </DialogContent>
        </Dialog>
      </section>

    {/* New block for displaying tables */}
    <section className="space-y-4">
        <h2 className="text-xl font-semibold">All tables that have a defined SQLModel class</h2>
        <Card className="max-w-sm">
          <CardContent className="p-6">
            {loading ? (
              <p>Loading tables...</p>
            ) : (
              <ul>
                {tables.map((table) => (
                  <li key={table} className="font-mono">{table}</li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      </section>
    </div>
  );
}

export default App;
