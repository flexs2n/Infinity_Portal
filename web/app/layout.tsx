import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { ClientSafeProvider } from "@/lib/client-safe-context"
import Link from "next/link"
import { ClientSafeToggle } from "@/components/client-safe-toggle"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Wealth Management Evidence Platform",
  description: "Trust-first stock movement analysis using static social media datasets",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <ClientSafeProvider>
          <div className="min-h-screen flex flex-col">
            <header className="border-b bg-white">
              <div className="container mx-auto px-4 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-8">
                    <Link href="/" className="flex items-center gap-2">
                      <div className="w-8 h-8 bg-primary rounded flex items-center justify-center text-white font-bold">
                        E
                      </div>
                      <span className="font-semibold text-lg">Evidence Platform</span>
                    </Link>

                    <nav className="hidden md:flex items-center gap-6">
                      <Link
                        href="/"
                        className="text-sm text-muted-foreground hover:text-foreground transition"
                      >
                        Dashboard
                      </Link>
                      <Link
                        href="/audit"
                        className="text-sm text-muted-foreground hover:text-foreground transition"
                      >
                        Audit Log
                      </Link>
                    </nav>
                  </div>

                  <ClientSafeToggle />
                </div>
              </div>
            </header>

            <main className="flex-1 bg-gray-50">
              {children}
            </main>

            <footer className="border-t bg-white py-6">
              <div className="container mx-auto px-4">
                <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-muted-foreground">
                  <p>
                    Evidence Platform for Wealth Management Professionals
                  </p>
                  <p className="text-xs">
                    Static dataset analysis • Not investment advice • Correlation not causation
                  </p>
                </div>
              </div>
            </footer>
          </div>
        </ClientSafeProvider>
      </body>
    </html>
  )
}
