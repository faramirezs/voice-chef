import { usePDFs, uploadPDF, deletePDF, getPDFUrl } from '@/api/pdfs';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { useState, useRef } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { HugeiconsIcon } from '@hugeicons/react';
import { Delete02Icon } from '@hugeicons/core-free-icons';

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

export function FilesPage() {
  const { data: pdfs = [], isLoading, error } = usePDFs();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const queryClient = useQueryClient();
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  const uploadMutation = useMutation({
    mutationFn: uploadPDF,
    onSuccess: () => {
      setUploadError(null);
      queryClient.invalidateQueries({ queryKey: ['pdfs'] });
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    },
    onError: (err: any) => {
      setUploadError(err?.response?.data?.detail || 'Failed to upload file');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deletePDF,
    onSuccess: () => {
      setDeleteError(null);
      queryClient.invalidateQueries({ queryKey: ['pdfs'] });
    },
    onError: (err: any) => {
      setDeleteError(err?.response?.data?.detail || 'Failed to delete file');
    },
  });

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      uploadMutation.mutate(file);
    }
  };

  const handleDelete = (filename: string) => {
    if (window.confirm(`Are you sure you want to delete "${filename}"?`)) {
      deleteMutation.mutate(filename);
    }
  };

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold">Files</h1>
        <p className="text-muted-foreground">Manage your files here</p>
      </div>

      <div className="flex gap-2">
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          onChange={handleFileSelect}
          disabled={uploadMutation.isPending}
          className="hidden"
        />
        <Button
          onClick={() => fileInputRef.current?.click()}
          disabled={uploadMutation.isPending}
        >
          {uploadMutation.isPending ? 'Uploading...' : 'Upload PDF'}
        </Button>
      </div>

      {uploadError && (
        <div className="p-4 bg-destructive/10 text-destructive rounded-md">
          {uploadError}
        </div>
      )}

      {deleteError && (
        <div className="p-4 bg-destructive/10 text-destructive rounded-md">
          {deleteError}
        </div>
      )}

      <div className="space-y-4">
        <h2 className="text-xl font-semibold">PDF Files</h2>
        
        {isLoading && (
          <div className="space-y-2">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-12 w-full" />
            ))}
          </div>
        )}

        {error && (
          <div className="p-4 bg-destructive/10 text-destructive rounded-md">
            Error loading files
          </div>
        )}

        {!isLoading && pdfs.length === 0 && (
          <div className="p-6 text-center text-muted-foreground border border-dashed rounded-md">
            No PDF files found
          </div>
        )}

        {!isLoading && pdfs.length > 0 && (
          <div className="border rounded-lg">
            <table className="w-full">
              <thead className="border-b bg-muted/50">
                <tr>
                  <th className="text-left p-4 font-semibold">Filename</th>
                  <th className="text-right p-4 font-semibold">Size</th>
                  <th className="text-right p-4 font-semibold">Actions</th>
                </tr>
              </thead>
              <tbody>
                {pdfs.map((pdf) => (
                  <tr key={pdf.filename} className="border-b hover:bg-muted/30 transition-colors">
                    <td className="p-4">
                      <a 
                        href={getPDFUrl(pdf.filename)}
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-primary hover:underline truncate"
                      >
                        {pdf.filename}
                      </a>
                    </td>
                    <td className="p-4 text-right text-sm text-muted-foreground">
                      {formatFileSize(pdf.size)}
                    </td>
                    <td className="p-4 text-right">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDelete(pdf.filename)}
                        disabled={deleteMutation.isPending}
                        className="text-destructive hover:text-destructive hover:bg-destructive/10"
                      >
                        <HugeiconsIcon icon={Delete02Icon} strokeWidth={2} />
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
