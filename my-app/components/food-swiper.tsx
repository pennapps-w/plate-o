"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  motion,
  AnimatePresence,
  useMotionValue,
  useTransform,
} from "framer-motion";
import { X, Heart, DollarSign, Leaf } from "lucide-react";

const restaurants = [
  {
    name: "Bella Italia",
    dish: "Margherita Pizza",
    image: "/placeholder.svg?height=300&width=300",
    esgScore: 7.5,
    price: 2,
    summary:
      "Authentic Italian pizzeria with a cozy atmosphere and wood-fired oven.",
  },
  {
    name: "Sushi Haven",
    dish: "Dragon Roll",
    image: "/placeholder.svg?height=300&width=300",
    esgScore: 8.2,
    price: 3,
    summary:
      "Fresh, sustainable sushi with creative fusion rolls and traditional nigiri.",
  },
  {
    name: "Burger Joint",
    dish: "Classic Cheeseburger",
    image: "/placeholder.svg?height=300&width=300",
    esgScore: 6.8,
    price: 2,
    summary:
      "Juicy, locally-sourced beef burgers with a variety of toppings and house-made sauces.",
  },
  {
    name: "Taco Town",
    dish: "Carne Asada Tacos",
    image: "/placeholder.svg?height=300&width=300",
    esgScore: 7.9,
    price: 1,
    summary:
      "Authentic street-style tacos with a range of fillings and homemade salsas.",
  },
];

export function FoodSwiper() {
  const router = useRouter();
  const [currentIndex, setCurrentIndex] = useState(0);
  const [direction, setDirection] = useState<"left" | "right" | null>(null);

  const x = useMotionValue(0);
  const rotate = useTransform(x, [-200, 200], [-30, 30]);
  const opacity = useTransform(x, [-200, -100, 0, 100, 200], [0, 1, 1, 1, 0]);

  const nextRestaurant = () => {
    setCurrentIndex((prevIndex) => (prevIndex + 1) % restaurants.length);
  };

  const handleSwipe = (swipeDirection: "left" | "right") => {
    if (swipeDirection === "right") {
      router.push("/success");
    } else {
      setDirection(swipeDirection);
    }
  };

  const handleDragEnd = (event: any, info: any) => {
    const swipeThreshold = 100;
    if (info.offset.x > swipeThreshold) {
      router.push("/success");
    } else if (info.offset.x < -swipeThreshold) {
      handleSwipe("left");
    }
  };

  useEffect(() => {
    if (direction) {
      const timer = setTimeout(() => {
        nextRestaurant();
        setDirection(null);
      }, 300);
      return () => clearTimeout(timer);
    }
  }, [direction]);

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

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-orange-200 to-red-300 p-4">
      <div className="w-full max-w-sm">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentIndex}
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
                src={restaurants[currentIndex].image}
                alt={restaurants[currentIndex].name}
                className="w-full h-full object-cover"
              />
            </div>
            <div className="p-4">
              <h1 className="text-3xl font-bold mb-1 text-orange-600">
                {restaurants[currentIndex].name}
              </h1>
              <h2 className="text-xl text-gray-700 mb-3">
                {restaurants[currentIndex].dish}
              </h2>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-gray-600 font-semibold">
                    ESG Score:
                  </span>
                  <div className="flex items-center">
                    <Leaf className="w-5 h-5 text-green-500 mr-1" />
                    <span className="text-lg font-bold">
                      {restaurants[currentIndex].esgScore.toFixed(1)}
                    </span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600 font-semibold">Price:</span>
                  <div className="flex">
                    {renderPriceIcons(restaurants[currentIndex].price)}
                  </div>
                </div>
                <p className="text-gray-800 text-sm mt-2">
                  {restaurants[currentIndex].summary}
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
            onClick={() => router.push("/success")}
            className="bg-green-500 rounded-full p-4 shadow-lg transition-transform hover:scale-110"
          >
            <Heart className="w-8 h-8 text-white" />
          </button>
        </div>
      </div>
    </div>
  );
}