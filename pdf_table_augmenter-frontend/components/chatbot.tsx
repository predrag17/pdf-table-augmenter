"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Send } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import toast from "react-hot-toast";

interface ChatbotModalProps {
  open: boolean;
  onClose: () => void;
  askQuestion: (question: string) => Promise<string>;
  suggestedQuestions: string[];
}

export default function ChatbotModal({
  open,
  onClose,
  askQuestion,
  suggestedQuestions,
}: ChatbotModalProps) {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<
    { question: string; answer: string }[]
  >([]);
  const [isLoading, setIsLoading] = useState(false);
  const [suggestedQuestionClose, setSuggestedQuestionClose] =
    useState<boolean>(true);

  const handleAsk = async (q: string) => {
    setSuggestedQuestionClose(false);
    setIsLoading(true);
    try {
      const answer = await askQuestion(q);
      setMessages((prev) => [...prev, { question: q, answer }]);
      setQuestion("");
    } catch (err) {
      console.error("Error asking question:", err);
      toast.error("Error generating the question");
    } finally {
      setIsLoading(false);
    }
  };

  const handleClose = () => {
    setMessages([]);
    setSuggestedQuestionClose(true);
    onClose();
  };

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            className="fixed inset-0 bg-black/50 z-50"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={handleClose}
          />
          <motion.div
            className="fixed z-50 inset-0 flex items-center justify-center p-4"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
          >
            <div
              className="bg-white rounded-2xl shadow-xl max-w-lg w-full max-h-[80vh] p-6 relative overflow-hidden"
              onClick={(e) => e.stopPropagation()}
            >
              <Button
                onClick={handleClose}
                className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
                variant="ghost"
              >
                <X />
              </Button>
              <h2 className="text-lg font-semibold mb-4">
                Ask About This Table
              </h2>
              <div className="max-h-[50vh] overflow-y-auto mb-4">
                {messages.map((msg, idx) => (
                  <div key={idx} className="mb-4">
                    <p className="text-sm font-medium text-blue-600">
                      Q: {msg.question}
                    </p>
                    <p className="text-sm text-gray-700">A: {msg.answer}</p>
                  </div>
                ))}
              </div>
              <div className="flex gap-2 mb-4">
                <Input
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="Type your question..."
                  onKeyDown={(e) => e.key === "Enter" && handleAsk(question)}
                />
                <Button
                  onClick={() => handleAsk(question)}
                  disabled={isLoading || !question}
                >
                  <Send className="w-4 h-4" />
                </Button>
              </div>

              {suggestedQuestionClose && (
                <div>
                  <p className="text-sm font-medium mb-2">
                    Suggested Questions:
                  </p>
                  <div className="flex overflow-x-auto gap-2 pb-2">
                    {suggestedQuestions.map((q, idx) => (
                      <Button
                        key={idx}
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          handleAsk(q);
                          setSuggestedQuestionClose(false);
                        }}
                        disabled={isLoading}
                      >
                        {q}
                      </Button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
