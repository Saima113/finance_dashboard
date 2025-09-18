class StockAnalytics {
    constructor() {
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setupAutoRefresh();
        this.initializeComponents();
    }
    
    setupEventListeners() {
        // Global search functionality
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'k') {
                e.preventDefault();
                this.focusSearch();
            }
        });
        
        // Escape key handling
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.clearSearch();
            }
        });
    }
    
    setupAutoRefresh() {
        // Auto-refresh for pending analyses
        const pendingElements = document.querySelectorAll('.status-pending');
        if (pendingElements.length > 0) {
            setTimeout(() => {
                window.location.reload();
            }, 30000); // Refresh after 30 seconds
        }
    }
    
    initializeComponents() {
        // Initialize tooltips, animations, etc.
        this.animateCounters();
        this.setupProgressiveLoading();
    }
    
    focusSearch() {
        const searchInput = document.getElementById('companySearch') || 
                          document.getElementById('companyFilter');
        if (searchInput) {
            searchInput.focus();
            searchInput.select();
        }
    }
    
    clearSearch() {
        const searchInput = document.getElementById('companySearch') || 
                          document.getElementById('companyFilter');
        if (searchInput) {
            searchInput.value = '';
            searchInput.focus();
        }
    }
    
    animateCounters() {
        const counters = document.querySelectorAll('.stat-number');
        counters.forEach(counter => {
            const target = parseInt(counter.textContent);
            let current = 0;
            const increment = target / 50;
            
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    counter.textContent = target;
                    clearInterval(timer);
                } else {
                    counter.textContent = Math.floor(current);
                }
            }, 30);
        });
    }
    
    setupProgressiveLoading() {
        // Lazy loading for company cards
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        });
        
        document.querySelectorAll('.company-card, .feature-card').forEach(card => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(30px)';
            card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            observer.observe(card);
        });
    }
}

// Utility Functions
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check' : type === 'error' ? 'times' : 'info'}-circle"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

function formatPercentage(value) {
    return `${value.toFixed(1)}%`;
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    new StockAnalytics();
});
