import { createContext, useContext, useState } from 'react';

const InterviewContext = createContext();

export function InterviewProvider({ children }) {
  const [jd, setJd] = useState({ filename: '', text: '', preview: '' });
  const [resume, setResume] = useState({ filename: '', text: '', preview: '' });
  const [questions, setQuestions] = useState([]);
  const [context, setContext] = useState(null);
  const [notes, setNotes] = useState({});
  const [meta, setMeta] = useState({ retries: 0, qualityScore: 0 });

  const reset = () => {
    setJd({ filename: '', text: '', preview: '' });
    setResume({ filename: '', text: '', preview: '' });
    setQuestions([]);
    setContext(null);
    setNotes({});
    setMeta({ retries: 0, qualityScore: 0 });
  };

  return (
    <InterviewContext.Provider
      value={{
        jd,
        setJd,
        resume,
        setResume,
        questions,
        setQuestions,
        context,
        setContext,
        notes,
        setNotes,
        meta,
        setMeta,
        reset,
      }}
    >
      {children}
    </InterviewContext.Provider>
  );
}

export function useInterview() {
  return useContext(InterviewContext);
}
