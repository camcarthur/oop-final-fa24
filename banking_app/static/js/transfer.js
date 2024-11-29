document.addEventListener("DOMContentLoaded", () => {
    const transferTypeRadios = document.querySelectorAll('input[name="transferType"]');
    const toAccountGroup = document.getElementById("toAccountGroup");
    const internalDropdown = document.getElementById("toInternalAccount");
    const transferForm = document.getElementById("transferForm");
    let externalInput = null;

    // Create external account input field
    const createExternalAccountInput = () => {
        const input = document.createElement("input");
        input.type = "text";
        input.id = "toExternalAccount";
        input.name = "toExternalAccount";
        input.placeholder = "Enter recipient account number";
        input.required = true;
        input.classList.add("form-control");
        input.style.padding = "10px"; // Consistent padding
        input.style.borderRadius = "5px";
        return input;
    };

    // Toggle between internal and external transfers
    const toggleTransferType = () => {
        const selectedType = document.querySelector('input[name="transferType"]:checked').value;

        if (selectedType === "internal") {
            toAccountGroup.replaceChildren(internalDropdown);
            document.getElementById("notesGroup").style.display = "none";
        } else if (selectedType === "external") {
            if (!externalInput) {
                externalInput = createExternalAccountInput();
            }
            toAccountGroup.replaceChildren(externalInput);
            document.getElementById("notesGroup").style.display = "block";
        }
    };

    // Add event listeners
    transferTypeRadios.forEach((radio) => radio.addEventListener("change", toggleTransferType));

    // Handle form submission
    transferForm.addEventListener("submit", (event) => {
        event.preventDefault(); // Prevent default form submission

        // Simulate form submission (e.g., send data via fetch or a server call)
        // For now, we assume the transfer is successful
        alert("Transfer initiated"); // Show success message
        window.location.reload(); // Reload the page after showing the message
    });

    // Initialize
    toggleTransferType();
});
