"use client";

import { useState, useCallback } from "react";
import { UploadCloud, ArrowRight, ArrowLeft } from "lucide-react";
import FileUploader from "@/components/file-uploader";
import toast from "react-hot-toast";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import ExtractPanel from "@/components/extract-panel";
import { useRouter } from "next/navigation";

export default function UploadPage() {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [showExtract, setShowExtract] = useState(false);

  const router = useRouter();

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(e.type === "dragenter" || e.type === "dragover");
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    const droppedFile = e.dataTransfer?.files?.[0];
    if (droppedFile && droppedFile.type === "application/pdf") {
      setFile(droppedFile);
      toast.success(`${droppedFile.name} uploaded!`);
    } else {
      toast.error("Please upload a valid PDF file.");
    }
  }, []);

  const handleFileChange = (f: File | null) => {
    if (f && f.type === "application/pdf") {
      setFile(f);
      toast.success(`${f.name} selected!`);
    } else {
      setFile(null);
      setShowExtract(false);
      toast.error("Please select a PDF.");
    }
  };

  const openExtract = () => {
    if (!file) return;
    setShowExtract(true);
  };

  const goBack = () => {
    router.push("/");
  };

  return (
    <div className="min-h-screen h-full bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center px-6 py-16">
      <div className="w-full max-w-4xl space-y-12">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <div
            className={`group w-full p-20 border-4 border-dashed rounded-3xl transition-all duration-300 cursor-pointer ${
              dragActive
                ? "border-indigo-500 bg-indigo-50/70 shadow-2xl scale-105"
                : "border-gray-300 bg-white shadow-xl hover:shadow-2xl"
            }`}
            onDragEnter={handleDrag}
            onDragOver={handleDrag}
            onDragLeave={() => setDragActive(false)}
            onDrop={handleDrop}
          >
            <div className="flex flex-col items-center space-y-8 text-center">
              <motion.div
                animate={{ y: dragActive ? -20 : 0 }}
                transition={{
                  repeat: dragActive ? Infinity : 0,
                  repeatType: "reverse",
                  duration: 0.6,
                }}
                className="from-indigo-100 to-purple-100 rounded-full group-hover:scale-110 transition-transform"
              >
                <UploadCloud className="w-10 h-10 text-indigo-600" />
              </motion.div>

              <div>
                <motion.p
                  animate={{ scale: dragActive ? 1.1 : 1 }}
                  className="text-xl md:text-2xl font-semibold text-gray-800"
                >
                  {dragActive ? "Drop it here!" : "Drop Your PDF Here"}
                </motion.p>
                <p className="text-sm md:text-lg text-gray-500 mt-3 mb-3">
                  or click to browse from your device
                </p>
              </div>

              {dragActive && (
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="flex gap-2 mb-3"
                >
                  {[...Array(3)].map((_, i) => (
                    <motion.div
                      key={i}
                      animate={{ y: [0, -15, 0] }}
                      transition={{
                        repeat: Infinity,
                        duration: 0.5,
                        delay: i * 0.1,
                      }}
                      className="w-3 h-3 bg-indigo-600 rounded-full"
                    />
                  ))}
                </motion.div>
              )}
            </div>

            <div className="flex justify-center align-center">
              <FileUploader
                field={{
                  value: file,
                  onChange: handleFileChange,
                }}
              />
            </div>

            <AnimatePresence>
              {file && !showExtract && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="flex justify-center mt-6"
                >
                  <Button
                    onClick={openExtract}
                    className="h-14 px-8 text-lg font-semibold rounded-2xl
                              bg-gradient-to-r from-indigo-600 to-purple-600
                              hover:from-indigo-700 hover:to-purple-700
                              shadow-xl hover:shadow-2xl transition-all duration-300
                              flex items-center gap-3 cursor-pointer"
                  >
                    Go to Extraction
                    <ArrowRight className="w-6 h-6" />
                  </Button>
                </motion.div>
              )}
            </AnimatePresence>

            <AnimatePresence>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="flex justify-center mt-6"
              >
                <Button
                  onClick={goBack}
                  variant="outline"
                  className="h-14 px-8 text-lg font-semibold rounded-2xl
                              border-2 border-indigo-600 text-indigo-600
                              hover:bg-indigo-50 hover:border-indigo-700
                              shadow-lg hover:shadow-xl transition-all duration-300
                              flex items-center gap-3 cursor-pointer"
                >
                  <ArrowLeft className="w-6 h-6" />
                  Back to Home
                </Button>
              </motion.div>
            </AnimatePresence>
          </div>
        </motion.div>

        <AnimatePresence>
          {showExtract && file && (
            <ExtractPanel file={file} onClose={() => setShowExtract(false)} />
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
