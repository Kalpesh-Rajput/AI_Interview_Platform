import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import LandingPage from './pages/LandingPage';
import UploadPage from './pages/UploadPage';
import QuestionsPage from './pages/QuestionsPage';
import JDAnalysisPage from './pages/JDAnalysisPage';
import ResumeAnalysisPage from './pages/ResumeAnalysisPage';

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<LandingPage />} />
        <Route path="upload" element={<UploadPage />} />
        <Route path="questions" element={<QuestionsPage />} />
        <Route path="jd-analysis" element={<JDAnalysisPage />} />
        <Route path="resume-analysis" element={<ResumeAnalysisPage />} />
      </Route>
    </Routes>
  );
}
