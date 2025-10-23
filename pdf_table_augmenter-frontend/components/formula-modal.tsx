/* eslint-disable @typescript-eslint/no-explicit-any */
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

  if (!formulas[index]) return null;

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            className="fixed inset-0 bg-black/70 z-40"
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
              className="bg-white rounded-2xl shadow-2xl max-w-6xl w-full max-h-[95vh] flex flex-col"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="p-6 border-b flex justify-between items-center">
                <div className="flex items-center gap-4">
                  <Button
                    onClick={() => setIndex(index - 1)}
                    disabled={index === 0}
                    className="text-blue-600 disabled:opacity-30"
                    variant="outline"
                    size="sm"
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </Button>

                  <span className="text-sm text-gray-500 font-medium">
                    Formula {index + 1} of {formulas.length}
                  </span>

                  <Button
                    onClick={() => setIndex(index + 1)}
                    disabled={index === formulas.length - 1}
                    className="text-blue-600 disabled:opacity-30"
                    variant="outline"
                    size="sm"
                  >
                    <ChevronRight className="w-4 h-4" />
                  </Button>
                </div>

                <div className="flex gap-2">
                  <Button
                    onClick={() => setChatbotOpen(true)}
                    className="flex items-center gap-2 text-sm"
                    variant="outline"
                    size="sm"
                  >
                    <MessageCircle className="w-4 h-4" />
                    Ask Question
                  </Button>

                  <Button
                    onClick={onClose}
                    className="text-gray-400 hover:text-gray-600"
                    variant="ghost"
                    size="sm"
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              </div>

              <div className="flex-1 overflow-hidden flex flex-col min-h-0">
                <AnimatePresence mode="wait">
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: 50 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -50 }}
                    transition={{ duration: 0.3 }}
                    className="flex-1 flex flex-col overflow-hidden"
                  >
                    <div className="flex-1 overflow-y-auto p-6 border-b">
                      <div className="flex justify-center">
                        <div className="text-2xl p-4 bg-gray-50 rounded border">
                          <InlineMath
                            math={sanitizeLatex(formulas[index].preview_data)}
                          />
                        </div>
                      </div>
                    </div>

                    <div className="p-6 bg-gray-50">
                      <h3 className="font-medium text-gray-900 mb-3 text-sm">
                        Formula Description:
                      </h3>
                      <div className="max-h-48 overflow-y-auto">
                        <p className="text-sm text-gray-700 whitespace-pre-wrap">
                          {formulas[index].description ||
                            "No description available."}
                        </p>
                      </div>
                    </div>
                  </motion.div>
                </AnimatePresence>
              </div>
            </div>
          </motion.div>

          <ChatbotModal
            open={chatbotOpen}
            onClose={() => setChatbotOpen(false)}
            askQuestion={askQuestionHandler}
            suggestedQuestions={suggestedQuestions}
            title="Ask About this Formula"
          />
        </>
      )}
    </AnimatePresence>
  );
}
