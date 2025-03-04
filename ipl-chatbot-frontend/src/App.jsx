import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import "./App.css";

const App = () => {
  const [messages, setMessages] = useState([
    {
      sender: "bot",
      text: "Greetings! I’m your IPL Chatbot, here to answer all your IPL stats questions. What’s on your mind?",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
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
      const botMessage = {
        sender: "bot",
        text: response.data.answer || "I couldn’t find that data. Try rephrasing your question!",
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error("Error:", error);
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "Oops, something went wrong. Let’s try that again." },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle Enter key
  const handleKeyPress = (e) => {
    if (e.key === "Enter") sendMessage();
  };

  // Example questions
  const examples = [
    "How many runs did Virat Kohli score in 2016?",
    "Who scored more runs in 2020, Mumbai Indians or Chennai Super Kings?",
    "How many runs did RCB score against MI where Kohli was Player of the Match?",
    "Which team has the most IPL titles?",
  ];

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <h1>IPL Chatbot</h1>
        <p>Ask me anything about IPL stats!</p>
      </header>

      {/* Chat messages area */}
      <div className="messages-container">
        {/* Disclaimer */}
        {messages.length <= 1 && (
          <div className="disclaimer" style={{ color: "yellow" }} >
          Disclaimer: Each question is standalone. Please ensure to include full context (e.g., player, year, team) when providing answers or information.


          </div>
        )}

        {/* Messages */}
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`message ${msg.sender === "user" ? "user-message" : "bot-message"}`}
          >
            <span className="message-text">{msg.text}</span>
          </div>
        ))}

        {/* Loading indicator */}
        {isLoading && (
          <div className="bot-message loading">
            <span className="dot"></span>
            <span className="dot"></span>
            <span className="dot"></span>
          </div>
        )}

        {/* Example questions */}
        {messages.length <= 1 && (
          <div className="examples-container">
            <p>Try asking:</p>
            <div className="examples-buttons">
              {examples.map((q, i) => (
                <button key={i} onClick={() => setInput(q)} className="example-button">
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="input-container">
        <input
          ref={inputRef}
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your IPL question here..."
          disabled={isLoading}
        />
        <button
          onClick={sendMessage}
          disabled={isLoading || !input.trim()}
          className={!input.trim() || isLoading ? "disabled" : ""}
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default App;