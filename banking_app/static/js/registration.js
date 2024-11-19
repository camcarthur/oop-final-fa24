// registration.js

document.addEventListener("DOMContentLoaded", () => {
    const registrationForm = document.getElementById("registrationForm");

    registrationForm.addEventListener("submit", (event) => {
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

        // Mock registration success (can be replaced with actual backend call later)
        const newUser = { username, email, password };
        console.log("New User Registered:", newUser);

        alert("Registration successful! You can now log in.");
        registrationForm.reset(); // Clear the form after successful registration
        window.location.href = "/"; // Redirect to login page
    });
});
