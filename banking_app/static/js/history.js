document.addEventListener("DOMContentLoaded", () => {
    const tableBody = document.getElementById("historyTableBody");
    const filterDate = document.getElementById("filterDate");
    const filterType = document.getElementById("filterType");
    const applyFiltersButton = document.getElementById("applyFilters");

    function fetchTransactions() {
        fetch('/api/transactions')
            .then(response => response.json())
            .then(data => {
                renderTransactions(data);
            })
            .catch(error => {
                console.error('Error fetching transactions:', error);
            });
    }

    function renderTransactions(transactions) {
        tableBody.innerHTML = "";
        if (transactions.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="5">No transactions found.</td></tr>`;
            return;
        }

        transactions.forEach((transaction) => {
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

    function applyFilters() {
        const selectedDate = filterDate.value;
        const selectedType = filterType.value;

        fetch('/api/transactions')
            .then(response => response.json())
            .then(data => {
                const filteredTransactions = data.filter((transaction) => {
                    const matchesDate = selectedDate ? transaction.date === selectedDate : true;
                    const matchesType = selectedType ? transaction.type === selectedType : true;
                    return matchesDate && matchesType;
                });
                renderTransactions(filteredTransactions);
            })
            .catch(error => {
                console.error('Error fetching transactions:', error);
            });
    }

    applyFiltersButton.addEventListener("click", () => {
        applyFilters();
    });

    fetchTransactions();
});