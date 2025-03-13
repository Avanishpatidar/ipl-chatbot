import React, { useState, useEffect, useRef } from "react";
import "./App.css";
import axios from "axios";
import { MessageCircle, Send, Info, Trophy  , HelpCircle, HistoryIcon } from "lucide-react";

const App = () => {
  const [messages, setMessages] = useState([
    {
      sender: "bot",
      text: "Welcome to IPL Stats Wizard! I'm your cricket companion ready to bowl you over with IPL statistics. What would you like to know about teams, players, or memorable matches?",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll and focus input
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    inputRef.current?.focus();  
  }, [messages]);

  // Send message to backend
  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;
  
    const userMessage = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);
    const userQuery = input;
    setInput("");
    setIsLoading(true);
  
    try {
      const response = await axios.post("http://127.0.0.1:8000/ask", { text: userQuery });
      console.log("Backend response:", response.data);
      
      // Adding slight delay for animation effect
      setTimeout(() => {
        const botMessage = {
          sender: "bot",
          text: response.data.answer || "I couldn't find that data. Try rephrasing your question!",
        };
        setMessages((prev) => [...prev, botMessage]);
        setIsLoading(false);
      }, 1500);
      
    } catch (error) {
      console.error("Axios error:", error);
      let errorMessage = "Oops, something went wrong. Let's try that again.";
      if (error.response) {
        console.log("Error response data:", error.response.data);
        console.log("Error status:", error.response.status);
        errorMessage = error.response.data.answer || `Server error (${error.response.status}): Please try again.`;
      } else if (error.request) {
        console.log("No response received:", error.request);
        errorMessage = "Network error: Couldn't reach the server. Is it running?";
      }
      
      setTimeout(() => {
        setMessages((prev) => [
          ...prev,
          { sender: "bot", text: errorMessage },
        ]);
        setIsLoading(false);
      }, 1000);
    }
  };

  // Handle Enter key
  const handleKeyPress = (e) => {
    if (e.key === "Enter") sendMessage();
  };

  // Toggle sidebar
  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  // Example questions
  const examples = [
    "How many runs did Virat Kohli score in 2016?",
    "Who scored more runs in 2020, Mumbai Indians or Chennai Super Kings?",
    "How many runs did RCB score against MI where Kohli was Player of the Match?",
    "Which team has the most IPL titles?",
    "Who hit the most sixes in IPL 2023?",
    "What's the highest team total in IPL history?",
  ];


  return (
    <div className="app-container">
      <div className="stadium-bg"></div>
      
      {/* Sidebar Toggle Button for Mobile */}
      <button className="sidebar-toggle" onClick={toggleSidebar}>
        <MessageCircle size={24} />
      </button>
      
      {/* Sidebar */}
      <div className={`sidebar ${isSidebarOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <div className="logo-container">
            <Trophy size={32} className="trophy-icon" />
            <div className="logo-text">
              <h2>IPL Stats Wizard</h2>
              <p>Your ultimate cricket companion</p>
            </div>
          </div>
        </div>
        
        <div className="sidebar-section">
          <h3>
            <HelpCircle size={16} className="section-icon" />
            Popular Questions
          </h3>
          <div className="example-list">
            {examples.map((q, i) => (
              <button 
                key={i} 
                onClick={() => setInput(q)} 
                className="example-button"
              >
                {q}
              </button>
            ))}
          </div>
        </div>
        
        <div className="sidebar-footer">
          <div className="app-info">
            <Info size={16} />
            <span>IPL Stats Wizard v2.0</span>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        {/* Header */}
        <header className="main-header">
          <h1>
            <Trophy size={28} className="header-icon" />
            IPL Stats Conversation
          </h1>
          <div className="header-actions">
            <button className="theme-toggle">
              <span>🏏</span>
            </button>
          </div>
        </header>

        {/* Messages Area */}
        <div className="messages-area">
          {/* Disclaimer */}
          {messages.length <= 1 && (
            <div className="disclaimer">
              <Info size={20} className="disclaimer-icon" />
              <div>
                <h4>Get the best out of IPL Stats Wizard</h4>
                <p>Include player names, teams, and seasons in your questions for more accurate answers.</p>
              </div>
            </div>
          )}

          {/* Messages */}
          <div className="messages-container">
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`message ${msg.sender === "user" ? "user-message" : "bot-message"}`}
              >
                <div className={`message-avatar ${msg.sender === "user" ? "user-avatar" : "bot-avatar"}`}>
                  {msg.sender === "user" ? <span className="avatar-icon">🏏</span> : <span className="avatar-icon">🤖</span>}
                </div>
                <div className="message-content">
                  <p>{msg.text}</p>
                  <div className="message-time">
                    {new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                  </div>
                </div>
              </div>
            ))}

            {/* Loading Indicator */}
            {isLoading && (
              <div className="message bot-message">
                <div className="message-avatar bot-avatar">
                  <span className="avatar-icon">🤖</span>
                </div>
                <div className="message-content loading-content">
                  <div className="cricket-pitch">
                    <div className="wicket left-wicket">
                      <div className="stump"></div>
                      <div className="stump"></div>
                      <div className="stump"></div>
                      <div className="bail"></div>
                    </div>
                    <div className="cricket-ball"></div>
                    <div className="batsman">
                      <div className="bat"></div>
                      <div className="player"></div>
                    </div>
                    <div className="wicket right-wicket">
                      <div className="stump"></div>
                      <div className="stump"></div>
                      <div className="stump"></div>
                      <div className="bail"></div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className="input-area">
          <div className="input-container">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about IPL stats, players, or teams..."
              disabled={isLoading}
            />
            <button
              onClick={sendMessage}
              disabled={isLoading || !input.trim()}
              className={`send-button ${(!input.trim() || isLoading) ? 'disabled' : ''}`}
              aria-label="Send message"
            >
              <Send size={20} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;