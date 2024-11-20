document.addEventListener("DOMContentLoaded", () => {
    const transferTypeRadios = document.querySelectorAll('input[name="transferType"]');
    const toAccountGroup = document.getElementById("toAccountGroup");
    const internalDropdown = document.getElementById("toInternalAccount");
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

    // Initialize
    toggleTransferType();
});
