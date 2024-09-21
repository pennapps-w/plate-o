"use client";

import { useState, useEffect } from "react";
import {
  motion,
  AnimatePresence,
  useMotionValue,
  useTransform,
} from "framer-motion";
import { X, Heart, DollarSign, Leaf } from "lucide-react";

interface Restaurant {
  name: string;
  dish: string;
  image: string;
  esgScore: number;
  price: number;
  summary: string;
}

export function FoodSwiper() {
  const [currentRestaurant, setCurrentRestaurant] = useState<Restaurant | null>(
    null
  );
  const [direction, setDirection] = useState<"left" | "right" | null>(null);

  const x = useMotionValue(0);
  const rotate = useTransform(x, [-200, 200], [-30, 30]);
  const opacity = useTransform(x, [-200, -100, 0, 100, 200], [0, 1, 1, 1, 0]);

  const fetchRecommendation = async () => {
    try {
      const response = await fetch(
        "https://blobotic-service1--8000.prod1.defang.dev/get_recommendation/66ee6b3a7aa3130e68418c7d"
      );
      if (!response.ok) {
        throw new Error("Failed to fetch recommendation");
      }
      const data = await response.json();
      setCurrentRestaurant(data);
    } catch (error) {
      console.error("Error fetching recommendation:", error);
    }
  };

  useEffect(() => {
    fetchRecommendation();
  }, []);

  const handleSwipe = (swipeDirection: "left" | "right") => {
    setDirection(swipeDirection);
    if (swipeDirection === "left") {
      fetchRecommendation();
    }
  };

  const handleDragEnd = (event: any, info: any) => {
    const swipeThreshold = 100;
    if (info.offset.x > swipeThreshold) {
      handleSwipe("right");
    } else if (info.offset.x < -swipeThreshold) {
      handleSwipe("left");
    }
  };

  const renderPriceIcons = (price: number) => {
    return Array(3)
      .fill(0)
      .map((_, index) => (
        <DollarSign
          key={index}
          className={`w-4 h-4 ${
            index < price ? "text-green-500" : "text-gray-300"
          }`}
        />
      ));
  };

  if (!currentRestaurant) {
    return <div>Loading...</div>;
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-orange-200 to-red-300 p-4">
      <div className="w-full max-w-sm">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentRestaurant.name}
            className="bg-white rounded-3xl shadow-xl overflow-hidden border-4 border-yellow-400"
            drag="x"
            dragConstraints={{ left: 0, right: 0 }}
            onDragEnd={handleDragEnd}
            style={{ x, rotate, opacity }}
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.8, opacity: 0 }}
            transition={{ type: "spring", stiffness: 300, damping: 20 }}
          >
            <div className="relative h-48">
              <img
                src={currentRestaurant.image}
                alt={currentRestaurant.name}
                className="w-full h-full object-cover"
              />
            </div>
            <div className="p-4">
              <h1 className="text-3xl font-bold mb-1 text-orange-600">
                {currentRestaurant.name}
              </h1>
              <h2 className="text-xl text-gray-700 mb-3">
                {currentRestaurant.dish}
              </h2>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-gray-600 font-semibold">
                    ESG Score:
                  </span>
                  <div className="flex items-center">
                    <Leaf className="w-5 h-5 text-green-500 mr-1" />
                    <span className="text-lg font-bold">
                      {currentRestaurant.esgScore.toFixed(1)}
                    </span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600 font-semibold">Price:</span>
                  <div className="flex">
                    {renderPriceIcons(currentRestaurant.price)}
                  </div>
                </div>
                <p className="text-gray-800 text-sm mt-2">
                  {currentRestaurant.summary}
                </p>
              </div>
            </div>
          </motion.div>
        </AnimatePresence>
        <div className="flex justify-center mt-8 space-x-4">
          <button
            onClick={() => handleSwipe("left")}
            className="bg-red-500 rounded-full p-4 shadow-lg transition-transform hover:scale-110"
          >
            <X className="w-8 h-8 text-white" />
          </button>
          <button
            onClick={() => handleSwipe("right")}
            className="bg-green-500 rounded-full p-4 shadow-lg transition-transform hover:scale-110"
          >
            <Heart className="w-8 h-8 text-white" />
          </button>
        </div>
      </div>
    </div>
  );
}
