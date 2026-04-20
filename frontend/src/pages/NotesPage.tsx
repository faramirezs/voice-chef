import { Button } from "@/components/ui/button";

const NOTES = [
  {
    id: "1",
    timestamp: "2024-06-01T12:00:00Z",
    title: "Note 1",
    content: "This is the content of note 1. It can be a recipe idea, a cooking tip, or anything else you want to jot down.",
  },
    {
    id: "2",
    timestamp: "2024-06-01T12:00:00Z",
    title: "Note 2",
    content: "This is the content of note 2. It can be a recipe idea, a cooking tip, or anything else you want to jot down.",
  },
    {
    id: "3",
    timestamp: "2024-06-01T12:00:00Z",
    title: "Note 3",
    content: "This is the content of note 3. It can be a recipe idea, a cooking tip, or anything else you want to jot down.",
  },
]

export function NotesPage() {
  return (
    <div className="space-y-6">
      <div className="space-y-1">
        <h1 className="text-2xl font-semibold">Notes</h1>
        <p className="text-muted-foreground">Keep track of your kitchen notes and ideas.</p>
      </div>
        <Button onClick={() => alert('Create new note functionality coming soon!')}>
          Create new note
        </Button>

      <div className="rounded-lg border border-dashed p-12 text-left text-muted-foreground">
          {NOTES.map((note) => (
          <div key={note.id} className="mb-6">
            <h2 className="text-xl font-semibold">{note.title}</h2>
            <p className="text-sm text-muted-foreground">{new Date(note.timestamp).toLocaleString()}</p>
            <p className="mt-2">{note.content}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
