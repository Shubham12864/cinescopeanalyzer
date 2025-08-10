"use client"

import { Bar } from "react-chartjs-2"
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  type ChartOptions,
} from "chart.js"

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

export interface RatingDistributionData {
  ratings: number[] // Array of counts for 1★ to 10★
}

export function RatingDistribution({ data: ratingData }: { data: RatingDistributionData }) {
  const data = {
    labels: ["1★", "2★", "3★", "4★", "5★", "6★", "7★", "8★", "9★", "10★"],
    datasets: [
      {
        label: "Number of Reviews",
        data: ratingData.ratings,
        backgroundColor: "rgba(78, 205, 196, 0.8)",
        borderColor: "rgba(78, 205, 196, 1)",
        borderWidth: 1,
        borderRadius: 8,
        borderSkipped: false,
      },
    ],
  }

  const options: ChartOptions<"bar"> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        backgroundColor: "rgba(0, 0, 0, 0.8)",
        titleColor: "#fafafa",
        bodyColor: "#fafafa",
        borderColor: "rgba(255, 255, 255, 0.2)",
        borderWidth: 1,
      },
    },
    scales: {
      x: {
        grid: {
          display: false,
        },
        ticks: {
          color: "#9ca3af",
        },
      },
      y: {
        grid: {
          color: "rgba(255, 255, 255, 0.1)",
        },
        ticks: {
          color: "#9ca3af",
        },
      },
    },
  }

  return (
    <div className="glass-strong rounded-2xl p-6">
      <h3 className="text-xl font-semibold text-white mb-6 font-poppins">Rating Distribution</h3>
      <div className="h-80">
        <Bar data={data} options={options} />
      </div>
    </div>
  )
}
