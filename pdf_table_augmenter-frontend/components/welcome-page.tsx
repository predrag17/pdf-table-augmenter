import { Sparkles, FileText } from "lucide-react";
import { motion } from "framer-motion";

export default function WelcomePage() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8, ease: "easeOut" }}
      className="text-center space-y-6"
    >
      <motion.div
        initial={{ scale: 0.8 }}
        animate={{ scale: 1 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="flex justify-center"
      >
        <div className="p-5 bg-gradient-to-r from-indigo-100 to-purple-100 rounded-full shadow-xl">
          <Sparkles className="w-14 h-14 text-indigo-600" />
        </div>
      </motion.div>

      <motion.h1
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
        className="text-5xl md:text-7xl font-extrabold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent"
      >
        PDF Augmenter
      </motion.h1>

      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
        className="text-xl md:text-2xl text-gray-700 max-w-3xl mx-auto leading-relaxed"
      >
        Extract <strong className="text-indigo-600">tables</strong>,{" "}
        <strong className="text-purple-600">images</strong>, and{" "}
        <strong className="text-pink-600">formulas</strong> from PDFs —{" "}
        <span className="italic">with AI-powered explanations</span>.
      </motion.p>

      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8 }}
        className="text-sm text-gray-500 flex items-center justify-center gap-2"
      >
        <FileText className="w-5 h-5" />
        Drag and drop your PDF below to begin
      </motion.p>
    </motion.div>
  );
}
