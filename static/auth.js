// Check if current page is an auth page
function isAuthPage() {
    const path = window.location.pathname;
    return path === '/login' || path === '/register';
}

// Check authentication status and handle redirects
async function checkAuthStatus() {
    const token = localStorage.getItem('access_token');
    const user = JSON.parse(localStorage.getItem('user'));

    if (token && user) {
        if (isAuthPage()) {
            // If on auth page and authenticated, redirect to home
            window.location.href = '/';
            return;
        }
    } else {
        // If not authenticated and trying to access protected pages
        if (!isAuthPage() && window.location.pathname !== '/') {
            // Check if the current page requires authentication
            try {
                const response = await fetch('/api/me', {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                
                if (!response.ok) {
                    // If not authenticated, redirect to login
                    window.location.href = '/login';
                }
            } catch (error) {
                window.location.href = '/login';
            }
        }
    }
}

function updateAuthButtons() {
    const user = JSON.parse(localStorage.getItem('user'));
    const authButtons = document.getElementById('auth-buttons');
    const mobileAuthButtons = document.getElementById('mobile-auth-buttons');

    if (user) {
        authButtons.innerHTML = `
            <div class="relative group">
                <button 
                    class="flex items-center space-x-2 text-gray-700 hover:text-blue-600 transition duration-300"
                    id="profileButton"
                >
                    <span>${user.name}</span>
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                    </svg>
                </button>
                <div 
                    class="absolute right-0 w-48 mt-2 py-2 bg-white rounded-md shadow-xl transition-all duration-200 ease-in-out opacity-0 invisible"
                    id="profileDropdown"
                    style="transform-origin: top right;"
                >
                    <a href="/profile" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Profile</a>
                    <a href="/settings" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Settings</a>
                    <button onclick="logout()" class="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-100">Logout</button>
                </div>
            </div>
        `;

        // Add event listeners for the dropdown
        const profileButton = document.getElementById('profileButton');
        const profileDropdown = document.getElementById('profileDropdown');
        let timeoutId;

        function showDropdown() {
            clearTimeout(timeoutId);
            profileDropdown.classList.remove('opacity-0', 'invisible');
            profileDropdown.classList.add('opacity-100', 'visible');
        }

        function hideDropdown() {
            timeoutId = setTimeout(() => {
                profileDropdown.classList.remove('opacity-100', 'visible');
                profileDropdown.classList.add('opacity-0', 'invisible');
            }, 100);
        }

        profileButton.addEventListener('mouseenter', showDropdown);
        profileButton.addEventListener('mouseleave', hideDropdown);
        profileDropdown.addEventListener('mouseenter', showDropdown);
        profileDropdown.addEventListener('mouseleave', hideDropdown);

        mobileAuthButtons.innerHTML = `
            <div class="px-3 py-2">
                <p class="text-sm font-medium text-gray-700">${user.name}</p>
            </div>
            <a href="/profile" class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50">Profile</a>
            <a href="/settings" class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50">Settings</a>
            <button onclick="logout()" class="w-full text-left px-3 py-2 rounded-md text-base font-medium text-red-600 hover:text-red-700 hover:bg-gray-50">Logout</button>
        `;
    } else {
        authButtons.innerHTML = `
            <a href="/login" class="text-gray-700 hover:text-blue-600 transition duration-300">Login</a>
            <a href="/register" class="bg-blue-600 text-white px-4 py-2 rounded-full hover:bg-blue-700 transition duration-300">Register</a>
        `;

        mobileAuthButtons.innerHTML = `
            <a href="/login" class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50">Login</a>
            <a href="/register" class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50">Register</a>
        `;
    }
}

async function logout() {
    try {
        const response = await fetch('/logout', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });

        if (response.ok) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('user');
            
            window.location.href = '/';
        }
    } catch (error) {
        console.error('Logout error:', error);
    }
}

// Initialize auth state
document.addEventListener('DOMContentLoaded', () => {
    updateAuthButtons();
    checkAuthStatus();
}); 