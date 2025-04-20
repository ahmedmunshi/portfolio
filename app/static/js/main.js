document.addEventListener('DOMContentLoaded', () => {
    // Mobile menu toggle
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
        });
    }
    
    // Header scroll effects
    const header = document.getElementById('site-header');
    let lastScrollPosition = 0;
    
    const handleHeaderOnScroll = () => {
        const currentScrollPosition = window.pageYOffset;
        
        // Add/remove scrolled class for background
        if (currentScrollPosition > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
        
        // Show/hide header on scroll direction
        if (currentScrollPosition > lastScrollPosition && currentScrollPosition > 200) {
            // Scrolling down - hide header
            header.classList.add('hidden');
        } else {
            // Scrolling up - show header
            header.classList.remove('hidden');
        }
        
        lastScrollPosition = currentScrollPosition;
    };
    
    // Add scroll event listener
    window.addEventListener('scroll', handleHeaderOnScroll);
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]:not([href="#"])').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80, // Adjust for header height
                    behavior: 'smooth'
                });
                
                // Close mobile menu if open
                if (mobileMenu) {
                    mobileMenu.classList.add('hidden');
                }
            }
        });
    });
    
    // Lazy loading for images
    const lazyLoadImages = () => {
        const lazyImages = document.querySelectorAll('img.lazy-load');
        
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.classList.add('loaded');
                        imageObserver.unobserve(img);
                    }
                });
            });
            
            lazyImages.forEach(img => {
                imageObserver.observe(img);
            });
        } else {
            // Fallback for browsers that don't support IntersectionObserver
            lazyImages.forEach(img => {
                img.classList.add('loaded');
            });
        }
    };
    
    // Initialize lazy loading
    lazyLoadImages();
    
    // Page transitions
    const initPageTransitions = () => {
        // Add page transition element if it doesn't exist
        if (!document.querySelector('.page-transition')) {
            const pageTransition = document.createElement('div');
            pageTransition.className = 'page-transition';
            document.body.appendChild(pageTransition);
        }
        
        // Handle all internal links for page transitions
        document.querySelectorAll('a').forEach(link => {
            // Skip links that are anchors, external, or have special behaviors
            if (link.getAttribute('href').startsWith('#') || 
                link.getAttribute('href').startsWith('http') ||
                link.getAttribute('target') === '_blank' ||
                link.getAttribute('href') === '' ||
                link.hasAttribute('download') ||
                link.getAttribute('href').includes('mailto:') ||
                link.getAttribute('href').includes('tel:')) {
                return;
            }
            
            link.addEventListener('click', e => {
                e.preventDefault();
                const destination = link.getAttribute('href');
                
                // Animate page transition
                const pageTransition = document.querySelector('.page-transition');
                pageTransition.classList.add('active');
                
                // Navigate to the new page after animation completes
                setTimeout(() => {
                    window.location.href = destination;
                }, 600);
            });
        });
    };
    
    // Initialize page transitions
    // initPageTransitions(); // Uncomment to enable page transitions
    
    // Add current year to footer copyright
    const footerYear = document.querySelector('.footer-year');
    if (footerYear) {
        footerYear.textContent = new Date().getFullYear();
    }
}); 