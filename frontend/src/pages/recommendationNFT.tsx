import { useState } from "react";
import { X, Send } from "lucide-react";

interface Props {
  brandName: string;
  onClose: () => void;
}

type ChatMessage = {
  sender: "user" | "assistant";
  text: string;
};

export default function RecommendationViewer({ brandName, onClose }: Props) {
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [recommendations, setRecommendations] = useState<string[]>([]);
  const [rationale, setRationale] = useState("");

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: ChatMessage = { sender: "user", text: input };
    setChatHistory((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8002/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: input }),
      });

      const data = await res.json();
      const botMessage: ChatMessage = {
        sender: "assistant",
        text: data.answer || "No response",
      };
      setChatHistory((prev) => [...prev, botMessage]);
    } catch (err) {
      console.error("Chat error:", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchRecommendations = async () => {
    if (!brandName) return;

    setLoading(true);
    try {
      const res = await fetch("http://localhost:8002/recommendations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ brand_name: brandName }),
      });

      const data = await res.json();
      setRecommendations(data.recommendations || []);
      setRationale(data.rationale || "");
    } catch (err) {
      console.error("Recommendation error:", err);
    } finally {
      setLoading(false);
    }
  };

return (
  <div className="fixed inset-0 z-50 flex justify-end pointer-events-none">
    {/* Sidebar floating over page */}
    <div className="relative w-full max-w-md h-full pointer-events-auto flex flex-col rounded-l-3xl shadow-2xl overflow-hidden bg-[#11141a]/95 backdrop-blur-md border-l border-[#2a2e3a]">
      
      {/* Top Header */}
      <div className="flex justify-between items-center px-6 py-4 bg-[#161822] border-b border-[#2a2e3a]">
        <h2 className="text-lg font-bold text-white tracking-wide">NBC AI Chat</h2>
        <button
          onClick={onClose}
          aria-label="Close Chat"
          className="text-text-muted hover:text-red-500 transition"
        >
          <X size={24} />
        </button>
      </div>

      {/* Brand Info */}
      {brandName && (
        <div className="px-6 py-3 bg-[#1a1e28] border-b border-[#2a2e3a] text-center">
          <p className="text-text-muted text-sm">
            Generating NFT recommendations for:{" "}
            <span className="font-semibold text-white">{brandName}</span>
          </p>
        </div>
      )}

      {/* Suggested Prompts */}
      <div className="px-6 py-3 flex flex-wrap gap-2 bg-[#1b1f29] border-b border-[#2a2e3a]">
        {[
          "Which NFT collection is better suited for Coca Cola?",
          "Best NFT collections for tech startups",
          "Trending NFT collections for gaming",
          "NFT ideas for artists",
          "Top NFT collections this week",
        ].map((prompt, idx) => (
          <button
            key={idx}
            onClick={() => setInput(prompt)}
            className="bg-[#161822] text-text-primary px-3 py-1 rounded-xl text-xs hover:bg-gradient-to-r hover:from-[#3b82f6] hover:to-[#8b5cf6] hover:text-white transition shadow-sm"
          >
            {prompt.length > 35 ? prompt.slice(0, 55) + "..." : prompt}
          </button>
        ))}
      </div>

      {/* Chat / Recommendations */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Loading */}
        {loading && (
          <div className="px-6 py-3 bg-[#1a1d28] border-b border-[#2a2e3a] text-center">
            <p className="text-text-muted text-sm animate-pulse">Loading recommendations...</p>
          </div>
        )}

        {/* Recommendations */}
        {recommendations.length > 0 && !loading && (
          <div className="px-6 py-3 bg-[#1a1d28] border-b border-[#2a2e3a]">
            <p className="text-sm font-semibold text-[#3b82f6] mb-2">Suggested Collections:</p>
            <ul className="list-disc pl-5 text-text-muted text-sm space-y-1">
              {recommendations.map((rec, idx) => (
                <li key={idx}>{rec}</li>
              ))}
            </ul>
            {rationale && <p className="text-xs text-text-muted mt-2">{rationale}</p>}
          </div>
        )}

        {/* Chat History */}
        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-3 scrollbar-thin scrollbar-thumb-gray-700 scrollbar-track-gray-900">
          {chatHistory.length === 0 && !loading && (
            <p className="text-text-muted text-sm text-center">
              Start the conversation by asking about NFT collections.
            </p>
          )}
          {chatHistory.map((msg, i) => (
            <div
              key={i}
              className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
            >
              <span
                className={`inline-block px-4 py-2 rounded-2xl max-w-[75%] break-words text-sm ${
                  msg.sender === "user"
                    ? "bg-gradient-to-r from-[#3b82f6] to-[#8b5cf6] text-white shadow-md"
                    : "bg-[#161822] text-text-muted"
                }`}
              >
                {msg.text}
              </span>
            </div>
          ))}
        </div>

        {/* Input Box */}
        <div className="flex items-center px-4 py-3 border-t border-[#2a2e3a] bg-[#161822]">
          <input
            type="text"
            aria-label="Type a message"
            className="flex-1 p-3 rounded-2xl outline-none text-sm bg-[#12141a] placeholder-text-muted text-text-primary mr-3 transition focus:ring-2 focus:ring-[#3b82f6]"
            placeholder="Ask about NFT collections..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
          />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            aria-label="Send message"
            className="bg-gradient-to-r from-[#3b82f6] to-[#8b5cf6] text-white px-4 py-2 rounded-2xl font-semibold text-sm disabled:opacity-60 transition shadow-md hover:shadow-lg"
          >
            {loading ? "Loading..." : "Send"}
          </button>
        </div>
      </div>
    </div>
  </div>
);

}