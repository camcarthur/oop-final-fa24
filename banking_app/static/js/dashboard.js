document.addEventListener("DOMContentLoaded", () => {
    window.navigateToFilteredHistory = function (filterType) {
        let queryParams = "";

        switch (filterType) {
            case "expenses":
                queryParams = "?type=debit";
                break;
            case "income":
                queryParams = "?type=credit";
                break;
            case "transfers":
                queryParams = "?type=transfer";
                break;
        }

        window.location.href = `/history${queryParams}`;
    };
});
