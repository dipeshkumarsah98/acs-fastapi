const passwordCriteria = {
    length: {
        min: 12,
        recommended: 14,
        max: 16,
        check: (password) => password.length >= 12 && password.length <= 16
    },
    uppercase: {
        check: (password) => /[A-Z]/.test(password)
    },
    lowercase: {
        check: (password) => /[a-z]/.test(password)
    },
    number: {
        check: (password) => /[0-9]/.test(password)
    },
    symbol: {
        check: (password) => /[!@#$%^&*(),.?":{}|<>]/.test(password)
    },
    sequential: {
        check: (password) => !/(?:123|234|345|456|567|678|789|012|abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)/i.test(password)
    },
    repetitive: {
        check: (password) => !/(.)\1{2,}/.test(password)
    }
};

function containsPersonalInfo(password, email, username) {
    if (!email && !username) return false;
    
    const emailParts = email ? email.split('@')[0].toLowerCase() : '';
    const usernameLower = username ? username.toLowerCase() : '';
    const passwordLower = password.toLowerCase();
    
    return passwordLower.includes(emailParts) || passwordLower.includes(usernameLower);
}

function areAllCriteriaMet(password, email = '', username = '') {
    return Object.values(passwordCriteria).every(criteria => criteria.check(password)) &&
           !containsPersonalInfo(password, email, username);
}

function updatePasswordCriteria(password, email = '', username = '') {
    const criteriaList = document.getElementById('password-criteria');
    if (!criteriaList) return;

    const lengthItem = criteriaList.querySelector('[data-criteria="length"]');
    if (lengthItem) {
        const lengthCheck = passwordCriteria.length.check(password);
        const lengthIcon = lengthItem.querySelector('.criteria-icon');
        const lengthText = lengthItem.querySelector('.criteria-text');
        
        if (lengthCheck) {
            lengthIcon.innerHTML = '<svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>';
            lengthText.classList.remove('text-red-500');
            lengthText.classList.add('text-green-500');
        } else {
            lengthIcon.innerHTML = '<svg class="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>';
            lengthText.classList.remove('text-green-500');
            lengthText.classList.add('text-red-500');
        }
    }

    // Update other criteria
    ['uppercase', 'lowercase', 'number', 'symbol', 'sequential', 'repetitive'].forEach(criteria => {
        const item = criteriaList.querySelector(`[data-criteria="${criteria}"]`);
        if (item) {
            const icon = item.querySelector('.criteria-icon');
            const text = item.querySelector('.criteria-text');
            const check = passwordCriteria[criteria].check(password);
            
            if (check) {
                icon.innerHTML = '<svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>';
                text.classList.remove('text-red-500');
                text.classList.add('text-green-500');
            } else {
                icon.innerHTML = '<svg class="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>';
                text.classList.remove('text-green-500');
                text.classList.add('text-red-500');
            }
        }
    });

    const personalInfoItem = criteriaList.querySelector('[data-criteria="personal-info"]');
    if (personalInfoItem) {
        const icon = personalInfoItem.querySelector('.criteria-icon');
        const text = personalInfoItem.querySelector('.criteria-text');
        const hasPersonalInfo = containsPersonalInfo(password, email, username);
        
        if (!hasPersonalInfo) {
            icon.innerHTML = '<svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>';
            text.classList.remove('text-red-500');
            text.classList.add('text-green-500');
        } else {
            icon.innerHTML = '<svg class="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>';
            text.classList.remove('text-green-500');
            text.classList.add('text-red-500');
        }
    }

    updateSubmitButtonState();
}

function togglePasswordVisibility(inputId, toggleId) {
    const passwordInput = document.getElementById(inputId);
    const toggleButton = document.getElementById(toggleId);
    
    if (passwordInput && toggleButton) {
        toggleButton.addEventListener('click', () => {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            
            // Update icon
            toggleButton.innerHTML = type === 'password' 
                ? '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>'
                : '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/></svg>';
        });
    }
}

function doPasswordsMatch() {
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm_password').value;
    return password === confirmPassword && password !== '';
}

function updateSubmitButtonState() {
    const submitButton = document.querySelector('button[type="submit"]');
    const password = document.getElementById('password').value;
    
    const allCriteriaMet = areAllCriteriaMet(password);
    const passwordsMatch = doPasswordsMatch();
    
    if (submitButton) {
        submitButton.disabled = !(allCriteriaMet && passwordsMatch);
        submitButton.classList.toggle('opacity-50', !(allCriteriaMet && passwordsMatch));
        submitButton.classList.toggle('cursor-not-allowed', !(allCriteriaMet && passwordsMatch));
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm_password');
    const form = document.querySelector('form');

    togglePasswordVisibility('password', 'toggle-password');
    togglePasswordVisibility('confirm_password', 'toggle-confirm-password');

    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            updatePasswordCriteria(this.value);
        });
    }

    if (confirmPasswordInput && passwordInput) {
        confirmPasswordInput.addEventListener('input', function() {
            const match = this.value === passwordInput.value;
            const confirmText = document.getElementById('confirm-password-match');
            if (confirmText) {
                confirmText.textContent = match ? 'Passwords match' : 'Passwords do not match';
                confirmText.className = match ? 'text-green-500' : 'text-red-500';
            }
            updateSubmitButtonState();
        });
    }

    updateSubmitButtonState();
}); 