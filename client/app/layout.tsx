import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'AlphaQuant Terminal',
  description: 'Web3 Quant Trading Agent Dashboard',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-gray-950 text-white min-h-screen">
        {children}
      </body>
    </html>
  )
}
