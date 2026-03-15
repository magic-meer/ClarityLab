"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import mermaid from "mermaid";
import styles from "./page.module.css";
import MarkdownRenderer from "./components/MarkdownRenderer";

/**
 * Utility to convert values to strings safely.
 */
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

/**
 * Circular progress indicator that shows current step status.
 */
function CircularProgress({ status }) {
  if (!status) return null;
  return (
    <div className={styles.circularProgressContainer}>
      <div className={styles.circularLoader} />
      <span className={styles.statusText}>{status}</span>
    </div>
  );
}

export default function Home() {
  const [question, setQuestion] = useState("");
  const [difficulty, setDifficulty] = useState("auto");
  const [generateDiagram, setGenerateDiagram] = useState(true);
  const [generateImage, setGenerateImage] = useState(true);
  const [generateVideo, setGenerateVideo] = useState(true);
  
  const [showDifficultyMenu, setShowDifficultyMenu] = useState(false);
  const [showFeaturesMenu, setShowFeaturesMenu] = useState(false);
  
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [theme, setTheme] = useState("light");
  const [statusMessage, setStatusMessage] = useState(null);
  
  const chatEndRef = useRef(null);
  const inputRef = useRef(null);
  const diffMenuRef = useRef(null);
  const featMenuRef = useRef(null);

  // Theme management
  useEffect(() => {
    const saved = localStorage.getItem("theme");
    if (saved) setTheme(saved);
    else if (window.matchMedia("(prefers-color-scheme: dark)").matches) setTheme("dark");
  }, []);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

  const toggleTheme = () => setTheme(prev => prev === "light" ? "dark" : "light");

  // Auto-scroll
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [conversations, loading, statusMessage]);

  // Click outside menus
  useEffect(() => {
    function handleClickOutside(event) {
      if (diffMenuRef.current && !diffMenuRef.current.contains(event.target)) setShowDifficultyMenu(false);
      if (featMenuRef.current && !featMenuRef.current.contains(event.target)) setShowFeaturesMenu(false);
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim() || loading) return;

    const userQ = question.trim();
    setQuestion("");
    setError(null);
    setConversations(prev => [...prev, { role: "user", content: userQ }]);
    setLoading(true);
    setStatusMessage("Analyzing and planning...");

    try {
      // Step 1: Reasoning Plan
      const planRes = await fetch("/api/plan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          question: userQ, 
          difficulty,
          generate_diagram: generateDiagram,
          generate_image: generateImage,
          generate_video: generateVideo,
          generate_audio: false // Handled via TTS button now
        }),
      });
      
      const planData = await planRes.json();
      if (planData.status !== "success") throw new Error(planData.message || "Failed to create plan");

      const plan = planData.plan;
      
      // Add initial assistant message with placeholders
      const assistantMsgIdx = conversations.length + 1;
      setConversations(prev => [
        ...prev,
        { 
          role: "assistant", 
          topic: plan.topic,
          difficulty: plan.difficulty,
          explanation: null, // Loading
          diagram: null,
          image: null,
          video: null,
          followups: null,
          prompts: plan // Keep prompts for component fetching
        }
      ]);

      setLoading(false); // Planning done, now components fetch
      setStatusMessage(null);
    } catch (err) {
      setError(err.message);
      setConversations(prev => [...prev, { role: "assistant", error: err.message }]);
      setLoading(false);
      setStatusMessage(null);
    }
  };

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div className={styles.brand} onClick={() => window.location.reload()} style={{cursor: 'pointer'}}>
          <div className={styles.brandIcon}>✦</div>
          <h1 className={styles.brandName}>ClarityLab</h1>
        </div>
        <button className={styles.themeToggle} onClick={toggleTheme} title="Toggle theme">
          {theme === "light" ? "🌙" : "☀️"}
        </button>
      </header>

      <main className={styles.main}>
        <div className={styles.chatArea}>
          {conversations.length === 0 && (
            <div className={styles.emptyState}>
              <div className={styles.emptyIcon}>✦</div>
              <h2>What's on your mind?</h2>
              <p>Get deep, multimodal explanations with diagrams and video.</p>
              <div className={styles.suggestionsRow}>
                {["Black holes", "Photosynthesis", "Neural networks", "Quantum bits"].map(s => (
                  <button key={s} className={styles.suggestionBtn} onClick={() => setQuestion(s)}>
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {conversations.map((msg, i) => (
            <div key={i} className={`${styles.message} ${msg.role === "user" ? styles.userMessage : styles.assistantMessage} fade-in`}>
              {msg.role === "user" ? (
                <UserBubble content={msg.content} />
              ) : msg.error ? (
                <ErrorBubble message={msg.error} />
              ) : (
                <AssistantBubble data={msg} />
              )}
            </div>
          ))}
          
          {statusMessage && <CircularProgress status={statusMessage} />}
          <div ref={chatEndRef} />
        </div>

        <div className={styles.inputContainer}>
          <form className={styles.inputArea} onSubmit={handleSubmit}>
            <div className={styles.settingsRow}>
              <div className={styles.dropdown} ref={diffMenuRef}>
                <button type="button" className={styles.dropdownBtn} onClick={() => setShowDifficultyMenu(!showDifficultyMenu)}>
                  <span>Difficulty: {difficulty}</span>
                </button>
                {showDifficultyMenu && (
                  <div className={styles.dropdownMenu}>
                    {['beginner', 'intermediate', 'advanced', 'expert', 'auto'].map(lvl => (
                      <button key={lvl} type="button" onClick={() => { setDifficulty(lvl); setShowDifficultyMenu(false); }}>
                        {lvl}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              <div className={styles.dropdown} ref={featMenuRef}>
                <button type="button" className={styles.dropdownBtn} onClick={() => setShowFeaturesMenu(!showFeaturesMenu)}>
                  <span>Assets</span>
                </button>
                {showFeaturesMenu && (
                  <div className={styles.dropdownMenu}>
                    <label><input type="checkbox" checked={generateDiagram} onChange={e => setGenerateDiagram(e.target.checked)} /> Diagrams</label>
                    <label><input type="checkbox" checked={generateImage} onChange={e => setGenerateImage(e.target.checked)} /> Images</label>
                    <label><input type="checkbox" checked={generateVideo} onChange={e => setGenerateVideo(e.target.checked)} /> Video</label>
                  </div>
                )}
              </div>
            </div>

            <div className={styles.inputWrapper}>
              <input
                ref={inputRef}
                type="text"
                className={styles.input}
                placeholder="Explain..."
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                disabled={loading}
              />
              <button type="submit" className={styles.sendBtn} disabled={loading || !question.trim()}>
                {loading ? "..." : "→"}
              </button>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
}

function UserBubble({ content }) {
  return (
    <div className={styles.userBubble}>
      <p>{content}</p>
    </div>
  );
}

function ErrorBubble({ message }) {
  return (
    <div className={styles.errorBubble}>
      <span>⚠ {message}</span>
    </div>
  );
}

function AssistantBubble({ data }) {
  const [explanation, setExplanation] = useState(null);
  const [diagram, setDiagram] = useState(null);
  const [image, setImage] = useState(null);
  const [video, setVideo] = useState(null);
  const [followups, setFollowups] = useState(null);
  const [loadingText, setLoadingText] = useState(true);
  const [status, setStatus] = useState("Generating content...");
  const [expandedAsset, setExpandedAsset] = useState(null);

  const prompts = data.prompts;

  useEffect(() => {
    if (!prompts) return;

    // Fetch Explanation
    const fetchExplanation = async () => {
      try {
        const res = await fetch("/api/generate-explanation", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ prompt: prompts.explanation_prompt })
        });
        const d = await res.json();
        setExplanation(d.data?.text || d.data);
      } catch (e) { console.error(e); }
      setLoadingText(false);
    };

    // Fetch Assets in parallel
    const fetchAsset = async (endpoint, prompt, setter) => {
      if (!prompt) return;
      try {
        const res = await fetch(endpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ prompt })
        });
        const d = await res.json();
        setter(d.data);
      } catch (e) { console.error(e); }
    };

    fetchExplanation();
    fetchAsset("/api/generate-diagram", prompts.diagram_prompt, setDiagram);
    fetchAsset("/api/generate-image", prompts.image_prompt, setImage);
    fetchAsset("/api/generate-video", prompts.video_prompt, setVideo);
    fetchAsset("/api/generate-explanation", prompts.followup_prompt, (d) => setFollowups(d?.text || d));

  }, [prompts]);

  const speak = () => {
    const text = toStr(explanation);
    const utterance = new SpeechSynthesisUtterance(text);
    window.speechSynthesis.speak(utterance);
  };

  return (
    <div className={styles.assistantContent}>
      <div className={styles.textbookHeader}>
        <h2 className={styles.topicTitle}>{data.topic}</h2>
        <span className={styles.difficultyTag}>{data.difficulty}</span>
      </div>

      {video && (
        <div className={styles.videoHero}>
           <video src={`data:${video.mime_type || 'video/mp4'};base64,${video.video_base64}`} controls autoPlay loop />
        </div>
      )}

      <div className={styles.textbookLayout}>
        <div className={styles.explanationCol}>
          {loadingText ? (
            <div className={styles.skeleton}>Generating explanation...</div>
          ) : (
            <MarkdownRenderer content={toStr(explanation)} />
          )}
          
          {followups && (
             <div className={styles.followupsSection}>
                <h4>Dive Deeper</h4>
                <MarkdownRenderer content={toStr(followups)} />
             </div>
          )}
          
          <button className={styles.ttsBtn} onClick={speak} disabled={!explanation}>
            🔊 Read Aloud
          </button>
        </div>

        <aside className={styles.assetSidebar}>
          {diagram && (
            <div className={`${styles.assetCard} ${styles.expandable}`} onClick={() => setExpandedAsset({ type: 'diagram', data: diagram.text || diagram })}>
              <h5>Visual Representation</h5>
              <DiagramRenderer code={diagram.text || diagram} />
            </div>
          )}
          {image && (
            <div className={`${styles.assetCard} ${styles.expandable}`} onClick={() => setExpandedAsset({ type: 'image', data: image })}>
              <img src={`data:${image.mime_type || 'image/jpeg'};base64,${image.image_base64}`} alt="Illustration" />
            </div>
          )}
        </aside>
      </div>

      {!loadingText && !status && <CircularProgress status="Complete" />}
      {loadingText && <CircularProgress status="Generating text..." />}

      {expandedAsset && (
        <div className={styles.modalOverlay} onClick={() => setExpandedAsset(null)}>
          <div className={styles.modalContent} onClick={e => e.stopPropagation()}>
            <button className={styles.closeModal} onClick={() => setExpandedAsset(null)}>×</button>
            {expandedAsset.type === 'image' ? (
              <img src={`data:${expandedAsset.data.mime_type || 'image/jpeg'};base64,${expandedAsset.data.image_base64}`} alt="Expanded view" />
            ) : (
              <div className={styles.modalDiagram}>
                <DiagramRenderer code={expandedAsset.data} />
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function DiagramRenderer({ code }) {
  const containerRef = useRef(null);
  const [svg, setSvg] = useState(null);

  useEffect(() => {
    if (!code) return;
    const render = async () => {
      try {
        const cleanCode = code.replace(/```mermaid\n?|```/g, "").trim();
        
        // If it's already an SVG, just set it
        if (cleanCode.includes('<svg') && cleanCode.includes('</svg>')) {
          setSvg(cleanCode);
          return;
        }

        // Otherwise try to render as mermaid
        const { svg } = await mermaid.render(`id-${Math.random().toString(36).substr(2,9)}`, cleanCode);
        setSvg(svg);
      } catch (e) { 
        console.error("Diagram render error:", e);
        // Fallback: If it looks like text but failed mermaid, maybe it's raw text?
        // For now, just show the error in the console.
      }
    };
    render();
  }, [code]);

  return svg ? <div dangerouslySetInnerHTML={{ __html: svg }} /> : <div>Loading diagram...</div>;
}
