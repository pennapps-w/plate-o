"use client";

import { useState, useEffect } from "react";
import {
  motion,
  AnimatePresence,
  useMotionValue,
  useTransform,
} from "framer-motion";
import { X, Heart, DollarSign, Leaf, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";

interface Restaurant {
  name: string;
  description: string;
  menu: Array<{ name: string; price: string }>;
  final_score: number;
  price_point: string;
  id: string;
}

export function FoodSwiper() {
  const [currentRestaurant, setCurrentRestaurant] = useState<Restaurant | null>(
    null
  );
  const [isLoading, setIsLoading] = useState(false);
  const [otherReason, setOtherReason] = useState("");
  const [showRejectModal, setShowRejectModal] = useState(false); // Added initialization
  const [rejectReason, setRejectReason] = useState(""); // Added initialization

  const x = useMotionValue(0);
  const rotate = useTransform(x, [-200, 200], [-30, 30]);
  const opacity = useTransform(x, [-200, -100, 0, 100, 200], [0, 1, 1, 1, 0]);

  const fetchRecommendation = async () => {
    setIsLoading(true);
    console.log("CURRENTLY FETCHING RECOMMENDATION");
    try {
      const response = await fetch(
        "https://blobotic-service1--8000.prod1.defang.dev/get_recommendation/66ee6b3a7aa3130e68418c7d"
      );
      if (!response.ok) {
        throw new Error("Failed to fetch recommendation");
      }
      const data = await response.json();
      setCurrentRestaurant(data.recommendation);
      console.log(data.recommendation);
      // console.log("HIHIHIHIHIHIHI");
      console.log(data);
    } catch (error) {
      console.error("Error fetching recommendation:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendation();
  }, []);

  const handleSwipe = (swipeDirection: "left" | "right") => {
    if (swipeDirection === "left") {
      setShowRejectModal(true);
    } else if (swipeDirection === "right") {
      // Handle right swipe logic here if needed
    }
  };

  const handleReject = async () => {
    setIsLoading(true);
    try {
      const reason = rejectReason === "other" ? otherReason : rejectReason;
      console.log("Reject reason:", reason);
      const tmpbody = JSON.stringify({
        id: "66ee6b3a7aa3130e68418c7d",
        reason,
        restaurant_id: currentRestaurant?.id || "",
      });
      console.log(tmpbody);
      const response = await fetch(
        "https://blobotic-service1--8000.prod1.defang.dev/dislike_because/66ee6b3a7aa3130e68418c7d",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
          },
          body: tmpbody,
          credentials: "include",
        }
      );
      console.log(response);
      if (!response.ok) {
        throw new Error("Failed to reject recommendation");
      }
      await fetchRecommendation();
    } catch (error) {
      console.error("Error handling reject:", error);
    } finally {
      setIsLoading(false);
      setShowRejectModal(false);
      setRejectReason("");
      setOtherReason("");
    }
  };

  const handleDragEnd = (
    event: React.MouseEvent<HTMLDivElement>,
    info: {
      offset: { x: number; y: number };
      velocity: { x: number; y: number };
    }
  ) => {
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
        <Dialog open={showRejectModal} onOpenChange={setShowRejectModal}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>
                Why do you dislike about this restaurant?
              </DialogTitle>
              <DialogDescription>
                Your feedback helps us improve our algorithm.
              </DialogDescription>
            </DialogHeader>
            <div className="mt-4">
              <Label htmlFor="otherReason">Please specify:</Label>
              <Input
                id="otherReason"
                value={otherReason}
                onChange={(e) => setOtherReason(e.target.value)}
                placeholder="Enter your reason here"
              />
            </div>
            <DialogFooter>
              <Button onClick={handleReject} disabled={!otherReason.trim()}>
                Submit
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
}
