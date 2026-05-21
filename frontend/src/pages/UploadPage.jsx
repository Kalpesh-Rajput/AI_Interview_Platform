import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import FileUpload from '../components/FileUpload';
import LoadingOverlay from '../components/LoadingOverlay';
import { useInterview } from '../context/InterviewContext';
import { uploadJD, uploadResume, generateQuestions } from '../services/api';

export default function UploadPage() {
  const navigate = useNavigate();
  const { jd, setJd, resume, setResume, setQuestions, setContext, setMeta } = useInterview();
  const [jdLoading, setJdLoading] = useState(false);
  const [resumeLoading, setResumeLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState('');

  const handleJD = async (file) => {
    setError('');
    setJdLoading(true);
    try {
      const data = await uploadJD(file);
      setJd({ filename: data.filename, text: data.text, preview: data.preview });
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to upload JD');
    } finally {
      setJdLoading(false);
    }
  };

  const handleResume = async (file) => {
    setError('');
    setResumeLoading(true);
    try {
      const data = await uploadResume(file);
      setResume({ filename: data.filename, text: data.text, preview: data.preview });
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to upload resume');
    } finally {
      setResumeLoading(false);
    }
  };

  const handleJdTextChange = (text) => {
    if (!text) {
      setJd({ filename: '', text: '', preview: '' });
    } else {
      setJd({
        filename: 'Pasted Job Description',
        text: text,
        preview: text.slice(0, 500),
      });
    }
  };

  const handleResumeTextChange = (text) => {
    if (!text) {
      setResume({ filename: '', text: '', preview: '' });
    } else {
      setResume({
        filename: 'Pasted Resume',
        text: text,
        preview: text.slice(0, 500),
      });
    }
  };

  const handleGenerate = async () => {
    if (!jd.text || !resume.text) {
      setError('Please upload or paste both a job description and a resume.');
      return;
    }
    setError('');
    setGenerating(true);
    try {
      const data = await generateQuestions(jd.text, resume.text);
      setQuestions(data.questions);
      setContext(data.context);
      setMeta({ retries: data.retries, qualityScore: data.quality_score });
      navigate('/questions');
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Generation failed');
    } finally {
      setGenerating(false);
    }
  };

  const ready = jd.text && resume.text;

  return (
    <>
      <LoadingOverlay active={generating} />
      <section className="mx-auto max-w-6xl px-6 py-12">
        <div className="mb-10">
          <h1 className="text-3xl font-bold tracking-tight text-ink dark:text-white">Upload Workspace</h1>
          <p className="mt-2 text-ink-muted dark:text-gray-400">
            Upload or paste the job description and candidate resume to generate contextual interview questions.
          </p>
        </div>

        {error && (
          <div className="mb-6 rounded-xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-300">
            {error}
          </div>
        )}

        <div className="grid gap-8 lg:grid-cols-2">
          <FileUpload
            label="Job Description"
            description="Role requirements and responsibilities"
            fileInfo={jd}
            onUpload={handleJD}
            loading={jdLoading}
            onTextChange={handleJdTextChange}
            placeholder="Paste the complete job description details including requirements and responsibilities here..."
          />
          <FileUpload
            label="Candidate Resume"
            description="Projects, experience, and technical skills"
            fileInfo={resume}
            onUpload={handleResume}
            loading={resumeLoading}
            onTextChange={handleResumeTextChange}
            placeholder="Paste the candidate's resume text, including work history, technical skills, projects, and education here..."
          />
        </div>

        <div className="mt-10 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
          <button
            onClick={handleGenerate}
            disabled={!ready || generating}
            className="btn-primary min-w-[220px] disabled:cursor-not-allowed disabled:opacity-50"
          >
            {generating ? 'Generating...' : 'Generate 10 Questions'}
          </button>
          {!ready && (
            <p className="text-sm text-ink-faint dark:text-gray-500">Provide both documents to continue</p>
          )}
        </div>
      </section>
    </>
  );
}
