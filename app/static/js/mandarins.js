// Падающие мандарины
class Mandarins {
    constructor() {
        this.canvas = document.createElement('canvas');
        this.ctx = this.canvas.getContext('2d');
        this.particles = [];
        this.init();
    }

    init() {
        this.canvas.style.position = 'fixed';
        this.canvas.style.top = '0';
        this.canvas.style.left = '0';
        this.canvas.style.width = '100%';
        this.canvas.style.height = '100%';
        this.canvas.style.pointerEvents = 'none';
        this.canvas.style.zIndex = '9999';
        this.canvas.style.opacity = '0.2';
        
        document.body.appendChild(this.canvas);
        
        this.resize();
        this.createParticles(30);
        this.animate();
        
        window.addEventListener('resize', () => this.resize());
    }

    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    createParticles(count) {
        for (let i = 0; i < count; i++) {
            this.particles.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                size: Math.random() * 20 + 15,
                speed: Math.random() * 1.5 + 0.5,
                rotation: Math.random() * 360,
                rotationSpeed: (Math.random() - 0.5) * 0.5
            });
        }
    }

    drawMandarin(x, y, size, rotation) {
        this.ctx.save();
        this.ctx.translate(x, y);
        this.ctx.rotate((rotation * Math.PI) / 180);
        
        // Градиент для мандарина
        const gradient = this.ctx.createRadialGradient(-size/3, -size/3, 0, 0, 0, size);
        gradient.addColorStop(0, '#fbbf24');
        gradient.addColorStop(0.5, '#f59e0b');
        gradient.addColorStop(1, '#d97706');
        
        this.ctx.beginPath();
        this.ctx.arc(0, 0, size/2, 0, Math.PI * 2);
        this.ctx.fillStyle = gradient;
        this.ctx.fill();
        
        // Листик
        this.ctx.beginPath();
        this.ctx.moveTo(size/3, -size/2);
        this.ctx.quadraticCurveTo(size/2, -size/1.5, size/1.5, -size/2);
        this.ctx.fillStyle = '#10b981';
        this.ctx.fill();
        
        this.ctx.restore();
    }

    animate() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        for (let p of this.particles) {
            p.y += p.speed;
            p.rotation += p.rotationSpeed;
            
            if (p.y > this.canvas.height + p.size) {
                p.y = -p.size;
                p.x = Math.random() * this.canvas.width;
            }
            
            this.drawMandarin(p.x, p.y, p.size, p.rotation);
        }
        
        requestAnimationFrame(() => this.animate());
    }
}

// Запускаем на всех страницах
document.addEventListener('DOMContentLoaded', () => {
    new Mandarins();
});