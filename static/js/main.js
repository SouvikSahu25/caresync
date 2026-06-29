// CareSync General Client-Side Interactivity

document.addEventListener('DOMContentLoaded', function() {
    // Automatically close alert messages after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            // Apply fade out effect
            alert.style.transition = 'opacity 0.5s ease-out, transform 0.5s ease-out';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            
            // Remove from DOM after transition completes
            setTimeout(function() {
                alert.remove();
            }, 500);
        }, 5000);
    });
});
