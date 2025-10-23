/* filepath: Python_Testing/static/js/app.js */
document.addEventListener('DOMContentLoaded', function() {
    // Effet parallax pour le header
    window.addEventListener('scroll', function() {
        const scrolled = window.pageYOffset;
        const header = document.querySelector('.header');
        if (header) {
            header.style.transform = `translateY(${scrolled * 0.1}px)`;
        }
    });

    // Animation de compteur pour les points
    function animateCounter(element, start, end, duration) {
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            const value = Math.floor(progress * (end - start) + start);
            element.textContent = value;
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        };
        window.requestAnimationFrame(step);
    }

    // Lancer l'animation des compteurs
    const pointsNumbers = document.querySelectorAll('.points-number');
    pointsNumbers.forEach(element => {
        const finalValue = parseInt(element.textContent);
        element.textContent = '0';
        setTimeout(() => {
            animateCounter(element, 0, finalValue, 2000);
        }, 500);
    });

    // Effet de typing pour les titres
    function typeWriter(element, text, speed = 100) {
        let i = 0;
        element.innerHTML = '';
        function type() {
            if (i < text.length) {
                element.innerHTML += text.charAt(i);
                i++;
                setTimeout(type, speed);
            }
        }
        type();
    }

    // Calculateur de coût en temps réel amélioré
    window.calculateCost = function() {
        const placesInput = document.getElementById('places');
        const places = parseInt(placesInput.value) || 0;
        const clubPoints = parseInt(document.querySelector('[data-club-points]')?.dataset.clubPoints) || 0;
        const costPreview = document.getElementById('costPreview');
        
        if (places > 0) {
            const totalCost = places * 3;
            const remaining = clubPoints - totalCost;
            
            // Mise à jour avec animations
            updateWithAnimation('selectedPlaces', places);
            updateWithAnimation('totalCost', totalCost);
            updateWithAnimation('remainingPoints', remaining);
            
            costPreview.style.display = 'block';
            costPreview.classList.add('fade-in');
            
            // Couleur dynamique
            const remainingElement = document.getElementById('remainingPoints');
            remainingElement.style.color = remaining < 0 ? '#dc3545' : '#28a745';
            
            // Effet de shake si pas assez de points
            if (remaining < 0) {
                placesInput.classList.add('shake');
                setTimeout(() => placesInput.classList.remove('shake'), 500);
            }
        } else {
            costPreview.style.display = 'none';
        }
    };

    function updateWithAnimation(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.style.transform = 'scale(1.1)';
            element.textContent = value;
            setTimeout(() => {
                element.style.transform = 'scale(1)';
            }, 200);
        }
    }

    // Effet de particules flottantes
    function createFloatingParticles() {
        const container = document.body;
        for (let i = 0; i < 50; i++) {
            const particle = document.createElement('div');
            particle.className = 'floating-particle';
            particle.style.cssText = `
                position: fixed;
                width: ${Math.random() * 4 + 1}px;
                height: ${Math.random() * 4 + 1}px;
                background: rgba(255, 255, 255, ${Math.random() * 0.3 + 0.1});
                border-radius: 50%;
                left: ${Math.random() * 100}vw;
                top: ${Math.random() * 100}vh;
                pointer-events: none;
                z-index: -1;
                animation: floatParticle ${Math.random() * 20 + 10}s linear infinite;
            `;
            container.appendChild(particle);
        }
    }

    // Ajouter les styles pour les particules
    const style = document.createElement('style');
    style.textContent = `
        @keyframes floatParticle {
            0% { transform: translateY(100vh) rotate(0deg); opacity: 0; }
            10% { opacity: 1; }
            90% { opacity: 1; }
            100% { transform: translateY(-100vh) rotate(360deg); opacity: 0; }
        }
        
        .shake {
            animation: shake 0.5s cubic-bezier(0.36, 0.07, 0.19, 0.97);
        }
        
        @keyframes shake {
            10%, 90% { transform: translate3d(-1px, 0, 0); }
            20%, 80% { transform: translate3d(2px, 0, 0); }
            30%, 50%, 70% { transform: translate3d(-4px, 0, 0); }
            40%, 60% { transform: translate3d(4px, 0, 0); }
        }
    `;
    document.head.appendChild(style);

    // Lancer les particules
    createFloatingParticles();

    // Smooth scroll pour les liens
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

    // Intersection Observer pour les animations d'apparition
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);

    // Observer tous les éléments avec la classe animate-on-scroll
    document.querySelectorAll('.card, .competition-item, .points-display').forEach(el => {
        el.classList.add('animate-on-scroll');
        observer.observe(el);
    });
});