import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "APSO",
  description: "AI-powered SDLC productivity and release intelligence.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
