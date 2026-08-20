'use client';

import React, { useState } from 'react';
import { MessageSquare, X, Send, Bot, User, CheckCircle2 } from 'lucide-react';
import { BusinessData } from '../types/business';

interface Message {
  sender: 'bot' | 'user';
  text: string;
}

interface ChatbotWidgetProps {
  business: BusinessData;
}

export const ChatbotWidget: React.FC<ChatbotWidgetProps> = ({ business }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      sender: 'bot',
      text: `Hello! Welcome to ${business.name}. I am your 24/7 AI Receptionist. How can I assist you today?`
    }
  ]);
  const [input, setInput] = useState('');
  const [isCapturingLead, setIsCapturingLead] = useState(false);
  const [leadForm, setLeadForm] = useState({ name: '', phone: '', service: business.services[0] || 'Consultation' });
  const [leadSubmitted, setLeadSubmitted] = useState(false);

  const handleSend = () => {
    if (!input.trim()) return;

    const userMsg = input.trim();
    setMessages((prev) => [...prev, { sender: 'user', text: userMsg }]);
    setInput('');

    // Simulate AI response logic
    setTimeout(() => {
      let botResponse = `Thank you for asking! At ${business.name}, we specialize in ${business.services.slice(0, 2).join(' and ')}. Would you like to schedule a call or appointment?`;
      
      if (userMsg.toLowerCase().includes('book') || userMsg.toLowerCase().includes('appointment') || userMsg.toLowerCase().includes('cost') || userMsg.toLowerCase().includes('price')) {
        botResponse = `We would love to help you with that! Please leave your contact phone number below so our staff at ${business.name} can assist you right away.`;
        setIsCapturingLead(true);
      }

      setMessages((prev) => [...prev, { sender: 'bot', text: botResponse }]);
    }, 600);
  };

  const handleLeadSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setLeadSubmitted(true);
    setMessages((prev) => [
      ...prev,
      {
        sender: 'bot',
        text: `Awesome! Thank you ${leadForm.name}. A representative from ${business.name} will call you back at ${leadForm.phone} shortly!`
      }
    ]);
  };

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {/* Floating Toggle Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="gradient-button text-white w-14 h-14 rounded-full flex items-center justify-center shadow-2xl hover:scale-105 transition-transform"
        >
          <MessageSquare className="w-6 h-6 animate-pulse" />
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className="glass-card w-[360px] sm:w-[400px] h-[520px] rounded-3xl flex flex-col overflow-hidden border border-cyan-500/30 shadow-2xl">
          {/* Chat Header */}
          <div className="bg-slate-900/90 px-5 py-4 flex items-center justify-between border-b border-slate-800">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 rounded-full bg-cyan-500/20 border border-cyan-400 flex items-center justify-center text-cyan-400">
                <Bot className="w-4 h-4" />
              </div>
              <div>
                <h4 className="text-sm font-bold text-white">AI Virtual Receptionist</h4>
                <p className="text-[10px] text-emerald-400 flex items-center space-x-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping inline-block" />
                  <span>Online • {business.name}</span>
                </p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="text-slate-400 hover:text-white p-1 rounded-lg"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Messages Body */}
          <div className="flex-1 p-4 overflow-y-auto space-y-3 text-sm">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex items-start space-x-2 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {msg.sender === 'bot' && (
                  <div className="w-6 h-6 rounded-full bg-cyan-500/20 flex items-center justify-center text-cyan-400 shrink-0 mt-1">
                    <Bot className="w-3.5 h-3.5" />
                  </div>
                )}
                <div
                  className={`p-3 rounded-2xl max-w-[80%] leading-relaxed ${
                    msg.sender === 'user'
                      ? 'bg-cyan-600 text-white rounded-tr-none'
                      : 'bg-slate-800 text-slate-200 rounded-tl-none border border-slate-700'
                  }`}
                >
                  {msg.text}
                </div>
                {msg.sender === 'user' && (
                  <div className="w-6 h-6 rounded-full bg-slate-700 flex items-center justify-center text-slate-300 shrink-0 mt-1">
                    <User className="w-3.5 h-3.5" />
                  </div>
                )}
              </div>
            ))}

            {/* In-Chat Lead Form Capture */}
            {isCapturingLead && !leadSubmitted && (
              <form onSubmit={handleLeadSubmit} className="bg-slate-900/90 p-4 rounded-2xl border border-cyan-500/30 space-y-3 mt-2">
                <p className="text-xs font-semibold text-cyan-400">Request Callback & Priority Booking</p>
                <input
                  type="text"
                  required
                  placeholder="Your Name"
                  value={leadForm.name}
                  onChange={(e) => setLeadForm({ ...leadForm, name: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-white text-xs focus:outline-none focus:border-cyan-500"
                />
                <input
                  type="tel"
                  required
                  placeholder="Phone Number"
                  value={leadForm.phone}
                  onChange={(e) => setLeadForm({ ...leadForm, phone: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-white text-xs focus:outline-none focus:border-cyan-500"
                />
                <button
                  type="submit"
                  className="w-full gradient-button text-white py-2 rounded-lg text-xs font-bold"
                >
                  Submit Callback Request
                </button>
              </form>
            )}
          </div>

          {/* Input Bar */}
          <div className="p-3 bg-slate-900/90 border-t border-slate-800 flex items-center space-x-2">
            <input
              type="text"
              placeholder="Ask a question..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              className="flex-1 px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-white text-xs focus:outline-none focus:border-cyan-500"
            />
            <button
              onClick={handleSend}
              className="gradient-button text-white p-2.5 rounded-xl flex items-center justify-center shadow-md"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
