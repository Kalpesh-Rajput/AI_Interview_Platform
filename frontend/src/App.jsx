import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import LandingPage from './pages/LandingPage';
import UploadPage from './pages/UploadPage';
import QuestionsPage from './pages/QuestionsPage';

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<LandingPage />} />
        <Route path="upload" element={<UploadPage />} />
        <Route path="questions" element={<QuestionsPage />} />
      </Route>
    </Routes>
  );
}
