// registration.js

document.addEventListener("DOMContentLoaded", () => {
    const registrationForm = document.getElementById("registrationForm");

    registrationForm.addEventListener("submit", async (event) => {
        event.preventDefault(); // Prevent default form submission

        const username = document.getElementById("username").value.trim();
        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value;
        const confirmPassword = document.getElementById("confirmPassword").value;

        // Basic validation
        if (!username || !email || !password || !confirmPassword) {
            alert("Please fill out all fields.");
            return;
        }

        if (password !== confirmPassword) {
            alert("Passwords do not match. Please try again.");
            return;
        }

        // Prepare data to send to the server
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('email', email);
        formData.append('password', password);

        try {
            const response = await fetch('/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: formData.toString(),
            });

            if (response.redirected) {
                // If the server redirects, follow the redirect
                window.location.href = response.url;
            } else if (response.ok) {
                // Registration successful
                alert("Registration successful! You can now log in.");
                registrationForm.reset();
                window.location.href = "/";
            } else {
                const errorText = await response.text();
                alert("Registration failed: " + errorText);
            }
        } catch (error) {
            alert("An error occurred: " + error.message);
        }
    });
});
