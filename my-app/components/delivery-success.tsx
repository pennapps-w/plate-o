"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowUpCircle, Loader2 } from "lucide-react";

export default function DeliverySuccess() {
  const [showContent, setShowContent] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
      setShowContent(true);
    }, 2000);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-orange-200 to-red-300 p-4">
      <AnimatePresence>
        {!showContent && (
          <motion.div
            initial={{ opacity: 1 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
            className="fixed inset-0 flex flex-col items-center justify-center"
          >
            <motion.div
              initial={{ y: "100vh" }}
              animate={{ y: 0 }}
              transition={{ type: "spring", stiffness: 50, damping: 20 }}
              className="mb-8"
            >
              <ArrowUpCircle className="w-24 h-24 text-orange-500" />
            </motion.div>
            <motion.svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 1052 170"
              className="w-48 h-16 mb-4"
              initial={{ scale: 0.5, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.5, duration: 0.5 }}
            >
              {/* <path
                fill="#FF8C00"
                d="M166.54 0h-23.07l-26.8 71.31L89.43 0H0l74.54 196.81 68.92-183.89 23.08 61.65zm850.61 153.19c-10.44 0-18.88-8.44-18.88-18.88 0-10.43 8.44-18.87 18.88-18.87 10.43 0 18.87 8.44 18.87 18.87 0 10.44-8.44 18.88-18.87 18.88zM791.39 39.37c-14.31 0-27.58 5.56-37.45 15.81V0h-45.51v153.19h45.51V84.88c0-12.51 10.13-22.64 22.64-22.64s22.64 10.13 22.64 22.64v68.31h45.51V84.88c0-25.13-20.38-45.51-45.51-45.51zm-206.89 0c-39.44 0-71.31 31.87-71.31 71.31s31.87 71.31 71.31 71.31 71.31-31.87 71.31-71.31-31.87-71.31-71.31-71.31zm0 97.39c-14.31 0-25.8-11.49-25.8-25.8s11.49-25.8 25.8-25.8 25.8 11.49 25.8 25.8-11.49 25.8-25.8 25.8zm-105.08-97.39c-14.31 0-27.58 5.56-37.45 15.81V0h-45.51v153.19h45.51V84.88c0-12.51 10.13-22.64 22.64-22.64s22.64 10.13 22.64 22.64v68.31h45.51V84.88c0-25.13-20.38-45.51-45.51-45.51zm-206.9 0c-39.44 0-71.31 31.87-71.31 71.31s31.87 71.31 71.31 71.31 71.31-31.87 71.31-71.31-31.87-71.31-71.31-71.31zm0 97.39c-14.31 0-25.8-11.49-25.8-25.8s11.49-25.8 25.8-25.8 25.8 11.49 25.8 25.8-11.49 25.8-25.8 25.8z"
              /> */}
            </motion.svg>
            <motion.h1
              className="text-3xl font-bold text-orange-600"
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.7, duration: 0.5 }}
            >
              Order Placed Successfully
            </motion.h1>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {showContent && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            transition={{ duration: 0.5 }}
            className="w-full max-w-sm bg-white rounded-3xl shadow-xl overflow-hidden border-4 border-yellow-400"
          >
            {isLoading ? (
              <div className="flex items-center justify-center h-64">
                <Loader2 className="w-16 h-16 text-orange-500 animate-spin" />
              </div>
            ) : (
              <div className="p-4">
                <h2 className="text-3xl font-bold mb-1 text-orange-600">
                  Order Details
                </h2>
                <p className="text-xl text-gray-700 mb-3">
                  Your order is on its way!
                </p>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600 font-semibold">
                      Estimated delivery time:
                    </span>
                    <span className="text-lg font-bold text-black">
                      {(() => {
                        const min = Math.floor(Math.random() * 60) + 15; // Random number between 15 and 74
                        return `${min}-${min + 15} minutes`;
                      })()}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600 font-semibold">
                      Order number:
                    </span>
                    <span className="text-lg font-bold text-black">
                      #{Math.floor(100000 + Math.random() * 900000)}
                    </span>
                  </div>
                  <p className="text-gray-800 text-sm mt-2">
                    Your order has been successfully placed and is being
                    prepared. You'll receive updates on your order status.
                  </p>
                </div>
                <button className="w-full bg-orange-500 text-white py-2 rounded-full mt-4 hover:bg-orange-600 transition-colors">
                  Track Order
                </button>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
