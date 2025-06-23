"use client"

import { motion } from "framer-motion"
import { Film, Settings, Home, Star } from "lucide-react"
import Link from "next/link"
import { useRouter } from "next/navigation"

const navigationItems = [
  { id: "home", label: "Home", icon: Home, href: "/" },
  { id: "favorites", label: "My List", icon: Star, href: "/favorites" },
  { id: "settings", label: "Settings", icon: Settings, href: "/settings" },
]

export function Navigation() {
  const router = useRouter()
  return (
    <motion.nav
      initial={{ x: -100, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="fixed left-0 top-0 h-full w-64 bg-black/95 backdrop-blur-sm z-50 hidden lg:block border-r border-red-900/20"
    >
      <div className="p-6">
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="flex items-center gap-3 mb-8"
        >
          <div className="w-10 h-10 bg-gradient-to-r from-red-600 to-red-500 rounded-lg flex items-center justify-center">
            <Film className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold font-poppins text-white">CineAnalyzer</h1>
            <p className="text-sm text-gray-400">Movie Intelligence</p>
          </div>
        </motion.div>

        <ul className="space-y-2">
          {navigationItems.map((item, index) => (
            <motion.li
              key={item.id}
              initial={{ x: -50, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: 0.1 * index }}
            >
              <Link href={item.href} legacyBehavior>
                <a className="w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 group text-gray-300 hover:bg-red-600/20 hover:text-white">
                  <item.icon className="w-5 h-5 transition-transform duration-200 group-hover:scale-105" />
                  <span className="font-medium">{item.label}</span>
                </a>
              </Link>
            </motion.li>
          ))}
        </ul>
      </div>
    </motion.nav>
  )
}
