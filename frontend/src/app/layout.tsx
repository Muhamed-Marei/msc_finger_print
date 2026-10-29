import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'منظومة بصمات الأطباء والعاملين | Medical Services Co.',
  description: 'لوحة التحكم الذكية والمؤتمتة لتحليل بصمات الحضور والانصراف، احتساب الشفتات، العجز والساعات الإضافية، واستخراج تقارير PDF و Excel المعتمدة.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ar" dir="rtl">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body>{children}</body>
    </html>
  );
}
