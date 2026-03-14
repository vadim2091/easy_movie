// Падающие мандарины
class MandarinParticles {
    constructor() {
        this.canvas = document.createElement('canvas');
        this.ctx = this.canvas.getContext('2d');
        this.particles = [];
        this.init();
    }

    init() {
        // Стили для канваса
        this.canvas.style.position = 'fixed';
        this.canvas.style.top = '0';
        this.canvas.style.left = '0';
        this.canvas.style.width = '100%';
        this.canvas.style.height = '100%';
        this.canvas.style.pointerEvents = 'none';
        this.canvas.style.zIndex = '9999';
        this.canvas.style.opacity = '0.3';
        
        document.body.appendChild(this.canvas);
        
        this.resize();
        this.createParticles();
        this.animate();
        
        window.addEventListener('resize', () => this.resize());
    }

    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    createParticles() {
        // Создаем 30 мандаринов
        for (let i = 0; i < 30; i++) {
            this.particles.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                size: Math.random() * 20 + 15, // 15-35px
                speed: Math.random() * 2 + 1,    // 1-3 скорость
                opacity: Math.random() * 0.5 + 0.2,
                rotation: Math.random() * 360,
                rotationSpeed: (Math.random() - 0.5) * 2
            });
        }
    }

    drawMandarin(x, y, size, opacity, rotation) {
        this.ctx.save();
        this.ctx.translate(x, y);
        this.ctx.rotate((rotation * Math.PI) / 180);
        this.ctx.globalAlpha = opacity;
        
        // Рисуем мандарин (круг)
        this.ctx.beginPath();
        this.ctx.arc(0, 0, size/2, 0, Math.PI * 2);
        
        // Градиент для мандарина
        const gradient = this.ctx.createRadialGradient(-size/4, -size/4, 0, 0, 0, size/2);
        gradient.addColorStop(0, '#ffb347');
        gradient.addColorStop(0.5, '#ff8c00');
        gradient.addColorStop(1, '#e67e22');
        
        this.ctx.fillStyle = gradient;
        this.ctx.fill();
        
        // Листик
        this.ctx.beginPath();
        this.ctx.moveTo(size/4, -size/3);
        this.ctx.quadraticCurveTo(size/2, -size/2, size/2, -size/4);
        this.ctx.fillStyle = '#27ae60';
        this.ctx.fill();
        
        this.ctx.restore();
    }

    animate() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        for (let p of this.particles) {
            // Движение вниз
            p.y += p.speed;
            p.rotation += p.rotationSpeed;
            
            // Если упал за экран - появляется сверху
            if (p.y > this.canvas.height + p.size) {
                p.y = -p.size;
                p.x = Math.random() * this.canvas.width;
            }
            
            this.drawMandarin(p.x, p.y, p.size, p.opacity, p.rotation);
        }
        
        requestAnimationFrame(() => this.animate());
    }
}

// Запускаем после загрузки страницы
document.addEventListener('DOMContentLoaded', () => {
    // Запускаем только на определенных страницах
    const path = window.location.pathname;
    if (path === '/' || path === '/tasks' || path === '/profile') {
        new MandarinParticles();
    }
});