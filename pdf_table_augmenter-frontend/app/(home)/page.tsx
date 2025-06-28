"use client";

import { useState, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { UploadCloud } from "lucide-react";
import FileUploader from "@/components/file-uploader";
import toast from "react-hot-toast";
import { extractTablesFromFile } from "@/service/table-augmenter-service";
import TableModal from "@/components/table-modal";

export default function Home() {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [tableResults, setTableResults] = useState<any[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);

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
    }
  }, []);

  const handleProcess = async () => {
    if (!file) return;
    setIsProcessing(true);
    try {
      const data = await extractTablesFromFile(file);
      setTableResults(data);
      setModalOpen(true);
      setCurrentIndex(0);
    } catch (err: any) {
      toast.error("Error while parsing the PDF file");
      console.error("Error while processing the file", err);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 sm:px-20 bg-gray-100">
      <div className="flex flex-col items-center w-full max-w-2xl gap-8">
        <div
          className={`flex flex-col items-center justify-center w-full p-8 border-2 border-dashed rounded-2xl transition-colors ${
            dragActive
              ? "border-blue-500 bg-blue-50"
              : "border-gray-300 bg-white"
          }`}
          onDragEnter={handleDrag}
          onDragOver={handleDrag}
          onDragLeave={() => setDragActive(false)}
          onDrop={handleDrop}
        >
          <UploadCloud className="w-10 h-10 text-gray-400 mb-4" />
          <p className="text-lg font-medium text-gray-700 mb-2">
            Drag & Drop your PDF here
          </p>
          <p className="text-sm text-gray-500 mb-4">
            or click to browse from your computer
          </p>

          <FileUploader
            field={{
              value: file,
              onChange: (file: File | null) => {
                setFile(file);
              },
            }}
          />
        </div>

        {file && (
          <div className="w-full bg-white p-6 rounded-xl shadow-sm border text-gray-700">
            <p className="text-sm mb-4 text-gray-500">
              Do you want to process this file?
            </p>
            <Button onClick={handleProcess} disabled={isProcessing}>
              {isProcessing ? "Processing..." : "Process PDF"}
            </Button>
          </div>
        )}

        <TableModal
          open={modalOpen}
          onClose={() => setModalOpen(false)}
          tables={tableResults}
          index={currentIndex}
          setIndex={setCurrentIndex}
        />
      </div>
    </div>
  );
}
