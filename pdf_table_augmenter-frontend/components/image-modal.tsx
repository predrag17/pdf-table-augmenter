"use client";

import { motion, AnimatePresence } from "framer-motion";
import { X, ChevronLeft, ChevronRight, MessageCircle } from "lucide-react";
import { useEffect, useState } from "react";
import { Button } from "./ui/button";
import ChatbotModal from "./chatbot";
import { askQuestion } from "@/service/table-augmenter-service";

export default function ImageModal({
  open,
  onClose,
  images,
  index,
  setIndex,
}: {
  open: boolean;
  onClose: () => void;
  images: any[];
  index: number;
  setIndex: (i: number) => void;
}) {
  const [chatbotOpen, setChatbotOpen] = useState(false);

  const suggestedQuestions = [
    "What is the main purpose of this image?",
    "What are the key elements shown in the image?",
    "What type of image is this (e.g., chart, diagram, photo)?",
    "What trends or patterns are evident in the image?",
    "What is the most prominent feature in the image?",
    "Are there any notable details or anomalies in the image?",
    "What insights can be drawn from the image?",
    "How does this image relate to the document’s content?",
  ];

  const askQuestionHandler = async (question: string) => {
    try {
      const response = await askQuestion(question, images[index].description);
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
                  Image {index + 1} of {images.length} ({images[index]?.page})
                </span>

                <Button
                  onClick={() => setIndex(index + 1)}
                  disabled={index === images.length - 1}
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
                  Ask About Image
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
                    {images[index] && (
                      <>
                        <div className="mb-4 flex justify-center">
                          <img
                            src={images[index].base64}
                            alt={`Image ${index + 1}`}
                            className="max-w-full max-h-[50vh] object-contain rounded border"
                          />
                        </div>

                        <div className="flex-row justify-center p-7">
                          <p className="text-sm text-gray-700 whitespace-pre-wrap bg-gray-50 p-4 rounded border">
                            {images[index].description}
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
                title="Ask About this Image"
              />
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
