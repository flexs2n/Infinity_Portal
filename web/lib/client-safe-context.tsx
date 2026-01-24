'use client'

/**
 * Client-safe mode context provider
 * Controls whether sensitive information (handles, full post text) is displayed
 */

import React, { createContext, useContext, useState, useEffect } from 'react'
import { logAuditAction } from './audit-logger'

interface ClientSafeContextType {
  isClientSafe: boolean
  toggle: () => void
  setClientSafe: (value: boolean) => void
}

const ClientSafeContext = createContext<ClientSafeContextType>({
  isClientSafe: false,
  toggle: () => {},
  setClientSafe: () => {},
})

export function ClientSafeProvider({ children }: { children: React.ReactNode }) {
  const [isClientSafe, setIsClientSafe] = useState(false)
  const [mounted, setMounted] = useState(false)

  // Load from localStorage on mount
  useEffect(() => {
    setMounted(true)
    const stored = localStorage.getItem('client_safe_mode')
    if (stored) {
      setIsClientSafe(JSON.parse(stored))
    }
  }, [])

  const toggle = () => {
    const newState = !isClientSafe
    setIsClientSafe(newState)
    localStorage.setItem('client_safe_mode', JSON.stringify(newState))
    logAuditAction('toggled_client_safe', { new_state: newState })
  }

  const setClientSafe = (value: boolean) => {
    setIsClientSafe(value)
    localStorage.setItem('client_safe_mode', JSON.stringify(value))
    logAuditAction('toggled_client_safe', { new_state: value })
  }

  // Prevent hydration mismatch
  if (!mounted) {
    return (
      <ClientSafeContext.Provider value={{ isClientSafe: false, toggle, setClientSafe }}>
        {children}
      </ClientSafeContext.Provider>
    )
  }

  return (
    <ClientSafeContext.Provider value={{ isClientSafe, toggle, setClientSafe }}>
      {children}
    </ClientSafeContext.Provider>
  )
}

export function useClientSafe() {
  const context = useContext(ClientSafeContext)
  if (!context) {
    throw new Error('useClientSafe must be used within ClientSafeProvider')
  }
  return context
}
