"use strict";

// One shared dialog; closing with Escape is equivalent to cancelling.
window.confirmDeletion = function (message) {
    const dialog = document.getElementById("confirm-delete");
    if (dialog.open) return Promise.resolve(false);
    const trigger = document.activeElement;
    document.getElementById("confirm-delete-message").textContent = message;
    dialog.returnValue = "cancel";
    return new Promise((resolve) => {
        dialog.addEventListener("close", () => {
            trigger?.focus();
            resolve(dialog.returnValue === "confirm");
        }, { once: true });
        dialog.showModal();
    });
};
