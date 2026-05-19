import { useCallback, useState } from 'react';

const ACCEPT = '.pdf,.doc,.docx,.txt';

export default function FileUpload({ label, description, fileInfo, onUpload, loading }) {
  const [dragOver, setDragOver] = useState(false);

  const handleFiles = useCallback(
    async (files) => {
      const file = files?.[0];
      if (!file) return;
      await onUpload(file);
    },
    [onUpload]
  );

  const onDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    handleFiles(e.dataTransfer.files);
  };

  return (
    <div className="card flex flex-col gap-4">
      <div>
        <h3 className="text-lg font-semibold text-white">{label}</h3>
        <p className="mt-1 text-sm text-gray-400">{description}</p>
      </div>

      <label
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
        className={`flex min-h-[180px] cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed px-6 py-8 transition ${
          dragOver
            ? 'border-accent bg-accent/5'
            : 'border-surface-border hover:border-accent/40 hover:bg-surface-elevated/50'
        }`}
      >
        <input
          type="file"
          accept={ACCEPT}
          className="hidden"
          disabled={loading}
          onChange={(e) => handleFiles(e.target.files)}
        />
        {loading ? (
          <div className="flex flex-col items-center gap-3">
            <div className="h-8 w-8 animate-spin rounded-full border-2 border-accent border-t-transparent" />
            <p className="text-sm text-gray-400">Processing file...</p>
          </div>
        ) : fileInfo?.filename ? (
          <div className="text-center">
            <p className="font-medium text-accent-light">{fileInfo.filename}</p>
            <p className="mt-2 text-xs text-gray-500">Click or drag to replace</p>
          </div>
        ) : (
          <div className="text-center">
            <svg className="mx-auto h-10 w-10 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            <p className="mt-3 text-sm text-gray-300">Drag & drop or click to upload</p>
            <p className="mt-1 text-xs text-gray-500">PDF, DOC, DOCX, TXT</p>
          </div>
        )}
      </label>

      {fileInfo?.preview && (
        <div className="rounded-xl bg-surface-elevated/60 p-4">
          <p className="mb-2 text-xs font-medium uppercase tracking-wider text-gray-500">Preview</p>
          <p className="line-clamp-4 text-sm leading-relaxed text-gray-300">{fileInfo.preview}</p>
        </div>
      )}
    </div>
  );
}
