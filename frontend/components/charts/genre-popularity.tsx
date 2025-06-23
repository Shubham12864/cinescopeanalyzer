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

export function GenrePopularity() {
  const data = {
    labels: ["Action", "Drama", "Comedy", "Sci-Fi", "Horror", "Romance", "Thriller"],
    datasets: [
      {
        label: "Popularity Score",
        data: [85, 92, 78, 88, 65, 72, 81],
        backgroundColor: [
          "rgba(255, 107, 107, 0.8)",
          "rgba(78, 205, 196, 0.8)",
          "rgba(255, 206, 84, 0.8)",
          "rgba(54, 162, 235, 0.8)",
          "rgba(153, 102, 255, 0.8)",
          "rgba(255, 159, 64, 0.8)",
          "rgba(199, 199, 199, 0.8)",
        ],
        borderColor: [
          "rgba(255, 107, 107, 1)",
          "rgba(78, 205, 196, 1)",
          "rgba(255, 206, 84, 1)",
          "rgba(54, 162, 235, 1)",
          "rgba(153, 102, 255, 1)",
          "rgba(255, 159, 64, 1)",
          "rgba(199, 199, 199, 1)",
        ],
        borderWidth: 1,
        borderRadius: 8,
        borderSkipped: false,
      },
    ],
  }

  const options: ChartOptions<"bar"> = {
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: "y" as const,
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
          color: "rgba(255, 255, 255, 0.1)",
        },
        ticks: {
          color: "#9ca3af",
        },
      },
      y: {
        grid: {
          display: false,
        },
        ticks: {
          color: "#9ca3af",
        },
      },
    },
  }

  return (
    <div className="glass-strong rounded-2xl p-6">
      <h3 className="text-xl font-semibold text-white mb-6 font-poppins">Genre Popularity</h3>
      <div className="h-80">
        <Bar data={data} options={options} />
      </div>
    </div>
  )
}
