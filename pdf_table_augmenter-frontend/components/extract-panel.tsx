/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";

import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { TableIcon, Brain, CheckCircle, X } from "lucide-react";
import toast from "react-hot-toast";
import {
  extractFormulasFromFile,
  extractImagesFromFile,
} from "@/service/table-augmenter-service";
import axiosInstance from "@/config/axiosInstance";
import { useState } from "react";
import TableModal from "./table-modal";
import ImageModal from "./image-modal";
import FormulaModal from "./formula-modal";

interface ExtractPanelProps {
  file: File;
  onClose: () => void;
}

export default function ExtractPanel({ file, onClose }: ExtractPanelProps) {
  const [tableResults, setTableResults] = useState<any[]>([]);
  const [imageResults, setImageResults] = useState<any[]>([]);
  const [formulaResults, setFormulaResults] = useState<any[]>([]);
  const [tableModalOpen, setTableModalOpen] = useState(false);
  const [imageModalOpen, setImageModalOpen] = useState(false);
  const [formulaModalOpen, setFormulaModalOpen] = useState(false);

  const [currentIndex, setCurrentIndex] = useState(0);

  const [extractOption, setExtractOption] = useState<
    "tables" | "images" | "formulas" | null
  >(null);
  const [tableCase, setTableCase] = useState<
    "case1" | "case2" | "case3" | null
  >(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleProcess = async () => {
    if (!extractOption) return;

    setIsProcessing(true);
    try {
      let data: any[] = [];

      if (extractOption === "tables") {
        if (!tableCase) {
          toast.error("Please select a case.");
          setIsProcessing(false);
          return;
        }

        const endpoint =
          tableCase === "case1"
            ? "/extract-description/first-case/tables"
            : tableCase === "case2"
            ? "/extract-description/second-case/tables"
            : "/extract-description/tables";

        const formData = new FormData();
        formData.append("pdf", file);

        const response = await axiosInstance.post(endpoint, formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });
        data = response.data;
      } else if (extractOption === "images") {
        data = await extractImagesFromFile(file);
      } else if (extractOption === "formulas") {
        data = await extractFormulasFromFile(file);
      }

      if (data.length > 0) {
        if (extractOption === "tables") {
          setTableResults(data);
          setTableModalOpen(true);
        } else if (extractOption === "images") {
          setImageResults(data);
          setImageModalOpen(true);
        } else if (extractOption === "formulas") {
          setFormulaResults(data);
          setFormulaModalOpen(true);
        }
      } else {
        toast.error(`No ${extractOption} found.`);
      }
    } catch (err: any) {
      toast.error("Processing failed.", err);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <>
      <motion.div
        initial={{ opacity: 0, y: 50, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: 50, scale: 0.95 }}
        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-6"
        onClick={onClose}
      >
        <motion.div
          className="bg-white rounded-3xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto p-8"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-lg md:text-xl font-semibold text-gray-800">
              Extract from PDF
            </h2>
            <button
              onClick={onClose}
              disabled={isProcessing}
              className="p-2 hover:bg-gray-100 rounded-full transition"
            >
              <X className="w-6 h-6 text-gray-600" />
            </button>
          </div>

          <div className="bg-gradient-to-r from-indigo-50 to-purple-50 p-5 rounded-2xl flex items-center gap-3 mb-6">
            <CheckCircle className="w-8 h-8 text-indigo-600" />
            <div>
              <p className="font-semibold">File ready</p>
              <p className="text-sm text-gray-700">{file.name}</p>
            </div>
          </div>

          <div className="space-y-6">
            <Select
              value={extractOption || undefined}
              onValueChange={(v) => {
                setExtractOption(v as any);
                setTableCase(null);
              }}
              disabled={isProcessing}
            >
              <SelectTrigger className="w-full md:w-50 text-md md:text-lg">
                <SelectValue placeholder="What to extract?" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="tables">Tables</SelectItem>
                <SelectItem value="images">Images</SelectItem>
                <SelectItem value="formulas">Formulas</SelectItem>
              </SelectContent>
            </Select>

            {extractOption === "tables" && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="p-6 bg-gradient-to-r from-blue-50 to-purple-50 rounded-2xl border-2 border-indigo-200"
              >
                <p className="text-center font-bold text-indigo-800 mb-4">
                  How do you want to get the description?
                </p>
                <div className="flex flex-col justify-center align-center gap-3">
                  <button
                    onClick={() => setTableCase("case1")}
                    disabled={isProcessing}
                    className={`p-4 rounded-xl border-2 transition-all cursor-pointer ${
                      tableCase === "case1"
                        ? "bg-blue-600 text-white shadow-md ring-2 ring-blue-400"
                        : "bg-white hover:border-blue-500"
                    }`}
                  >
                    <TableIcon className="w-6 h-6 mx-auto mb-1" />
                    <div className="font-semibold">Case 1</div>
                    <div className="text-xs">Table Data Only</div>
                  </button>

                  <button
                    onClick={() => setTableCase("case2")}
                    disabled={isProcessing}
                    className={`p-4 rounded-xl border-2 transition-all cursor-pointer ${
                      tableCase === "case2"
                        ? "bg-indigo-600 text-white shadow-md ring-2 ring-indigo-400"
                        : "bg-white hover:border-indigo-500"
                    }`}
                  >
                    <TableIcon className="w-6 h-6 mx-auto mb-1" />
                    <div className="font-semibold">Case 2</div>
                    <div className="text-xs">Before and after context</div>
                  </button>

                  <button
                    onClick={() => setTableCase("case3")}
                    disabled={isProcessing}
                    className={`p-4 rounded-xl border-2 transition-all cursor-pointer ${
                      tableCase === "case3"
                        ? "bg-purple-600 text-white shadow-md ring-2 ring-purple-400"
                        : "bg-white hover:border-purple-500"
                    }`}
                  >
                    <Brain className="w-6 h-6 mx-auto mb-1" />
                    <div className="font-semibold">Case 3</div>
                    <div className="text-xs">References + Title</div>
                  </button>
                </div>
              </motion.div>
            )}

            <Button
              onClick={handleProcess}
              disabled={
                isProcessing ||
                !extractOption ||
                (extractOption === "tables" && !tableCase)
              }
              className="
            w-full h-16 text-md md:text-xl font-semibold rounded-2xl
            bg-gradient-to-r from-indigo-600 to-purple-600
            hover:from-indigo-700 hover:to-purple-700
            disabled:opacity-50 hover:shadow-xl"
            >
              {isProcessing ? (
                <span className="flex items-center gap-3">
                  <div className="w-6 h-6 border-3 border-white/30 border-t-white rounded-full animate-spin" />
                  Processing...
                </span>
              ) : extractOption ? (
                `Extract ${extractOption}`
              ) : (
                "Select to extract"
              )}
            </Button>
          </div>
        </motion.div>
      </motion.div>

      <TableModal
        open={tableModalOpen}
        onClose={() => {
          setTableModalOpen(false);
          setCurrentIndex(0);
        }}
        tables={tableResults}
        index={currentIndex}
        setIndex={setCurrentIndex}
      />

      <ImageModal
        open={imageModalOpen}
        onClose={() => {
          setImageModalOpen(false);
          setCurrentIndex(0);
        }}
        images={imageResults}
        index={currentIndex}
        setIndex={setCurrentIndex}
      />

      <FormulaModal
        open={formulaModalOpen}
        onClose={() => {
          setFormulaModalOpen(false);
          setCurrentIndex(0);
        }}
        formulas={formulaResults}
        index={currentIndex}
        setIndex={setCurrentIndex}
      />
    </>
  );
}
