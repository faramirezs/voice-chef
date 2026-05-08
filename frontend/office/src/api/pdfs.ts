import { api } from './axios';
import type { AxiosProgressEvent } from 'axios';
import { useQuery } from '@tanstack/react-query';

export interface PDFFile {
  filename: string;
  size: number;
}

export const getPDFUrl = (filename: string): string => {
  return `/api/pdfs/${encodeURIComponent(filename)}`;
};

export const getPDFs = async (): Promise<PDFFile[]> => {
  const { data } = await api.get('/pdfs');
  return data;
};

export const usePDFs = () => {
  return useQuery({
    queryKey: ['pdfs'],
    queryFn: getPDFs,
  });
};

export const deletePDF = async (filename: string) => {
  await api.delete(`/pdfs/${filename}`);
};

export const uploadPDF = (
  file: File,
  onUploadProgress?: (progressEvent: AxiosProgressEvent) => void,
) => {
  const formData = new FormData();
  formData.append('file', file);

  return api.post('/pdfs', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress,
  });
};
