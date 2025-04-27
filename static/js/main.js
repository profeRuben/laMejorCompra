document.addEventListener('DOMContentLoaded', function() {
  // Add to cart quantity increment/decrement
  const quantityInputs = document.querySelectorAll('.quantity-input');
  
  quantityInputs.forEach(input => {
    const decBtn = input.parentElement.querySelector('.quantity-dec');
    const incBtn = input.parentElement.querySelector('.quantity-inc');
    
    if (decBtn) {
      decBtn.addEventListener('click', () => {
        const currentValue = parseInt(input.value);
        if (currentValue > 1) {
          input.value = currentValue - 1;
        }
      });
    }
    
    if (incBtn) {
      incBtn.addEventListener('click', () => {
        const currentValue = parseInt(input.value);
        input.value = currentValue + 1;
      });
    }
  });
  
  // Payment method toggling
  const paymentMethodSelect = document.getElementById('payment_method');
  const creditCardFields = document.getElementById('credit-card-fields');
  
  if (paymentMethodSelect && creditCardFields) {
    paymentMethodSelect.addEventListener('change', function() {
      if (this.value === 'credit_card') {
        creditCardFields.classList.remove('d-none');
      } else {
        creditCardFields.classList.add('d-none');
      }
    });
    
    // Initial state
    if (paymentMethodSelect.value === 'credit_card') {
      creditCardFields.classList.remove('d-none');
    } else {
      creditCardFields.classList.add('d-none');
    }
  }
  
  // Auto-dismiss flash messages
  const flashMessages = document.querySelectorAll('.alert-dismissible');
  
  flashMessages.forEach(message => {
    setTimeout(() => {
      const closeButton = message.querySelector('.btn-close');
      if (closeButton) {
        closeButton.click();
      }
    }, 5000);
  });
  
  // Desactivamos el efecto de zoom en imágenes
  // No más efectos de hover o animaciones en las imágenes
  document.addEventListener('mouseover', function(e) {
    // Cancelar cualquier animación o transformación en elementos
    e.target.style.transform = 'none';
    e.target.style.transition = 'none';
  }, true);
});
