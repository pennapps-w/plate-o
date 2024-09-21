"use client";

import { useState, useEffect } from "react";
import {
  motion,
  AnimatePresence,
  useMotionValue,
  useTransform,
} from "framer-motion";
import { X, Heart, DollarSign, Leaf, Loader2 } from "lucide-react";

interface Restaurant {
  name: string;
  description: string;
  menu: Array<{ name: string; price: string }>;
  final_score: number;
  price_point: string;
}

export function FoodSwiper() {
  const [currentRestaurant, setCurrentRestaurant] = useState<Restaurant | null>(
    null
  );
  const [direction, setDirection] = useState<"left" | "right" | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const x = useMotionValue(0);
  const rotate = useTransform(x, [-200, 200], [-30, 30]);
  const opacity = useTransform(x, [-200, -100, 0, 100, 200], [0, 1, 1, 1, 0]);

  const fetchRecommendation = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(
        "http://127.0.0.1:8000/get_recommendation/66ee6b3a7aa3130e68418c7d"
      );
      if (!response.ok) {
        throw new Error("Failed to fetch recommendation");
      }
      const data = await response.json();
      setCurrentRestaurant(data);
    } catch (error) {
      console.error("Error fetching recommendation:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendation();
  }, []);

  const handleSwipe = async (swipeDirection: "left" | "right") => {
    setDirection(swipeDirection);
    if (swipeDirection === "left") {
      setIsLoading(true);
      try {
        // Call rejected_recommendation
        const response = await fetch(
          "http://127.0.0.1:8000/rejected_recommendation/66ee6b3a7aa3130e68418c7d",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ reason: "Not interested" }), // You might want to add a reason input
          }
        );
        if (!response.ok) {
          throw new Error("Failed to update rejected recommendation");
        }
        // Fetch new recommendation
        await fetchRecommendation();
      } catch (error) {
        console.error("Error handling swipe:", error);
      } finally {
        setIsLoading(false);
      }
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

  const renderPriceIcons = (pricePoint: string) => {
    const priceLevel = pricePoint.length;
    return Array(3)
      .fill(0)
      .map((_, index) => (
        <DollarSign
          key={index}
          className={`w-4 h-4 ${
            index < priceLevel ? "text-green-500" : "text-gray-300"
          }`}
        />
      ));
  };

  if (!currentRestaurant && !isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-orange-200 to-red-300 p-4">
      <div className="w-full max-w-sm">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentRestaurant?.name || "loading"}
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
            {isLoading ? (
              <div className="flex items-center justify-center h-64">
                <Loader2 className="w-16 h-16 text-orange-500 animate-spin" />
              </div>
            ) : (
              <div className="p-4">
                <h1 className="text-3xl font-bold mb-1 text-orange-600">
                  {currentRestaurant?.name}
                </h1>
                <h2 className="text-xl text-gray-700 mb-3">
                  {currentRestaurant?.menu[0].name}
                </h2>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600 font-semibold">
                      ESG Score:
                    </span>
                    <div className="flex items-center">
                      <Leaf className="w-5 h-5 text-green-500 mr-1" />
                      <span className="text-lg font-bold">
                        {currentRestaurant?.final_score.toFixed(1)}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600 font-semibold">Price:</span>
                    <div className="flex">
                      {renderPriceIcons(currentRestaurant?.price_point || "")}
                    </div>
                  </div>
                  <p className="text-gray-800 text-sm mt-2">
                    {currentRestaurant?.description}
                  </p>
                </div>
              </div>
            )}
          </motion.div>
        </AnimatePresence>
        <div className="flex justify-center mt-8 space-x-4">
          <button
            onClick={() => handleSwipe("left")}
            className="bg-red-500 rounded-full p-4 shadow-lg transition-transform hover:scale-110"
            disabled={isLoading}
          >
            <X className="w-8 h-8 text-white" />
          </button>
          <button
            onClick={() => handleSwipe("right")}
            className="bg-green-500 rounded-full p-4 shadow-lg transition-transform hover:scale-110"
            disabled={isLoading}
          >
            <Heart className="w-8 h-8 text-white" />
          </button>
        </div>
      </div>
    </div>
  );
}
