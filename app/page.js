"use client";

import { useState, useRef, useEffect } from "react";
import styles from "./page.module.css";

const DIFFICULTY_OPTIONS = [
  { value: "beginner", label: "Beginner", emoji: "🌱" },
  { value: "intermediate", label: "Intermediate", emoji: "📘" },
  { value: "advanced", label: "Advanced", emoji: "🔬" },
  { value: "expert", label: "Expert", emoji: "🧠" },
];

export default function Home() {
  const [question, setQuestion] = useState("");
  const [difficulty, setDifficulty] = useState("beginner");
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const chatEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [conversations, loading]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim() || loading) return;

    const userQ = question.trim();
    setQuestion("");
    setError(null);

    // Add user message
    setConversations((prev) => [
      ...prev,
      { role: "user", content: userQ, difficulty },
    ]);
    setLoading(true);

    try {
      const res = await fetch("/api/explain", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: userQ, difficulty }),
      });

      const data = await res.json();

      if (data.status === "success" && data.data) {
        setConversations((prev) => [
          ...prev,
          { role: "assistant", content: data.data },
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
          <h3 className={styles.sidebarTitle}>Difficulty</h3>
          <div className={styles.difficultyGrid}>
            {DIFFICULTY_OPTIONS.map((opt) => (
              <button
                key={opt.value}
                className={`${styles.difficultyBtn} ${
                  difficulty === opt.value ? styles.difficultyActive : ""
                }`}
                onClick={() => setDifficulty(opt.value)}
              >
                <span>{opt.emoji}</span>
                <span>{opt.label}</span>
              </button>
            ))}
          </div>
        </div>

        <div className={styles.sidebarSection}>
          <h3 className={styles.sidebarTitle}>Try asking</h3>
          <div className={styles.suggestions}>
            {[
              "Explain quantum entanglement",
              "How does photosynthesis work?",
              "What is a neural network?",
              "Explain the theory of relativity",
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
                <UserBubble content={msg.content} difficulty={msg.difficulty} />
              ) : msg.error ? (
                <ErrorBubble message={msg.error} />
              ) : (
                <AssistantBubble data={msg.content} />
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
          <div className={styles.inputWrapper}>
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
                <span className={styles.spinner} />
              ) : (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
              )}
            </button>
          </div>
        </form>
      </main>
    </div>
  );
}

/* Sub-components */

function UserBubble({ content, difficulty }) {
  return (
    <div className={styles.userBubble}>
      <div className={styles.userAvatar}>You</div>
      <div>
        <p className={styles.userText}>{content}</p>
        <span className={`${styles.tag} ${styles[`tag_${difficulty}`]}`}>
          {difficulty}
        </span>
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

function AssistantBubble({ data }) {
  if (!data) return null;

  return (
    <div className={styles.assistantBubble}>
      {/* Topic header */}
      <div className={styles.topicHeader}>
        <span className={styles.assistantAvatar}>✦</span>
        <div>
          <h2 className={styles.topicTitle}>{data.topic}</h2>
          <span className={`${styles.tag} ${styles[`tag_${data.difficulty}`]}`}>
            {data.difficulty}
          </span>
        </div>
      </div>

      {/* Explanation */}
      <div className={styles.section}>
        <h3 className={styles.sectionTitle}>📝 Explanation</h3>
        <p className={styles.sectionBody}>{data.explanation}</p>
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

      {/* Diagram prompt */}
      {data.diagram_prompt && (
        <div className={styles.section}>
          <h3 className={styles.sectionTitle}>🎨 Diagram Concept</h3>
          <div className={styles.promptCard}>{data.diagram_prompt}</div>
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

      {/* Narration */}
      {data.narration_script && (
        <div className={styles.section}>
          <h3 className={styles.sectionTitle}>🎙️ Narration Script</h3>
          <blockquote className={styles.narration}>
            {data.narration_script}
          </blockquote>
        </div>
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
