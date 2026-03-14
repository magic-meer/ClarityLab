"use client";

import { useState, useRef, useEffect } from "react";
import mermaid from "mermaid";
import styles from "./page.module.css";
import MarkdownRenderer from "./components/MarkdownRenderer";

function toStr(value) {
  if (value == null) return "";
  if (typeof value === "string") return value;
  if (typeof value === "object") {
    for (const key of ["description", "text", "content", "summary", "body", "value"]) {
      if (typeof value[key] === "string") return value[key];
    }
    return JSON.stringify(value);
  }
  return String(value);
}

export default function Home() {
  const [question, setQuestion] = useState("");
  const [modelName, setModelName] = useState("gemini-2.5-flash");
  const [voiceName, setVoiceName] = useState("en-US-Journey-D");
  const [generateDiagram, setGenerateDiagram] = useState(true);
  const [generateImage, setGenerateImage] = useState(true);
  const [generateAudio, setGenerateAudio] = useState(true);
  const [generateVideo, setGenerateVideo] = useState(true);
  const [difficulty, setDifficulty] = useState("auto");
  const [processingStep, setProcessingStep] = useState("idle");
  const [file, setFile] = useState(null);
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [theme, setTheme] = useState("light");
  const chatEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    const saved = localStorage.getItem("theme");
    if (saved) {
      setTheme(saved);
    } else if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
      setTheme("dark");
    }
  }, []);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === "light" ? "dark" : "light");
  };

  const [textModels, setTextModels] = useState([
    { name: "gemini-2.5-flash",      display_name: "Gemini 2.5 Flash" },
    { name: "gemini-2.0-flash",      display_name: "Gemini 2.0 Flash" },
    { name: "gemini-2.0-flash-lite", display_name: "Gemini 2.0 Flash Lite" },
    { name: "gemini-1.5-pro",        display_name: "Gemini 1.5 Pro" },
    { name: "gemini-1.5-flash",      display_name: "Gemini 1.5 Flash" },
    { name: "gemini-1.5-flash-8b",   display_name: "Gemini 1.5 Flash 8B" },
  ]);
  const [audioVoices, setAudioVoices] = useState([
    { name: "en-US-Journey-D", display_name: "Journey (US Male)" },
    { name: "en-US-Journey-F", display_name: "Journey (US Female)" },
    { name: "en-US-Standard-A", display_name: "Standard (US Male)" },
    { name: "en-US-Standard-C", display_name: "Standard (US Female)" },
    { name: "en-GB-Standard-A", display_name: "Standard (UK Female)" },
    { name: "en-GB-Standard-B", display_name: "Standard (UK Male)" },
    { name: "en-AU-Standard-A", display_name: "Standard (AU Female)" },
  ]);

  useEffect(() => {
    async function fetchModels() {
      try {
        const res = await fetch("/api/models");
        const data = await res.json();
        if (data.status === "success") {
          if (data.text_models?.length)  setTextModels(data.text_models);
          if (data.audio_voices?.length) setAudioVoices(data.audio_voices);
          if (data.text_models?.length && !data.text_models.find(m => m.name === modelName)) {
            setModelName(data.text_models[0].name);
          }
        }
      } catch (err) {
        console.warn("Could not refresh model list from backend:", err);
      }
    }
    fetchModels();
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [conversations, loading]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim() || loading) return;

    const userQ = question.trim();
    const currentFile = file;
    setQuestion("");
    setFile(null);
    setError(null);

    let fileUrl = null;
    if (currentFile) {
      fileUrl = URL.createObjectURL(currentFile);
    }

    setConversations((prev) => [
      ...prev,
      { role: "user", content: userQ, fileUrl },
    ]);
    setLoading(true);
    setProcessingStep("thinking");

    try {
      let res;
      if (currentFile) {
        const formData = new FormData();
        formData.append("question", userQ);
        formData.append("model_name", modelName);
        formData.append("file", currentFile);
        formData.append("generate_diagram", generateDiagram);
        formData.append("generate_image", generateImage);
        formData.append("generate_audio", generateAudio);
        formData.append("difficulty", difficulty);

        res = await fetch("/api/analyze", {
          method: "POST",
          body: formData,
        });
      } else {
        setProcessingStep("generating");
        res = await fetch("/api/explain/steps", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ 
            question: userQ, 
            model_name: modelName,
            generate_diagram: generateDiagram,
            generate_image: generateImage,
            generate_audio: generateAudio,
            generate_video: generateVideo,
            difficulty: difficulty
          }),
        });
      }

      const data = await res.json();
      const payload = data.data || data;

      const usage = data.usage || payload.usage || null;

      if (data.status === "success" && payload) {
        setConversations((prev) => [
          ...prev,
          { role: "assistant", content: payload, usage: usage },
        ]);
      } else {
        setError(data.error || "Something went wrong");
        setConversations((prev) => [
          ...prev,
          {
            role: "assistant",
            content: null,
            error: data.error || "Failed to generate explanation",
          },
        ]);
      }
    } catch (err) {
      const msg = "Could not reach the server. Please ensure the Python backend is running.";
      setError(msg);
      setConversations((prev) => [
        ...prev,
        { role: "assistant", content: null, error: msg },
      ]);
    } finally {
      setLoading(false);
      setProcessingStep("idle");
      inputRef.current?.focus();
    }
  };

  return (
    <div className={styles.container}>
      {/* Sidebar */}
      <aside className={styles.sidebar}>
        <div className={styles.sidebarHeader}>
          <div className={styles.brand}>
            <div className={styles.brandIcon}>✦</div>
            <h1 className={styles.brandName}>ClarityLab</h1>
          </div>
          <button className={styles.themeToggle} onClick={toggleTheme} title="Toggle theme">
            {theme === "light" ? (
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
              </svg>
            ) : (
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
              </svg>
            )}
          </button>
        </div>

        <div className={styles.sidebarSection}>
          <h3 className={styles.sidebarTitle}>Model Settings</h3>
          <div className={styles.settingsGroup}>
            <label className={styles.settingsLabel}>Text Model</label>
            <select className={styles.settingsSelect} value={modelName} onChange={(e) => setModelName(e.target.value)}>
              {textModels.length > 0 ? textModels.map((m) => (
                <option key={m.name} value={m.name}>{m.display_name}</option>
              )) : (
                <option value={modelName}>Loading...</option>
              )}
            </select>
          </div>
          <div className={styles.settingsGroup}>
            <label className={styles.settingsLabel}>Audio Voice</label>
            <select className={styles.settingsSelect} value={voiceName} onChange={(e) => setVoiceName(e.target.value)}>
              {audioVoices.length > 0 ? audioVoices.map((v) => (
                <option key={v.name} value={v.name}>{v.display_name}</option>
              )) : (
                <option value={voiceName}>Loading...</option>
              )}
            </select>
          </div>
        </div>

        <div className={styles.sidebarSection}>
          <h3 className={styles.sidebarTitle}>Difficulty Level</h3>
          <div className={styles.difficultyGrid}>
            {[
              { value: "auto", label: "Auto" },
              { value: "beginner", label: "Beginner" },
              { value: "intermediate", label: "Intermediate" },
              { value: "advanced", label: "Advanced" },
              { value: "expert", label: "Expert" },
            ].map((level) => (
              <button
                key={level.value}
                className={`${styles.difficultyBtn} ${difficulty === level.value ? styles.difficultyActive : ""}`}
                onClick={() => setDifficulty(level.value)}
              >
                {level.label}
              </button>
            ))}
          </div>
        </div>

        <div className={styles.sidebarSection}>
          <h3 className={styles.sidebarTitle}>Features</h3>
          <div className={styles.settingsGroup}>
            <label className={styles.checkboxLabel}>
              <input type="checkbox" checked={generateDiagram} onChange={(e) => setGenerateDiagram(e.target.checked)} /> 
              Diagrams (Auto)
            </label>
            <label className={styles.checkboxLabel}>
              <input type="checkbox" checked={generateImage} onChange={(e) => setGenerateImage(e.target.checked)} /> 
              Images (Auto)
            </label>
            <label className={styles.checkboxLabel}>
              <input type="checkbox" checked={generateAudio} onChange={(e) => setGenerateAudio(e.target.checked)} /> 
              Audio (Auto)
            </label>
            <label className={styles.checkboxLabel}>
              <input type="checkbox" checked={generateVideo} onChange={(e) => setGenerateVideo(e.target.checked)} /> 
              Video (VEO)
            </label>
          </div>
        </div>

        <div className={styles.sidebarSection}>
          <h3 className={styles.sidebarTitle}>Try asking</h3>
          <div className={styles.suggestions}>
            {[
              "Explain quantum entanglement",
              "How does photosynthesis work?",
              "What is a neural network?",
              "Explain recursion in programming",
            ].map((s) => (
              <button
                key={s}
                className={styles.suggestionBtn}
                onClick={() => {
                  setQuestion(s);
                  inputRef.current?.focus();
                }}
              >
                {s}
              </button>
            ))}
          </div>
        </div>

        <div className={styles.sidebarFooter}>
          <span className={styles.footerText}>Powered by Gemini AI</span>
        </div>
      </aside>

      {/* Main area */}
      <main className={styles.main}>
        {/* Chat area */}
        <div className={styles.chatArea}>
          {conversations.length === 0 && !loading && (
            <div className={styles.emptyState}>
              <div className={styles.emptyIcon}>✦</div>
              <h2>Welcome to ClarityLab</h2>
              <p>
                Ask any question and get a rich, structured explanation with
                diagrams, animations, narration scripts, and follow-up
                questions.
              </p>
            </div>
          )}

          {conversations.map((msg, i) => (
            <div
              key={i}
              className={`${styles.message} ${
                msg.role === "user" ? styles.userMessage : styles.assistantMessage
              } fade-in-up`}
              style={{ animationDelay: `${0.05 * i}s` }}
            >
              {msg.role === "user" ? (
                <UserBubble content={msg.content} fileUrl={msg.fileUrl} />
              ) : msg.error ? (
                <ErrorBubble message={msg.error} />
              ) : (
                <AssistantBubble 
                  data={msg.content} 
                  usage={msg.usage} 
                  voiceName={voiceName}
                />
              )}
            </div>
          ))}

          {loading && (
            <div className={`${styles.message} ${styles.assistantMessage} fade-in-up`}>
              <LoadingSkeleton step={processingStep} />
            </div>
          )}

          <div ref={chatEndRef} />
        </div>

        {/* Input area */}
        <form className={styles.inputArea} onSubmit={handleSubmit}>
          {file && (
            <div className={styles.filePreviewContainer}>
              <div className={styles.filePreviewThumb}>
                <img src={URL.createObjectURL(file)} alt="Preview" />
                <button type="button" className={styles.removeFileBtn} onClick={() => setFile(null)}>✕</button>
              </div>
            </div>
          )}
          <div className={styles.inputWrapper}>
            <label className={styles.fileInputBtn} title="Upload Image">
              <input 
                type="file" 
                accept="image/*" 
                className={styles.fileInput}
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    setFile(e.target.files[0]);
                  }
                }}
                disabled={loading}
              />
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/></svg>
            </label>
            <input
              ref={inputRef}
              type="text"
              className={styles.input}
              placeholder="Ask anything — science, math, history, programming..."
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              disabled={loading}
            />
            <button
              type="submit"
              className={styles.sendBtn}
              disabled={loading || !question.trim()}
            >
              {loading ? (
                <div className={styles.spinner} />
              ) : (
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
              )}
            </button>
          </div>
        </form>

        {error && (
          <div className={styles.globalError}>
            <span>⚠ {error}</span>
          </div>
        )}
      </main>
    </div>
  );
}

function UserBubble({ content, fileUrl }) {
  return (
    <div className={styles.userBubble}>
      <div className={styles.userAvatar}>You</div>
      <div>
        {fileUrl && (
          <div className={styles.userImageWrapper}>
             <img src={fileUrl} alt="Uploaded" className={styles.userImage} />
          </div>
        )}
        <p className={styles.userText}>{content}</p>
      </div>
    </div>
  );
}

function ErrorBubble({ message }) {
  return (
    <div className={styles.errorBubble}>
      <span className={styles.errorIcon}>⚠</span>
      <p>{message}</p>
    </div>
  );
}

function AssistantBubble({ data, usage, voiceName }) {
  if (!data) return null;

  return (
    <div className={styles.assistantBubble}>
      {/* Topic header */}
      <div className={styles.topicHeader}>
        <span className={styles.assistantAvatar}>✦</span>
        <div>
          <h2 className={styles.topicTitle}>{data.topic || "Analysis Result"}</h2>
          {data.difficulty && (
            <span className={`${styles.tag} ${styles[`tag_${data.difficulty}`]}`}>
              {data.difficulty}
            </span>
          )}
        </div>
      </div>

      {/* Explanation or Analysis */}
      <div className={styles.section}>
        <h3 className={styles.sectionTitle}>📝 Explanation</h3>
        <MarkdownRenderer content={toStr(data.explanation || data.analysis || data)} />
      </div>

      {/* Key points */}
      {data.key_points?.length > 0 && (
        <div className={styles.section}>
          <h3 className={styles.sectionTitle}>💡 Key Points</h3>
          <ul className={styles.keyPoints}>
            {data.key_points.map((pt, i) => (
              <li key={i} className={styles.keyPoint}>
                <MarkdownRenderer content={toStr(pt)} />
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Diagram Rendering */}
      {(data.diagram_code || data.diagrams) && (
        <div className={styles.section}>
          <h3 className={styles.sectionTitle}>🎨 Diagram</h3>
          {/* Support a single diagram (legacy shape) */}
          {data.diagram_code && data.diagram_type && (
            <DiagramRenderer type={data.diagram_type} code={data.diagram_code} />
          )}
          {/* Support richer multiple diagrams */}
          {Array.isArray(data.diagrams) &&
            data.diagrams.map((d, idx) =>
              d?.code ? (
                <div key={idx} className={styles.diagramGroup}>
                  {d.title && <h4 className={styles.diagramSubtitle}>{toStr(d.title)}</h4>}
                  <DiagramRenderer type={d.type || data.diagram_type || "mermaid"} code={d.code} />
                </div>
              ) : null
            )}
        </div>
      )}

      {/* Generated Image Rendering */}
      {data.image_base64 && (
        <div className={styles.section}>
          <h3 className={styles.sectionTitle}>🖼️ Generated Image</h3>
          <img 
            src={`data:${data.image_mime_type || 'image/jpeg'};base64,${data.image_base64}`} 
            alt="Generated illustration" 
            style={{ width: "100%", borderRadius: "8px", border: "1px solid var(--border)" }} 
          />
        </div>
      )}

      {/* Narration — auto-plays */}
      {data.narration_script && (
        <NarrationPlayer text={data.narration_script} voiceName={voiceName} />
      )}

      {/* Video Rendering */}
      {data.video_base64 && (
        <div className={styles.section}>
          <h3 className={styles.sectionTitle}>🎥 Generated Video (VEO)</h3>
          <video 
            src={`data:${data.video_mime_type || 'video/mp4'};base64,${data.video_base64}`} 
            controls 
            autoPlay 
            loop 
            style={{ width: "100%", borderRadius: "8px", border: "1px solid var(--border)" }} 
          />
        </div>
      )}

      {/* Follow-up */}
      {data.follow_up_questions?.length > 0 && (
        <div className={styles.section}>
          <h3 className={styles.sectionTitle}>🤔 Follow-up Questions</h3>
          <div className={styles.followUps}>
            {data.follow_up_questions.map((q, i) => (
              <div key={i} className={styles.followUpCard}>
                <MarkdownRenderer content={toStr(q)} />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Usage Stats Footer */}
      {usage && usage.total_tokens > 0 && (
        <div className={styles.usageStats}>
          <div className={styles.statItem}>
            <span><b>{usage.prompt_tokens}</b> prompt</span>
          </div>
          <div className={styles.statItem}>
            <span><b>{usage.completion_tokens}</b> completion</span>
          </div>
          <div className={styles.statItem}>
            <span><b>{usage.total_tokens}</b> total tokens</span>
          </div>
        </div>
      )}
    </div>
  );
}

function DiagramRenderer({ type, code }) {
  const containerRef = useRef(null);
  const [error, setError] = useState(null);
  const [svgContent, setSvgContent] = useState(null);

  useEffect(() => {
    if (!code) return;
    
    setError(null);
    setSvgContent(null);

    const renderDiagram = async () => {
      if (type === "mermaid") {
        try {
          await mermaid.initialize({ 
            startOnLoad: false, 
            theme: "neutral",
            securityLevel: "loose",
            flowchart: { useMaxWidth: true, htmlLabels: true }
          });
          
          const renderId = `mermaid-${Math.random().toString(36).substr(2, 9)}`;
          const { svg } = await mermaid.render(renderId, code);
          setSvgContent(svg);
        } catch (err) {
          console.error("Mermaid parsing error:", err);
          const errMsg = err.message || "Invalid Mermaid syntax";
          setError(`Diagram code error: ${errMsg}. Check the generated code below.`);
        }
      } else if (type === "svg") {
        try {
          setSvgContent(code);
        } catch (err) {
          setError("Failed to render SVG diagram.");
        }
      }
    };

    renderDiagram();
  }, [type, code]);

  return (
    <div className={styles.diagramWrapper}>
      {error ? (
        <div className={styles.errorBubble} style={{ marginTop: 0 }}>
          <span className={styles.errorIcon}>⚠</span>
          <p>{error}</p>
          <details style={{ marginTop: "8px" }}>
            <summary style={{ cursor: "pointer", color: "var(--text-secondary)", fontSize: "12px" }}>
              View diagram code
            </summary>
            <pre style={{ fontSize: "11px", overflowX: "auto", marginTop: "8px", textAlign: "left" }}>
              {code}
            </pre>
          </details>
        </div>
      ) : svgContent ? (
        <div 
          ref={containerRef} 
          className={styles.diagramContainer}
          dangerouslySetInnerHTML={{ __html: svgContent }}
        />
      ) : (
        <div className={styles.diagramContainer} ref={containerRef} />
      )}
    </div>
  );
}

function LoadingSkeleton({ step = "generating" }) {
  const stepLabels = {
    idle: "Preparing...",
    thinking: "Thinking...",
    generating: "Generating explanation...",
    keypoints: "Extracting key points...",
    diagram: "Creating diagram...",
    image: "Generating image...",
    narration: "Creating narration...",
    video: "Generating animation video (VEO)...",
    questions: "Generating follow-up questions...",
    complete: "Finalizing..."
  };

  const steps = [
    { key: "generating", label: "Explanation" },
    { key: "keypoints", label: "Key Points" },
    { key: "diagram", label: "Diagram" },
    { key: "image", label: "Image" },
    { key: "narration", label: "Narration" },
    { key: "video", label: "Video" },
    { key: "questions", label: "Follow-ups" },
  ];

  const currentIndex = steps.findIndex(s => s.key === step);
  const progress = currentIndex >= 0 ? ((currentIndex + 1) / steps.length) * 100 : 5;

  return (
    <div className={styles.assistantBubble}>
      <div className={styles.topicHeader}>
        <span className={styles.assistantAvatar}>✦</span>
        <div>
          <div className={`skeleton ${styles.skeletonTitle}`} style={{ width: "180px" }} />
          <span className={styles.processingLabel}>{stepLabels[step] || "Processing..."}</span>
        </div>
      </div>
      
      <div className={styles.progressContainer}>
        <div className={styles.progressBar}>
          <div className={styles.progressFill} style={{ width: `${progress}%` }} />
        </div>
        <div className={styles.stepsIndicator}>
          {steps.map((s, i) => (
            <span 
              key={s.key} 
              className={`${styles.stepDot} ${i <= currentIndex ? styles.stepComplete : ''} ${i === currentIndex ? styles.stepActive : ''}`}
              title={s.label}
            >
              {i + 1}
            </span>
          ))}
        </div>
      </div>

      <div className={styles.section}>
        <div className={`skeleton ${styles.skeletonLine}`} />
        <div className={`skeleton ${styles.skeletonLine}`} style={{ width: "85%" }} />
        <div className={`skeleton ${styles.skeletonLine}`} style={{ width: "60%" }} />
      </div>
    </div>
  );
}

function NarrationPlayer({ text, voiceName }) {
  const [audioUrl, setAudioUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    async function synthesize() {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch("/api/tts", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text, voice_name: voiceName }),
        });
        if (!res.ok) {
          throw new Error("Failed to synthesize audio");
        }
        const blob = await res.blob();
        if (!cancelled) {
          setAudioUrl(URL.createObjectURL(blob));
        }
      } catch (err) {
        if (!cancelled) {
          console.error(err);
          setError("Could not synthesize speech.");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    synthesize();
    return () => { cancelled = true; };
  }, [text, voiceName]);

  return (
    <div className={styles.section}>
      <h3 className={styles.sectionTitle}>🎙️ Narration</h3>
      <div className={styles.narrationWrapper}>
        <blockquote className={styles.narration}>
          <MarkdownRenderer content={text} />
        </blockquote>
        <div className={styles.audioControls}>
          {loading && <span style={{ fontSize: "12px", color: "var(--text-secondary)" }}>⏳ Synthesizing audio...</span>}
          {audioUrl && <audio src={audioUrl} controls autoPlay className={styles.audioPlayer} />}
          {error && <span className={styles.audioError}>{error}</span>}
        </div>
      </div>
    </div>
  );
}
