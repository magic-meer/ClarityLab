"use client";

import { useState, useRef, useEffect } from "react";
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
 * Strips markdown syntax to make text cleaner for TTS.
 */
function stripMarkdown(text) {
  if (!text) return "";
  return text
    .replace(/#+\s+/g, "") // Headers
    .replace(/\*\*/g, "")  // Bold
    .replace(/\*/g, "")    // Italic
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1") // Links
    .replace(/`{1,3}[^`]*`{1,3}/g, "") // Code blocks
    .replace(/[-*+]\s+/g, "") // List items
    .replace(/\n+/g, " "); // Newlines to spaces
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

function Icon({ name }) {
  const icons = {
    spark: (
      <>
        {/* 
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <path d="M12 3l1.8 4.2L18 9l-4.2 1.8L12 15l-1.8-4.2L6 9l4.2-1.8L12 3z" />
        </svg>
        */}
        <img src="/icon.svg" alt="ClarityLab Spark" style={{ width: '100%', height: '100%', display: 'block' }} />
      </>
    ),
    moon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" />
      </svg>
    ),
    sun: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <circle cx="12" cy="12" r="4" />
        <path d="M12 2v2.2M12 19.8V22M4.9 4.9l1.6 1.6M17.5 17.5l1.6 1.6M2 12h2.2M19.8 12H22M4.9 19.1l1.6-1.6M17.5 6.5l1.6-1.6" />
      </svg>
    ),
    plus: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M12 5v14M5 12h14" />
      </svg>
    ),
    sliders: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M4 6h16M4 12h16M4 18h16" />
        <circle cx="8" cy="6" r="2" fill="currentColor" />
        <circle cx="15" cy="12" r="2" fill="currentColor" />
        <circle cx="11" cy="18" r="2" fill="currentColor" />
      </svg>
    ),
    grid: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <rect x="4" y="4" width="6" height="6" rx="1.5" />
        <rect x="14" y="4" width="6" height="6" rx="1.5" />
        <rect x="4" y="14" width="6" height="6" rx="1.5" />
        <rect x="14" y="14" width="6" height="6" rx="1.5" />
      </svg>
    ),
    volume: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M5 9v6h4l5 4V5L9 9H5z" />
        <path d="M18 9.5a4.5 4.5 0 0 1 0 5" />
      </svg>
    ),
  };

  return <span className={styles.icon}>{icons[name]}</span>;
}

function AssetToggle({ label, value, onChange }) {
  const isAuto = value === "auto";

  return (
    <button
      type="button"
      className={`${styles.assetToggleRow} ${isAuto ? styles.assetToggleRowActive : ""}`}
      onClick={() => onChange(isAuto ? "off" : "auto")}
      aria-label={`Toggle ${label}`}
    >
      <span className={styles.toggleLabel}>{label}</span>
      <div className={`${styles.checkbox} ${isAuto ? styles.checkboxChecked : ""}`}>
        {isAuto && <span className={styles.checkIcon}>✓</span>}
      </div>
    </button>
  );
}

export default function Home() {
  const [question, setQuestion] = useState("");
  const [difficulty, setDifficulty] = useState("auto");
  const [generateDiagram, setGenerateDiagram] = useState("off");
  const [generateImage, setGenerateImage] = useState("off");
  const [generateVideo, setGenerateVideo] = useState("off");

  const [showDifficultyMenu, setShowDifficultyMenu] = useState(false);
  const [showFeaturesMenu, setShowFeaturesMenu] = useState(false);

  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [theme, setTheme] = useState("light");
  const [statusMessage, setStatusMessage] = useState(null);

  const hasConversation = conversations.length > 0;
  const sessionLabel = hasConversation
    ? `Session • ${conversations.length} message${conversations.length === 1 ? "" : "s"}`
    : "New session";

  const chatEndRef = useRef(null);
  const inputRef = useRef(null);
  const diffMenuRef = useRef(null);
  const featMenuRef = useRef(null);

  // Theme management
  useEffect(() => {
    const saved = localStorage.getItem("theme");
    if (saved) {
      setTheme(saved);
    } else {
      const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
      setTheme(prefersDark ? "dark" : "light");
    }
  }, []);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    // Explicitly check if user has manually set a theme before saving
    // This allows us to potentially clear localStorage later to go back to system sync
    if (localStorage.getItem("theme") || theme !== "light") {
      localStorage.setItem("theme", theme);
    }
  }, [theme]);

  const toggleTheme = () => setTheme(prev => prev === "light" ? "dark" : "light");
  const resetSession = () => {
    setConversations([]);
    setError(null);
    setStatusMessage(null);
    setQuestion("");
    inputRef.current?.focus();
  };

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
    setStatusMessage("Analyzing and planning...");
    setConversations(prev => [...prev, { role: "user", content: userQ }]);
    setLoading(true);

    try {
      // Step 1: Reasoning Plan
      const planRes = await fetch("/api/plan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: userQ,
          difficulty,
          generate_diagram: generateDiagram === "auto",
          generate_image: generateImage === "auto",
          generate_video: generateVideo === "auto",
          generate_audio: false // Handled via TTS button now
        }),
      });

      const planData = await planRes.json();
      if (planData.status !== "success") throw new Error(planData.message || "Failed to create plan");

      const plan = planData.plan;

      // Add initial assistant message with placeholders
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
        <div className={styles.brand} onClick={() => window.location.reload()} style={{ cursor: "pointer" }}>
          <div className={styles.brandIcon} aria-hidden="true"><Icon name="spark" /></div>
          <h1 className={styles.brandName}>ClarityLab</h1>
        </div>
        <div className={styles.headerActions}>
          <p className={styles.sessionText}>{sessionLabel}</p>
          <div className={styles.actionGroup}>
            <button className={styles.actionButton} onClick={toggleTheme} title="Toggle theme" aria-label="Toggle theme">
              <Icon name={theme === "light" ? "moon" : "sun"} />
            </button>
            <button className={`${styles.actionButton} ${styles.hideOnMobile}`} onClick={resetSession} title="Start new chat" aria-label="Start new chat">
              <Icon name="plus" />
            </button>
          </div>
        </div>
      </header>

      <main className={styles.main}>
        <div className={`${styles.layoutWrapper} ${!hasConversation ? styles.heroMode : styles.chatMode}`}>
          {!hasConversation && (
            <div className={styles.emptyState}>
              <div className={styles.emptyIcon}><Icon name="spark" /></div>
              <h1 className={styles.welcomeTitle}>What's on your mind?</h1>
              <p className={styles.welcomeSubTitle}>Get deep, multimodal explanations with diagrams and video.</p>
              <div className={styles.suggestionsRow}>
                {["Black holes", "Photosynthesis", "Neural networks", "Quantum bits"].map(s => (
                  <button key={s} className={styles.suggestionBtn} onClick={() => setQuestion(s)}>
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {hasConversation && (
            <div className={styles.chatArea}>
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
          )}

          <div className={`${styles.inputContainer} ${!hasConversation ? styles.inputHero : ""}`}>
            <form className={styles.inputArea} onSubmit={handleSubmit}>
              <div className={styles.inputWrapper}>
                <div className={styles.composerControls}>
                  <div className={styles.dropdown} ref={diffMenuRef}>
                    <button type="button" className={styles.dropdownBtn} onClick={() => setShowDifficultyMenu(!showDifficultyMenu)}>
                      <Icon name="sliders" />
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
                      <Icon name="grid" />
                      <span>Assets</span>
                    </button>
                    {showFeaturesMenu && (
                      <div className={styles.dropdownMenu}>
                        <AssetToggle label="Diagrams" value={generateDiagram} onChange={setGenerateDiagram} />
                        <AssetToggle label="Images" value={generateImage} onChange={setGenerateImage} />
                        <AssetToggle label="Video" value={generateVideo} onChange={setGenerateVideo} />
                      </div>
                    )}
                  </div>
                </div>

                <div className={styles.textInputRow}>
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
              </div>
            </form>
          </div>
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
      <span>Error: {message}</span>
    </div>
  );
}

function AssistantBubble({ data }) {
  const [explanation, setExplanation] = useState(null);
  const [diagram, setDiagram] = useState(null);
  const [image, setImage] = useState(null);
  const [video, setVideo] = useState(null);
  const [followups, setFollowups] = useState(null);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [ttsError, setTtsError] = useState(false);
  const prompts = data.prompts;

  const [bubbleLoading, setBubbleLoading] = useState({
    explanation: true,
    diagram: prompts?.diagram_prompt ? true : false,
    image: prompts?.image_prompt ? true : false,
    video: prompts?.video_prompt ? true : false,
    followups: prompts?.followup_prompt ? true : false
  });
  const [status, setStatus] = useState("Generating explanation...");
  const [expandedAsset, setExpandedAsset] = useState(null);
  
  const voiceRef = useRef(null);
  const stopRequestedRef = useRef(false);
  const keepAliveRef = useRef(null);

  const startKeepAlive = () => {
    if (keepAliveRef.current) clearInterval(keepAliveRef.current);
    keepAliveRef.current = setInterval(() => {
      if (window.speechSynthesis.speaking && !window.speechSynthesis.paused) {
        window.speechSynthesis.pause();
        window.speechSynthesis.resume();
      }
    }, 10000);
  };

  const stopKeepAlive = () => {
    if (keepAliveRef.current) {
      clearInterval(keepAliveRef.current);
      keepAliveRef.current = null;
    }
  };

  // Pre-load voices
  useEffect(() => {
    if (typeof window === "undefined" || !window.speechSynthesis) return;
    const pickVoice = () => {
      const voices = window.speechSynthesis.getVoices();
      if (!voices.length) return;
      voiceRef.current = voices.find(v => v.lang.startsWith("en") && (v.name.includes("Google") || v.name.includes("Natural")))
        || voices.find(v => v.lang.startsWith("en"))
        || voices[0];
    };
    pickVoice();
    window.speechSynthesis.addEventListener("voiceschanged", pickVoice);
    return () => window.speechSynthesis.removeEventListener("voiceschanged", pickVoice);
  }, []);

  // Cleanup speech on unmount
  useEffect(() => {
    return () => {
      if (window.speechSynthesis) window.speechSynthesis.cancel();
      if (keepAliveRef.current) clearInterval(keepAliveRef.current);
    };
  }, []);

  useEffect(() => {
    if (!prompts) return;

    // Helper to update status
    const updateStatus = (states) => {
      if (states.explanation) return "Generating text...";
      if (states.image) return "Generating image...";
      if (states.diagram) return "Generating diagram...";
      if (states.video) return "Generating video...";
      if (states.followups) return "Rounding up...";
      return "";
    };

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
      setBubbleLoading(prev => {
        const next = { ...prev, explanation: false };
        setStatus(updateStatus(next));
        return next;
      });
    };

    // Fetch Asset
    const fetchAsset = async (endpoint, prompt, key, setter) => {
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
      setBubbleLoading(prev => {
        const next = { ...prev, [key]: false };
        setStatus(updateStatus(next));
        return next;
      });
    };

    fetchExplanation();
    fetchAsset("/api/generate-diagram", prompts.diagram_prompt, "diagram", setDiagram);
    fetchAsset("/api/generate-image", prompts.image_prompt, "image", setImage);
    fetchAsset("/api/generate-video", prompts.video_prompt, "video", setVideo);
    fetchAsset("/api/generate-explanation", prompts.followup_prompt, "followups", (d) => setFollowups(d?.text || d));

  }, [prompts]);

  const chunkText = (text, maxLen = 160) => {
    const sentences = text.match(/[^.!?]+[.!?]+\s*/g) || [text];
    const chunks = [];
    let current = "";
    for (const sentence of sentences) {
      if ((current + sentence).length > maxLen && current.length > 0) {
        chunks.push(current.trim());
        current = sentence;
      } else {
        current += sentence;
      }
    }
    if (current.trim()) chunks.push(current.trim());
    return chunks;
  };

  const speak = () => {
    if (!window.speechSynthesis) {
      setTtsError(true);
      return;
    }

    if (isSpeaking) {
      stopRequestedRef.current = true;
      window.speechSynthesis.cancel();
      stopKeepAlive();
      setIsSpeaking(false);
      return;
    }

    const text = stripMarkdown(toStr(explanation));
    if (!text.trim()) return;

    window.speechSynthesis.cancel();
    stopRequestedRef.current = false;
    setTtsError(false);
    const chunks = chunkText(text);
    if (chunks.length === 0) return;

    setIsSpeaking(true);
    startKeepAlive();
    const speakChunk = (index) => {
      if (index >= chunks.length || stopRequestedRef.current) {
        setIsSpeaking(false);
        return;
      }

      const utterance = new SpeechSynthesisUtterance(chunks[index]);
      const voice = voiceRef.current;
      if (voice) {
        utterance.voice = voice;
        utterance.lang = voice.lang;
      } else {
        utterance.lang = "en";
      }

      utterance.onend = () => {
        if (!stopRequestedRef.current) speakChunk(index + 1);
      };
      utterance.onerror = (e) => {
        if (e.error === "interrupted" || e.error === "canceled") return;

        // On first chunk failure, retry once without a specific voice
        if (index === 0 && voice && !stopRequestedRef.current) {
          console.warn("SpeechSynthesis: retrying chunk 0 with generic lang...");
          const retry = new SpeechSynthesisUtterance(chunks[0]);
          retry.lang = "en";
          retry.onend = () => {
            if (!stopRequestedRef.current) speakChunk(1);
          };
          retry.onerror = (err) => {
            console.error("SpeechSynthesis definitive failure:", err.error);
            setTtsError(true);
            stopKeepAlive();
            setIsSpeaking(false);
          };
          window.speechSynthesis.speak(retry);
          return;
        }

        console.warn("SpeechSynthesis error on chunk", index, ":", e.error);
        if (e.error === "synthesis-failed" || e.error === "not-allowed") {
          setTtsError(true);
        }
        stopKeepAlive();
        setIsSpeaking(false);
      };

      window.speechSynthesis.speak(utterance);
    };

    speakChunk(0);
  };
  const anyLoading = Object.values(bubbleLoading).some(v => v);

  return (
    <div className={styles.assistantContent}>
      <div className={styles.textbookHeader}>
        <h2 className={styles.topicTitle}>{data.topic}</h2>
        <span className={styles.difficultyTag}>{data.difficulty}</span>
      </div>

      {(video || bubbleLoading.video) && (
        <div className={styles.videoHero}>
          {video ? (
            <video src={`data:${video.mime_type || 'video/mp4'};base64,${video.video_base64}`} controls autoPlay loop />
          ) : (
            <div className={styles.videoPlaceholder}>
              <div className={styles.videoPlaceholderIcon}><Icon name="grid" /></div>
              <span>Generating your educational video...</span>
            </div>
          )}
        </div>
      )}

      <div className={styles.textbookLayout}>
        <div className={styles.explanationCol}>
          <section className={styles.responseCard}>
            <h3 className={styles.responseCardTitle}>Explanation</h3>
            {bubbleLoading.explanation ? (
              <div className={styles.skeleton}>Generating explanation...</div>
            ) : (
              <MarkdownRenderer content={toStr(explanation)} />
            )}
          </section>

          {followups && (
            <section className={styles.responseCard}>
              <h4 className={styles.responseCardTitle}>Dive Deeper</h4>
              <MarkdownRenderer content={toStr(followups)} />
            </section>
          )}

          <button
            className={`${styles.ttsBtn} ${isSpeaking ? styles.ttsBtnActive : ""} ${ttsError ? styles.ttsBtnError : ""}`}
            onClick={speak}
            disabled={!explanation || (ttsError && !isSpeaking)}
          >
            <Icon name={ttsError ? "grid" : isSpeaking ? "moon" : "volume"} />
            {ttsError ? "Not Supported" : isSpeaking ? "Stop Reading" : "Read Aloud"}
          </button>
        </div>

        <aside className={styles.assetSidebar}>
          {diagram && diagram.image_base64 && (
            <section className={`${styles.assetCard} ${styles.expandable}`} onClick={() => setExpandedAsset({ type: 'diagram', data: diagram })}>
              <h5>Visual Diagram</h5>
              <img src={`data:${diagram.mime_type || 'image/jpeg'};base64,${diagram.image_base64}`} alt="Diagram" />
            </section>
          )}
          {image && (
            <section className={`${styles.assetCard} ${styles.expandable}`} onClick={() => setExpandedAsset({ type: 'image', data: image })}>
              <h5>Illustration</h5>
              <img src={`data:${image.mime_type || 'image/jpeg'};base64,${image.image_base64}`} alt="Illustration" />
            </section>
          )}
        </aside>
      </div>

      {anyLoading && status && (
        <CircularProgress status={status} />
      )}

      {expandedAsset && (
        <div className={styles.modalOverlay} onClick={() => setExpandedAsset(null)}>
          <div className={styles.modalContent} onClick={e => e.stopPropagation()}>
            <button className={styles.closeModal} onClick={() => setExpandedAsset(null)}>×</button>
            {expandedAsset.type === 'image' || expandedAsset.type === 'diagram' ? (
              <img src={`data:${expandedAsset.data.mime_type || 'image/jpeg'};base64,${expandedAsset.data.image_base64}`} alt="Expanded view" />
            ) : (
              <div className={styles.modalDiagram}>
                <p>Unable to display</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}