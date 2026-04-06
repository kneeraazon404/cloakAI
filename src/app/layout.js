import "./globals.css";
import { Inter, JetBrains_Mono } from "next/font/google";

const inter = Inter({ subsets: ["latin"], variable: "--font-main" });
const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
});

export const metadata = {
  metadataBase: new URL(
    process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000",
  ),
  title: "CloakAI - AI Image Security Platform",
  description:
    "AI-powered image protection platform. Cloak your images against unauthorized AI training and facial recognition.",
  keywords: ["AI image security", "image protection", "AI cloaking", "privacy"],
  openGraph: {
    title: "CloakAI - AI Image Security Platform",
    description:
      "AI-powered image protection platform. Cloak your images against unauthorized AI training.",
    images: ["/logo-hero.png"],
    type: "website",
  },
  icons: {
    icon: [
      { url: "/favicon.ico", sizes: "any" },
      { url: "/icon-32.png", sizes: "32x32", type: "image/png" },
    ],
    apple: "/icon-512.png",
  },
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={`${inter.variable} ${jetbrainsMono.variable}`}>
        {children}
      </body>
    </html>
  );
}
