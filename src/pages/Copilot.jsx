import React, { useState, useRef, useEffect } from "react"
import { Send, Loader2 } from "lucide-react"
import { api } from "../services/api"

export default function Copilot() {
  const [messages, setMessages] = useState([
    { sender: 'ai', text: "Hello! I'm your Revenue Command Copilot. I'm connected to your latest Excel upload. How can I help you today?" }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput("");
    setMessages(prev => [...prev, { sender: 'user', text: userMessage }]);
    setIsLoading(true);

    try {
      const res = await api.chat(userMessage, sessionId);
      setSessionId(res.session_id);
      setMessages(prev => [...prev, { sender: 'ai', text: res.reply }]);
    } catch (err) {
      setMessages(prev => [...prev, { sender: 'ai', text: "Sorry, I encountered an error. Please try again later.", isError: true }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] max-w-4xl mx-auto animate-in fade-in duration-500">
      <div className="mb-6">
        <h2 className="text-3xl font-bold tracking-tight text-foreground">AI Copilot</h2>
        <p className="text-muted-foreground mt-2">Ask questions about your data, generate insights, and get recommendations grounded in your database.</p>
      </div>
      
      <div className="flex-1 glass-panel rounded-xl flex flex-col overflow-hidden relative">
        <div className="flex-1 p-6 overflow-y-auto space-y-6">
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex items-start gap-4 ${msg.sender === 'user' ? 'flex-row-reverse' : ''}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white font-bold shrink-0 ${msg.sender === 'user' ? 'bg-primary' : 'bg-gradient-to-br from-blue-500 to-indigo-600'}`}>
                {msg.sender === 'user' ? 'ME' : 'AI'}
              </div>
              <div className={`p-4 rounded-xl max-w-[80%] text-sm leading-relaxed ${msg.sender === 'user' ? 'bg-primary text-primary-foreground rounded-tr-none' : msg.isError ? 'bg-destructive/10 text-destructive border border-destructive/20 rounded-tl-none' : 'bg-accent/20 border border-accent/30 text-foreground rounded-tl-none'}`}>
                <p className="whitespace-pre-wrap">{msg.text}</p>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex items-start gap-4">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white shrink-0">
                AI
              </div>
              <div className="bg-accent/20 p-4 rounded-xl rounded-tl-none flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin text-primary" /> <span className="text-sm text-muted-foreground">Thinking...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        
        <div className="p-4 border-t border-[var(--glass-border)] bg-background/50 backdrop-blur-md">
          <div className="relative">
            <input 
              type="text" 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask anything about your data..." 
              className="w-full pl-4 pr-12 py-3 bg-accent/20 border border-border rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/50 text-foreground placeholder:text-muted-foreground transition-all"
              disabled={isLoading}
            />
            <button 
              onClick={handleSend}
              disabled={isLoading || !input.trim()}
              className="absolute right-2 top-2 p-1.5 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50"
            >
              <Send size={18} />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
