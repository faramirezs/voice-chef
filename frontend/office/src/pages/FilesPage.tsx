import { usePDFs, uploadPDF, deletePDF, getPDFUrl } from '@/api/pdfs';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { useEffect, useState, useRef } from 'react';
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
  const uploadSuccessTimerRef = useRef<number | null>(null);
  const queryClient = useQueryClient();
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [uploadBytesLoaded, setUploadBytesLoaded] = useState<number>(0);
  const [uploadBytesTotal, setUploadBytesTotal] = useState<number>(0);
  const [uploadFileName, setUploadFileName] = useState<string | null>(null);

  useEffect(() => {
    return () => {
      if (uploadSuccessTimerRef.current) {
        window.clearTimeout(uploadSuccessTimerRef.current);
      }
    };
  }, []);

  const uploadMutation = useMutation({
    mutationFn: ({
      file,
      onProgress,
    }: {
      file: File;
      onProgress?: Parameters<typeof uploadPDF>[1];
    }) => uploadPDF(file, onProgress),
    onSuccess: () => {
      setUploadError(null);
      setUploadSuccess('File uploaded successfully');
      setUploadProgress(0);
      setUploadBytesLoaded(0);
      setUploadBytesTotal(0);
      setUploadFileName(null);

      if (uploadSuccessTimerRef.current) {
        window.clearTimeout(uploadSuccessTimerRef.current);
      }
      uploadSuccessTimerRef.current = window.setTimeout(() => {
        setUploadSuccess(null);
        uploadSuccessTimerRef.current = null;
      }, 3000);

      queryClient.invalidateQueries({ queryKey: ['pdfs'] });
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    },
    onError: (err: any) => {
      setUploadError(err?.response?.data?.detail || 'Failed to upload file');
      setUploadSuccess(null);
      setUploadProgress(0);
      setUploadBytesLoaded(0);
      setUploadBytesTotal(0);
      setUploadFileName(null);
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
      setUploadError(null);
      setUploadFileName(file.name);
      setUploadBytesTotal(file.size);
      setUploadBytesLoaded(0);
      setUploadProgress(0);

      uploadMutation.mutate({
        file,
        onProgress: (progressEvent) => {
          if (!progressEvent.total) return;
          setUploadBytesLoaded(progressEvent.loaded);
          setUploadBytesTotal(progressEvent.total);
          setUploadProgress(Math.round((progressEvent.loaded / progressEvent.total) * 100));
        },
      });
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

      {uploadSuccess && (
        <div className="rounded-lg bg-green-50 p-4 text-sm text-green-700 border border-green-200">
          {uploadSuccess}
        </div>
      )}

      {uploadMutation.isPending && uploadFileName && (
        <div className="space-y-2 rounded-lg border bg-muted/20 p-4">
          <div className="flex items-center justify-between gap-4 text-sm">
            <div className="min-w-0">
              <p className="font-medium truncate">Uploading {uploadFileName}</p>
              <p className="text-muted-foreground">
                {formatFileSize(uploadBytesLoaded)} / {formatFileSize(uploadBytesTotal)}
              </p>
            </div>
            <p className="shrink-0 font-semibold">{uploadProgress}%</p>
          </div>
          <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
            <div
              className="h-full rounded-full bg-primary transition-all duration-200 ease-out"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
        </div>
      )}

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
