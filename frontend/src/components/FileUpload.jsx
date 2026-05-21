import { useCallback, useState, useEffect } from 'react';

const ACCEPT = '.pdf,.doc,.docx,.txt';

export default function FileUpload({
  label,
  description,
  fileInfo,
  onUpload,
  loading,
  onTextChange,
  placeholder = 'Paste your text here...'
}) {
  const [dragOver, setDragOver] = useState(false);

  // Detect if the fileInfo represents a pasted input
  const isPasted = fileInfo?.filename?.startsWith('Pasted') || false;
  const [mode, setMode] = useState(isPasted ? 'paste' : 'file');

  // Sync mode if fileInfo changes externally (e.g. on reset)
  useEffect(() => {
    if (!fileInfo?.text) {
      if (!fileInfo?.filename) {
        setMode('file');
      }
    } else if (isPasted) {
      setMode('paste');
    } else {
      setMode('file');
    }
  }, [fileInfo?.text, fileInfo?.filename, isPasted]);

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

  const getWordCount = (str) => {
    if (!str) return 0;
    return str.trim().split(/\s+/).filter(Boolean).length;
  };

  const getCharCount = (str) => {
    return str?.length || 0;
  };

  return (
    <div className="card flex flex-col gap-4">
      {/* Header section with layout and Tabs */}
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
        <div>
          <h3 className="text-lg font-semibold text-ink dark:text-white">{label}</h3>
          <p className="mt-1 text-sm text-ink-muted dark:text-gray-400">{description}</p>
        </div>

        {onTextChange && (
          <div className="inline-flex rounded-xl bg-cream-muted/50 p-1 dark:bg-surface-elevated/40 border border-cream-dark/10 dark:border-surface-border/40 shrink-0 self-start sm:self-center">
            <button
              type="button"
              onClick={() => setMode('file')}
              className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition-all duration-200 ${
                mode === 'file'
                  ? 'bg-white text-accent dark:bg-surface dark:text-accent-light shadow-soft'
                  : 'text-ink-muted hover:text-ink dark:text-gray-400 dark:hover:text-white'
              }`}
            >
              Upload File
            </button>
            <button
              type="button"
              onClick={() => setMode('paste')}
              className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition-all duration-200 ${
                mode === 'paste'
                  ? 'bg-white text-accent dark:bg-surface dark:text-accent-light shadow-soft'
                  : 'text-ink-muted hover:text-ink dark:text-gray-400 dark:hover:text-white'
              }`}
            >
              Paste Text
            </button>
          </div>
        )}
      </div>

      {mode === 'file' ? (
        <>
          <label
            onDragOver={(e) => {
              e.preventDefault();
              setDragOver(true);
            }}
            onDragLeave={() => setDragOver(false)}
            onDrop={onDrop}
            className={`flex min-h-[200px] cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed px-6 py-8 transition duration-300 ${
              dragOver
                ? 'border-accent bg-accent/5'
                : 'border-cream-dark hover:border-accent/40 hover:bg-cream-muted/50 dark:border-surface-border dark:hover:bg-surface-elevated/50'
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
            ) : fileInfo?.filename && !isPasted ? (
              <div className="text-center">
                <p className="font-semibold text-accent-light text-base">{fileInfo.filename}</p>
                <p className="mt-2 text-xs text-ink-faint dark:text-gray-500">Click or drag to replace file</p>
              </div>
            ) : (
              <div className="text-center">
                <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-cream-muted dark:bg-surface-elevated text-ink-muted dark:text-gray-400 mb-3">
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                </div>
                <p className="text-sm font-medium text-ink dark:text-gray-300">Drag & drop or click to upload</p>
                <p className="mt-1 text-xs text-ink-faint dark:text-gray-500">PDF, DOC, DOCX, TXT</p>
              </div>
            )}
          </label>

          {fileInfo?.preview && !isPasted && (
            <div className="rounded-2xl bg-cream-muted/60 p-4 dark:bg-surface-elevated/40 border border-cream-dark/10 dark:border-surface-border/20 transition-all duration-300">
              <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-accent dark:text-accent-light">Parsed Preview</p>
              <p className="line-clamp-4 text-sm leading-relaxed text-ink-muted dark:text-gray-300">{fileInfo.preview}</p>
            </div>
          )}
        </>
      ) : (
        <div className="flex flex-col gap-2">
          <div className="relative">
            <textarea
              value={isPasted ? fileInfo?.text || '' : ''}
              onChange={(e) => onTextChange(e.target.value)}
              placeholder={placeholder}
              className="w-full min-h-[200px] rounded-2xl border border-cream-dark bg-white p-4 text-sm leading-relaxed text-ink placeholder-ink-faint focus:outline-none focus:ring-2 focus:ring-accent/20 focus:border-accent dark:border-surface-border dark:bg-surface-card dark:text-gray-100 dark:placeholder-gray-500 transition-all duration-300 font-sans resize-y"
            />
            {isPasted && fileInfo?.text && (
              <button
                type="button"
                onClick={() => onTextChange('')}
                className="absolute top-3 right-3 text-xs bg-cream-dark/40 hover:bg-cream-dark/80 dark:bg-surface-elevated/60 dark:hover:bg-surface-elevated text-ink-muted dark:text-gray-400 hover:text-ink dark:hover:text-white px-2.5 py-1 rounded-lg transition-all duration-200"
              >
                Clear
              </button>
            )}
          </div>
          <div className="flex justify-between items-center px-1 text-xs text-ink-faint dark:text-gray-500">
            <span>
              {getWordCount(isPasted ? fileInfo?.text : '')} words
            </span>
            <span>
              {getCharCount(isPasted ? fileInfo?.text : '')} characters
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
