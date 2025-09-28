"use client";

import { motion, AnimatePresence } from "framer-motion";
import { X, ChevronLeft, ChevronRight, MessageCircle } from "lucide-react";
import { useEffect, useState } from "react";
import { Button } from "./ui/button";
import ChatbotModal from "./chatbot";
import { askQuestion } from "@/service/table-augmenter-service";
import { InlineMath } from "react-katex";
import "katex/dist/katex.min.css";

const sanitizeLatex = (latex: string): string => {
  if (!latex) return "\\text{No formula data}";
  return (
    latex.replace(/\u02c6/g, "^").replace(/[^\x00-\x7F]/g, "") ||
    "\\text{No formula data}"
  );
};

export default function FormulaModal({
  open,
  onClose,
  formulas,
  index,
  setIndex,
}: {
  open: boolean;
  onClose: () => void;
  formulas: any[];
  index: number;
  setIndex: (i: number) => void;
}) {
  const [chatbotOpen, setChatbotOpen] = useState(false);

  const suggestedQuestions = [
    "What is the main purpose of this formula?",
    "What are the key variables in the formula?",
    "What type of formula is this (e.g., algebraic, differential)?",
    "What physical or mathematical concept does this formula represent?",
    "Can you explain the derivation of this formula?",
    "What are the implications or applications of this formula?",
    "Are there any notable assumptions in this formula?",
    "How does this formula relate to the document’s content?",
  ];

  const askQuestionHandler = async (question: string) => {
    try {
      const response = await askQuestion(question, formulas[index].description);
      return response.answer;
    } catch (err) {
      console.error("Error fetching answer:", err);
      return "Error answering question.";
    }
  };

  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleEsc);
    return () => window.removeEventListener("keydown", handleEsc);
  }, [onClose]);

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            className="fixed inset-0 bg-black/50 z-40"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />

          <motion.div
            className="fixed z-50 inset-0 flex items-center justify-center p-4"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
          >
            <div
              className="bg-white rounded-2xl shadow-xl max-w-4xl w-full max-h-[90vh] p-6 relative overflow-hidden"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex justify-end">
                <Button
                  onClick={onClose}
                  className="text-gray-400 hover:text-gray-600"
                  variant="ghost"
                >
                  <X />
                </Button>
              </div>

              <div className="flex justify-between items-center mb-4">
                <Button
                  onClick={() => setIndex(index - 1)}
                  disabled={index === 0}
                  className="text-blue-600 disabled:opacity-30"
                  variant="outline"
                >
                  <ChevronLeft />
                </Button>

                <span className="text-sm text-gray-500">
                  Formula {index + 1} of {formulas.length} (
                  {formulas[index]?.page})
                </span>

                <Button
                  onClick={() => setIndex(index + 1)}
                  disabled={index === formulas.length - 1}
                  className="text-blue-800 disabled:opacity-30"
                  variant="outline"
                >
                  <ChevronRight />
                </Button>
              </div>

              <div className="flex justify-end mb-4">
                <Button
                  onClick={() => setChatbotOpen(true)}
                  className="flex items-center gap-2"
                  variant="outline"
                >
                  <MessageCircle className="w-4 h-4" />
                  Ask About Formula
                </Button>
              </div>

              <div className="overflow-hidden relative h-[65vh]">
                <AnimatePresence mode="wait">
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: 50 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -50 }}
                    transition={{ duration: 0.3 }}
                    className="absolute w-full h-full overflow-y-auto pr-2"
                  >
                    {formulas[index] && (
                      <>
                        <div className="mb-4 flex justify-center">
                          <div className="text-2xl p-4 bg-gray-50 rounded border">
                            <InlineMath
                              math={sanitizeLatex(formulas[index].preview_data)}
                            />
                          </div>
                        </div>

                        <div className="flex-row justify-center p-7">
                          <p className="text-sm text-gray-700 whitespace-pre-wrap bg-gray-50 p-4 rounded border">
                            {formulas[index].description}
                          </p>
                        </div>
                      </>
                    )}
                  </motion.div>
                </AnimatePresence>
              </div>

              <ChatbotModal
                open={chatbotOpen}
                onClose={() => setChatbotOpen(false)}
                askQuestion={askQuestionHandler}
                suggestedQuestions={suggestedQuestions}
                title="Ask About this Formula"
              />
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
