// history.js

document.addEventListener("DOMContentLoaded", () => {
    const transactions = [
        // Sample transactions (replace with data fetched from the server)
        { date: "2024-11-01", type: "credit", account: "Checking", amount: 500.0, notes: "Salary" },
        { date: "2024-11-05", type: "debit", account: "Savings", amount: 200.0, notes: "Groceries" },
        { date: "2024-11-10", type: "transfer", account: "Business", amount: 1000.0, notes: "Vendor Payment" },
        { date: "2024-11-15", type: "debit", account: "Checking", amount: 50.0, notes: "Electric Bill" },
    ];

    const tableBody = document.getElementById("historyTableBody");
    const filterDate = document.getElementById("filterDate");
    const filterType = document.getElementById("filterType");
    const applyFiltersButton = document.getElementById("applyFilters");

    // Function to render transactions
    function renderTransactions(filteredTransactions) {
        tableBody.innerHTML = ""; // Clear current rows
        if (filteredTransactions.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="5">No transactions found.</td></tr>`;
            return;
        }

        filteredTransactions.forEach((transaction) => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${transaction.date}</td>
                <td>${transaction.type}</td>
                <td>${transaction.account}</td>
                <td>$${transaction.amount.toFixed(2)}</td>
                <td>${transaction.notes || "N/A"}</td>
            `;
           
            tableBody.appendChild(row);
        });
    }

    // Function to filter transactions
    function applyFilters() {
        const selectedDate = filterDate.value;
        const selectedType = filterType.value;

        const filteredTransactions = transactions.filter((transaction) => {
            const matchesDate = selectedDate ? transaction.date === selectedDate : true;
            const matchesType = selectedType ? transaction.type === selectedType : true;
            return matchesDate && matchesType;
        });

        renderTransactions(filteredTransactions);
    }

    // Event listener for applying filters
    applyFiltersButton.addEventListener("click", () => {
        applyFilters();
    });

    // Initial render of all transactions
    renderTransactions(transactions);
});