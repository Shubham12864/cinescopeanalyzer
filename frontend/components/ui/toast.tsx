"use client"

import { useEffect, useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { CheckCircle, AlertCircle, X } from "lucide-react"

interface ToastData {
  id: string
  type: 'success' | 'error' | 'info'
  title: string
  description?: string
  duration?: number
}

interface ToastProps extends ToastData {
  onClose: (id: string) => void
}

export function Toast({ id, type, title, description, duration = 4000, onClose }: ToastProps) {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose(id)
    }, duration)

    return () => clearTimeout(timer)
  }, [id, duration, onClose])

  const icons = {
    success: CheckCircle,
    error: AlertCircle,
    info: AlertCircle
  }

  const colors = {
    success: 'bg-green-600/20 border-green-600 text-green-300',
    error: 'bg-red-600/20 border-red-600 text-red-300',
    info: 'bg-blue-600/20 border-blue-600 text-blue-300'
  }

  const Icon = icons[type]

  return (
    <motion.div
      initial={{ opacity: 0, x: 300 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 300 }}
      className={`${colors[type]} border px-4 py-3 rounded-lg backdrop-blur-sm shadow-lg max-w-sm`}
    >
      <div className="flex items-start gap-3">
        <Icon className="w-5 h-5 flex-shrink-0 mt-0.5" />
        <div className="flex-1 min-w-0">
          <div className="font-medium text-sm">{title}</div>
          {description && (
            <div className="text-xs opacity-80 mt-1">{description}</div>
          )}
        </div>
        <button
          onClick={() => onClose(id)}
          className="opacity-60 hover:opacity-100 transition-opacity"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </motion.div>
  )
}

export function ToastContainer({ toasts, onRemoveToast }: { toasts: ToastData[], onRemoveToast: (id: string) => void }) {
  return (
    <div className="fixed top-4 right-4 z-50 space-y-2">
      <AnimatePresence>
        {toasts.map((toast) => (
          <Toast
            key={toast.id}
            {...toast}
            onClose={onRemoveToast}
          />
        ))}
      </AnimatePresence>
    </div>
  )
}
