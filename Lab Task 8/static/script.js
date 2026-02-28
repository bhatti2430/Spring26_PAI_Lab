/* ============================================================
   NASA APOD - JavaScript Functionality
   ============================================================ */

/* ============================================================
   DOM Elements & State
   ============================================================ */
const themeToggle = document.getElementById('themeToggle');
const datePicker = document.getElementById('datePicker');
const searchBtn = document.getElementById('searchBtn');
const loadingSpinner = document.getElementById('loadingSpinner');
const shareBtn = document.getElementById('shareBtn');
const downloadBtn = document.getElementById('downloadBtn');

// State
let isDarkMode = localStorage.getItem('darkMode') === 'true';

/* ============================================================
   Initialize Application
   ============================================================ */
function initializeApp() {
    // Apply saved theme
    applyTheme();
    
    // Set date picker to today
    setDatePickerDefault();
    
    // Event listeners
    setupEventListeners();
}

/* ============================================================
   Theme Toggle Functionality
   ============================================================ */
function applyTheme() {
    const body = document.body;
    
    if (isDarkMode) {
        body.classList.add('dark-mode');
        updateThemeIcon();
    } else {
        body.classList.remove('dark-mode');
        updateThemeIcon();
    }
}

function updateThemeIcon() {
    const icon = themeToggle.querySelector('i');
    if (isDarkMode) {
        icon.classList.remove('fa-moon');
        icon.classList.add('fa-sun');
    } else {
        icon.classList.remove('fa-sun');
        icon.classList.add('fa-moon');
    }
}

function toggleTheme() {
    isDarkMode = !isDarkMode;
    localStorage.setItem('darkMode', isDarkMode);
    applyTheme();
    
    // Add smooth transition animation
    document.body.style.opacity = '0.95';
    setTimeout(() => {
        document.body.style.opacity = '1';
    }, 50);
}

/* ============================================================
   Date Picker Initialization
   ============================================================ */
function setDatePickerDefault() {
    const today = new Date();
    const dateString = today.toISOString().split('T')[0];
    datePicker.value = dateString;
    datePicker.max = dateString;
    
    // Set minimum date (NASA APOD started from 1995-06-16)
    datePicker.min = '1995-06-16';
}

/* ============================================================
   Search & Navigation Functionality
   ============================================================ */
function handleSearch() {
    const selectedDate = datePicker.value;
    
    if (!selectedDate) {
        showNotification('Please select a date', 'warning');
        return;
    }
    
    // Navigate to the date
    navigateToDate(selectedDate);
}

function navigateToDate(date) {
    // Show loading spinner
    showLoadingSpinner(true);
    
    // Navigate to the URL
    window.location.href = `/${date}`;
}

function showLoadingSpinner(show) {
    if (show) {
        loadingSpinner.classList.add('active');
    } else {
        loadingSpinner.classList.remove('active');
    }
}

/* ============================================================
   Share Functionality
   ============================================================ */
function shareContent() {
    const title = document.querySelector('.content-title')?.textContent || 'NASA APOD';
    const url = window.location.href;
    
    // Check if Web Share API is available
    if (navigator.share) {
        navigator.share({
            title: title,
            text: 'Check out this amazing astronomy picture from NASA!',
            url: url
        }).catch(err => {
            if (err.name !== 'AbortError') {
                console.error('Error sharing:', err);
            }
        });
    } else {
        // Fallback: Copy to clipboard
        copyToClipboard(url);
    }
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Link copied to clipboard!', 'success');
    }).catch(() => {
        showNotification('Failed to copy link', 'error');
    });
}

/* ============================================================
   Download Functionality
   ============================================================ */
function downloadImage() {
    const imageElement = document.querySelector('.media-image');
    
    if (!imageElement) {
        showNotification('No image to download', 'warning');
        return;
    }
    
    const imageUrl = imageElement.src;
    const title = document.querySelector('.content-title')?.textContent || 'NASA_APOD';
    
    // Create a temporary download link
    const downloadLink = document.createElement('a');
    downloadLink.href = imageUrl;
    downloadLink.download = `${sanitizeFilename(title)}.jpg`;
    
    // Trigger download
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
    
    showNotification('Image download started!', 'success');
}

function sanitizeFilename(filename) {
    return filename
        .replace(/[^a-z0-9]/gi, '_')
        .replace(/_+/g, '_')
        .toLowerCase()
        .substring(0, 50);
}

/* ============================================================
   Notification System
   ============================================================ */
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        font-weight: 500;
        z-index: 10000;
        animation: slideIn 0.3s ease;
        max-width: 400px;
    `;
    
    // Color based on type
    const colors = {
        success: '#10b981',
        warning: '#f59e0b',
        error: '#ef4444',
        info: '#0b3d91'
    };
    
    const bgColors = {
        success: '#d1fae5',
        warning: '#fef3c7',
        error: '#fee2e2',
        info: '#e0f2fe'
    };
    
    notification.style.background = bgColors[type] || bgColors.info;
    notification.style.color = colors[type] || colors.info;
    notification.style.border = `2px solid ${colors[type] || colors.info}`;
    
    // Add to document
    document.body.appendChild(notification);
    
    // Remove after 4 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 4000);
}

/* ============================================================
   Keyboard Shortcuts
   ============================================================ */
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + D: Toggle dark mode
    if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
        e.preventDefault();
        toggleTheme();
    }
    
    // Ctrl/Cmd + K: Focus on date picker
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        datePicker.focus();
    }
    
    // Enter: Search for selected date
    if (e.key === 'Enter' && document.activeElement === datePicker) {
        handleSearch();
    }
});

/* ============================================================
   Accessibility Enhancements
   ============================================================ */
function enhanceAccessibility() {
    // Add skip to main link
    const skipLink = document.createElement('a');
    skipLink.href = '#main';
    skipLink.textContent = 'Skip to main content';
    skipLink.style.cssText = `
        position: absolute;
        left: -9999px;
        z-index: 999;
    `;
    skipLink.addEventListener('focus', function() {
        this.style.left = '0';
    });
    skipLink.addEventListener('blur', function() {
        this.style.left = '-9999px';
    });
    document.body.insertBefore(skipLink, document.body.firstChild);
    
    // Add ARIA labels where needed
    if (themeToggle) {
        themeToggle.setAttribute('aria-label', 'Toggle dark mode');
    }
    
    if (searchBtn) {
        searchBtn.setAttribute('aria-label', 'Search for APOD by date');
    }
    
    if (shareBtn) {
        shareBtn.setAttribute('aria-label', 'Share this image');
    }
    
    if (downloadBtn) {
        downloadBtn.setAttribute('aria-label', 'Download this image');
    }
}

/* ============================================================
   Event Listeners Setup
   ============================================================ */
function setupEventListeners() {
    // Theme toggle
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
    
    // Search functionality
    if (searchBtn) {
        searchBtn.addEventListener('click', handleSearch);
    }
    
    // Date picker enter key
    if (datePicker) {
        datePicker.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                handleSearch();
            }
        });
    }
    
    // Share button
    if (shareBtn) {
        shareBtn.addEventListener('click', shareContent);
    }
    
    // Download button
    if (downloadBtn) {
        downloadBtn.addEventListener('click', downloadImage);
    }
    
    // Enhance accessibility
    enhanceAccessibility();
}

/* ============================================================
   Smooth Scroll Animation
   ============================================================ */
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

/* ============================================================
   Animations - Add CSS Animations to Document
   ============================================================ */
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
    
    @media (max-width: 768px) {
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
    }
`;
document.head.appendChild(style);

/* ============================================================
   Lazy Loading & Performance
   ============================================================ */
function setupLazyLoading() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                        observer.unobserve(img);
                    }
                }
            });
        });
        
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
}

/* ============================================================
   Window Load Event
   ============================================================ */
window.addEventListener('load', () => {
    setupLazyLoading();
    showLoadingSpinner(false);
});

/* ============================================================
   Initialize on DOM Ready
   ============================================================ */
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}

/* ============================================================
   Prevent Default Form Submission
   ============================================================ */
document.addEventListener('submit', (e) => {
    if (e.target.classList.contains('api-form')) {
        e.preventDefault();
        handleSearch();
    }
});

/* ============================================================
   Performance: Monitor API Response Time
   ============================================================ */
window.addEventListener('load', () => {
    const perfData = window.performance.timing;
    const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
    console.log('Page load time:', pageLoadTime, 'ms');
});

/* ============================================================
   Request Idle Callback for Non-Critical Tasks
   ============================================================ */
if ('requestIdleCallback' in window) {
    requestIdleCallback(() => {
        // Preload next common dates
        console.log('Idle callback: Ready for non-critical tasks');
    });
}
