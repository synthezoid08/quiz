export function loadNavbar() {
    const navbar = `
    <nav class="bg-white dark:bg-gray-800 shadow-md p-4 sticky top-0 z-50">
        <div class="container mx-auto flex justify-between items-center">
            <a href="/" class="text-2xl font-bold text-primary">AdaptQuiz</a>
            <div id="nav-links" class="flex space-x-4 items-center">
                <!-- Dynamically injected based on auth -->
            </div>
        </div>
    </nav>
    `;
    const container = document.getElementById('navbar-container');
    if (container) {
        container.innerHTML = navbar;
        updateNavState();
    }
}

export function loadSidebar() {
    const sidebar = `
    <aside class="w-64 bg-white dark:bg-gray-800 h-screen shadow-md hidden md:block fixed left-0 top-0 pt-20">
        <div class="p-6 overflow-y-auto h-full">
            <nav class="space-y-2">
                <a href="/src/pages/student/dashboard.html" class="block p-3 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition">Dashboard</a>
                <a href="/src/pages/notes/library.html" class="block p-3 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition">My Notes</a>
                <a href="/src/pages/notes/upload.html" class="block p-3 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition text-sm ml-4">Upload Note</a>
                <a href="/src/pages/quiz/generate.html" class="block p-3 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition">AI Quiz</a>
                <a href="/src/pages/quiz/history.html" class="block p-3 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition text-sm ml-4">History</a>
            </nav>
        </div>
    </aside>
    `;
    const container = document.getElementById('sidebar-container');
    if (container) {
        container.innerHTML = sidebar;
    }
}

function updateNavState() {
    const token = localStorage.getItem('access_token');
    const navLinks = document.getElementById('nav-links');
    if (!navLinks) return;
    
    if (token) {
        navLinks.innerHTML = `
            <a href="/src/pages/student/dashboard.html" class="text-gray-600 dark:text-gray-300 hover:text-primary">Dashboard</a>
            <button onclick="logout()" class="px-4 py-2 bg-red-500 text-white rounded-md shadow hover:bg-red-600 transition">Logout</button>
        `;
    } else {
        navLinks.innerHTML = `
            <a href="/src/pages/auth/login.html" class="px-4 py-2 text-gray-600 dark:text-gray-300 hover:text-primary">Login</a>
            <a href="/src/pages/auth/register.html" class="px-4 py-2 bg-primary text-white rounded-md shadow hover:bg-indigo-600 transition">Sign Up</a>
        `;
    }
}

window.logout = function() {
    localStorage.removeItem('access_token');
    window.location.href = '/src/pages/auth/login.html';
}

// Auto-initialize if DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    loadNavbar();
    loadSidebar();
});
