document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("loginForm");

    loginForm.addEventListener("submit", (event) => {
        event.preventDefault(); // Prevent default form submission

        const username = document.getElementById("username").value.trim();
        const password = document.getElementById("password").value.trim();

        if (username === "" || password === "") {
            alert("Please fill in all fields.");
            return;
        }

        // Submit login data via fetch
        fetch("/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: new URLSearchParams({ username, password }),
        })
            .then((response) => {
                if (response.ok) {
                    window.location.href = "/dashboard"; // Redirect to /dashboard
                } else {
                    return response.text();
                }
            })
            .then((errorMessage) => {
                if (errorMessage) {
                    alert(errorMessage); // Show server error message
                }
            })
            .catch((error) => {
                console.error("Login error:", error);
            });
    });
});