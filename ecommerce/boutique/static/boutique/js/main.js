document.addEventListener('DOMContentLoaded', function() {
    // Gestion des messages
    setTimeout(() => {
        document.querySelectorAll('.alert').forEach(alert => {
            new bootstrap.Alert(alert).close();
        });
    }, 5000);

    // Système de notation
    document.querySelectorAll('.rating-stars i').forEach(star => {
        star.addEventListener('click', function() {
            const stars = this.parentElement.children;
            const rating = parseInt(this.dataset.value);
            
            Array.from(stars).forEach((s, index) => {
                s.classList.toggle('text-warning', index < rating);
            });
            
            document.querySelector('#id_note').value = rating;
        });
    });
});