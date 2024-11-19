document.addEventListener('DOMContentLoaded', () => {
    const passwordInput = document.querySelector('#password');
    passwordInput.addEventListener('input', (event) => {
        const strengthMessage = document.querySelector('#strengthMessage');
        if (event.target.value.length < 6) {
            strengthMessage.innerText = 'Password too weak';
            strengthMessage.style.color = 'red';
        } else {
            strengthMessage.innerText = 'Password is strong';
            strengthMessage.style.color = 'green';
        }
    });
});
