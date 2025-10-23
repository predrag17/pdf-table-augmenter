import { UploadCloud, ArrowDown } from "lucide-react";
import { motion } from "framer-motion";
import FileUploader from "@/components/file-uploader";

interface UploadZoneProps {
  dragActive: boolean;
  file: File | null;
  onFileChange: (file: File | null) => void;
  onDragEnter: () => void;
  onDragOver: () => void;
  onDragLeave: () => void;
  onDrop: (e: React.DragEvent) => void;
}

export default function UploadZone({
  dragActive,
  file,
  onFileChange,
  onDragEnter,
  onDragOver,
  onDragLeave,
  onDrop,
}: UploadZoneProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5, delay: 0.3 }}
      className={`group relative w-full p-16 border-4 border-dashed rounded-3xl transition-all duration-300 cursor-pointer ${
        dragActive
          ? "border-indigo-500 bg-indigo-50/80 shadow-2xl scale-105"
          : "border-gray-300 bg-white shadow-xl hover:shadow-2xl"
      }`}
      onDragEnter={onDragEnter}
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      onDrop={onDrop}
    >
      <div className="flex flex-col items-center space-y-6 text-center">
        <motion.div
          animate={{ y: dragActive ? -10 : 0 }}
          transition={{
            repeat: dragActive ? Infinity : 0,
            repeatType: "reverse",
            duration: 0.5,
          }}
          className="p-6 bg-gradient-to-r from-indigo-100 to-purple-100 rounded-full group-hover:scale-110 transition-transform"
        >
          <UploadCloud className="w-20 h-20 text-indigo-600" />
        </motion.div>

        <div>
          <motion.p
            animate={{ scale: dragActive ? 1.05 : 1 }}
            className="text-2xl md:text-3xl font-bold text-gray-800"
          >
            {dragActive ? "Drop it here!" : "Drop Your PDF Here"}
          </motion.p>
          <p className="text-sm text-gray-500 mt-2">or click to browse</p>
        </div>

        {dragActive && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            exit={{ scale: 0 }}
            className="flex gap-1"
          >
            {[...Array(3)].map((_, i) => (
              <motion.div
                key={i}
                animate={{ y: [0, -10, 0] }}
                transition={{ repeat: Infinity, duration: 0.5, delay: i * 0.1 }}
                className="w-2 h-2 bg-indigo-500 rounded-full"
              />
            ))}
          </motion.div>
        )}

        <ArrowDown className="w-10 h-10 text-gray-400 animate-bounce" />
      </div>

      <FileUploader
        field={{
          value: file,
          onChange: onFileChange,
        }}
      />
    </motion.div>
  );
}
