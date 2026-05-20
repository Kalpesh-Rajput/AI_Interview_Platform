import axios from 'axios';


const api = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_URL || "http://localhost:8000",
  timeout: 180000,
});

export async function uploadJD(file) {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await api.post('/api/interview/upload/jd', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

export async function uploadResume(file) {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await api.post('/api/interview/upload/resume', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

export async function generateQuestions(jdText, resumeText) {
  const { data } = await api.post('/api/interview/generate', {
    jd_text: jdText,
    resume_text: resumeText,
  });
  return data;
}

export default api;
