"use client";

import { Button } from "@/components/ui/button";
import { Sparkles, ArrowRight } from "lucide-react";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";

export default function WelcomePage() {
  const router = useRouter();

  return (
    <div className="min-h-screen relative overflow-hidden bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 flex items-center justify-center px-6 py-16">
      <div className="absolute inset-0 -z-10">
        <motion.div
          animate={{
            x: [0, 140, 0],
            y: [0, -120, 0],
            scale: [1, 1.15, 1],
          }}
          transition={{
            duration: 22,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          className="absolute top-10 left-10 w-[420px] h-[420px] bg-gradient-to-r from-indigo-500/25 via-purple-500/20 to-transparent rounded-full blur-3xl"
        />

        <motion.div
          animate={{
            x: [0, -160, 0],
            y: [0, 100, 0],
            scale: [1, 1.2, 1],
          }}
          transition={{
            duration: 28,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          className="absolute bottom-10 right-10 w-[380px] h-[380px] bg-gradient-to-l from-pink-500/25 via-purple-500/20 to-transparent rounded-full blur-3xl"
        />

        <motion.div
          animate={{
            scale: [1, 1.35, 1],
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{
            duration: 18,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[650px] h-[650px] bg-gradient-to-tr from-indigo-400/15 via-purple-400/15 to-pink-400/15 rounded-full blur-3xl"
        />
      </div>

      {[...Array(12)].map((_, i) => (
        <motion.div
          key={`spark-${i}`}
          initial={{ opacity: 0, scale: 0 }}
          animate={{
            opacity: [0, 1, 0],
            scale: [0, 1.5, 0],
            x: [0, i % 2 === 0 ? 80 : -80, 0],
            y: [0, -300, -600],
          }}
          transition={{
            duration: 6 + i * 0.4,
            repeat: Infinity,
            ease: "easeOut",
            delay: i * 0.5,
          }}
          className="absolute w-2 h-2 bg-white/80 rounded-full shadow-lg"
          style={{
            left: `${10 + i * 7}%`,
            bottom: "10%",
          }}
        />
      ))}

      {[...Array(3)].map((_, i) => (
        <motion.div
          key={`pulse-${i}`}
          animate={{
            scale: [1, 3, 1],
            opacity: [0.1, 0.4, 0.1],
          }}
          transition={{
            duration: 4,
            repeat: Infinity,
            ease: "easeOut",
            delay: i * 1.3,
          }}
          className="absolute w-32 h-32 border border-indigo-400/30 rounded-full"
          style={{
            top: `${30 + i * 20}%`,
            left: i % 2 === 0 ? "20%" : "70%",
          }}
        />
      ))}

      <motion.div
        animate={{
          y: [0, -30, 0],
          rotate: [0, 5, 0],
        }}
        transition={{
          duration: 12,
          repeat: Infinity,
          ease: "easeInOut",
        }}
        className="absolute top-32 left-1/4 w-24 h-24 bg-gradient-to-br from-indigo-300/10 to-purple-300/10 rounded-3xl blur-xl"
      />
      <motion.div
        animate={{
          y: [0, 25, 0],
          rotate: [0, -8, 0],
        }}
        transition={{
          duration: 15,
          repeat: Infinity,
          ease: "easeInOut",
        }}
        className="absolute bottom-40 right-1/3 w-20 h-20 bg-gradient-to-tl from-pink-300/10 to-purple-300/10 rounded-3xl blur-xl"
      />

      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.9, ease: "easeOut" }}
        className="text-center space-y-10 max-w-3xl z-20 relative"
      >
        <motion.div
          initial={{ scale: 0.7, rotate: -15 }}
          animate={{ scale: 1, rotate: 0 }}
          transition={{
            duration: 0.7,
            delay: 0.2,
            type: "spring",
            stiffness: 120,
          }}
          className="flex justify-center"
        >
          <div className="relative p-6 bg-white/80 backdrop-blur-md rounded-full shadow-2xl border border-white/50">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
              className="absolute inset-0 rounded-full bg-gradient-to-tr from-indigo-400/20 via-purple-400/20 to-pink-400/20 blur-xl"
            />
            <Sparkles className="w-14 h-14 text-indigo-600 relative z-10 animate-pulse" />
          </div>
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.9 }}
          className="pb-5 text-5xl md:text-7xl font-extrabold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent leading-tight"
          style={{
            textShadow: "0 4px 20px rgba(79, 70, 229, 0.2)",
          }}
        >
          PDF Augmenter
        </motion.h1>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6, duration: 0.9 }}
          className="text-lg md:text-xl text-gray-700 leading-relaxed max-w-2xl backdrop-blur-sm bg-white/30 rounded-2xl"
        >
          Effortlessly extract{" "}
          <strong className="text-indigo-600">tables</strong>,{" "}
          <strong className="text-purple-600">images</strong>, and{" "}
          <strong className="text-pink-600">formulas</strong> from your PDFs,
          and generate clear, contextual descriptions for each.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8, duration: 0.7 }}
          className="flex justify-center"
        >
          <Button
            onClick={() => router.push("/upload")}
            className="group relative w-full max-w-md h-16 text-xl md:text-2xl font-semibold rounded-2xl
              bg-gradient-to-r from-indigo-600 to-purple-600
              hover:from-indigo-700 hover:to-purple-700
              shadow-2xl hover:shadow-indigo-500/50
              transition-all duration-300 hover:scale-105
              flex items-center justify-center gap-3 overflow-hidden cursor-pointer"
          >
            <motion.div
              animate={{ x: [0, 5, 0] }}
              transition={{ duration: 2, repeat: Infinity }}
              className="absolute inset-0 bg-white/10"
            />
            <span className="relative z-10">Start Extraction</span>
            <motion.div
              animate={{ x: [0, 4, 0] }}
              transition={{ duration: 1.5, repeat: Infinity }}
            >
              <ArrowRight className="w-6 h-6 relative z-10" />
            </motion.div>
          </Button>
        </motion.div>
      </motion.div>

      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 40, repeat: Infinity, ease: "linear" }}
        className="absolute top-10 right-10 w-16 h-16 border-2 border-indigo-300/30 rounded-xl"
      />
      <motion.div
        animate={{ rotate: -360 }}
        transition={{ duration: 35, repeat: Infinity, ease: "linear" }}
        className="absolute bottom-10 left-10 w-12 h-12 border border-purple-300/30 rounded-full"
      />
    </div>
  );
}
