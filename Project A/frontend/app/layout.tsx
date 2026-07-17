import "./globals.css";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <main className="min-h-screen bg-gray-50 p-4">
          <div className="max-w-4xl mx-auto">
            {children}
          </div>
        </main>
      </body>
    </html>
  )
}
