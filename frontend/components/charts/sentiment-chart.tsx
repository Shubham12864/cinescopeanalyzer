"use client"

import { Doughnut } from "react-chartjs-2"
import { Chart as ChartJS, ArcElement, Tooltip, Legend, type ChartOptions } from "chart.js"

ChartJS.register(ArcElement, Tooltip, Legend)

export interface SentimentData {
  positive: number
  neutral: number
  negative: number
}

export function SentimentChart({ data: sentiment }: { data: SentimentData }) {
  const data = {
    labels: ["Positive", "Neutral", "Negative"],
    datasets: [
      {
        data: [sentiment.positive, sentiment.neutral, sentiment.negative],
        backgroundColor: ["rgba(78, 205, 196, 0.8)", "rgba(255, 206, 84, 0.8)", "rgba(255, 107, 107, 0.8)"],
        borderColor: ["rgba(78, 205, 196, 1)", "rgba(255, 206, 84, 1)", "rgba(255, 107, 107, 1)"],
        borderWidth: 2,
        hoverOffset: 10,
      },
    ],
  }

  const options: ChartOptions<"doughnut"> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "bottom",
        labels: {
          color: "#fafafa",
          padding: 20,
          font: {
            size: 14,
          },
        },
      },
      tooltip: {
        backgroundColor: "rgba(0, 0, 0, 0.8)",
        titleColor: "#fafafa",
        bodyColor: "#fafafa",
        borderColor: "rgba(255, 255, 255, 0.2)",
        borderWidth: 1,
      },
    },
    cutout: "60%",
  }

  return (
    <div className="glass-strong rounded-2xl p-6">
      <h3 className="text-xl font-semibold text-white mb-6 font-poppins">Sentiment Analysis</h3>
      <div className="h-80">
        <Doughnut data={data} options={options} />
      </div>
      <div className="mt-6 grid grid-cols-3 gap-4 text-center">
        <div>
          <div className="text-2xl font-bold text-teal">{sentiment.positive}%</div>
          <div className="text-sm text-gray-400">Positive</div>
        </div>
        <div>
          <div className="text-2xl font-bold text-yellow-400">{sentiment.neutral}%</div>
          <div className="text-sm text-gray-400">Neutral</div>
        </div>
        <div>
          <div className="text-2xl font-bold text-coral">{sentiment.negative}%</div>
          <div className="text-sm text-gray-400">Negative</div>
        </div>
      </div>
    </div>
  )
}
