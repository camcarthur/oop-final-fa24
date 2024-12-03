document.addEventListener("DOMContentLoaded", () => {
    const transferTypeRadios = document.querySelectorAll('input[name="transferType"]');
    const toAccountGroup = document.getElementById("toAccountGroup");
    const internalDropdown = document.getElementById("toInternalAccount");
    const transferForm = document.getElementById("transferForm");
    let externalInput = null;


    const createExternalAccountInput = () => {
        const input = document.createElement("input");
        input.type = "number";
        input.id = "toExternalAccount";
        input.name = "toExternalAccount";
        input.placeholder = "Enter recipient account ID";
        input.required = true;
        input.classList.add("form-control");
        input.style.padding = "10px";
        input.style.borderRadius = "5px";
        return input;
    };

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

    // event listeners
    transferTypeRadios.forEach((radio) => radio.addEventListener("change", toggleTransferType));

    toggleTransferType();
});