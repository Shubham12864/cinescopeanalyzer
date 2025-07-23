export interface ToastData {
  id: string
  type: 'success' | 'error' | 'info'
  title: string
  description?: string
  duration?: number
}

export interface ToastProps extends ToastData {
  onClose: (id: string) => void
}

export interface ToastContainerProps {
  toasts: ToastData[]
  onRemoveToast: (id: string) => void
}
