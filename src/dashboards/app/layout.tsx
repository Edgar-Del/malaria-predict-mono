import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Sistema de Previsão de Risco de Malária - Bié',
  description: 'Dashboard interativo para monitoramento e previsão de risco de malária na província do Bié, Angola',
  keywords: ['malária', 'previsão', 'risco', 'Bié', 'Angola', 'saúde pública'],
  authors: [{ name: 'Sistema de Previsão de Malária' }],
  viewport: 'width=device-width, initial-scale=1',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pt">
      <body className={inter.className}>
        <div className="min-h-screen bg-gray-50">
          {children}
        </div>
      </body>
    </html>
  )
}