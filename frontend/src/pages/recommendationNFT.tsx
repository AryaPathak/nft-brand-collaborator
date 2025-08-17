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
    <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
      <div className="bg-white p-6 rounded-xl shadow-lg w-full max-w-lg relative flex flex-col">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-3 right-3 text-gray-500 hover:text-gray-800"
        >
          <X size={20} />
        </button>

        {/* Title */}
        <h2 className="text-xl font-bold text-purple-600 mb-4">
          NFT Brand Chat & Recommendations
        </h2>

        {/* Brand Info */}
        {brandName ? (
          <p className="text-gray-700 mb-3">
            Generating NFT collection recommendations for brand:{" "}
            <span className="font-semibold">{brandName}</span>
          </p>
        ) : (
          <p className="text-gray-500">Please enter a brand name to continue.</p>
        )}

        {/* Recommendations Section */}
        <div className="bg-gray-50 p-3 rounded-lg mb-3">
          <button
            onClick={fetchRecommendations}
            className="bg-purple-600 text-white px-3 py-1 rounded-lg text-sm hover:bg-purple-700"
            disabled={loading}
          >
            {loading ? "Loading..." : "Get Recommendations"}
          </button>

          {recommendations.length > 0 && (
            <div className="mt-2">
              <p className="text-sm font-semibold">Suggested Collections:</p>
              <ul className="list-disc pl-5 text-gray-700 text-sm">
                {recommendations.map((rec, idx) => (
                  <li key={idx}>{rec}</li>
                ))}
              </ul>
              <p className="text-xs text-gray-500 mt-2">{rationale}</p>
            </div>
          )}
        </div>

        {/* Chat History */}
        <div className="flex-1 overflow-y-auto border rounded-lg p-3 mb-3 bg-gray-50">
          {chatHistory.map((msg, i) => (
            <div
              key={i}
              className={`mb-2 ${
                msg.sender === "user" ? "text-right" : "text-left"
              }`}
            >
              <span
                className={`inline-block px-3 py-2 rounded-xl ${
                  msg.sender === "user"
                    ? "bg-purple-600 text-white"
                    : "bg-gray-200 text-gray-800"
                }`}
              >
                {msg.text}
              </span>
            </div>
          ))}
        </div>

        {/* Input Box */}
        <div className="flex items-center border rounded-lg px-2">
          <input
            type="text"
            className="flex-1 p-2 outline-none text-sm"
            placeholder="Ask about NFT collections..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
          />
          <button
            onClick={handleSend}
            disabled={loading}
            className="text-purple-600 hover:text-purple-800 p-2"
          >
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}
