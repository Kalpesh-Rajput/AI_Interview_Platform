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

  const handleGenerate = async () => {
    if (!jd.text || !resume.text) {
      setError('Please upload both a job description and a resume.');
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
          <h1 className="text-3xl font-bold text-white">Upload Workspace</h1>
          <p className="mt-2 text-gray-400">
            Upload the job description and candidate resume to generate contextual interview questions.
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
            description="Role requirements, tech stack, and responsibilities"
            fileInfo={jd}
            onUpload={handleJD}
            loading={jdLoading}
          />
          <FileUpload
            label="Candidate Resume"
            description="Projects, experience, and technical skills"
            fileInfo={resume}
            onUpload={handleResume}
            loading={resumeLoading}
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
            <p className="text-sm text-gray-500">Upload both documents to continue</p>
          )}
        </div>
      </section>
    </>
  );
}
