'use client';

import React, { useState } from 'react';
import katex from 'katex';

function MathSpan({ math, block = false }: { math: string; block?: boolean }) {
  try {
    const html = katex.renderToString(math, {
      displayMode: block,
      throwOnError: false,
    });
    return <span dangerouslySetInnerHTML={{ __html: html }} />;
  } catch (err) {
    return <span>{math}</span>;
  }
}


interface ChatSource {
  document_title: string;
  chapter?: string;
  page_number?: number;
}

interface ChatResponse {
  text: string;
  subject: string;
  intent: string;
  exam?: string;
  sources: ChatSource[];
}

interface MCQQuestion {
  id: number;
  question: string;
  options: Record<string, string>;
  correct_option: string;
  explanation: string;
}

interface QuizResponse {
  questions: MCQQuestion[];
  subject: string;
  exam?: string;
}

interface EvaluationResponse {
  score: number;
  max_score: number;
  feedback: string;
  missing_points: string[];
  revision_tip: string;
}

export default function StudyMateDashboard() {
  // Input states
  const [yearOfStudy, setYearOfStudy] = useState('2nd PUC');
  const [board, setBoard] = useState('Karnataka State Board');
  const [subject, setSubject] = useState('physics');
  const [prompt, setPrompt] = useState('');
  
  // App mode & UI states
  const [activeTab, setActiveTab] = useState<'chat' | 'quiz' | 'evaluate'>('chat');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Result states
  const [chatResult, setChatResult] = useState<ChatResponse | null>(null);
  const [quizResult, setQuizResult] = useState<QuizResponse | null>(null);
  const [studentAnswers, setStudentAnswers] = useState<Record<string, string>>({});
  const [evaluationResult, setEvaluationResult] = useState<EvaluationResponse | null>(null);

  // Use the environment base URL or fall back to local backend port
  const backendUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8080';

  // Custom response text parser to render math equations and markdown content beautifully
  const formatResponseText = (text: string) => {
    if (!text) return null;
    
    // Split by LaTeX math block delimiters $$
    const parts = text.split(/\$\$([\s\S]*?)\$\$/g);
    return parts.map((part, index) => {
      // Odd indexes are math formulas
      if (index % 2 === 1) {
        return (
          <div 
            key={index} 
            className="my-6 p-5 bg-slate-950/80 border border-sky-500/20 border-l-4 border-l-sky-400 rounded-r-2xl text-center shadow-lg overflow-x-auto text-base backdrop-blur-sm"
          >
            <MathSpan math={part.trim()} block={true} />
          </div>
        );
      }
      
      // Even indexes are standard text / markdown lines
      const lines = part.split('\n');
      return lines.map((line, lIdx) => {
        const trimmed = line.trim();
        
        // 1. Heading level 3 check (### Heading)
        if (trimmed.startsWith('###')) {
          return (
            <h3 key={lIdx} className="text-base font-bold text-sky-400 mt-6 mb-3 tracking-wide border-b border-slate-800 pb-1.5 uppercase text-xs">
              {parseInlineElements(trimmed.replace('###', '').trim())}
            </h3>
          );
        }
        
        // 2. Heading level 2 check (## Heading)
        if (trimmed.startsWith('##')) {
          return (
            <h2 key={lIdx} className="text-lg font-extrabold text-indigo-400 mt-8 mb-4 tracking-wide border-b border-indigo-950/80 pb-2">
              {parseInlineElements(trimmed.replace('##', '').trim())}
            </h2>
          );
        }

        // 3. Math formula line detection
        const isMathFormulaLine = (t: string) => {
          const s = t.trim();
          if (!s) return false;
          if (s.startsWith('\\') || s.includes('\\frac') || s.includes('\\text') || s.includes('\\Delta') || s.includes('^') || s.includes('_')) {
            const spaces = s.split(' ').length;
            if (spaces <= 5 || s.includes('\\text{') || s.includes('=')) {
              return true;
            }
          }
          return false;
        };

        if (isMathFormulaLine(trimmed)) {
          return (
            <div key={lIdx} className="my-6 p-4 bg-slate-950/80 border border-sky-500/10 border-l-4 border-l-sky-500 rounded-r-2xl text-center shadow-lg overflow-x-auto text-base backdrop-blur-sm">
              <MathSpan math={trimmed} block={true} />
            </div>
          );
        }

        // 4. Simple list item check (* or -)
        if (trimmed.startsWith('*') || trimmed.startsWith('-')) {
          const cleanedLine = trimmed.replace(/^[\*\-]\s*/, '');
          return (
            <li key={lIdx} className="ml-6 text-sm text-slate-300 list-disc leading-relaxed my-2 pl-1">
              {parseInlineElements(cleanedLine)}
            </li>
          );
        }
        
        // 5. Empty paragraph check
        if (trimmed === '') {
          return <div key={lIdx} className="h-3"></div>;
        }

        // 6. Default text block
        return (
          <p key={lIdx} className="text-sm text-slate-300 leading-relaxed my-2.5">
            {parseInlineElements(trimmed)}
          </p>
        );
      });
    });
  };

  const parseInlineElements = (text: string) => {
    if (!text) return null;
    const parts = text.split(/(\$\$[\s\S]*?\$\$|\$.*?\$|\*\*.*?\*\*)/g);
    return parts.map((part, index) => {
      if (part.startsWith('$$') && part.endsWith('$$')) {
        const math = part.slice(2, -2).trim();
        return <MathSpan key={index} math={math} block={true} />;
      }
      if (part.startsWith('$') && part.endsWith('$')) {
        const math = part.slice(1, -1).trim();
        return <MathSpan key={index} math={math} block={false} />;
      }
      if (part.startsWith('**') && part.endsWith('**')) {
        const boldText = part.slice(2, -2);
        return <strong key={index} className="text-slate-100 font-bold bg-slate-800/40 px-1 py-0.5 rounded">{boldText}</strong>;
      }
      return part;
    });
  };

  // Handle Ask Question submission
  const handleChatSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    setLoading(true);
    setError(null);
    setChatResult(null);

    try {
      const response = await fetch(`${backendUrl}/api/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          year: yearOfStudy,
          board: board,
          subject: subject,
          query: prompt,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch response from agent.');
      }

      const rawData = await response.json();
      const mappedData: ChatResponse = {
        text: rawData.answer || rawData.text || '',
        subject: rawData.metadata?.subject || rawData.subject || '',
        intent: rawData.metadata?.intent || rawData.intent || '',
        exam: rawData.metadata?.exam || rawData.exam,
        sources: (rawData.sources || []).map((s: any) => ({
          document_title: s.title || s.document_title || '',
          chapter: s.chapter,
          page_number: s.page_number
        }))
      };
      setChatResult(mappedData);
    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred.');
    } finally {
      setLoading(false);
    }
  };

  // Handle Quiz Generation
  const handleQuizSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    setLoading(true);
    setError(null);
    setQuizResult(null);
    setStudentAnswers({});
    setEvaluationResult(null);

    try {
      const response = await fetch(`${backendUrl}/api/v1/quiz`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          year: yearOfStudy,
          board: board,
          subject: subject,
          query: prompt,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to generate quiz.');
      }

      const data: QuizResponse = await response.json();
      setQuizResult(data);
      setActiveTab('quiz'); // Swap directly to Quiz Tab view
    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred.');
    } finally {
      setLoading(false);
    }
  };

  // Handle Quiz Submission / Evaluation
  const handleEvaluateSubmit = async () => {
    if (!quizResult) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${backendUrl}/api/v1/evaluate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          questions: quizResult.questions,
          student_answers: studentAnswers,
          subject: quizResult.subject,
          exam: quizResult.exam,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to evaluate answers.');
      }

      const data: EvaluationResponse = await response.json();
      setEvaluationResult(data);
      setActiveTab('evaluate'); // Switch view tab to show score
    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred.');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectOption = (questionId: number, optionKey: string) => {
    setStudentAnswers((prev) => ({
      ...prev,
      [questionId.toString()]: optionKey,
    }));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 p-4 md:p-12 text-slate-100 antialiased font-sans">
      
      {/* Sleek Header Design with Brand Colors */}
      <header className="max-w-6xl mx-auto mb-10 text-center relative">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-48 h-12 bg-sky-500/10 rounded-full blur-3xl -z-10"></div>
        <h1 className="text-3xl md:text-5xl font-black tracking-tight bg-gradient-to-r from-sky-400 via-sky-200 to-indigo-400 bg-clip-text text-transparent">
          StudyMateAI
        </h1>
        <p className="mt-2 text-slate-400 text-xs md:text-sm font-medium tracking-wide uppercase">
          Your AI Partner to Learn, Practice, and Excel
        </p>
      </header>

      {/* Main Container Dashboard layout */}
      <main className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        
        {/* Left Side: Configuration Card */}
        <section className="lg:col-span-5 bg-slate-900/50 backdrop-blur-xl rounded-3xl border border-slate-800 p-6 md:p-8 shadow-2xl relative overflow-hidden">
          <div className="absolute top-0 right-0 w-24 h-24 bg-gradient-to-b from-indigo-500/5 to-transparent rounded-full blur-2xl"></div>
          <h2 className="text-sm font-bold tracking-widest text-sky-400 uppercase mb-6 flex items-center gap-2">
            <span className="w-1.5 h-3 bg-sky-400 rounded-full"></span> Learning Context
          </h2>
          
          <div className="space-y-5">
            <div>
              <label htmlFor="year-select" className="block text-[11px] font-bold text-slate-400 uppercase tracking-widest mb-2">Year of Study</label>
              <select
                id="year-select"
                value={yearOfStudy}
                onChange={(e) => setYearOfStudy(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-sky-500/40 focus:border-sky-500 cursor-pointer transition duration-200"
              >
                <option value="1st PUC">1st PUC / Class 11</option>
                <option value="2nd PUC">2nd PUC / Class 12</option>
                <option value="Class 10">Class 10</option>
              </select>
            </div>

            <div>
              <label htmlFor="board-select" className="block text-[11px] font-bold text-slate-400 uppercase tracking-widest mb-2">University / Board</label>
              <select
                id="board-select"
                value={board}
                onChange={(e) => setBoard(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-sky-500/40 focus:border-sky-500 cursor-pointer transition duration-200"
              >
                <option value="Karnataka State Board">Karnataka State Board</option>
                <option value="CBSE">CBSE</option>
              </select>
            </div>

            <div>
              <label htmlFor="subject-select" className="block text-[11px] font-bold text-slate-400 uppercase tracking-widest mb-2">Subject</label>
              <select
                id="subject-select"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-sky-500/40 focus:border-sky-500 cursor-pointer transition duration-200"
              >
                <option value="physics">Physics</option>
                <option value="chemistry">Chemistry</option>
              </select>
            </div>
            
            <div className="border-t border-slate-800/80 pt-5">
              <label htmlFor="prompt-input" className="block text-[11px] font-bold text-slate-400 uppercase tracking-widest mb-2">Ask or Generate</label>
              <textarea
                id="prompt-input"
                rows={4}
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="e.g., Explain Ray Optics for NEET, or Generate KCET quiz on Atomic Structure"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-sky-500/40 focus:border-sky-500 resize-none transition duration-200"
              />
            </div>

            <div className="flex gap-4 pt-2">
              <button
                onClick={handleChatSubmit}
                disabled={loading || !prompt.trim()}
                className="flex-1 bg-gradient-to-r from-sky-600 to-sky-500 hover:from-sky-500 hover:to-sky-400 active:scale-95 disabled:scale-100 disabled:opacity-50 text-white text-xs font-bold py-3.5 rounded-xl transition duration-200 shadow-lg shadow-sky-950/40"
              >
                Ask Buddy
              </button>
              <button
                onClick={handleQuizSubmit}
                disabled={loading || !prompt.trim()}
                className="flex-1 bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 active:scale-95 disabled:scale-100 disabled:opacity-50 text-white text-xs font-bold py-3.5 rounded-xl transition duration-200 shadow-lg shadow-indigo-950/40"
              >
                Get Quiz
              </button>
            </div>
          </div>
        </section>

        {/* Right Side: Workspace output container */}
        <section className="lg:col-span-7 bg-slate-900/40 backdrop-blur-xl rounded-3xl border border-slate-800/80 p-6 md:p-8 shadow-2xl flex flex-col min-h-[500px]">
          
          {/* Navigation Tab selection */}
          <div className="flex border-b border-slate-800/80 pb-4 mb-6 gap-6">
            <button
              onClick={() => setActiveTab('chat')}
              className={`text-xs font-bold tracking-wider uppercase transition pb-2.5 border-b-2 ${activeTab === 'chat' ? 'text-sky-400 border-sky-400' : 'text-slate-500 border-transparent hover:text-slate-300'}`}
            >
              Mentor response
            </button>
            <button
              onClick={() => setActiveTab('quiz')}
              className={`text-xs font-bold tracking-wider uppercase transition pb-2.5 border-b-2 ${activeTab === 'quiz' ? 'text-sky-400 border-sky-400' : 'text-slate-500 border-transparent hover:text-slate-300'}`}
            >
              Active Quiz {quizResult ? `(${(quizResult.questions || []).length})` : ''}
            </button>
            <button
              onClick={() => setActiveTab('evaluate')}
              className={`text-xs font-bold tracking-wider uppercase transition pb-2.5 border-b-2 ${activeTab === 'evaluate' ? 'text-sky-400 border-sky-400' : 'text-slate-500 border-transparent hover:text-slate-300'}`}
            >
              Self-Assessment
            </button>
          </div>

          {/* Active Tab Output renderer */}
          <div className="flex-1">
            {loading && (
              <div className="flex flex-col items-center justify-center py-24">
                <div className="relative">
                  <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-sky-400"></div>
                  <div className="absolute top-0 left-0 w-12 h-12 border-2 border-sky-400/10 rounded-full"></div>
                </div>
                <span className="mt-4 text-slate-400 text-xs font-medium uppercase tracking-wider animate-pulse">Consulting SME Agents...</span>
              </div>
            )}

            {error && (
              <div className="bg-red-950/30 border border-red-900/60 text-red-200 text-xs rounded-xl p-4 mb-6 leading-relaxed shadow-lg">
                <span className="font-extrabold text-red-400 uppercase tracking-wider block mb-1">Execution Failure:</span>
                {error}
              </div>
            )}

            {!loading && !error && (
              <div className="animation-fade-in">
                
                {/* Chat tab panel view */}
                {activeTab === 'chat' && (
                  <div className="space-y-6">
                    {chatResult ? (
                      <div className="space-y-6">
                        <div className="flex justify-between items-center bg-slate-950/60 px-4 py-2.5 rounded-xl border border-slate-800/80 text-[10px] font-bold text-slate-400 tracking-wider">
                          <span className="uppercase">Subject: {chatResult.subject}</span>
                          <span className="uppercase">Intent: {chatResult.intent.replace('_', ' ')}</span>
                          {chatResult.exam && <span className="bg-sky-950/80 text-sky-400 px-2 py-0.5 rounded font-black uppercase">{chatResult.exam} Mode</span>}
                        </div>
                        
                        {/* Beautified AI Output Text */}
                        <div className="text-slate-300 leading-relaxed text-sm bg-slate-950/20 rounded-2xl p-2">
                          {formatResponseText(chatResult.text)}
                        </div>

                        {/* Collapsible references map list */}
                        {chatResult.sources && chatResult.sources.length > 0 && (
                          <div className="mt-8 border-t border-slate-800/80 pt-5">
                            <h4 className="text-[10px] font-bold text-sky-400 tracking-wider uppercase mb-3">Academic Grounds / Reference Sources</h4>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                              {chatResult.sources.map((src, i) => (
                                <div key={i} className="bg-slate-950/40 border border-slate-800/60 p-3 rounded-xl hover:border-slate-700/80 transition duration-200">
                                  <div className="text-xs font-semibold text-slate-200 truncate">{src.document_title}</div>
                                  <div className="text-[10px] text-slate-500 mt-1 flex justify-between">
                                    <span>{src.chapter ? `Chapter: ${src.chapter}` : 'Curriculum Chunks'}</span>
                                    {src.page_number && <span className="text-sky-400 font-bold">Page {src.page_number}</span>}
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="text-center text-slate-500 py-24 flex flex-col items-center">
                        <svg className="w-10 h-10 text-slate-700 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                        </svg>
                        <p className="text-xs font-bold uppercase tracking-wider mb-1.5 text-slate-400">Ask Your Doubt</p>
                        <p className="text-xs text-slate-500 max-w-sm">Enter your learning topic or concept doubt on the left, then click &quot;Ask Buddy&quot; to review curriculum explanations.</p>
                      </div>
                    )}
                  </div>
                )}

                {/* Quiz tab panel view */}
                {activeTab === 'quiz' && (
                  <div className="space-y-6">
                    {quizResult ? (
                      <div className="space-y-6">
                        <div className="flex justify-between items-center bg-slate-950/60 px-4 py-2.5 rounded-xl border border-slate-800/80 text-[10px] font-bold text-slate-400 tracking-wider">
                          <span className="uppercase">Topic Assessment: {quizResult.subject}</span>
                          {quizResult.exam && <span className="bg-indigo-950/80 text-indigo-400 px-2 py-0.5 rounded font-black uppercase">{quizResult.exam} Format</span>}
                        </div>
                        
                        <div className="space-y-5">
                          {(quizResult.questions || []).map((q, idx) => (
                            <div key={q.id} className="bg-slate-950/40 border border-slate-800/60 p-5 rounded-2xl hover:border-slate-800 transition duration-200">
                              <h3 className="text-xs font-bold text-slate-400 tracking-wider uppercase mb-2">Question {idx + 1}</h3>
                              <p className="text-sm font-semibold text-slate-100 mb-4">{q.question}</p>
                              
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                {Object.entries(q.options).map(([key, value]) => {
                                  const isSelected = studentAnswers[q.id.toString()] === key;
                                  return (
                                    <button
                                      key={key}
                                      onClick={() => handleSelectOption(q.id, key)}
                                      className={`text-left text-xs p-3.5 rounded-xl border transition-all duration-200 ${
                                        isSelected
                                          ? 'bg-sky-500/10 border-sky-500 text-sky-200 shadow-md shadow-sky-500/5'
                                          : 'bg-slate-900/30 border-slate-800/60 text-slate-400 hover:bg-slate-900/80 hover:text-slate-200'
                                      }`}
                                    >
                                      <span className={`font-bold mr-2 text-[10px] px-1.5 py-0.5 rounded ${
                                        isSelected ? 'bg-sky-500 text-slate-950' : 'bg-slate-950 text-sky-400'
                                      }`}>{key}</span> {value}
                                    </button>
                                  );
                                })}
                              </div>
                            </div>
                          ))}
                        </div>
                        
                        <div className="mt-6 flex justify-end">
                          <button
                            onClick={handleEvaluateSubmit}
                            disabled={Object.keys(studentAnswers).length < (quizResult.questions || []).length}
                            className="bg-sky-600 hover:bg-sky-500 active:scale-95 disabled:scale-100 disabled:opacity-50 text-white text-xs font-bold px-6 py-3.5 rounded-xl transition duration-200 shadow-lg shadow-sky-950/40"
                          >
                            Submit and Evaluate
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className="text-center text-slate-500 py-24 flex flex-col items-center">
                        <svg className="w-10 h-10 text-slate-700 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                        </svg>
                        <p className="text-xs font-bold uppercase tracking-wider mb-1.5 text-slate-400">Knowledge Assessment</p>
                        <p className="text-xs text-slate-500 max-w-sm">Enter your learning topic on the left and click &quot;Get Quiz&quot; to test your understanding with customized MCQs.</p>
                      </div>
                    )}
                  </div>
                )}

                {/* Evaluation tab panel view */}
                {activeTab === 'evaluate' && (
                  <div className="space-y-6">
                    {evaluationResult ? (
                      <div className="space-y-6 animate-fade-in">
                        {/* Interactive score visualizer card */}
                        <div className="flex flex-col items-center justify-center p-8 bg-gradient-to-b from-indigo-950/20 to-slate-950/40 border border-indigo-900/40 rounded-3xl text-center shadow-lg relative overflow-hidden">
                          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-sky-400 to-indigo-500"></div>
                          <h3 className="text-slate-400 text-[10px] font-bold uppercase tracking-widest mb-2">Self-Assessment Results</h3>
                          
                          <div className="flex items-baseline text-6xl font-black text-sky-400 mb-3">
                            {evaluationResult.score}
                            <span className="text-lg text-slate-600 font-bold ml-1.5">/ {evaluationResult.max_score}</span>
                          </div>
                          
                          <p className="text-slate-200 text-sm font-semibold max-w-md leading-relaxed">{evaluationResult.feedback}</p>
                        </div>

                        {/* Revision checklist section */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                          <div className="bg-slate-950/40 border border-slate-800/80 rounded-2xl p-5 hover:border-slate-800 transition">
                            <h4 className="text-[10px] font-bold text-sky-400 tracking-wider uppercase mb-3 flex items-center gap-1.5">
                              <span className="w-1 h-2 bg-sky-400 rounded-full"></span> Recommended Actions
                            </h4>
                            <ul className="space-y-3">
                              {evaluationResult.missing_points.map((pt, i) => (
                                <li key={i} className="text-xs text-slate-300 leading-relaxed flex items-start gap-2">
                                  <span className="text-indigo-400 font-bold text-sm mt-0.5">•</span>
                                  <span>{pt}</span>
                                </li>
                              ))}
                            </ul>
                          </div>

                          <div className="bg-slate-950/40 border border-slate-800/80 rounded-2xl p-5 hover:border-slate-800 transition">
                            <h4 className="text-[10px] font-bold text-indigo-400 tracking-wider uppercase mb-3 flex items-center gap-1.5">
                              <span className="w-1 h-2 bg-indigo-400 rounded-full"></span> Revision Guideline
                            </h4>
                            <p className="text-xs text-slate-300 leading-relaxed">{evaluationResult.revision_tip}</p>
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="text-center text-slate-500 py-24 flex flex-col items-center">
                        <svg className="w-10 h-10 text-slate-700 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <p className="text-xs font-bold uppercase tracking-wider mb-1.5 text-slate-400">Scorecard</p>
                        <p className="text-xs text-slate-500 max-w-sm">Detailed grading analytics and missing conceptual lists will render here after completing and submitting an active quiz.</p>
                      </div>
                    )}
                  </div>
                )}
                
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}
