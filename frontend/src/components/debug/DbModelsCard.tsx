import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { fetchDbTables } from '@/api/system';

/**
 * A simple component to fetch and display the list of defined SQLModel classes
 * from the backend. Intended for debugging and development purposes.
 */
export function DbModelsCard() {
  const [tables, setTables] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const getTables = async () => {
      try {
        setLoading(true);
        const response = await fetchDbTables();
        setTables(response.defined_models);
      } catch (err) {
        console.error("Failed to fetch DB models:", err);
        setError("Could not load models from the server.");
      } finally {
        setLoading(false);
      }
    };

    getTables();
  }, []); // The empty array ensures this effect runs only once

  return (
    <Card className="max-w-sm">
      <CardHeader>
        <CardTitle>Defined DB Models</CardTitle>
      </CardHeader>
      <CardContent className="p-6">
        {loading && <p>Loading tables...</p>}
        {error && <p className="text-destructive">{error}</p>}
        {!loading && !error && (
          <ul>
            {tables.map((table) => (
              <li key={table} className="font-mono">{table}</li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
