document.addEventListener('DOMContentLoaded', () => {
    // Initialize PhotoSwipe
    const initPhotoSwipe = (gallerySelector) => {
        // Get all gallery elements
        const galleryElements = document.querySelectorAll(gallerySelector);
        
        if (!galleryElements.length) return;
        
        galleryElements.forEach(galleryElement => {
            // Initialize PhotoSwipe for each gallery
            const lightbox = new PhotoSwipeLightbox({
                gallery: galleryElement,
                children: 'a',
                pswpModule: PhotoSwipe,
                showHideAnimationType: 'fade',
                bgOpacity: 0.9,
                padding: { top: 40, bottom: 40, left: 100, right: 100 },
                preloadFirstSlide: true,
                // Add EXIF info to slide captions
                paddingFn: (viewportSize) => {
                    return {
                        top: 40,
                        bottom: 40,
                        left: viewportSize.x < 768 ? 20 : 100,
                        right: viewportSize.x < 768 ? 20 : 100
                    };
                },
                arrowPrevSVG: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M15 19L8 12L15 5" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
                arrowNextSVG: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M9 5L16 12L9 19" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
                closeSVG: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M18 6L6 18M6 6L18 18" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
            });
            
            // Add custom UI elements or behaviors
            lightbox.on('uiRegister', () => {
                // Add keyboard navigation
                lightbox.pswp.on('keydown', (e) => {
                    if (e.key === 'ArrowLeft') {
                        lightbox.pswp.prev();
                    } else if (e.key === 'ArrowRight') {
                        lightbox.pswp.next();
                    }
                });
                
                // Improve captions
                lightbox.pswp.on('contentLoad', (e) => {
                    const { content } = e;
                    const photoTitle = content.data.element.getAttribute('data-title');
                    const photoDescription = content.data.element.getAttribute('data-description');
                    
                    if (photoTitle || photoDescription) {
                        const captionElement = lightbox.pswp.currSlide.data.element.querySelector('.pswp__caption__center');
                        
                        if (captionElement) {
                            let captionHTML = '';
                            
                            if (photoTitle) {
                                captionHTML += `<h3 class="pswp__caption-title">${photoTitle}</h3>`;
                            }
                            
                            if (photoDescription) {
                                captionHTML += `<p class="pswp__caption-description">${photoDescription}</p>`;
                            }
                            
                            captionElement.innerHTML = captionHTML;
                        }
                    }
                });
            });
            
            // Initialize the lightbox
            lightbox.init();
        });
    };
    
    // Initialize PhotoSwipe for gallery
    initPhotoSwipe('.photo-grid');
    initPhotoSwipe('.photo-detail-container');
    
    // Category filtering with animation
    const initCategoryFilters = () => {
        const categoryLinks = document.querySelectorAll('.category-filter');
        
        if (!categoryLinks.length) return;
        
        categoryLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault(); // Prevent default link behavior
                
                if (this.classList.contains('active')) return;
                
                // Get the category slug from href
                const href = this.getAttribute('href');
                const categorySlug = href.includes('?category=') ? href.split('?category=')[1] : '';
                
                // Update active class
                categoryLinks.forEach(l => l.classList.remove('active'));
                this.classList.add('active');
                
                // Show loading indicator
                const galleryContent = document.getElementById('gallery-content');
                galleryContent.innerHTML = '<div class="flex justify-center py-12"><div class="loading-spinner"></div></div>';
                
                // Fetch filtered content
                fetch(`${href}&ajax=1`)
                    .then(response => response.text())
                    .then(html => {
                        // Replace the gallery content
                        galleryContent.innerHTML = html;
                        
                        // Add fade-in classes to new photos
                        const newPhotos = galleryContent.querySelectorAll('.photo-item');
                        newPhotos.forEach((photo, index) => {
                            photo.classList.add('fade-in-grid');
                            photo.style.setProperty('--delay', `${index * 0.1}s`);
                        });
                        
                        // Reinitialize PhotoSwipe for new content
                        initPhotoSwipe('.photo-grid');
                        
                        // Update URL without page reload
                        window.history.pushState({path: href}, '', href);
                        
                        // Add event listeners to pagination links
                        initPaginationLinks();
                    })
                    .catch(error => {
                        console.error('Error fetching filtered gallery:', error);
                        galleryContent.innerHTML = '<div class="text-center py-12"><p class="text-red-500">Error loading photos. Please try again.</p></div>';
                    });
            });
        });
        
        // Handle browser back/forward navigation
        window.addEventListener('popstate', function(e) {
            const currentUrl = window.location.href;
            const categoryInUrl = currentUrl.includes('?category=') ? 
                currentUrl.split('?category=')[1].split('&')[0] : null;
            
            // Find the matching category link and click it
            categoryLinks.forEach(link => {
                const href = link.getAttribute('href');
                const linkCategory = href.includes('?category=') ? 
                    href.split('?category=')[1].split('&')[0] : null;
                
                if ((categoryInUrl === null && linkCategory === null) || 
                    (categoryInUrl === linkCategory)) {
                    link.click();
                }
            });
        });
    };
    
    // Initialize pagination links to use AJAX
    const initPaginationLinks = () => {
        const paginationLinks = document.querySelectorAll('.pagination-link');
        
        paginationLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                
                const href = this.getAttribute('href');
                const galleryContent = document.getElementById('gallery-content');
                
                // Show loading indicator
                galleryContent.innerHTML = '<div class="flex justify-center py-12"><div class="loading-spinner"></div></div>';
                
                // Fetch page content
                fetch(`${href}&ajax=1`)
                    .then(response => response.text())
                    .then(html => {
                        // Replace the gallery content
                        galleryContent.innerHTML = html;
                        
                        // Smooth scroll to top of gallery
                        document.querySelector('.category-filters').scrollIntoView({ behavior: 'smooth' });
                        
                        // Add fade-in classes to new photos
                        const newPhotos = galleryContent.querySelectorAll('.photo-item');
                        newPhotos.forEach((photo, index) => {
                            photo.classList.add('fade-in-grid');
                            photo.style.setProperty('--delay', `${index * 0.1}s`);
                        });
                        
                        // Reinitialize PhotoSwipe for new content
                        initPhotoSwipe('.photo-grid');
                        
                        // Update URL without page reload
                        window.history.pushState({path: href}, '', href);
                        
                        // Reinitialize pagination links
                        initPaginationLinks();
                    })
                    .catch(error => {
                        console.error('Error fetching paginated gallery:', error);
                        galleryContent.innerHTML = '<div class="text-center py-12"><p class="text-red-500">Error loading photos. Please try again.</p></div>';
                    });
            });
        });
    };
    
    // Initialize progressive image loading
    const initProgressiveLoading = () => {
        const lazyImages = document.querySelectorAll('.lazy-load');
        
        if (!lazyImages.length) return;
        
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries) => {
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
            // Fallback for browsers without IntersectionObserver
            lazyImages.forEach(img => {
                img.classList.add('loaded');
            });
        }
    };
    
    // Initialize category filters
    initCategoryFilters();
    
    // Initialize pagination
    initPaginationLinks();
    
    // Initialize progressive loading
    initProgressiveLoading();
}); 