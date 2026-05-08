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
import { Copy01Icon, Trash02Icon } from '@hugeicons/core-free-icons';

export function APIKeysPage() {
  const [apiKeys, setApiKeys] = useState<APIKeyListResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [selectedKeyId, setSelectedKeyId] = useState<string | null>(null);
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
      setApiKeys(response.data);
    } catch (err) {
      setError('Failed to load API keys');
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
      await loadApiKeys();
    } catch (err) {
      setError('Failed to create API key');
      console.error(err);
    } finally {
      setIsCreatingKey(false);
    }
  };

  const handleDeleteKey = async () => {
    if (!selectedKeyId) return;

    try {
      setError(null);
      await deleteAPIKey(selectedKeyId);
      await loadApiKeys();
      setSelectedKeyId(null);
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
            <Button>Create API Key</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create New API Key</DialogTitle>
              <DialogDescription>
                Create a new API key for accessing the API.
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

      {isDeleteDialogOpen && selectedKeyId && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 rounded-lg">
          <div className="bg-white rounded-lg p-6 max-w-sm mx-auto space-y-4">
            <h2 className="text-lg font-semibold">Delete API Key</h2>
            <p className="text-sm text-gray-600">
              Are you sure you want to delete the API key? This action cannot be undone.
            </p>
            <div className="flex gap-2 justify-end">
              <Button
                variant="outline"
                onClick={() => {
                  setIsDeleteDialogOpen(false);
                  setSelectedKeyId(null);
                }}
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
          Loading API keys...
        </div>
      ) : apiKeys.length === 0 ? (
        <div className="rounded-lg border border-dashed p-12 text-center text-muted-foreground">
          No API keys created yet. Create one to get started.
        </div>
      ) : (
        <div className="rounded-lg border overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-4 py-3 text-left font-semibold">Name</th>
                  <th className="px-4 py-3 text-left font-semibold">Key Preview</th>
                  <th className="px-4 py-3 text-left font-semibold">Description</th>
                  <th className="px-4 py-3 text-left font-semibold">Status</th>
                  <th className="px-4 py-3 text-left font-semibold">Created</th>
                  <th className="px-4 py-3 text-left font-semibold">Last Used</th>
                  <th className="px-4 py-3 text-center font-semibold">Actions</th>
                </tr>
              </thead>
              <tbody>
                {apiKeys.map((key) => (
                  <tr key={key.id} className="border-b hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium">{key.name}</td>
                    <td className="px-4 py-3 font-mono text-xs">{key.key_preview}</td>
                    <td className="px-4 py-3 max-w-xs truncate">
                      {key.description || '-'}
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          key.is_active
                            ? 'bg-green-50 text-green-700'
                            : 'bg-gray-50 text-gray-700'
                        }`}
                      >
                        {key.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-4 py-3">{formatDate(key.created_at)}</td>
                    <td className="px-4 py-3">{formatDate(key.last_used_at)}</td>
                    <td className="px-4 py-3 text-center">
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => {
                          setSelectedKeyId(key.id);
                          setIsDeleteDialogOpen(true);
                        }}
                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                      >
                        <HugeiconsIcon icon={Trash02Icon} strokeWidth={2} className="w-4 h-4" />
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
