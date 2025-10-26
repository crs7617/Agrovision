'use client'

import { Component, ReactNode } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { AlertCircle } from 'lucide-react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <Card className="bg-zinc-900 border-red-500/20 p-12 text-center">
          <AlertCircle className="h-16 w-16 mx-auto mb-4 text-red-500" />
          <h2 className="text-2xl font-bold text-white mb-2">Something went wrong</h2>
          <p className="text-gray-400 mb-6">
            {this.state.error?.message || 'An unexpected error occurred'}
          </p>
          <Button
            onClick={() => this.setState({ hasError: false, error: undefined })}
            className="bg-emerald-600 hover:bg-emerald-700"
          >
            Try Again
          </Button>
        </Card>
      )
    }

    return this.props.children
  }
}
