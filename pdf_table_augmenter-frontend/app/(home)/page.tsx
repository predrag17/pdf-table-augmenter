"use client";

import { useState, useCallback } from "react";
import { Button } from "@/components/ui/button";
import {
  ImageIcon,
  RemoveFormatting,
  TableIcon,
  UploadCloud,
} from "lucide-react";
import FileUploader from "@/components/file-uploader";
import toast from "react-hot-toast";
import {
  extractFormulasFromFile,
  extractImagesFromFile,
  extractTablesFromFile,
} from "@/service/table-augmenter-service";
import TableModal from "@/components/table-modal";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import ImageModal from "@/components/image-modal";
import FormulaModal from "@/components/formula-modal";

export default function Home() {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [tableResults, setTableResults] = useState<any[]>([]);
  const [imageResults, setImageResults] = useState<any[]>([]);
  const [formulaResults, setFormulaResults] = useState<any[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [tableModalOpen, setTableModalOpen] = useState(false);
  const [imageModalOpen, setImageModalOpen] = useState(false);
  const [formulaModalOpen, setFormulaModalOpen] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [extractOption, setExtractOption] = useState<
    "tables" | "images" | "formulas" | null
  >(null);

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
      setExtractOption(null);
    }
  }, []);

  const handleProcess = async () => {
    if (!file || !extractOption) return;
    setIsProcessing(true);
    try {
      if (extractOption === "tables") {
        const data = await extractTablesFromFile(file);
        if (data.length > 0) {
          setTableResults(data);
          setImageResults([]);
          setFormulaResults([]);
          setTableModalOpen(true);
          setCurrentIndex(0);
        } else {
          toast.error("The uploaded PDF does not contain any tables.");
        }
      } else if (extractOption === "images") {
        const data = await extractImagesFromFile(file);
        if (data.length > 0) {
          setImageResults(data);
          setTableResults([]);
          setFormulaResults([]);
          setImageModalOpen(true);
          setCurrentIndex(0);
        } else {
          toast.error("The uploaded PDF does not contain any images.");
        }
      } else if (extractOption === "formulas") {
        const data = await extractFormulasFromFile(file);
        if (data.length > 0) {
          setFormulaResults(data);
          setTableResults([]);
          setImageResults([]);
          setImageModalOpen(true);
          setCurrentIndex(0);
        } else {
          toast.error("The uploaded PDF does not contain any formulas.");
        }
      }
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
                setExtractOption(null);
              },
            }}
          />
        </div>

        {file && (
          <div className="w-full bg-white p-6 rounded-xl shadow-sm border text-gray-700">
            <p className="text-sm mb-4 text-gray-500">
              Select what to extract from the PDF:
            </p>
            <div className="mb-4">
              <Select
                value={extractOption || undefined}
                onValueChange={(value) =>
                  setExtractOption(
                    value as "tables" | "images" | "formulas" | null
                  )
                }
              >
                <SelectTrigger className="w-50">
                  <SelectValue placeholder="Select an option" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="tables">
                    <TableIcon />
                    Table
                  </SelectItem>
                  <SelectItem value="images">
                    <ImageIcon /> Image
                  </SelectItem>
                  <SelectItem value="formulas">
                    <RemoveFormatting /> Formula
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
            <Button
              onClick={handleProcess}
              disabled={isProcessing || !extractOption}
            >
              {isProcessing ? "Processing..." : "Process PDF"}
            </Button>
          </div>
        )}

        <TableModal
          open={tableModalOpen && extractOption === "tables"}
          onClose={() => setTableModalOpen(false)}
          tables={tableResults}
          index={currentIndex}
          setIndex={setCurrentIndex}
        />

        <ImageModal
          open={imageModalOpen && extractOption === "images"}
          onClose={() => setImageModalOpen(false)}
          images={imageResults}
          index={currentIndex}
          setIndex={setCurrentIndex}
        />

        <FormulaModal
          open={imageModalOpen && extractOption === "formulas"}
          onClose={() => setFormulaModalOpen(false)}
          formulas={formulaResults}
          index={currentIndex}
          setIndex={setCurrentIndex}
        />
      </div>
    </div>
  );
}
