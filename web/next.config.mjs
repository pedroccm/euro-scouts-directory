/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "export", // gera site estático em out/ (deploy Netlify)
  images: { unoptimized: true },
  eslint: { ignoreDuringBuilds: true },
};

export default nextConfig;
