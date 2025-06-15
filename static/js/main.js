// static/js/main.js

document.addEventListener('DOMContentLoaded', () => {
    // Flash message timeout (auto-hide)
    const flash = document.querySelector('.flash-message');
    if (flash) {
        setTimeout(() => {
            flash.style.display = 'none';
        }, 3000);
    }

    // Confirm submission (optional)
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            const confirmed = confirm("Are you sure you want to submit this form?");
            if (!confirmed) {
                e.preventDefault();
            }
        });
    });
});
