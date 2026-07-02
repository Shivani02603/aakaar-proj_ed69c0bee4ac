import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { ingestFile } from '../api/aiApi';
import { toast } from 'react-toastify';

interface DocumentUploaderProps {
  sessionId: string;
}

const DocumentUploader: React.FC<DocumentUploaderProps> = ({ sessionId }) => {
  const [uploadProgress, setUploadProgress] = useState<number | null>(null);
  const [chunksIndexed, setChunksIndexed] = useState<number | null>(null);

  const onDrop = async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) {
      toast.error('No valid files selected.');
      return;
    }

    const file = acceptedFiles[0];
    setUploadProgress(0);
    setChunksIndexed(null);

    try {
      const response = await ingestFile(file, sessionId, (event: ProgressEvent) => {
        if (event.lengthComputable) {
          const progress = Math.round((event.loaded / event.total) * 100);
          setUploadProgress(progress);
        }
      });

      if (response.headers.get('Content-Type')?.includes('application/json')) {
        const data = await response.json();
        if (response.ok) {
          setChunksIndexed(data.chunks_indexed);
          toast.success('File successfully indexed!');
        } else {
          toast.error(data.message || 'Failed to index the file.');
        }
      } else {
        toast.error('Unexpected response from the server.');
      }
    } catch (error) {
      toast.error('An error occurred while uploading the file.');
    } finally {
      setUploadProgress(null);
    }
  };

  const { getRootProps, getInputProps } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
  });

  return (
    <div className="flex flex-col items-center justify-center p-4 border-2 border-dashed border-gray-300 rounded-lg">
      <div
        {...getRootProps()}
        className="w-full h-32 flex flex-col items-center justify-center cursor-pointer bg-gray-50 hover:bg-gray-100"
      >
        <input {...getInputProps()} />
        <p className="text-gray-500">Drag and drop a file here, or click to select a file</p>
        <p className="text-sm text-gray-400">Accepted formats: .pdf, .xlsx, .xls, .docx</p>
      </div>
      {uploadProgress !== null && (
        <div className="w-full mt-4">
          <div className="relative w-full h-4 bg-gray-200 rounded">
            <div
              className="absolute top-0 left-0 h-4 bg-blue-500 rounded"
              style={{ width: `${uploadProgress}%` }}
            ></div>
          </div>
          <p className="text-sm text-gray-500 mt-2">{uploadProgress}% uploaded</p>
        </div>
      )}
      {chunksIndexed !== null && (
        <div className="mt-4">
          <span className="px-3 py-1 text-sm font-medium text-green-800 bg-green-100 rounded-full">
            ✓ Indexed {chunksIndexed} chunks
          </span>
        </div>
      )}
    </div>
  );
};

export default DocumentUploader;