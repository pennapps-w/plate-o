import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import Link from "next/link";

export default function Home() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-orange-200 to-red-300 p-4">
      <div className="w-full max-w-md space-y-6">
        <div className="bg-white rounded-3xl shadow-xl overflow-hidden border-4 border-yellow-400 p-6">
          <h2 className="text-2xl font-bold mb-4 text-orange-600">
            Bank Information
          </h2>
          <Textarea
            placeholder="Enter your bank information"
            className="mb-4"
          />
          <h2 className="text-2xl font-bold mb-4 text-orange-600">
            Food Preferences
          </h2>
          <Textarea
            placeholder="Enter your food preferences"
            className="mb-4"
          />
          <Link href="/start">
            <Button className="w-full">Submit</Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
