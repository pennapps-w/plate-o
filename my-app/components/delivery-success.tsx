"use client"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { ArrowUpCircle } from "lucide-react"

export function DeliverySuccessComponent() {
  const [showContent, setShowContent] = useState(false)

  useEffect(() => {
    const timer = setTimeout(() => setShowContent(true), 2000)
    return () => clearTimeout(timer)
  }, [])

  return (
    <div className="min-h-screen bg-black text-white flex flex-col items-center justify-center">
      <motion.div
        initial={{ opacity: 1 }}
        animate={{ opacity: showContent ? 0 : 1 }}
        transition={{ duration: 0.5 }}
        className="fixed inset-0 flex flex-col items-center justify-center"
      >
        <motion.div
          initial={{ y: "100vh" }}
          animate={{ y: 0 }}
          transition={{ type: "spring", stiffness: 50, damping: 20 }}
          className="mb-8"
        >
          <ArrowUpCircle className="w-24 h-24 text-green-500" />
        </motion.div>
        <motion.svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 1052 170"
          className="w-48 h-16 mb-4"
          initial={{ scale: 0.5, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.5, duration: 0.5 }}
        >
          <path
            fill="#FFFFFF"
            d="M166.54 0h-23.07l-26.8 71.31L89.43 0H0l74.54 196.81 68.92-183.89 23.08 61.65zm850.61 153.19c-10.44 0-18.88-8.44-18.88-18.88 0-10.43 8.44-18.87 18.88-18.87 10.43 0 18.87 8.44 18.87 18.87 0 10.44-8.44 18.88-18.87 18.88zM791.39 39.37c-14.31 0-27.58 5.56-37.45 15.81V0h-45.51v153.19h45.51V84.88c0-12.51 10.13-22.64 22.64-22.64s22.64 10.13 22.64 22.64v68.31h45.51V84.88c0-25.13-20.38-45.51-45.51-45.51zm-206.89 0c-39.44 0-71.31 31.87-71.31 71.31s31.87 71.31 71.31 71.31 71.31-31.87 71.31-71.31-31.87-71.31-71.31-71.31zm0 97.39c-14.31 0-25.8-11.49-25.8-25.8s11.49-25.8 25.8-25.8 25.8 11.49 25.8 25.8-11.49 25.8-25.8 25.8zm-105.08-97.39c-14.31 0-27.58 5.56-37.45 15.81V0h-45.51v153.19h45.51V84.88c0-12.51 10.13-22.64 22.64-22.64s22.64 10.13 22.64 22.64v68.31h45.51V84.88c0-25.13-20.38-45.51-45.51-45.51zm-206.9 0c-39.44 0-71.31 31.87-71.31 71.31s31.87 71.31 71.31 71.31 71.31-31.87 71.31-71.31-31.87-71.31-71.31-71.31zm0 97.39c-14.31 0-25.8-11.49-25.8-25.8s11.49-25.8 25.8-25.8 25.8 11.49 25.8 25.8-11.49 25.8-25.8 25.8z"
          />
        </motion.svg>
        <motion.h1
          className="text-3xl font-bold"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.7, duration: 0.7 }}
        >
          Order Placed Successfully
        </motion.h1>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: showContent ? 1 : 0, scale: showContent ? 1 : 0.9 }}
        transition={{ duration: 0.7 }}
        className="w-full max-w-md mx-auto p-6 bg-white text-black rounded-lg shadow-lg"
      >
        <h2 className="text-2xl font-bold mb-4">Order Details</h2>
        <p className="mb-2">Your order has been successfully placed and is being prepared.</p>
        <p className="mb-4"><b>Estimated delivery time:</b> 30-45 minutes</p>
        <button className="w-full bg-black text-white py-2 rounded hover:bg-gray-800 transition-colors">
          Track Order
        </button>
      </motion.div>
    </div>
  )
}