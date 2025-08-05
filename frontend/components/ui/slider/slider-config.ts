/**
 * Comprehensive Slider Configuration Presets for CineScope
 * Supports different types of movie content display
 */

import { SwiperOptions } from 'swiper/types'

export interface SliderConfig {
  slidesPerView?: number | 'auto'
  spaceBetween?: number
  effect?: 'slide' | 'fade' | 'cube' | 'coverflow' | 'flip' | 'cards'
  autoplay?: boolean | {
    delay: number
    disableOnInteraction?: boolean
    pauseOnMouseEnter?: boolean
  }
  navigation?: boolean
  pagination?: boolean | {
    clickable: boolean
    dynamicBullets?: boolean
    type?: 'bullets' | 'fraction' | 'progressbar'
  }
  scrollbar?: boolean | {
    hide?: boolean
    draggable?: boolean
  }
  freeMode?: boolean
  loop?: boolean
  centeredSlides?: boolean
  speed?: number
  slidesPerGroup?: number
  fadeEffect?: {
    crossFade?: boolean
  }
  coverflowEffect?: {
    rotate?: number
    stretch?: number
    depth?: number
    modifier?: number
    slideShadows?: boolean
  }
  cardsEffect?: {
    perSlideOffset?: number
    perSlideRotate?: number
    rotate?: boolean
    slideShadows?: boolean
  }
  cubeEffect?: {
    shadow?: boolean
    slideShadows?: boolean
    shadowOffset?: number
    shadowScale?: number
  }
  flipEffect?: {
    slideShadows?: boolean
    limitRotation?: boolean
  }
  watchSlidesProgress?: boolean
  centerInsufficientSlides?: boolean
  breakpoints?: {
    [width: number]: Partial<SliderConfig>
  }
}

export const SLIDER_PRESETS: Record<string, SliderConfig> = {
  // Main movie row slider - horizontal scrolling
  movieRow: {
    slidesPerView: 'auto',
    spaceBetween: 16,
    freeMode: true,
    navigation: true,
    scrollbar: {
      hide: false,
      draggable: true,
    },
    breakpoints: {
      320: { 
        slidesPerView: 2,
        spaceBetween: 12,
        slidesPerGroup: 2
      },
      480: { 
        slidesPerView: 2.5,
        spaceBetween: 14,
        slidesPerGroup: 2
      },
      640: { 
        slidesPerView: 3,
        spaceBetween: 16,
        slidesPerGroup: 3
      },
      768: { 
        slidesPerView: 4,
        spaceBetween: 18,
        slidesPerGroup: 4
      },
      1024: { 
        slidesPerView: 5,
        spaceBetween: 20,
        slidesPerGroup: 5
      },
      1280: { 
        slidesPerView: 6,
        spaceBetween: 22,
        slidesPerGroup: 6
      },
      1440: { 
        slidesPerView: 7,
        spaceBetween: 24,
        slidesPerGroup: 7
      }
    }
  },

  // Hero banner slider - full screen with fade effect
  heroBanner: {
    effect: 'fade',
    fadeEffect: {
      crossFade: true
    },
    autoplay: {
      delay: 8000,
      disableOnInteraction: false,
      pauseOnMouseEnter: true
    },
    pagination: {
      clickable: true,
      dynamicBullets: true
    },
    navigation: true,
    loop: true,
    speed: 1000
  },

  // Popular movies with cover flow effect
  popular: {
    effect: 'coverflow',
    coverflowEffect: {
      rotate: 30,
      stretch: 0,
      depth: 100,
      modifier: 1,
      slideShadows: true
    },
    centeredSlides: true,
    slidesPerView: 3,
    loop: true,
    autoplay: {
      delay: 4000,
      disableOnInteraction: false
    },
    pagination: {
      clickable: true
    },
    breakpoints: {
      320: { 
        slidesPerView: 1,
        coverflowEffect: {
          rotate: 0,
          stretch: 0,
          depth: 0,
          modifier: 1
        }
      },
      640: { 
        slidesPerView: 2,
        coverflowEffect: {
          rotate: 20,
          stretch: 0,
          depth: 50,
          modifier: 1
        }
      },
      1024: { 
        slidesPerView: 3,
        coverflowEffect: {
          rotate: 30,
          stretch: 0,
          depth: 100,
          modifier: 1
        }
      }
    }
  },

  // Top rated movies with cards effect
  topRated: {
    effect: 'cards',
    cardsEffect: {
      perSlideOffset: 8,
      perSlideRotate: 2,
      rotate: true,
      slideShadows: true
    },
    navigation: true,
    autoplay: {
      delay: 5000,
      disableOnInteraction: false
    },
    breakpoints: {
      768: {
        effect: 'slide',
        slidesPerView: 2,
        spaceBetween: 20
      },
      1024: {
        effect: 'slide',
        slidesPerView: 3,
        spaceBetween: 24
      }
    }
  },

  // Cast and crew slider
  cast: {
    slidesPerView: 'auto',
    spaceBetween: 12,
    freeMode: true,
    navigation: true,
    scrollbar: {
      hide: false,
      draggable: true
    },
    breakpoints: {
      320: { 
        slidesPerView: 3,
        spaceBetween: 8
      },
      480: { 
        slidesPerView: 4,
        spaceBetween: 10
      },
      640: { 
        slidesPerView: 5,
        spaceBetween: 12
      },
      768: { 
        slidesPerView: 6,
        spaceBetween: 14
      },
      1024: { 
        slidesPerView: 8,
        spaceBetween: 16
      }
    }
  },

  // Screenshots/gallery slider
  gallery: {
    effect: 'cube',
    cubeEffect: {
      shadow: true,
      slideShadows: true,
      shadowOffset: 20,
      shadowScale: 0.94
    },
    pagination: {
      type: 'fraction',
      clickable: true
    },
    navigation: true,
    loop: true,
    autoplay: {
      delay: 3000,
      disableOnInteraction: false
    },
    breakpoints: {
      768: {
        effect: 'slide',
        slidesPerView: 2,
        spaceBetween: 20
      },
      1024: {
        effect: 'slide',
        slidesPerView: 3,
        spaceBetween: 24
      }
    }
  },

  // Related movies - simple slide
  related: {
    slidesPerView: 'auto',
    spaceBetween: 16,
    navigation: true,
    freeMode: true,
    breakpoints: {
      320: { 
        slidesPerView: 2,
        spaceBetween: 12
      },
      640: { 
        slidesPerView: 3,
        spaceBetween: 14
      },
      1024: { 
        slidesPerView: 4,
        spaceBetween: 16
      }
    }
  },

  // Recent movies with flip effect
  recent: {
    effect: 'flip',
    flipEffect: {
      slideShadows: true,
      limitRotation: true
    },
    navigation: true,
    pagination: {
      clickable: true
    },
    autoplay: {
      delay: 6000,
      disableOnInteraction: false
    },
    breakpoints: {
      768: {
        effect: 'slide',
        slidesPerView: 2,
        spaceBetween: 20
      },
      1024: {
        effect: 'slide',
        slidesPerView: 3,
        spaceBetween: 24
      }
    }
  },

  // Thumbnail navigation slider
  thumbs: {
    slidesPerView: 'auto',
    spaceBetween: 8,
    freeMode: true,
    watchSlidesProgress: true,
    centerInsufficientSlides: true,
    breakpoints: {
      320: { 
        slidesPerView: 3,
        spaceBetween: 6
      },
      640: { 
        slidesPerView: 5,
        spaceBetween: 8
      },
      1024: { 
        slidesPerView: 7,
        spaceBetween: 10
      }
    }
  }
}

// Animation variants for Framer Motion
export const SLIDER_ANIMATIONS = {
  slide: {
    initial: { opacity: 0, x: 50 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: -50 },
    transition: { duration: 0.3 }
  },
  fade: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    exit: { opacity: 0 },
    transition: { duration: 0.5 }
  },
  scale: {
    initial: { opacity: 0, scale: 0.8 },
    animate: { opacity: 1, scale: 1 },
    exit: { opacity: 0, scale: 0.8 },
    transition: { duration: 0.4 }
  }
}

// Responsive breakpoints for consistent use
export const RESPONSIVE_BREAKPOINTS = {
  xs: 320,
  sm: 480,
  md: 640,
  lg: 768,
  xl: 1024,
  '2xl': 1280,
  '3xl': 1440
} as const

// Touch/gesture settings
export const TOUCH_SETTINGS = {
  touchRatio: 1,
  touchAngle: 45,
  simulateTouch: true,
  allowTouchMove: true,
  touchMoveStopPropagation: false,
  touchStartPreventDefault: false,
  touchStartForcePreventDefault: false,
  touchReleaseOnEdges: false
}

// Accessibility settings
export const A11Y_SETTINGS = {
  prevSlideMessage: 'Previous slide',
  nextSlideMessage: 'Next slide',
  firstSlideMessage: 'This is the first slide',
  lastSlideMessage: 'This is the last slide',
  paginationBulletMessage: 'Go to slide {{index}}',
  containerMessage: 'Movie carousel',
  containerRoleDescriptionMessage: 'carousel',
  itemRoleDescriptionMessage: 'slide'
}

// Performance optimization settings
export const PERFORMANCE_SETTINGS = {
  lazy: {
    loadPrevNext: true,
    loadPrevNextAmount: 2,
    loadOnTransitionStart: false,
    elementClass: 'swiper-lazy',
    loadingClass: 'swiper-lazy-loading',
    loadedClass: 'swiper-lazy-loaded',
    preloaderClass: 'swiper-lazy-preloader'
  },
  preloadImages: false,
  updateOnImagesReady: true,
  watchSlidesProgress: true,
  watchSlidesVisibility: true
}
