"use client"

import { Line } from "react-chartjs-2"
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  type ChartOptions,
} from "chart.js"

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler)

export interface ReviewTimelineData {
  months: string[]
  reviewCounts: number[]
}

export function ReviewTimeline({ data: timelineData }: { data: ReviewTimelineData }) {
  const data = {
    labels: timelineData.months,
    datasets: [
      {
        label: "Reviews",
        data: timelineData.reviewCounts,
        borderColor: "rgba(78, 205, 196, 1)",
        backgroundColor: "rgba(78, 205, 196, 0.1)",
        borderWidth: 3,
        fill: true,
        tension: 0.4,
        pointBackgroundColor: "rgba(78, 205, 196, 1)",
        pointBorderColor: "#ffffff",
        pointBorderWidth: 2,
        pointRadius: 6,
        pointHoverRadius: 8,
      },
    ],
  }

  const options: ChartOptions<"line"> = {
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
    interaction: {
      intersect: false,
      mode: "index",
    },
  }

  return (
    <div className="glass-strong rounded-2xl p-6">
      <h3 className="text-xl font-semibold text-white mb-6 font-poppins">Review Timeline</h3>
      <div className="h-80">
        <Line data={data} options={options} />
      </div>
    </div>
  )
}
