"use client"

import { useEffect, useRef, useState } from "react"

interface Particle {
  x: number
  y: number
  vx: number
  vy: number
  size: number
  opacity: number
}

export function ParticleBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const particlesRef = useRef<Particle[]>([])
  const animationRef = useRef<number>()
  const [hasError, setHasError] = useState(false)

  useEffect(() => {
    try {
      const canvas = canvasRef.current
      if (!canvas) return

      const ctx = canvas.getContext("2d")
      if (!ctx) return

      const resizeCanvas = () => {
        try {
          canvas.width = window.innerWidth
          canvas.height = window.innerHeight
        } catch (error) {
          console.warn("Canvas resize failed, using fallback")
          canvas.width = 1200
          canvas.height = 800
        }
      }

      const createParticles = () => {
        const particles: Particle[] = []
        const particleCount = Math.floor((canvas.width * canvas.height) / 15000)

        for (let i = 0; i < particleCount; i++) {
          particles.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            vx: (Math.random() - 0.5) * 0.5,
            vy: (Math.random() - 0.5) * 0.5,
            size: Math.random() * 2 + 1,
            opacity: Math.random() * 0.5 + 0.2,
          })
        }
        particlesRef.current = particles
      }

      const animate = () => {
        try {
          if (!canvas || !ctx) return
          
          ctx.clearRect(0, 0, canvas.width, canvas.height)

          particlesRef.current.forEach((particle, index) => {
            // Update position
            particle.x += particle.vx
            particle.y += particle.vy

            // Bounce off edges
            if (particle.x < 0 || particle.x > canvas.width) particle.vx *= -1
            if (particle.y < 0 || particle.y > canvas.height) particle.vy *= -1

            // Keep particles in bounds
            particle.x = Math.max(0, Math.min(canvas.width, particle.x))
            particle.y = Math.max(0, Math.min(canvas.height, particle.y))

            // Draw particle with red theme
            ctx.beginPath()
            ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2)
            ctx.fillStyle = `rgba(229, 9, 20, ${particle.opacity})`
            ctx.fill()

            // Draw connections (optimized for performance)
            if (index % 2 === 0) {
              particlesRef.current.slice(index + 1, index + 5).forEach((otherParticle) => {
                const dx = particle.x - otherParticle.x
                const dy = particle.y - otherParticle.y
                const distance = Math.sqrt(dx * dx + dy * dy)

                if (distance < 80) {
                  ctx.beginPath()
                  ctx.moveTo(particle.x, particle.y)
                  ctx.lineTo(otherParticle.x, otherParticle.y)
                  ctx.strokeStyle = `rgba(229, 9, 20, ${0.15 * (1 - distance / 80)})`
                  ctx.lineWidth = 0.5
                  ctx.stroke()
                }
              })
            }
          })

          if (!hasError) {
            animationRef.current = requestAnimationFrame(animate)
          }
        } catch (error) {
          console.error("Error in particle animation:", error)
          setHasError(true)
        }
      }

      resizeCanvas()
      createParticles()
      animate()

      const handleResize = () => {
        try {
          resizeCanvas()
          createParticles()
        } catch (error) {
          console.error("Error handling resize:", error)
          setHasError(true)
        }
      }

      window.addEventListener("resize", handleResize)

      return () => {
        if (animationRef.current) {
          cancelAnimationFrame(animationRef.current)
        }
        window.removeEventListener("resize", handleResize)
      }
    } catch (error) {
      console.error("Error initializing particle background:", error)
      setHasError(true)
    }
  }, [hasError])

  // Fallback UI if particles fail to load
  if (hasError) {
    return (
      <div className="absolute inset-0 bg-gradient-to-br from-red-900/10 via-transparent to-red-900/5" />
    )
  }

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 pointer-events-none opacity-60"
      style={{ background: 'transparent' }}
    />
  )
}
