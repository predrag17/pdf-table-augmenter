"use client";

import { motion, AnimatePresence } from "framer-motion";
import { X, ChevronLeft, ChevronRight } from "lucide-react";
import { useEffect } from "react";
import { Button } from "./ui/button";

export default function TableModal({
  open,
  onClose,
  tables,
  index,
  setIndex,
}: {
  open: boolean;
  onClose: () => void;
  tables: any[];
  index: number;
  setIndex: (i: number) => void;
}) {
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleEsc);
    return () => window.removeEventListener("keydown", handleEsc);
  }, [onClose]);

  const table = tables[index];

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
              className="bg-white rounded-2xl shadow-xl max-w-3xl w-full p-15 relative"
              onClick={(e) => e.stopPropagation()}
            >
              <Button
                onClick={onClose}
                className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
                variant="ghost"
              >
                <X />
              </Button>

              <div className="flex justify-between items-center mb-4">
                <Button
                  onClick={() => setIndex(Math.max(0, index - 1))}
                  disabled={index === 0}
                  className="text-blue-600 disabled:opacity-30"
                  variant="outline"
                >
                  <ChevronLeft />
                </Button>

                <span className="text-sm text-gray-500">
                  Table {index + 1} of {tables.length}
                </span>

                <Button
                  onClick={() =>
                    setIndex(Math.min(tables.length - 1, index + 1))
                  }
                  disabled={index === tables.length - 1}
                  className="text-blue-800 disabled:opacity-30"
                  variant="outline"
                >
                  <ChevronRight />
                </Button>
              </div>

              <AnimatePresence mode="wait">
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: 50 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -50 }}
                  transition={{ duration: 0.3 }}
                >
                  <div className="overflow-auto mb-4 border rounded">
                    <table className="min-w-full text-sm text-left border-collapse">
                      <tbody>
                        {table.preview_data.map(
                          (row: string[], rowIndex: number) => (
                            <tr key={rowIndex} className="border-b">
                              {row.map((cell: string, colIndex: number) => (
                                <td
                                  key={colIndex}
                                  className="px-3 py-2 border-r"
                                >
                                  {cell}
                                </td>
                              ))}
                            </tr>
                          )
                        )}
                      </tbody>
                    </table>
                  </div>

                  <p className="text-sm text-gray-700 whitespace-pre-wrap bg-gray-50 p-4 rounded border">
                    {table.description}
                  </p>
                </motion.div>
              </AnimatePresence>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
