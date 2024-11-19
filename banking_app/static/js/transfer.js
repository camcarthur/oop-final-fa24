document.addEventListener("DOMContentLoaded", () => {
    const transferForm = document.getElementById("transferForm");

    transferForm.addEventListener("submit", (event) => {
        event.preventDefault(); // Prevent default form submission

        const fromAccount = document.getElementById("fromAccount").value;
        const toAccount = document.getElementById("toAccount").value.trim();
        const amount = parseFloat(document.getElementById("amount").value);
        const notes = document.getElementById("notes").value.trim();
        const frequency = document.getElementById("frequency").value;

        // Basic validation
        if (!fromAccount) {
            alert("Please select the account to transfer from.");
            return;
        }
        if (!toAccount) {
            alert("Please enter the recipient account number.");
            return;
        }
        if (isNaN(amount) || amount <= 0) {
            alert("Please enter a valid amount greater than 0.");
            return;
        }

        // Mock transfer success
        alert(`Transfer of $${amount.toFixed(2)} scheduled (${frequency}) to account ${toAccount}.`);
        transferForm.reset(); // Clear the form after successful submission
    });
});
