"use client";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function Home() {
  const [likes, setLikes] = useState("");
  const [dislikes, setDislikes] = useState("");
  const [never, setNever] = useState("");
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch(
        "https://blobotic-service1--8000.prod1.defang.dev/users/66ee6b3a7aa3130e68418c7d",
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            likes,
            dislikes,
            never,
          }),
        }
      );

      if (response.ok) {
        const updatedUser = await response.json();
        console.log("User updated successfully:", updatedUser);
        router.push("/bank");
      } else {
        console.error("Failed to update user preferences");
      }
    } catch (error) {
      console.error("Error updating user preferences:", error);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-orange-200 to-red-300 p-4">
      <div className="w-full max-w-md space-y-6">
        <form
          onSubmit={handleSubmit}
          className="bg-white rounded-3xl shadow-xl overflow-hidden border-4 border-yellow-400 p-6"
        >
          <h2 className="text-2xl font-bold mb-4 text-orange-600">
            Food Preferences
          </h2>
          <h3 className="text-xl font-bold mb-4 text-orange-600">Likes</h3>
          <Textarea
            placeholder="japanese food, sushi, noodles"
            className="mb-4 text-black"
            value={likes}
            onChange={(e) => setLikes(e.target.value)}
          />

          <h3 className="text-xl font-bold mb-4 text-orange-600">Dislikes</h3>
          <Textarea
            placeholder="cold subways, nuts"
            className="mb-4 text-black"
            value={dislikes}
            onChange={(e) => setDislikes(e.target.value)}
          />

          <h3 className="text-xl font-bold mb-4 text-orange-600">Never</h3>
          <Textarea
            placeholder="cilantro"
            className="mb-4 text-black"
            value={never}
            onChange={(e) => setNever(e.target.value)}
          />

          {/* <Button type="submit" className="w-full">
            Submit
          </Button> */}
          <button
            type="submit"
            className="w-full bg-orange-500 text-white py-2 rounded-full mt-4 hover:bg-orange-600 transition-colors"
          >
            Submit{" "}
          </button>
        </form>
      </div>
    </div>
  );
}
