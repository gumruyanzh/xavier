// Xavier Framework - Main JavaScript
document.addEventListener('DOMContentLoaded', function() {

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

    // Copy to clipboard functionality
    document.querySelectorAll('.copy-button').forEach(button => {
        button.addEventListener('click', async function() {
            const codeBlock = this.parentElement.querySelector('code');
            const text = codeBlock.textContent;

            try {
                await navigator.clipboard.writeText(text);
                const originalText = this.textContent;
                this.textContent = '✓ Copied!';
                this.style.background = '#10B981';

                setTimeout(() => {
                    this.textContent = originalText;
                    this.style.background = '';
                }, 2000);
            } catch (err) {
                console.error('Failed to copy text: ', err);
            }
        });
    });

    // Add copy buttons to all code blocks
    document.querySelectorAll('.code-block').forEach(block => {
        if (!block.querySelector('.copy-button')) {
            const button = document.createElement('button');
            button.className = 'copy-button';
            button.textContent = 'Copy';
            block.appendChild(button);
        }
    });

    // Animate feature cards on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe feature cards
    document.querySelectorAll('.feature-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(card);
    });

    // Observe command cards
    document.querySelectorAll('.command-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(card);
    });

    // Mobile menu toggle
    const mobileMenuButton = document.querySelector('.mobile-menu-toggle');
    const navLinks = document.querySelector('.nav-links');

    if (mobileMenuButton && navLinks) {
        mobileMenuButton.addEventListener('click', function(e) {
            e.stopPropagation();
            this.classList.toggle('active');
            navLinks.classList.toggle('mobile-active');
        });

        // Close mobile menu when clicking on a link
        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', function() {
                mobileMenuButton.classList.remove('active');
                navLinks.classList.remove('mobile-active');
            });
        });

        // Close mobile menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.nav-container')) {
                mobileMenuButton.classList.remove('active');
                navLinks.classList.remove('mobile-active');
            }
        });

        // Close mobile menu on window resize if desktop
        window.addEventListener('resize', function() {
            if (window.innerWidth > 768) {
                mobileMenuButton.classList.remove('active');
                navLinks.classList.remove('mobile-active');
            }
        });
    }

    // Add typing animation to hero title
    const heroTitle = document.querySelector('.hero h1');
    if (heroTitle && heroTitle.textContent.includes('Xavier')) {
        const originalText = heroTitle.textContent;
        heroTitle.textContent = '';
        let index = 0;

        function typeWriter() {
            if (index < originalText.length) {
                heroTitle.textContent += originalText.charAt(index);
                index++;
                setTimeout(typeWriter, 50);
            }
        }

        // Start typing animation after a short delay
        setTimeout(typeWriter, 500);
    }

    // Parallax effect for hero section
    const hero = document.querySelector('.hero');
    if (hero) {
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            const parallaxSpeed = 0.5;
            hero.style.transform = `translateY(${scrolled * parallaxSpeed}px)`;
        });
    }

    // Add interactive command preview
    const commandPreviews = document.querySelectorAll('.command-card');
    commandPreviews.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateX(10px)';
        });

        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateX(5px)';
        });
    });

    // Highlight active navigation item
    function highlightActiveNav() {
        const currentPath = window.location.pathname;
        const navItems = document.querySelectorAll('.nav-links a');

        navItems.forEach(item => {
            const href = item.getAttribute('href');
            if (currentPath.includes(href) && href !== 'index.html') {
                item.style.color = '#000';
                item.style.fontWeight = '600';
            } else if (currentPath.endsWith('/') && href === 'index.html') {
                item.style.color = '#000';
                item.style.fontWeight = '600';
            }
        });
    }

    highlightActiveNav();

    // Add loading animation for installation command
    const installBoxes = document.querySelectorAll('.install-box');
    installBoxes.forEach(box => {
        const codeBlock = box.querySelector('.code-block');
        if (codeBlock) {
            const button = codeBlock.querySelector('.copy-button');
            if (button) {
                button.addEventListener('click', function() {
                    // Simulate installation progress
                    const progressBar = document.createElement('div');
                    progressBar.style.cssText = `
                        height: 3px;
                        background: #000;
                        position: absolute;
                        bottom: 0;
                        left: 0;
                        width: 0%;
                        transition: width 2s ease;
                    `;
                    codeBlock.style.position = 'relative';
                    codeBlock.appendChild(progressBar);

                    setTimeout(() => {
                        progressBar.style.width = '100%';
                    }, 10);

                    setTimeout(() => {
                        progressBar.remove();
                    }, 2500);
                });
            }
        }
    });

    // Add stats counter animation
    const stats = [
        { element: null, target: 100, suffix: '%', label: 'Test Coverage' },
        { element: null, target: 20, suffix: ' lines', label: 'Max Function Size' },
        { element: null, target: 5, suffix: '+', label: 'Specialized Agents' }
    ];

    // Create stats if on index page
    if (window.location.pathname.endsWith('index.html') || window.location.pathname.endsWith('/')) {
        const featuresSection = document.querySelector('.features');
        if (featuresSection) {
            const statsContainer = document.createElement('div');
            statsContainer.style.cssText = `
                display: flex;
                justify-content: space-around;
                max-width: 800px;
                margin: 60px auto;
                padding: 40px;
                background: linear-gradient(135deg, #000 0%, #333 100%);
                border-radius: 16px;
                color: white;
            `;

            stats.forEach(stat => {
                const statElement = document.createElement('div');
                statElement.style.cssText = `
                    text-align: center;
                `;
                statElement.innerHTML = `
                    <div style="font-size: 36px; font-weight: bold;" data-target="${stat.target}" data-suffix="${stat.suffix}">0</div>
                    <div style="font-size: 14px; margin-top: 8px; opacity: 0.9;">${stat.label}</div>
                `;
                statsContainer.appendChild(statElement);
                stat.element = statElement.querySelector('[data-target]');
            });

            featuresSection.parentNode.insertBefore(statsContainer, featuresSection.nextSibling);

            // Animate stats when in view
            const statsObserver = new IntersectionObserver(function(entries) {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        stats.forEach(stat => {
                            if (stat.element) {
                                const target = parseInt(stat.element.dataset.target);
                                const suffix = stat.element.dataset.suffix;
                                let current = 0;
                                const increment = target / 50;

                                const timer = setInterval(() => {
                                    current += increment;
                                    if (current >= target) {
                                        current = target;
                                        clearInterval(timer);
                                    }
                                    stat.element.textContent = Math.floor(current) + suffix;
                                }, 30);
                            }
                        });
                        statsObserver.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.5 });

            statsObserver.observe(statsContainer);
        }
    }

    // Add terminal-like effect to code examples
    document.querySelectorAll('.code-example pre').forEach(pre => {
        pre.addEventListener('click', function() {
            this.style.background = '#0F172A';
            setTimeout(() => {
                this.style.background = '';
            }, 200);
        });
    });

    console.log('Xavier Framework initialized successfully');
});