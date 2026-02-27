function login() {
    localStorage.setItem("admin", "true");
    window.location.href = "/admin";
}

function checkAdmin() {
    if (!localStorage.getItem("admin")) {
        window.location.href = "/login";
    }
}

function logout() {
    localStorage.removeItem("admin");
    window.location.href = "/";
}
