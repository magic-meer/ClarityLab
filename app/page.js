"use client";

import { useState, useRef, useEffect } from "react";
import styles from "./page.module.css";

export default function Home() {
  const [question, setQuestion] = useState("");
  const [modelName, setModelName] = useState("gemini-2.5-flash");
  const [imageModel, setImageModel] = useState("imagen-3.0-generate-001");
  const [voiceName, setVoiceName] = useState("en-US-Journey-D");
  const [file, setFile] = useState(null);
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const chatEndRef = useRef(null);
  const inputRef = useRef(null);

  // Dynamic model lists from API
  const [textModels, setTextModels] = useState([]);
  const [imageModels, setImageModels] = useState([]);
  const [audioVoices, setAudioVoices] = useState([]);

  // Fetch available models on mount
  useEffect(() => {
    async function fetchModels() {
      try {
        const res = await fetch("/api/models");
        const data = await res.json();
        if (data.status === "success") {
          setTextModels(data.text_models || []);
          setImageModels(data.image_models || []);
          setAudioVoices(data.audio_voices || []);
          // Set default to first available if current default isn't in list
          if (data.text_models?.length && !data.text_models.find(m => m.name === modelName)) {
            setModelName(data.text_models[0].name);
          }
          if (data.image_models?.length && !data.image_models.find(m => m.name === imageModel)) {
            setImageModel(data.image_models[0].name);
          }
        }
      } catch (err) {
        console.error("Failed to fetch models:", err);
        // Fallback to hardcoded defaults
        setTextModels([
          { name: "gemini-2.5-flash", display_name: "Gemini 2.5 Flash" },
          { name: "gemini-2.5-pro", display_name: "Gemini 2.5 Pro" },
        ]);
        setImageModels([
          { name: "imagen-3.0-generate-001", display_name: "Imagen 3" },
        ]);
        setAudioVoices([
          { name: "en-US-Journey-D", display_name: "Journey (US Male)" },
          { name: "en-US-Standard-A", display_name: "Standard (US Male)" },
        ]);
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

    // Add user message
    setConversations((prev) => [
      ...prev,
      { role: "user", content: userQ, fileUrl },
    ]);
    setLoading(true);

    try {
      let res;
      if (currentFile) {
        const formData = new FormData();
        formData.append("question", userQ);
        formData.append("model_name", modelName);
        formData.append("file", currentFile);

        res = await fetch("/api/analyze", {
          method: "POST",
          body: formData,
        });
      } else {
        res = await fetch("/api/explain", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question: userQ, model_name: modelName }),
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
      inputRef.current?.focus();
    }
  };

  return (
    <div className={styles.container}>
      {/* Sidebar */}
      <aside className={styles.sidebar}>
        <div className={styles.brand}>
          <div className={styles.brandIcon}>✦</div>
          <h1 className={styles.brandName}>ClarityLab</h1>
        </div>
        <p className={styles.brandTagline}>
          AI-Powered Multimodal Learning Agent
        </p>

        <div className={styles.sidebarSection}>
          <h3 className={styles.sidebarTitle}>Model Settings</h3>
          <div className={styles.settingsSection}>
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
              <label className={styles.settingsLabel}>Image Model</label>
              <select className={styles.settingsSelect} value={imageModel} onChange={(e) => setImageModel(e.target.value)}>
                {imageModels.length > 0 ? imageModels.map((m) => (
                  <option key={m.name} value={m.name}>{m.display_name}</option>
                )) : (
                  <option value={imageModel}>Loading...</option>
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
                  imageModel={imageModel}
                  voiceName={voiceName}
                />
              )}
            </div>
          ))}

          {loading && (
            <div className={`${styles.message} ${styles.assistantMessage} fade-in-up`}>
              <LoadingSkeleton />
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
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
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

function AssistantBubble({ data, usage, imageModel, voiceName }) {
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
        <p className={styles.sectionBody}>{data.explanation || data.analysis || data}</p>
      </div>

      {/* Key points */}
      {data.key_points?.length > 0 && (
        <div className={styles.section}>
          <h3 className={styles.sectionTitle}>💡 Key Points</h3>
          <ul className={styles.keyPoints}>
            {data.key_points.map((pt, i) => (
              <li key={i} className={styles.keyPoint}>
                {pt}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Diagram prompt — auto-generates */}
      {data.diagram_prompt && (
        <div className={styles.section}>
          <h3 className={styles.sectionTitle}>🎨 Diagram</h3>
          <div className={styles.promptCard}>{data.diagram_prompt}</div>
          <DiagramGenerator prompt={data.diagram_prompt} modelName={imageModel} />
        </div>
      )}

      {/* Animation prompt */}
      {data.animation_prompt && (
        <div className={styles.section}>
          <h3 className={styles.sectionTitle}>🎬 Animation Concept</h3>
          <div className={styles.promptCard}>{data.animation_prompt}</div>
        </div>
      )}

      {/* Simulation prompt */}
      {data.simulation_prompt && (
        <div className={styles.section}>
          <h3 className={styles.sectionTitle}>🕹️ Simulation Idea</h3>
          <div className={styles.promptCard}>{data.simulation_prompt}</div>
        </div>
      )}

      {/* Narration — auto-plays */}
      {data.narration_script && (
        <NarrationPlayer text={data.narration_script} voiceName={voiceName} />
      )}

      {/* Follow-up */}
      {data.follow_up_questions?.length > 0 && (
        <div className={styles.section}>
          <h3 className={styles.sectionTitle}>🤔 Follow-up Questions</h3>
          <div className={styles.followUps}>
            {data.follow_up_questions.map((q, i) => (
              <div key={i} className={styles.followUpCard}>
                {q}
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

function DiagramGenerator({ prompt, modelName }) {
  const [imageUrl, setImageUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Auto-generate on mount
  useEffect(() => {
    let cancelled = false;
    async function generate() {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch("/api/generate-image", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ prompt, model_name: modelName }),
        });
        if (!res.ok) {
          const errData = await res.json().catch(() => ({}));
          throw new Error(errData.error || "Failed to generate image");
        }
        const data = await res.json();
        if (!cancelled && data.status === "success" && data.image_data) {
          setImageUrl(data.image_data);
        } else if (!cancelled) {
          throw new Error("Invalid image data");
        }
      } catch (err) {
        if (!cancelled) {
          console.error(err);
          setError(err.message || "Could not generate diagram.");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    generate();
    return () => { cancelled = true; };
  }, [prompt, modelName]);

  return (
    <div style={{ marginTop: "12px" }}>
      {loading && (
        <div className={styles.genImgBtn} style={{ cursor: "default", opacity: 0.7 }}>
          ⏳ Generating diagram...
        </div>
      )}
      {imageUrl && (
        <div className={styles.generatedImageWrapper}>
          <img src={imageUrl} alt="Generated diagram" className={styles.generatedImage} />
        </div>
      )}
      {error && <span className={styles.audioError} style={{ display: "block", marginTop: "4px" }}>⚠ {error}</span>}
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <div className={styles.assistantBubble}>
      <div className={styles.topicHeader}>
        <span className={styles.assistantAvatar}>✦</span>
        <div className={`skeleton ${styles.skeletonTitle}`} />
      </div>
      <div className={styles.section}>
        <div className={`skeleton ${styles.skeletonLine}`} />
        <div className={`skeleton ${styles.skeletonLine}`} style={{ width: "85%" }} />
        <div className={`skeleton ${styles.skeletonLine}`} style={{ width: "60%" }} />
      </div>
      <div className={styles.section}>
        <div className={`skeleton ${styles.skeletonLine}`} style={{ width: "40%" }} />
        <div className={`skeleton ${styles.skeletonLine}`} />
        <div className={`skeleton ${styles.skeletonLine}`} style={{ width: "75%" }} />
      </div>
    </div>
  );
}

function NarrationPlayer({ text, voiceName }) {
  const [audioUrl, setAudioUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Auto-synthesize on mount
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
          {text}
        </blockquote>
        <div className={styles.audioControls}>
          {loading && <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>⏳ Synthesizing audio...</span>}
          {audioUrl && <audio src={audioUrl} controls autoPlay className={styles.audioPlayer} />}
          {error && <span className={styles.audioError}>{error}</span>}
        </div>
      </div>
    </div>
  );
}
