/** @type {import('next').NextConfig} */
const nextConfig = {
  output: process.env.NEXT_BUILD_STANDALONE === "1" ? "standalone" : undefined,
};
module.exports = nextConfig;
