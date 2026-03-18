// Main JavaScript file for Brewly

document.addEventListener('DOMContentLoaded', function() {
    // --- Navbar scroll effect ---
    const navbar = document.getElementById('mainNavbar');
    if (navbar) {
        const handleScroll = function() {
            if (window.scrollY > 30) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        };
        window.addEventListener('scroll', handleScroll, { passive: true });
        handleScroll(); // Check initial state
    }

    // --- Navbar toggler animation ---
    const toggler = document.querySelector('.cs-toggler');
    if (toggler) {
        const navCollapse = document.getElementById('navbarNav');
        if (navCollapse) {
            navCollapse.addEventListener('show.bs.collapse', function() {
                toggler.setAttribute('aria-expanded', 'true');
            });
            navCollapse.addEventListener('hide.bs.collapse', function() {
                toggler.setAttribute('aria-expanded', 'false');
            });
        }
    }

    // --- Close mobile menu on link click ---
    const navLinks = document.querySelectorAll('.cs-nav-link, .cs-dropdown-item, .cs-btn-login, .cs-btn-register');
    const navCollapse = document.getElementById('navbarNav');
    if (navCollapse) {
        navLinks.forEach(function(link) {
            link.addEventListener('click', function() {
                if (window.innerWidth < 992) {
                    const collapse = bootstrap.Collapse.getInstance(navCollapse);
                    if (collapse) collapse.hide();
                }
            });
        });
    }

    // Auto-hide flash messages after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Confirm delete actions
    const deleteForms = document.querySelectorAll('form[onsubmit*="confirm"]');
    deleteForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            if (!confirm('Bạn có chắc chắn muốn thực hiện hành động này?')) {
                e.preventDefault();
            }
        });
    });
    
    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
    
    // Cart quantity validation
    const quantityInputs = document.querySelectorAll('input[name="quantity"]');
    quantityInputs.forEach(function(input) {
        input.addEventListener('change', function() {
            const max = parseInt(this.getAttribute('max'));
            const value = parseInt(this.value);
            if (value > max) {
                this.value = max;
                alert('Số lượng không được vượt quá tồn kho.');
            }
            if (value < 1) {
                this.value = 1;
            }
        });
    });
});

// Format currency helper
function formatCurrency(amount) {
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND'
    }).format(amount);
}
