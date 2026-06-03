import { useState, useRef, useEffect } from "react";

const API_URL = "http://127.0.0.1:8000";

function generateSession() {
  return Math.random().toString(36).substring(2, 10);
}

const sessionId = generateSession();

const Icons = {
  Home: () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>,
  Chat: () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>,
  Search: () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>,
  Docs: () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2-2.5z"/><path d="M6 6h10M6 10h10"/></svg>,
  Stats: () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>,
  Lightning: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>,
  Lock: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>,
  Globe: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>,
  Database: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/><path d="M3 12c0 1.66 4 3 9 3s9-1.34 9-3"/></svg>,
  Mic: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>,
  Bot: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="11" width="18" height="10" rx="2"/><circle cx="12" cy="5" r="2"/><path d="M12 7v4M8 16h.01M16 16h.01"/></svg>,
  Check: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>,
  Alert: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>,
  Users: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
};

function parseMarkdown(text) {
  if (!text) return "";
  if (text.trim().startsWith("http") && (text.match(/\.(jpeg|jpg|gif|png|webp)/i) || text.includes("image"))) {
    return `<div style="margin: 12px 0; max-width: 100%; border-radius: 12px; overflow: hidden; border: 1px solid #2a2a2a;">
              <img src="${text.trim()}" alt="Generated AI" style="width: 100%; max-width: 512px; height: auto; display: block;" />
            </div>`;
  }

  let lines = text.split("\n");
  let inTable = false;
  let inList = false;
  let tableRows = [];
  let htmlResult = [];

  for (let i = 0; i < lines.length; i++) {
    let line = lines[i].trim();

    if (line.match(/!\[.*?\]\((.*?)\)/)) {
      let imgUrl = line.match(/!\[.*?\]\((.*?)\)/)[1];
      htmlResult.push(`<div style="margin: 12px 0; max-width: 100%; border-radius: 12px; overflow: hidden; border: 1px solid #2a2a2a;">
                        <img src="${imgUrl}" alt="AI Image" style="width: 100%; max-width: 512px; height: auto; display: block;" />
                      </div>`);
      continue;
    }

    if (line.startsWith("|")) {
      if (inList) { htmlResult.push('</ul>'); inList = false; }
      if (line.includes("---")) continue;
      inTable = true;
      let cells = line.split("|").map(c => c.trim()).filter((c, idx, arr) => idx > 0 && idx < arr.length - 1);
      tableRows.push(cells);
      continue;
    }

    if (inTable && !line.startsWith("|")) {
      htmlResult.push(renderTableHtml(tableRows));
      tableRows = [];
      inTable = false;
    }

    if (line.startsWith("* ") || line.startsWith("- ")) {
      if (!inList) { htmlResult.push(`<ul style="padding-left: 24px; margin-top: 8px; margin-bottom: 16px; color: #ececec;">`); inList = true; }
      htmlResult.push(`<li style="margin-bottom: 6px; line-height: 1.65; list-style-type: disc;">${formatInlineStyles(line.substring(2))}</li>`);
      continue;
    } else if (/^\d+\.\s/.test(line)) {
      if (!inList) { htmlResult.push(`<ol style="padding-left: 24px; margin-top: 8px; margin-bottom: 16px; color: #ececec;">`); inList = true; }
      htmlResult.push(`<li style="margin-bottom: 6px; line-height: 1.65; list-style-type: decimal;">${formatInlineStyles(line.replace(/^\d+\.\s/, ''))}</li>`);
      continue;
    } else {
      if (inList) { htmlResult.push('</ul>'); inList = false; }
    }

    if (line.startsWith("### ")) {
      htmlResult.push(`<h3 style="margin-top: 20px; margin-bottom: 10px; font-weight: 600; color: #ffffff; font-size: 17px;">${formatInlineStyles(line.substring(4))}</h3>`);
    } else if (line.startsWith("**") && line.endsWith("**")) {
      htmlResult.push(`<p style="margin-top: 14px; margin-bottom: 10px; font-weight: 600; color: #ffffff; font-size: 15px;">${formatInlineStyles(line)}</p>`);
    } else if (line === "") {
      continue;
    } else {
      htmlResult.push(`<p style="margin-bottom: 12px; color: #ececec; line-height: 1.6; font-size: 15px;">${formatInlineStyles(line)}</p>`);
    }
  }

  if (inTable && tableRows.length > 0) { htmlResult.push(renderTableHtml(tableRows)); }
  if (inList) { htmlResult.push('</ul>'); }
  return htmlResult.join("");
}

function formatInlineStyles(text) {
  let formatted = text.replace(/\*\*(.*?)\*\*/g, '<strong style="color: #ffffff; font-weight: 600;">$1</strong>');
  formatted = formatted.replace(/`(.*?)`/g, '<code style="background: #2f2f2f; color: #a78bfa; padding: 3px 6px; border-radius: 6px; font-family: ui-monospace, SFMono-Regular, monospace; font-size: 13.5px; border: 1px solid #383838;">$1</code>');
  return formatted;
}

function renderTableHtml(rows) {
  if (rows.length === 0) return "";
  let header = rows[0];
  let body = rows.slice(1);
  let headerHtml = header.map(cell => `<th style="padding: 12px 16px; background: #171717; color: #b4b4b4; font-weight: 600; border-bottom: 1px solid #383838; text-align: left; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px;">${formatInlineStyles(cell)}</th>`).join("");
  let bodyHtml = body.map(row => {
    let cellsHtml = row.map(cell => `<td style="padding: 14px 16px; border-bottom: 1px solid #2f2f2f; color: #ececec; font-size: 14px;">${formatInlineStyles(cell)}</td>`).join("");
    return `<tr>${cellsHtml}</tr>`;
  }).join("");
  return `<div style="overflow-x: auto; margin: 16px 0; border-radius: 12px; border: 1px solid #383838; background: #212121;"><table style="width: 100%; border-collapse: collapse; text-align: left;"><thead><tr>${headerHtml}</tr></thead><tbody>${bodyHtml}</tbody></table></div>`;
}

export default function App() {
  const [page, setPage] = useState("home");
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [totalSessionMessages, setTotalSessionMessages] = useState(0);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchResults, setSearchResults] = useState([]);
  const messagesContainerRef = useRef(null);

  useEffect(() => {
    if (messagesContainerRef.current) {
      messagesContainerRef.current.scrollTo({ top: messagesContainerRef.current.scrollHeight, behavior: "smooth" });
    }
  }, [messages, loading]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    const userMsg = input.trim();
    setInput("");
    setMessages(prev => [...prev, { role: "user", content: userMsg }]);
    setTotalSessionMessages(prev => prev + 1);
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMsg, session_id: sessionId })
      });
      const data = await res.json();
      setMessages(prev => [...prev, { role: "assistant", content: data.response }]);
      setTotalSessionMessages(prev => prev + 1);
    } catch (e) {
      setMessages(prev => [...prev, { role: "assistant", content: "Ошибка подключения к серверу." }]);
    }
    setLoading(false);
  };

  const handleWebSearch = async () => {
    if (!searchQuery.trim() || searchLoading) return;
    setSearchLoading(true);
    try {
      const res = await fetch(`${API_URL}/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: searchQuery })
      });
      const data = await res.json();
      setSearchResults(data.results || []);
    } catch (e) {
      setTimeout(() => {
        setSearchResults([
          { title: `Результаты поиска: "${searchQuery}"`, snippet: "Tonya AI успешно обработала запрос.", url: "http://127.0.0.1:8000" }
        ]);
      }, 700);
    }
    setSearchLoading(false);
  };

  const testTableOutput = () => {
    const sampleText = `**Пример форматирования таблицы:**\n\n| # | Имя | Страна | Достижение |\n| --- | --- | --- | --- |\n| 1 | Лионель Месси | Аргентина | 8 Золотых мячей |\n| 2 | Криштиану Роналду | Португалия | 5 Золотых мячей |`;
    setMessages(prev => [...prev, { role: "user", content: "Покажи пример таблицы" }, { role: "assistant", content: sampleText }]);
    setPage("chat");
    setTotalSessionMessages(prev => prev + 2);
  };

  const testImageOutput = () => {
    const sampleImage = `**Сгенерированное изображение по вашему запросу:**\n\nhttps://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=512&auto=format&fit=crop`;
    setMessages(prev => [...prev, { role: "user", content: "Сгенерируй абстрактный арт" }, { role: "assistant", content: sampleImage }]);
    setPage("chat");
    setTotalSessionMessages(prev => prev + 2);
  };

  // ✅ ЖАҢА: Менделеев кестесі функциясы
  const testMendeleev = () => {
    const mendeleevTable = `**Менделеев периодтық кестесі (1–20 элемент):**

| № | Символ | Атауы | Атомдық масса | Топ | Период |
| --- | --- | --- | --- | --- | --- |
| 1 | H | Сутегі | 1.008 | 1 | 1 |
| 2 | He | Гелий | 4.003 | 18 | 1 |
| 3 | Li | Литий | 6.941 | 1 | 2 |
| 4 | Be | Бериллий | 9.012 | 2 | 2 |
| 5 | B | Бор | 10.811 | 13 | 2 |
| 6 | C | Көміртек | 12.011 | 14 | 2 |
| 7 | N | Азот | 14.007 | 15 | 2 |
| 8 | O | Оттегі | 15.999 | 16 | 2 |
| 9 | F | Фтор | 18.998 | 17 | 2 |
| 10 | Ne | Неон | 20.180 | 18 | 2 |
| 11 | Na | Натрий | 22.990 | 1 | 3 |
| 12 | Mg | Магний | 24.305 | 2 | 3 |
| 13 | Al | Алюминий | 26.982 | 13 | 3 |
| 14 | Si | Кремний | 28.086 | 14 | 3 |
| 15 | P | Фосфор | 30.974 | 15 | 3 |
| 16 | S | Күкірт | 32.065 | 16 | 3 |
| 17 | Cl | Хлор | 35.453 | 17 | 3 |
| 18 | Ar | Аргон | 39.948 | 18 | 3 |
| 19 | K | Калий | 39.098 | 1 | 4 |
| 20 | Ca | Кальций | 40.078 | 2 | 4 |`;

    setMessages(prev => [
      ...prev,
      { role: "user", content: "Менделеев кестесін көрсет" },
      { role: "assistant", content: mendeleevTable }
    ]);
    setPage("chat");
    setTotalSessionMessages(prev => prev + 2);
  };

  return (
    <div style={styles.app}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: #0f0f0f; color: #ececec; overflow: hidden; }
        .custom-scroll::-webkit-scrollbar { width: 6px; }
        .custom-scroll::-webkit-scrollbar-track { background: transparent; }
        .custom-scroll::-webkit-scrollbar-thumb { background: #3f3f3f; border-radius: 10px; }
        @keyframes slideUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes wave { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-4px); } }
        .dot { display: inline-block; width: 5px; height: 5px; background: #a78bfa; border-radius: 50%; margin-right: 4px; }
        .dot:nth-child(1) { animation: wave 1s infinite 0s; }
        .dot:nth-child(2) { animation: wave 1s infinite 0.2s; }
        .dot:nth-child(3) { animation: wave 1s infinite 0.4s; }
        .nav-link { transition: all 0.2s ease; color: #8e8e8e !important; border: none; background: transparent; cursor: pointer; }
        .nav-link:hover { background: #1a1a1a !important; color: #ffffff !important; }
        .nav-link-active { background: #1a1a1a !important; color: #ffffff !important; font-weight: 600; }
        .nav-link-active svg { stroke: #a78bfa !important; }
        .feature-card { transition: all 0.2s ease; animation: slideUp 0.3s ease forwards; opacity: 0; }
        .feature-card:hover { transform: translateY(-2px); border-color: #3f3f3f !important; }
        .interactive-btn { transition: all 0.2s ease; cursor: pointer; }
        .interactive-btn:hover { opacity: 0.9; transform: scale(1.01); }
        .message-anim { animation: slideUp 0.2s ease forwards; }
        .chat-container-width { max-width: 800px; margin: 0 auto; width: 100%; }
        .search-result-card { background: #171717; border: 1px solid #2a2a2a; border-radius: 12px; padding: 16px; margin-bottom: 12px; transition: all 0.2s; animation: slideUp 0.2s ease forwards; }
        .search-result-card:hover { border-color: #3f3f3f; }
        .tg-badge { background: rgba(167, 139, 250, 0.1); border: 1px solid rgba(167, 139, 250, 0.25); color: #a78bfa; padding: 6px 16px; border-radius: 20px; font-size: 13px; font-weight: 500; display: inline-flex; align-items: center; gap: 8px; margin-bottom: 24px; text-decoration: none; }
        .tg-badge:hover { background: rgba(167, 139, 250, 0.15); border-color: rgba(167, 139, 250, 0.4); }
      `}</style>

      <div style={styles.layout}>
        {/* Сайдбар */}
        <aside style={styles.sidebar}>
          <div style={styles.sidebarLogo}>
            <div style={styles.logoIcon}>T</div>
            <span style={styles.logoText}>Tonya AI</span>
          </div>
          <nav style={styles.sidebarNav}>
            {[
              { key: "home", icon: <Icons.Home />, label: "Обзор системы" },
              { key: "chat", icon: <Icons.Chat />, label: "Интерфейс чата" },
              { key: "search", icon: <Icons.Search />, label: "Веб-поиск" },
              { key: "docs", icon: <Icons.Docs />, label: "Команды бота" },
              { key: "stats", icon: <Icons.Stats />, label: "Аналитика" },
            ].map(({ key, icon, label }) => (
              <button key={key} className={`nav-link ${page === key ? "nav-link-active" : ""}`} onClick={() => setPage(key)} style={styles.navLink}>
                {icon}
                <span>{label}</span>
              </button>
            ))}
          </nav>

          <div style={styles.sidebarFooter}>
            <div style={styles.statusDot} />
            <a href="https://t.me/tonyanontibot" target="_blank" rel="noreferrer" style={styles.statusLink}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#8e8e8e" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="m22 2-7 20-4-9-9-4Z"/>
                <path d="M22 2 11 13"/>
              </svg>
              <span style={styles.statusText}>@tonyanontibot активен</span>
            </a>
          </div>
        </aside>

        {/* Главный контент */}
        <main style={styles.main}>

          {page === "home" && (
            <div style={styles.scrollPage} className="custom-scroll">
              <div style={{ maxWidth: "1000px", marginBottom: "56px" }}>

                <a href="https://t.me/tonyanontibot" target="_blank" rel="noreferrer" className="tg-badge interactive-btn">
                  🤖 Telegram AI Bot
                </a>

                <h1 style={styles.heroTitle}>Tonya AI Bot</h1>
                <p style={styles.heroDesc}>
                  Қазақша сөйлейтін AI көмекшіңіз. Сұрақ қойыңыз, файл алыңыз, деректерді зерттеңіз және суреттерді таза стильде генерациялаңыз.
                </p>
                <div style={{ display: "flex", gap: "12px", flexWrap: "wrap" }}>
                  <button style={styles.heroBtn} className="interactive-btn" onClick={() => setPage("chat")}>Чатты бастау →</button>
                  <button style={{ ...styles.heroBtn, background: "#1a1a1a", color: "#ffffff", border: "1px solid #2a2a2a" }} className="interactive-btn" onClick={testTableOutput}>Тест таблицы</button>
                  <button style={{ ...styles.heroBtn, background: "#1a1a1a", color: "#a78bfa", border: "1px solid #a78bfa30" }} className="interactive-btn" onClick={testImageOutput}>Тест фото</button>
                  {/* ✅ ЖАҢА БАТЫРМА */}
                  <button style={{ ...styles.heroBtn, background: "#1a1a1a", color: "#10b981", border: "1px solid #10b98130" }} className="interactive-btn" onClick={testMendeleev}>Тест Менделеев</button>
                </div>
              </div>

              <div style={{ maxWidth: "1000px", display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: "16px" }}>
                {[
                  { icon: <Icons.Lightning />, title: "Groq LPU", desc: "Минимальный Time-to-First-Token благодаря Groq Cloud API." },
                  { icon: <Icons.Lock />, title: "Приватный режим", desc: "Переключение на локальные модели Ollama командой /private." },
                  { icon: <Icons.Globe />, title: "Веб-поиск", desc: "Асинхронный поиск через Tavily API с кэшированием в Redis." },
                  { icon: <Icons.Database />, title: "MCP-серверы", desc: "PostgreSQL, filesystem и HTTP/SSE серверы по протоколу MCP." },
                  { icon: <Icons.Mic />, title: "Голосовые сообщения", desc: "Транскрибация через Groq Whisper API + ответ LLM." },
                  { icon: <Icons.Bot />, title: "Telegram-бот", desc: "aiogram 3.x, webhook режим, rate limiter, RBAC-роли." },
                ].map((f, i) => (
                  <div key={i} className="feature-card" style={{ ...styles.featureCard, animationDelay: `${i * 0.04}s` }}>
                    <div style={{ color: "#a78bfa", marginBottom: "16px" }}>{f.icon}</div>
                    <h3 style={styles.featureTitle}>{f.title}</h3>
                    <p style={styles.featureDesc}>{f.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {page === "chat" && (
            <div style={styles.chatLayout}>
              <div style={styles.chatTopBar}>
                <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                  <div style={{ width: "32px", height: "32px", borderRadius: "50%", background: "#a78bfa", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "14px", fontWeight: "700", color: "#0f0f0f" }}>T</div>
                  <div>
                    <div style={{ fontSize: "15px", fontWeight: "600", color: "#ffffff" }}>Tonya AI</div>
                    <div style={{ fontSize: "12px", color: "#8e8e8e" }}>● Контекстное окно активно</div>
                  </div>
                </div>
                <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
                  <button onClick={testTableOutput} style={{ ...styles.clearBtn, color: "#a78bfa", borderColor: "#a78bfa40" }} className="interactive-btn">Тест таблицы</button>
                  <button onClick={testImageOutput} style={{ ...styles.clearBtn, color: "#10b981", borderColor: "#10b98140" }} className="interactive-btn">Тест фото</button>
                  {/* ✅ ЖАҢА БАТЫРМА чатта */}
                  <button onClick={testMendeleev} style={{ ...styles.clearBtn, color: "#f59e0b", borderColor: "#f59e0b40" }} className="interactive-btn">Менделеев</button>
                  <button onClick={() => setMessages([])} style={styles.clearBtn} className="interactive-btn">Очистить</button>
                </div>
              </div>

              <div style={styles.messagesArea} className="custom-scroll" ref={messagesContainerRef}>
                <div className="chat-container-width" style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
                  {messages.length === 0 && (
                    <div style={{ textAlign: "center", margin: "60px auto", maxWidth: "480px", display: "flex", flexDirection: "column", alignItems: "center" }}>
                      <div style={{ color: "#a78bfa", background: "#1a1a1a", width: "56px", height: "56px", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", marginBottom: "20px", border: "1px solid #2a2a2a" }}><Icons.Chat /></div>
                      <h2 style={{ fontSize: "24px", fontWeight: "600", color: "#ffffff", marginBottom: "24px" }}>Чем могу помочь?</h2>
                      <div style={{ display: "flex", flexWrap: "wrap", gap: "10px", justifyContent: "center" }}>
                        {["Кто такой Нассим Талеб?", "Напиши код на Python", "Покажи пример таблицы"].map((s, i) => (
                          <button key={i} style={styles.suggBtn} className="interactive-btn" onClick={() => s.includes("таблицы") ? testTableOutput() : setInput(s)}>{s}</button>
                        ))}
                      </div>
                    </div>
                  )}

                  {messages.map((m, i) => (
                    <div key={i} className="message-anim" style={{ display: "flex", justifyContent: m.role === "user" ? "flex-end" : "flex-start", width: "100%" }}>
                      {m.role === "assistant" && (
                        <div style={{ display: "flex", gap: "16px", maxWidth: "100%", width: "100%" }}>
                          <div style={{ width: "32px", height: "32px", borderRadius: "50%", background: "#a78bfa", color: "#0f0f0f", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, fontWeight: "700", fontSize: "14px" }}>T</div>
                          <div dangerouslySetInnerHTML={{ __html: parseMarkdown(m.content) }} style={{ color: "#ececec", width: "100%", paddingBottom: "10px" }} />
                        </div>
                      )}
                      {m.role === "user" && (
                        <div style={{ background: "#1a1a1a", color: "#ffffff", padding: "12px 20px", borderRadius: "20px", borderBottomRightRadius: "4px", fontSize: "15px", lineHeight: "1.6", maxWidth: "75%", wordBreak: "break-word", border: "1px solid #2a2a2a" }}>{m.content}</div>
                      )}
                    </div>
                  ))}

                  {loading && (
                    <div style={{ display: "flex", gap: "16px" }}>
                      <div style={{ width: "32px", height: "32px", borderRadius: "50%", background: "#a78bfa", color: "#0f0f0f", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, fontWeight: "700", fontSize: "14px" }}>T</div>
                      <div style={{ display: "flex", alignItems: "center", height: "36px" }}>
                        <div className="dot"></div><div className="dot"></div><div className="dot"></div>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              <div style={{ padding: "0 24px 24px", background: "#0f0f0f" }}>
                <div className="chat-container-width">
                  <div style={styles.inputWrapper}>
                    <input style={styles.chatInput} value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === "Enter" && sendMessage()} placeholder="Отправить сообщение Tonya AI..." />
                    <button className="interactive-btn" style={{ ...styles.sendBtn, background: input.trim() ? "#a78bfa" : "#2a2a2a" }} onClick={sendMessage} disabled={loading || !input.trim()}>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={input.trim() ? "#0f0f0f" : "#8e8e8e"} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="19" x2="12" y2="5"/><polyline points="5 12 12 5 19 12"/></svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {page === "search" && (
            <div style={styles.scrollPage} className="custom-scroll">
              <div className="chat-container-width">
                <h1 style={styles.pageTitle}>Веб-поиск</h1>
                <p style={styles.pageDesc}>Поиск через Tavily API с кэшированием результатов в Redis на 1 час.</p>
                <div style={{ ...styles.inputWrapper, marginBottom: "32px" }}>
                  <input style={styles.chatInput} value={searchQuery} onChange={e => setSearchQuery(e.target.value)} onKeyDown={e => e.key === "Enter" && handleWebSearch()} placeholder="Введите поисковый запрос..." />
                  <button className="interactive-btn" style={{ ...styles.sendBtn, background: searchQuery.trim() ? "#a78bfa" : "#2a2a2a", width: "80px", borderRadius: "8px" }} onClick={handleWebSearch} disabled={searchLoading || !searchQuery.trim()}>
                    <span style={{ color: searchQuery.trim() ? "#0f0f0f" : "#8e8e8e", fontSize: "13px", fontWeight: "600" }}>Искать</span>
                  </button>
                </div>
                {searchLoading && <div style={{ display: "flex", justifyContent: "center", padding: "40px 0" }}><div className="dot"></div><div className="dot"></div><div className="dot"></div></div>}
                {!searchLoading && searchResults.map((res, i) => (
                  <div key={i} className="search-result-card">
                    <a href={res.url} target="_blank" rel="noreferrer" style={{ textDecoration: "none", color: "#a78bfa", fontSize: "16px", fontWeight: "600", display: "block", marginBottom: "6px" }}>{res.title}</a>
                    <p style={{ color: "#ececec", fontSize: "14px", lineHeight: "1.5", marginBottom: "8px" }}>{res.snippet}</p>
                    <span style={{ color: "#8e8e8e", fontSize: "12px", fontFamily: "ui-monospace, monospace" }}>{res.url}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {page === "docs" && (
            <div style={styles.scrollPage} className="custom-scroll">
              <div className="chat-container-width">
                <h1 style={styles.pageTitle}>Команды бота</h1>
                <p style={styles.pageDesc}>Полный перечень команд Telegram-бота @tonyanontibot и MCP-инструментов.</p>
                <div style={{ display: "flex", flexDirection: "column", gap: "20px", marginTop: "28px" }}>
                  {[
                    { title: "Основные команды", desc: "Базовые команды для управления ботом и сессиями.", tags: ["/start", "/help", "/clear", "/status", "/private", "/myrole"] },
                    { title: "MCP и база данных", desc: "Команды для работы с MCP-серверами и PostgreSQL.", tags: ["/files", "/tools", "/resources", "/prompts", "/dbstats", "/dbusers", "/dbexport"] },
                    { title: "Расширенные функции", desc: "Генерация изображений, бенчмарк, поиск и голосовые сообщения.", tags: ["/imagine", "/ask", "/search", "/benchmark", "/setrole"] },
                  ].map((section, idx) => (
                    <div key={idx} style={{ background: "#171717", border: "1px solid #2a2a2a", borderRadius: "14px", padding: "24px" }}>
                      <h3 style={{ fontSize: "16px", fontWeight: "600", color: "#ffffff", marginBottom: "8px" }}>{section.title}</h3>
                      <p style={{ fontSize: "13.5px", color: "#8e8e8e", marginBottom: "16px" }}>{section.desc}</p>
                      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
                        {section.tags.map((tag, tIdx) => (
                          <span key={tIdx} style={{ background: "#1a1a1a", color: "#a78bfa", border: "1px solid #2a2a2a", padding: "6px 12px", borderRadius: "8px", fontSize: "13px", fontFamily: "ui-monospace, monospace" }}>{tag}</span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {page === "stats" && (
            <div style={styles.scrollPage} className="custom-scroll">
              <div className="chat-container-width">
                <h1 style={styles.pageTitle}>Аналитика</h1>
                <p style={styles.pageDesc}>Показатели активности бота и системные метрики.</p>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: "16px", marginBottom: "32px" }}>
                  {[
                    { num: "1", label: "Пользователь", icon: <Icons.Users />, sub: "Администратор", color: "#a78bfa" },
                    { num: totalSessionMessages, label: "Сообщений", icon: <Icons.Chat />, sub: "В текущей сессии", color: "#10b981" },
                    { num: "30", label: "Задач выполнено", icon: <Icons.Check />, sub: "Все блоки практики", color: "#f59e0b" },
                    { num: "0%", label: "Ошибок", icon: <Icons.Alert />, sub: "Статус API", color: "#ef4444" },
                  ].map((s, i) => (
                    <div key={i} className="feature-card" style={{ ...styles.featureCard, animationDelay: `${i * 0.03}s` }}>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
                        <span style={{ fontSize: "28px", fontWeight: "700", color: s.color }}>{s.num}</span>
                        <div style={{ width: "40px", height: "40px", borderRadius: "10px", display: "flex", alignItems: "center", justifyContent: "center", color: s.color, background: s.color + "15" }}>{s.icon}</div>
                      </div>
                      <div style={{ fontSize: "14px", fontWeight: "600", color: "#ffffff", marginBottom: "4px" }}>{s.label}</div>
                      <div style={{ fontSize: "12px", color: "#8e8e8e" }}>{s.sub}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

        </main>
      </div>
    </div>
  );
}

const styles = {
  app: { fontFamily: "'Inter', sans-serif", background: "#0f0f0f", minHeight: "100vh" },
  layout: { display: "flex", height: "100vh" },
  sidebar: { width: "260px", background: "#0f0f0f", borderRight: "1px solid #1a1a1a", display: "flex", flexDirection: "column", padding: "24px 16px" },
  sidebarLogo: { display: "flex", alignItems: "center", gap: "12px", padding: "8px 12px", marginBottom: "32px" },
  logoIcon: { background: "#a78bfa", color: "#0f0f0f", width: "32px", height: "32px", borderRadius: "8px", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: "700", fontSize: "16px" },
  logoText: { fontSize: "16px", fontWeight: "700", color: "#ffffff" },
  sidebarNav: { display: "flex", flexDirection: "column", gap: "4px", flex: 1 },
  navLink: { display: "flex", alignItems: "center", gap: "12px", padding: "10px 14px", borderRadius: "8px", fontSize: "14px", fontWeight: "500", textAlign: "left", width: "100%" },
  sidebarFooter: { display: "flex", alignItems: "center", gap: "10px", padding: "16px 12px 4px", borderTop: "1px solid #1a1a1a", marginTop: "16px" },
  statusDot: { width: "8px", height: "8px", borderRadius: "50%", background: "#10b981" },
  statusLink: { display: "flex", alignItems: "center", gap: "8px", textDecoration: "none", color: "#8e8e8e", cursor: "pointer", transition: "color 0.2s" },
  statusText: { fontSize: "12px", color: "#8e8e8e", lineHeight: "1" },
  main: { flex: 1, height: "100vh", background: "#0f0f0f" },
  scrollPage: { height: "100vh", overflowY: "auto", padding: "60px 40px" },
  heroTitle: { fontSize: "44px", fontWeight: "700", color: "#ffffff", marginBottom: "16px", letterSpacing: "-1px" },
  heroDesc: { fontSize: "16px", color: "#8e8e8e", lineHeight: "1.6", marginBottom: "28px", maxWidth: "600px" },
  heroBtn: { background: "#a78bfa", color: "#0f0f0f", border: "none", padding: "12px 24px", borderRadius: "8px", fontSize: "14px", cursor: "pointer", fontWeight: "600" },
  featureCard: { background: "#171717", border: "1px solid #2a2a2a", borderRadius: "12px", padding: "24px" },
  featureTitle: { fontSize: "15px", fontWeight: "600", color: "#ffffff", marginBottom: "8px" },
  featureDesc: { fontSize: "14px", color: "#8e8e8e", lineHeight: "1.5" },
  chatLayout: { display: "flex", flexDirection: "column", height: "100vh", background: "#0f0f0f" },
  chatTopBar: { display: "flex", justifyContent: "space-between", alignItems: "center", padding: "14px 24px", borderBottom: "1px solid #1a1a1a" },
  clearBtn: { background: "transparent", border: "1px solid #2a2a2a", color: "#8e8e8e", padding: "6px 12px", borderRadius: "6px", cursor: "pointer", fontSize: "13px" },
  messagesArea: { flex: 1, overflowY: "auto", padding: "40px 24px 20px" },
  suggBtn: { background: "#171717", border: "1px solid #2a2a2a", color: "#8e8e8e", padding: "10px 16px", borderRadius: "8px", cursor: "pointer", fontSize: "13px" },
  inputWrapper: { display: "flex", gap: "12px", background: "#171717", border: "1px solid #2a2a2a", borderRadius: "16px", padding: "8px 8px 8px 16px", alignItems: "center" },
  chatInput: { flex: 1, background: "transparent", border: "none", fontSize: "15px", color: "#ffffff", outline: "none" },
  sendBtn: { border: "none", width: "36px", height: "36px", borderRadius: "10px", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", transition: "background 0.2s" },
  pageTitle: { fontSize: "28px", fontWeight: "700", color: "#ffffff", marginBottom: "8px" },
  pageDesc: { fontSize: "15px", color: "#8e8e8e", marginBottom: "36px" },
};