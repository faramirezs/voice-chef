import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { listAPIKeys, createAPIKey, deleteAPIKey } from '@/api/apiKeys';
import type { APIKeyListResponse, APIKeyCreateResponse } from '@/types/apiKeys';
import { HugeiconsIcon } from '@hugeicons/react';
import { Copy01Icon, Delete02Icon } from '@hugeicons/core-free-icons';

export function APIKeysPage() {
  const [apiKey, setApiKey] = useState<APIKeyListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [newKeyName, setNewKeyName] = useState('');
  const [newKeyDescription, setNewKeyDescription] = useState('');
  const [createdKey, setCreatedKey] = useState<APIKeyCreateResponse | null>(null);
  const [isCreatingKey, setIsCreatingKey] = useState(false);

  // Load API keys on mount
  useEffect(() => {
    loadApiKeys();
  }, []);

  const loadApiKeys = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await listAPIKeys();
      setApiKey(response.data.length > 0 ? response.data[0] : null);
    } catch (err) {
      setError('Failed to load API key');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateKey = async () => {
    if (!newKeyName.trim()) {
      setError('API key name is required');
      return;
    }

    try {
      setIsCreatingKey(true);
      setError(null);
      const response = await createAPIKey({
        name: newKeyName,
        description: newKeyDescription || undefined,
        is_active: true,
      });
      setCreatedKey(response.data);
      setNewKeyName('');
      setNewKeyDescription('');
      setIsCreateDialogOpen(false);
      await loadApiKeys();
    } catch (err) {
      setError('Failed to create API key');
      console.error(err);
    } finally {
      setIsCreatingKey(false);
    }
  };

  const handleDeleteKey = async () => {
    if (!apiKey) return;

    try {
      setError(null);
      await deleteAPIKey(apiKey.id);
      await loadApiKeys();
      setIsDeleteDialogOpen(false);
    } catch (err) {
      setError('Failed to delete API key');
      console.error(err);
    }
  };

  const handleCopyKey = (key: string) => {
    navigator.clipboard.writeText(key);
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div className="space-y-6">
      <div className="space-y-1">
        <h1 className="text-2xl font-semibold">API Keys</h1>
        <p className="text-muted-foreground">Manage API keys for your tenant.</p>
      </div>

      {error && (
        <div className="rounded-lg bg-red-50 p-4 text-sm text-red-600">
          {error}
        </div>
      )}

      {createdKey && (
        <div className="rounded-lg bg-blue-50 p-4 space-y-4">
          <div className="space-y-2">
            <p className="font-semibold text-blue-900">API Key Created Successfully</p>
            <p className="text-sm text-blue-800">
              Save this key in a secure place. You won't be able to see it again.
            </p>
          </div>
          <div className="flex items-center gap-2 bg-white p-3 rounded border border-blue-200">
            <code className="flex-1 font-mono text-sm break-all">{createdKey.key}</code>
            <Button
              size="sm"
              variant="outline"
              onClick={() => handleCopyKey(createdKey.key)}
            >
              <HugeiconsIcon icon={Copy01Icon} strokeWidth={2} className="w-4 h-4" />
            </Button>
          </div>
          <Button
            size="sm"
            onClick={() => setCreatedKey(null)}
            className="w-full"
          >
            Done
          </Button>
        </div>
      )}

      <div className="flex gap-2">
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>{apiKey ? 'Regenerate API Key' : 'Create API Key'}</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>{apiKey ? 'Regenerate API Key' : 'Create New API Key'}</DialogTitle>
              <DialogDescription>
                {apiKey 
                  ? 'Creating a new API key will replace your existing key. The old key will no longer work.'
                  : 'Create an API key for accessing the API. You can only have one API key per tenant.'}
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium">Name *</label>
                <Input
                  placeholder="e.g., Production API Key"
                  value={newKeyName}
                  onChange={(e) => setNewKeyName(e.target.value)}
                  className="mt-1"
                />
              </div>
              <div>
                <label className="text-sm font-medium">Description</label>
                <Textarea
                  placeholder="Optional description for this key"
                  value={newKeyDescription}
                  onChange={(e) => setNewKeyDescription(e.target.value)}
                  className="mt-1 resize-none"
                  rows={3}
                />
              </div>
              <div className="flex gap-2 justify-end">
                <Button
                  variant="outline"
                  onClick={() => {
                    setIsCreateDialogOpen(false);
                    setNewKeyName('');
                    setNewKeyDescription('');
                  }}
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleCreateKey}
                  disabled={isCreatingKey}
                >
                  {isCreatingKey ? 'Creating...' : 'Create'}
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {isDeleteDialogOpen && apiKey && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 rounded-lg">
          <div className="bg-white rounded-lg p-6 max-w-sm mx-auto space-y-4">
            <h2 className="text-lg font-semibold">Delete API Key</h2>
            <p className="text-sm text-gray-600">
              Are you sure you want to delete your API key? Once deleted, you'll need to create a new one to access the API. This action cannot be undone.
            </p>
            <div className="flex gap-2 justify-end">
              <Button
                variant="outline"
                onClick={() => setIsDeleteDialogOpen(false)}
              >
                Cancel
              </Button>
              <Button
                variant="destructive"
                onClick={handleDeleteKey}
              >
                Delete
              </Button>
            </div>
          </div>
        </div>
      )}

      {loading ? (
        <div className="rounded-lg border border-dashed p-12 text-center text-muted-foreground">
          Loading API key...
        </div>
      ) : !apiKey ? (
        <div className="rounded-lg border border-dashed p-12 text-center text-muted-foreground">
          <p>No API key created yet.</p>
          <p className="text-sm mt-2">Click the button above to create your API key.</p>
        </div>
      ) : (
        <div className="rounded-lg border p-6 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Name</p>
              <p className="text-lg font-semibold mt-1">{apiKey.name}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Key Preview</p>
              <p className="text-lg font-mono mt-1">{apiKey.key_preview}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Status</p>
              <span
                className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full mt-1 ${
                  apiKey.is_active
                    ? 'bg-green-50 text-green-700'
                    : 'bg-gray-50 text-gray-700'
                }`}
              >
                {apiKey.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Created</p>
              <p className="text-lg font-semibold mt-1">{formatDate(apiKey.created_at)}</p>
            </div>
            {apiKey.description && (
              <div className="md:col-span-2">
                <p className="text-sm font-medium text-muted-foreground">Description</p>
                <p className="text-base mt-1">{apiKey.description}</p>
              </div>
            )}
            <div className="md:col-span-2">
              <p className="text-sm font-medium text-muted-foreground">Last Used</p>
              <p className="text-lg font-semibold mt-1">{formatDate(apiKey.last_used_at)}</p>
            </div>
          </div>
          <div className="flex gap-2 justify-end pt-4 border-t">
            <Button
              variant="destructive"
              onClick={() => setIsDeleteDialogOpen(true)}
            >
              <HugeiconsIcon icon={Delete02Icon} strokeWidth={2} className="w-4 h-4 mr-2" />
              Delete API Key
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
