// Lussoux Hairs Modern JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('Lussoux Hairs app initialized');

    // Initialize AOS animations
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 800,
            easing: 'ease-in-out',
            once: true,
            offset: 100
        });
    }

    // Glass navigation scroll effect
    const navbar = document.querySelector('.glass-nav');
    let lastScrollTop = 0;

    window.addEventListener('scroll', function() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;

        if (scrollTop > 100) {
            navbar.style.background = 'rgba(255, 255, 255, 0.98)';
            navbar.style.boxShadow = '0 8px 32px rgba(0, 0, 0, 0.15)';
        } else {
            navbar.style.background = 'rgba(255, 255, 255, 0.95)';
            navbar.style.boxShadow = '0 8px 32px rgba(0, 0, 0, 0.1)';
        }

        lastScrollTop = scrollTop;
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Enhanced button interactions
    document.querySelectorAll('.btn-primary-modern, .category-btn, .product-btn, .view-all-btn').forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px) scale(1.02)';
        });

        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });

        button.addEventListener('click', function() {
            // Add ripple effect
            const ripple = document.createElement('span');
            ripple.classList.add('ripple');
            this.appendChild(ripple);

            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });

    // Search input enhancements
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        searchInput.addEventListener('focus', function() {
            this.parentElement.style.transform = 'scale(1.02)';
        });

        searchInput.addEventListener('blur', function() {
            this.parentElement.style.transform = 'scale(1)';
        });
    }

    // Product card hover effects
    document.querySelectorAll('.product-card-modern').forEach(card => {
        card.addEventListener('mouseenter', function() {
            const overlay = this.querySelector('.product-overlay');
            if (overlay) {
                overlay.style.opacity = '1';
            }
        });

        card.addEventListener('mouseleave', function() {
            const overlay = this.querySelector('.product-overlay');
            if (overlay) {
                overlay.style.opacity = '0';
            }
        });

    // Currency conversion
    const currencySelect = document.getElementById('currency-select');
    const convertedAmount = document.querySelector('.converted-amount');

    const rates = {
        USD: 1,
        NGN: 1550,
        GBP: 0.79
    };

    if (currencySelect) {
        currencySelect.addEventListener('change', function() {
            const originalAmount = parseFloat(document.querySelector('.cart-total').textContent.replace('$', ''));
            const targetCurrency = this.value;
            const convertedValue = originalAmount * rates[targetCurrency];

            const formatter = new Intl.NumberFormat(undefined, {
                style: 'currency',
                currency: targetCurrency
            });

            convertedAmount.textContent = `Converted: ${formatter.format(convertedValue)}`;
        });
    }
    });

    // Category card interactions
    document.querySelectorAll('.category-card-modern').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px) scale(1.02)';
        });

        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });

    // Newsletter form enhancement
    const newsletterForm = document.querySelector('.newsletter-form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const button = this.querySelector('button');
            const input = this.querySelector('input');

            if (input.value.trim()) {
                button.innerHTML = '<i class="fas fa-check"></i>';
                button.style.background = '#48bb78';

                setTimeout(() => {
                    button.innerHTML = '<i class="fas fa-arrow-right"></i>';
                    button.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
                    input.value = '';
                }, 2000);
            }
        });
    }

    // Parallax effect for hero section
    window.addEventListener('scroll', function() {
        const scrolled = window.pageYOffset;
        const heroImages = document.querySelectorAll('.hero-image-1, .hero-image-2');

        heroImages.forEach((img, index) => {
            const speed = 0.5 + (index * 0.2);
            img.style.transform = `translateY(${scrolled * speed}px)`;
        });
    });

    // Add loading states with better UX
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"], input[type="submit"]');
            if (submitBtn) {
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
                submitBtn.disabled = true;

                // Re-enable after 3 seconds if not redirected
                setTimeout(() => {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }, 3000);
            }
        });
    });

    // Add CSS for ripple effect
    const style = document.createElement('style');
    style.textContent = `
        .ripple {
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.6);
            transform: scale(0);
            animation: ripple 0.6s linear;
            pointer-events: none;
        }

        @keyframes ripple {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
});