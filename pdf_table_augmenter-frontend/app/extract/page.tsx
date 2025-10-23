/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { TableIcon, Brain, ArrowLeft, CheckCircle } from "lucide-react";
import toast from "react-hot-toast";
import {
  extractFormulasFromFile,
  extractImagesFromFile,
} from "@/service/table-augmenter-service";
import TableModal from "@/components/table-modal";
import ImageModal from "@/components/image-modal";
import FormulaModal from "@/components/formula-modal";
import axiosInstance from "@/config/axiosInstance";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
} from "@/components/ui/select";

export default function ExtractPage() {
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
  const [tableCase, setTableCase] = useState<"case1" | "case3" | null>(null);
  const router = useRouter();

  useEffect(() => {
    const stored = localStorage.getItem("uploaded_pdf");
    if (!stored) {
      toast.error("No file found. Please upload first.");
      router.push("/upload");
    }
  }, [router]);

  const handleProcess = async () => {
    if (!file || !extractOption) return;

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
        setCurrentIndex(0);
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
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center px-6 py-16">
      <div className="w-full max-w-3xl space-y-10">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center"
        >
          <button
            onClick={() => router.push("/upload")}
            className="flex items-center gap-2 text-indigo-600 hover:text-indigo-800 mx-auto mb-4"
          >
            <ArrowLeft className="w-5 h-5" /> Back to Upload
          </button>
          <h1 className="text-3xl font-semibold text-gray-800">
            Extract from PDF
          </h1>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white p-6 rounded-2xl shadow-lg flex items-center gap-3"
        >
          <CheckCircle className="w-8 h-8 text-green-500" />
          <div>
            <p className="font-semibold">File ready</p>
            <p className="text-sm text-gray-500">
              {localStorage.getItem("uploaded_pdf")
                ? JSON.parse(localStorage.getItem("uploaded_pdf")!).name
                : ""}
            </p>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white p-10 rounded-3xl shadow-2xl border space-y-8"
        >
          <Select
            value={extractOption || undefined}
            onValueChange={(v) => {
              setExtractOption(v as any);
              setTableCase(null);
            }}
          >
            <SelectTrigger className="h-10">What to extract?</SelectTrigger>
            <SelectContent>
              <SelectItem value="tables">Tables</SelectItem>
              <SelectItem value="images">Images</SelectItem>
              <SelectItem value="formulas">Formulas</SelectItem>
            </SelectContent>
          </Select>

          {extractOption === "tables" && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="p-6 bg-gradient-to-r from-blue-50 to-purple-50 rounded-2xl border-2 border-indigo-200"
            >
              <p className="text-center font-bold text-indigo-800 mb-4">
                Evaluation Case
              </p>
              <div className="grid grid-cols-2 gap-4">
                <button
                  onClick={() => setTableCase("case1")}
                  className={`p-4 rounded-xl border-2 ${
                    tableCase === "case1"
                      ? "bg-blue-600 text-white"
                      : "bg-white"
                  }`}
                >
                  <TableIcon className="w-6 h-6 mx-auto" />
                  <div className="font-bold">Case 1</div>
                  <div className="text-xs">Table Only</div>
                </button>
                <button
                  onClick={() => setTableCase("case3")}
                  className={`p-4 rounded-xl border-2 ${
                    tableCase === "case3"
                      ? "bg-purple-600 text-white"
                      : "bg-white"
                  }`}
                >
                  <Brain className="w-6 h-6 mx-auto" />
                  <div className="font-bold">Case 3</div>
                  <div className="text-xs">Full Context</div>
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
            className="w-full h-16 text-xl bg-gradient-to-r from-indigo-600 to-purple-600"
          >
            {isProcessing ? "Processing..." : `Extract ${extractOption}`}
          </Button>
        </motion.div>
      </div>

      <TableModal
        open={tableModalOpen}
        onClose={() => setTableModalOpen(false)}
        tables={tableResults}
        index={currentIndex}
        setIndex={setCurrentIndex}
      />

      <ImageModal
        open={imageModalOpen}
        onClose={() => setImageModalOpen(false)}
        images={imageResults}
        index={currentIndex}
        setIndex={setCurrentIndex}
      />

      <FormulaModal
        open={formulaModalOpen}
        onClose={() => setFormulaModalOpen(false)}
        formulas={formulaResults}
        index={currentIndex}
        setIndex={setCurrentIndex}
      />
    </div>
  );
}
