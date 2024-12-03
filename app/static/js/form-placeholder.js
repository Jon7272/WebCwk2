document.addEventListener('DOMContentLoaded', () => {
    const inputs = document.querySelectorAll('input, textarea');

    inputs.forEach(input => {
        // Clear placeholder when input is focused
        input.addEventListener('focus', function() {
            if (this.placeholder === this.getAttribute('placeholder')) {
                this.placeholder = '';
            }
        });

        // Restore placeholder if input is empty when it loses focus
        input.addEventListener('blur', function() {
            if (this.value === '') {
                this.placeholder = this.getAttribute('placeholder');
            }
        });
    });
});
