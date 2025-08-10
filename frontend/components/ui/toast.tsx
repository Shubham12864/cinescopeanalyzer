"use client"

import React, { useEffect, useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from 'lucide-react'
import { cn } from '@/lib/utils'

export interface ToastData {
  id: string
  type: 'success' | 'error' | 'info' | 'warning'
  title: string
  description?: string
  duration?: number
  action?: {
    label: string
    onClick: () => void
  }
}

interface ToastProps {
  toast: ToastData
  onRemove: (id: string) => void
}

const Toast: React.FC<ToastProps> = ({ toast, onRemove }) => {
  const [isVisible, setIsVisible] = useState(true)
  const [progress, setProgress] = useState(100)

  const duration = toast.duration || 5000

  const handleRemove = useCallback(() => {
    setIsVisible(false)
    setTimeout(() => onRemove(toast.id), 300)
  }, [onRemove, toast.id])

  useEffect(() => {
    if (duration > 0) {
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          const newProgress = prev - (100 / (duration / 100))
          if (newProgress <= 0) {
            clearInterval(progressInterval)
            handleRemove()
            return 0
          }
          return newProgress
        })
      }, 100)

      return () => clearInterval(progressInterval)
    }
  }, [duration, handleRemove]) // Add missing handleRemove dependency

  const getToastConfig = (type: ToastData['type']) => {
    switch (type) {
      case 'success':
        return {
          icon: CheckCircle,
          bgColor: 'bg-green-900/90',
          borderColor: 'border-green-600',
          iconColor: 'text-green-400',
          progressColor: 'bg-green-500'
        }
      case 'error':
        return {
          icon: AlertCircle,
          bgColor: 'bg-red-900/90',
          borderColor: 'border-red-600',
          iconColor: 'text-red-400',
          progressColor: 'bg-red-500'
        }
      case 'warning':
        return {
          icon: AlertTriangle,
          bgColor: 'bg-yellow-900/90',
          borderColor: 'border-yellow-600',
          iconColor: 'text-yellow-400',
          progressColor: 'bg-yellow-500'
        }
      case 'info':
      default:
        return {
          icon: Info,
          bgColor: 'bg-blue-900/90',
          borderColor: 'border-blue-600',
          iconColor: 'text-blue-400',
          progressColor: 'bg-blue-500'
        }
    }
  }

  const config = getToastConfig(toast.type)
  const Icon = config.icon

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, x: 300, scale: 0.9 }}
          animate={{ opacity: 1, x: 0, scale: 1 }}
          exit={{ opacity: 0, x: 300, scale: 0.9 }}
          transition={{ duration: 0.3, ease: "easeOut" }}
          className={cn(
            "relative overflow-hidden rounded-lg border backdrop-blur-sm shadow-lg max-w-sm w-full",
            config.bgColor,
            config.borderColor
          )}
        >
          {/* Progress bar */}
          {duration > 0 && (
            <div className="absolute top-0 left-0 h-1 bg-gray-700/50 w-full">
              <motion.div
                className={cn("h-full", config.progressColor)}
                style={{ width: `${progress}%` }}
                transition={{ duration: 0.1 }}
              />
            </div>
          )}

          <div className="p-4">
            <div className="flex items-start space-x-3">
              {/* Icon */}
              <div className="flex-shrink-0">
                <Icon className={cn("w-5 h-5", config.iconColor)} />
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <h4 className="text-sm font-medium text-white">
                  {toast.title}
                </h4>
                {toast.description && (
                  <p className="mt-1 text-sm text-gray-300">
                    {toast.description}
                  </p>
                )}
                {toast.action && (
                  <button
                    onClick={toast.action.onClick}
                    className="mt-2 text-sm font-medium text-white hover:text-gray-200 underline"
                  >
                    {toast.action.label}
                  </button>
                )}
              </div>

              {/* Close button */}
              <button
                onClick={handleRemove}
                className="flex-shrink-0 text-gray-400 hover:text-white transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

interface ToastContainerProps {
  toasts: ToastData[]
  onRemove: (id: string) => void
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center' | 'bottom-center'
}

export const ToastContainer: React.FC<ToastContainerProps> = ({ 
  toasts, 
  onRemove, 
  position = 'top-right' 
}) => {
  const getPositionClasses = (pos: string) => {
    switch (pos) {
      case 'top-left':
        return 'top-4 left-4'
      case 'top-center':
        return 'top-4 left-1/2 transform -translate-x-1/2'
      case 'top-right':
        return 'top-4 right-4'
      case 'bottom-left':
        return 'bottom-4 left-4'
      case 'bottom-center':
        return 'bottom-4 left-1/2 transform -translate-x-1/2'
      case 'bottom-right':
        return 'bottom-4 right-4'
      default:
        return 'top-4 right-4'
    }
  }
  return (
    <div className={cn(
      "fixed z-50 pointer-events-none",
      getPositionClasses(position)
    )}>
      <div className="space-y-3 pointer-events-auto">
        <AnimatePresence>
          {toasts.map((toast) => (
            <Toast
              key={toast.id}
              toast={toast}
              onRemove={onRemove}
            />
          ))}
        </AnimatePresence>
      </div>
    </div>
  )
}

// Hook for using toasts
export const useToast = () => {
  const [toasts, setToasts] = useState<ToastData[]>([])

  const addToast = (toast: Omit<ToastData, 'id'>) => {
    const id = Math.random().toString(36).substring(2, 11)
    const newToast: ToastData = { ...toast, id }
    
    setToasts(prev => [...prev, newToast])
    
    // Auto-remove after duration if specified
    if (toast.duration !== 0) {
      setTimeout(() => {
        removeToast(id)
      }, toast.duration || 5000)
    }
    
    return id
  }

  const removeToast = (id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id))
  }

  const removeAllToasts = () => {
    setToasts([])
  }

  // Convenience methods
  const success = (title: string, description?: string, duration?: number) => {
    return addToast({ type: 'success', title, description, duration })
  }

  const error = (title: string, description?: string, duration?: number) => {
    return addToast({ type: 'error', title, description, duration })
  }

  const warning = (title: string, description?: string, duration?: number) => {
    return addToast({ type: 'warning', title, description, duration })
  }

  const info = (title: string, description?: string, duration?: number) => {
    return addToast({ type: 'info', title, description, duration })
  }

  return {
    toasts,
    addToast,
    removeToast,
    removeAllToasts,
    success,
    error,
    warning,
    info
  }
}