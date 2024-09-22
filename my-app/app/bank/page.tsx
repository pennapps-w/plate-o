"use client";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function Home() {
  const [income, setIncome] = useState(0.0);
  const [bills, setBills] = useState(0.0);
  const [expenses, setExpenses] = useState(0.0);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log("handling submit!!!");
    try {
      const response = await fetch(
        "https://blobotic-service1--8000.prod1.defang.dev/users/66ee6b3a7aa3130e68418c7d/bank",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
          },
          body: JSON.stringify({
            income: income,
            bills: bills,
            expenses: expenses,
          }),
          credentials: "include",
        }
      );

      console.log("got a responsE!");

      if (response.ok) {
        // const updatedUser = await response.json();
        // console.log("User updated successfully:", updatedUser);
        router.push("/start");
      } else {
        console.error("Failed to update user preferences");
      }
    } catch (error) {
      console.error("Error updating user preferences:", error);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-orange-200 to-red-300 p-4">
      <div className="w-full max-w-lg space-y-6">
        <form
          onSubmit={handleSubmit}
          className="bg-white rounded-3xl shadow-xl overflow-hidden border-4 border-red-400 p-6"
        >
          <h2 className="text-2xl font-bold mb-4 text-orange-600">
            Financial information
          </h2>
          <h3 className="text-xl font-bold mb-4 text-orange-600">
            Monthly income
          </h3>
          <input
            value={income}
            onChange={(e) => setIncome(parseFloat(e.target.value))}
            className="w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-slate-400 hover:border-slate-300 shadow-sm focus:shadow mb-5"
          ></input>

          <h3 className="text-xl font-bold mb-4 text-orange-600">
            Monthly bills
          </h3>
          <input
            value={bills}
            onChange={(e) => setBills(parseFloat(e.target.value))}
            className="w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-slate-400 hover:border-slate-300 shadow-sm focus:shadow mb-5"
          ></input>

          <h3 className="text-xl font-bold mb-4 text-orange-600">Expenses</h3>
          <input
            value={expenses}
            onChange={(e) => setExpenses(parseFloat(e.target.value))}
            className="w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-slate-400 hover:border-slate-300 shadow-sm focus:shadow mb-5"
          ></input>

          <p className="text-right">
            <Button className="bg-green-500 middle mb-5 mt-2 ">
              Payment Authentication
            </Button>
          </p>

          <Button type="submit" className="w-full">
            Submit
          </Button>
        </form>
      </div>
    </div>
  );
}
