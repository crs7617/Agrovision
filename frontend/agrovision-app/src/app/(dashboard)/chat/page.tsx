'use client'

import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Send, Bot, User, Loader2, Trash2, Download, Sparkles, Globe } from 'lucide-react'
import toast from 'react-hot-toast'
import { formatDistanceToNow } from 'date-fns'

const USER_ID = '00000000-0000-0000-0000-000000000001'
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://agrovision-backend.onrender.com'

const LANGUAGES = {
  en: 'English',
  hi: 'हिन्दी (Hindi)',
  ta: 'தமிழ் (Tamil)',
  te: 'తెలుగు (Telugu)',
  ml: 'മലയാളം (Malayalam)',
  kn: 'ಕನ್ನಡ (Kannada)',
  bn: 'বাংলা (Bengali)',
}

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  contentNative?: string
  timestamp: Date
  suggestions?: string[]
}

const SUGGESTED_PROMPTS = [
  'Analyze my farm health',
  'What crops should I plant?',
  'Explain NDVI to me',
  'Show irrigation recommendations',
  'Detect pest issues',
  'Weather forecast impact',
]

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Hello! I am your AgroVision AI assistant. I can help you with farm health analysis, crop recommendations, and agricultural insights. How can I assist you today?',
      timestamp: new Date(),
      suggestions: SUGGESTED_PROMPTS.slice(0, 4),
    },
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [selectedLanguage, setSelectedLanguage] = useState('en')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async (message?: string) => {
    const content = message || input.trim()
    if (!content || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      console.log('API_BASE_URL:', API_BASE_URL)
      console.log('Calling:', `${API_BASE_URL}/api/chat`)
      
      const res = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: USER_ID,
          message: content,
          language: selectedLanguage !== 'en' ? selectedLanguage : undefined,
        }),
      })

      console.log('Response status:', res.status)
      
      if (!res.ok) {
        const errorText = await res.text()
        console.error('Response error:', errorText)
        throw new Error('Failed to get response')
      }

      const data = await res.json()
      console.log('Response data:', data)

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response_text || data.response || 'Sorry, I could not process that request.',
        contentNative: data.response_text_native,
        timestamp: new Date(),
        suggestions: data.suggestions || [],
      }

      setMessages((prev) => [...prev, assistantMessage])
      
      if (data.detected_language && data.detected_language !== 'en') {
        toast.success(`Detected language: ${LANGUAGES[data.detected_language as keyof typeof LANGUAGES]}`)
      }
    } catch (error) {
      console.error('Chat error:', error)
      toast.error('Failed to get AI response')
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again later.',
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleClearChat = () => {
    setMessages([
      {
        id: '1',
        role: 'assistant',
        content: 'Chat cleared! How can I help you?',
        timestamp: new Date(),
        suggestions: SUGGESTED_PROMPTS.slice(0, 4),
      },
    ])
    toast.success('Chat cleared')
  }

  const handleExportChat = () => {
    const chatText = messages
      .map(
        (msg) =>
          `[${msg.timestamp.toLocaleString()}] ${msg.role === 'user' ? 'You' : 'AI'}: ${msg.content}`
      )
      .join('\n\n')
    
    const blob = new Blob([chatText], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `agrovision-chat-${new Date().toISOString().split('T')[0]}.txt`
    a.click()
    toast.success('Chat exported')
  }

  return (
    <div className="max-w-5xl mx-auto h-[calc(100vh-12rem)]">
      <Card className="bg-zinc-900 border-white/10 h-full flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-emerald-500/10">
              <Sparkles className="h-6 w-6 text-emerald-500" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">AI Assistant</h2>
              <p className="text-sm text-gray-400">Ask me anything about your farms</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Select value={selectedLanguage} onValueChange={setSelectedLanguage}>
              <SelectTrigger className="w-[180px] bg-zinc-800 border-white/10 text-white">
                <Globe className="h-4 w-4 mr-2" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-zinc-800 border-white/10">
                {Object.entries(LANGUAGES).map(([code, name]) => (
                  <SelectItem key={code} value={code} className="text-white">
                    {name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button
              variant="outline"
              size="icon"
              onClick={handleExportChat}
              className="border-white/20 text-white hover:bg-white/5"
            >
              <Download className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="icon"
              onClick={handleClearChat}
              className="border-white/20 text-white hover:bg-white/5"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {message.role === 'assistant' && (
                <Avatar className="h-10 w-10 bg-emerald-600 shrink-0">
                  <AvatarFallback className="bg-emerald-600 text-white">
                    <Bot className="h-5 w-5" />
                  </AvatarFallback>
                </Avatar>
              )}

              <div className={`max-w-[80%] ${message.role === 'user' ? 'order-first' : ''}`}>
                <div
                  className={`p-4 rounded-lg ${
                    message.role === 'user'
                      ? 'bg-emerald-600 text-white'
                      : 'bg-black/50 text-white border border-white/10'
                  }`}
                >
                  {message.contentNative && (
                    <>
                      <p className="whitespace-pre-wrap mb-3 pb-3 border-b border-white/20">
                        {message.contentNative}
                      </p>
                      <p className="text-xs text-gray-400 mb-2">English translation:</p>
                    </>
                  )}
                  <p className="whitespace-pre-wrap">{message.content}</p>
                </div>

                <p className="text-xs text-gray-500 mt-1 px-1">
                  {formatDistanceToNow(message.timestamp, { addSuffix: true })}
                </p>

                {message.suggestions && message.suggestions.length > 0 && (
                  <div className="flex flex-wrap gap-2 mt-3">
                    {message.suggestions.map((suggestion, idx) => (
                      <Button
                        key={idx}
                        variant="outline"
                        size="sm"
                        onClick={() => handleSend(suggestion)}
                        className="border-white/20 text-white hover:bg-emerald-600 hover:border-emerald-600"
                      >
                        {suggestion}
                      </Button>
                    ))}
                  </div>
                )}
              </div>

              {message.role === 'user' && (
                <Avatar className="h-10 w-10 bg-blue-600 shrink-0">
                  <AvatarFallback className="bg-blue-600 text-white">
                    <User className="h-5 w-5" />
                  </AvatarFallback>
                </Avatar>
              )}
            </div>
          ))}

          {isLoading && (
            <div className="flex gap-3">
              <Avatar className="h-10 w-10 bg-emerald-600">
                <AvatarFallback className="bg-emerald-600 text-white">
                  <Bot className="h-5 w-5" />
                </AvatarFallback>
              </Avatar>
              <div className="p-4 rounded-lg bg-black/50 border border-white/10">
                <div className="flex items-center gap-2">
                  <Loader2 className="h-4 w-4 animate-spin text-emerald-500" />
                  <span className="text-gray-400">AI is thinking...</span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-4 border-t border-white/10">
          {messages.length === 1 && (
            <div className="mb-4 flex flex-wrap gap-2">
              {SUGGESTED_PROMPTS.map((prompt, idx) => (
                <Button
                  key={idx}
                  variant="outline"
                  size="sm"
                  onClick={() => handleSend(prompt)}
                  className="border-white/20 text-white hover:bg-emerald-600 hover:border-emerald-600"
                >
                  {prompt}
                </Button>
              ))}
            </div>
          )}

          <form
            onSubmit={(e) => {
              e.preventDefault()
              handleSend()
            }}
            className="flex gap-2"
          >
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about your farms, crops, or get recommendations..."
              className="flex-1 bg-black border-white/20 text-white placeholder:text-gray-500"
              disabled={isLoading}
            />
            <Button
              type="submit"
              className="bg-emerald-600 hover:bg-emerald-700 text-white"
              disabled={isLoading || !input.trim()}
            >
              <Send className="h-5 w-5" />
            </Button>
          </form>
        </div>
      </Card>
    </div>
  )
}
