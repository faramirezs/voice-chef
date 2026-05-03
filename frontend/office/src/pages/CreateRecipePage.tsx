import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCreateRecipe } from '@/hooks/useRecipes';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { cn } from '@/lib/utils';

const STATUS_STYLES: Record<string, string> = {
  draft: 'bg-yellow-100 text-yellow-800',
  active: 'bg-green-100 text-green-800',

};

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm uppercase tracking-wide text-muted-foreground font-medium">
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  );
}


export function CreateRecipePage() {
  const navigate = useNavigate();
  const createRecipe = useCreateRecipe();

  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [instructions, setInstructions] = useState('');
  const [error, setError] = useState<string | null>(null);
  const draftStatus = 'draft';

  const handleSave = () => {
    const trimmedName = name.trim();

    if (!trimmedName) {
      setError('Recipe name is required.');
      return;
    }

    setError(null);

    createRecipe.mutate(
      {
        name: trimmedName,
        description: description.trim() || null,
        instructions: instructions.trim() || null,
        status: 'draft',
      },
      {
        onSuccess: (recipe) => {
          navigate(`/recipes/${recipe.id}`, { state: { isNewRecipe: true } });
        },
      },
    );
  };

  const badgeClass = cn(
    'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium capitalize',
    STATUS_STYLES[draftStatus] ?? 'bg-gray-100 text-gray-600',
  );

  return (
    <div className="space-y-5 max-w-10xl">
      <div className="space-y-4">
        <Button size="sm" onClick={() => navigate(-1)}>← Back</Button>

        <div className="h-72 w-full overflow-hidden rounded-xl border bg-muted/30 flex items-center justify-center">
          <div className="text-center text-muted-foreground">
            <p className="text-sm">Recipe photo will appear here after saving</p>
          </div>
        </div>

        <div className="flex items-center gap-3 flex-wrap">
          <div className="space-y-1 w-full sm:w-auto sm:min-w-[28rem]">
            <Input
              id="recipe-name"
              value={name}
              onChange={(event) => {
                setName(event.target.value);
                if (error) {
                  setError(null);
                }
              }}
              placeholder="Untitled recipe"
              className="h-12 text-2xl font-semibold"
              autoFocus
            />
            {error && <p className="text-xs text-destructive">{error}</p>}
          </div>
          <span className={badgeClass}>{draftStatus}</span>
        </div>

        <div className="flex flex-wrap gap-3">
          <Button
            size="lg"
            type="button"
            className="min-w-40"
            onClick={handleSave}
            disabled={createRecipe.isPending}
            aria-busy={createRecipe.isPending}
          >
            {createRecipe.isPending ? 'Saving...' : 'Save recipe'}
          </Button>
          <Button
            size="lg"
            variant="outline"
            type="button"
            onClick={() => navigate('/recipes')}
            disabled={createRecipe.isPending}
          >
            Cancel
          </Button>
        </div>
      </div>

      <Section title="Description">
        <Textarea
          id="recipe-description"
          value={description}
          onChange={(event) => setDescription(event.target.value)}
          placeholder="Click to add description"
        />
      </Section>

      <Section title="Instructions">
        <Textarea
          id="recipe-instructions"
          value={instructions}
          onChange={(event) => setInstructions(event.target.value)}
          placeholder="Click to add instructions"
          className="min-h-40"
        />
      </Section>
    </div>
  );
}
