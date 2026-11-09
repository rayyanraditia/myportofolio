(() => {
    "use strict";

    const section = document.getElementById("education");
    if (!section) return;

    const searchForm = document.getElementById("education-search-form");
    const searchInput = document.getElementById("education-search-input");
    const retryButton = document.getElementById("education-retry");
    const grid = document.getElementById("education-grid");
    const cardTemplate = document.getElementById("education-card-template");
    const emptyMessage = document.getElementById("education-empty-message");
    const educationForm = document.getElementById("education-form");
    const educationModal = document.getElementById("add-education-modal");
    const editForm = document.getElementById("education-edit-form");
    const editModal = document.getElementById("edit-education-modal");

    const states = {
        loading: document.getElementById("education-loading"),
        error: document.getElementById("education-error"),
        empty: document.getElementById("education-empty"),
        ready: grid,
    };

    const SEARCH_DELAY = 300;
    const UUID_PLACEHOLDER = "00000000-0000-0000-0000-000000000000";

    let debounceTimer;
    let activeController;

    function showState(nextState) {
        Object.entries(states).forEach(([name, element]) => {
            element.classList.toggle("hide", name !== nextState);
        });

        grid.setAttribute("aria-busy", String(nextState === "loading"));
    }

    function getSafeImageUrl(value) {
        if (!value) return null;

        try {
            const url = new URL(value, window.location.origin);

            if (url.protocol === "http:" || url.protocol === "https:") {
                return url.href;
            }
        } catch {
            return null;
        }

        return null;
    }

    async function submitEducationAction(event, method) {
        event.preventDefault();

        const form = event.currentTarget;
        const button = form.querySelector("button[type='submit']");
        const isDelete = method === "DELETE";

        if (button.disabled) return;

        if (
            isDelete
            && !window.confirm("Yakin ingin menghapus pendidikan ini?")
        ) {
            return;
        }

        button.disabled = true;
        form.setAttribute("aria-busy", "true");

        try {
            const csrfToken = form.querySelector(
                "[name='csrfmiddlewaretoken']",
            ).value;

            const response = await fetch(form.action, {
                method,
                headers: {
                    Accept: "application/json",
                    "X-CSRFToken": csrfToken,
                },
            });

            // DELETE berhasil mengembalikan 204 tanpa body JSON.
            const result = response.status === 204
                ? {}
                : await response.json().catch(() => ({}));

            if (!response.ok) {
                showToast(
                    "Permintaan gagal",
                    getValidationMessage(result, response.status),
                    "error",
                    6000,
                );
                return;
            }

            const message = isDelete
                ? "Pendidikan berhasil dihapus."
                : (
                    result.is_starred
                        ? "Star berhasil ditambahkan."
                        : "Star berhasil dibatalkan."
                );

            showToast("Berhasil", message, "success");

            window.clearTimeout(debounceTimer);
            await fetchEducation();
        } catch (error) {
            console.error("Gagal memperbarui Education:", error);

            showToast(
                "Koneksi bermasalah",
                "Status perubahan belum dapat dipastikan. "
                    + "Muat ulang daftar sebelum mencoba kembali.",
                "error",
                6000,
            );
        } finally {
            button.disabled = false;
            form.removeAttribute("aria-busy");
        }
    }

    function buildEducationCard(item) {
        const education = item;
        const card = cardTemplate.content.firstElementChild.cloneNode(true);

        card.querySelector("[data-field='title']").textContent =
            education.title;
        card.querySelector(".education-category").textContent =
            education.category_display;
        card.querySelector(".education-description").textContent =
            education.description;
        card.querySelector(".education-status").textContent =
            education.is_ongoing ? "Sedang berlangsung" : "Selesai";
        card.querySelector(".star-count").textContent =
            education.star_count;

        const starButton = card.querySelector(".button-star");

        if (starButton) {
            starButton.classList.toggle("is-starred", education.is_starred);
            starButton.setAttribute(
                "aria-pressed",
                String(education.is_starred),
            );
            starButton.title = education.star_count > 0
                ? `Dibintangi oleh ${education.starred_by_names}`
                : "Jadilah yang pertama memberi star";

            card.querySelector("[data-field='star-label']").textContent =
                education.is_starred ? "Unstar" : "Star";
        }

        card.querySelectorAll("[data-url-template]").forEach((element) => {
            const url = element.dataset.urlTemplate.replace(
                UUID_PLACEHOLDER,
                encodeURIComponent(education.id),
            );

            if (element.tagName === "FORM") {
                element.action = url;
            } else if (element.tagName === "BUTTON") {
                element.dataset.endpoint = url;
            } else {
                element.href = url;
            }
        });

        const starForm = card.querySelector(".star-form");

        if (starForm) {
            starForm.addEventListener("submit", (event) => {
                submitEducationAction(event, "POST");
            });
        }

        const deleteForm = card.querySelector("[data-action='delete']");

        if (deleteForm) {
            deleteForm.addEventListener("submit", (event) => {
                submitEducationAction(event, "DELETE");
            });
        }

        const editButton = card.querySelector("[data-action='edit']");

        if (editButton && editForm && editModal) {
            editButton.addEventListener("click", () => {
                if (editForm.getAttribute("aria-busy") === "true") return;

                editForm.action = editButton.dataset.endpoint;

                for (const name of [
                    "title",
                    "description",
                    "category",
                    "thumbnail",
                ]) {
                    editForm.elements.namedItem(name).value = education[name] ?? "";
                }

                editModal.showPopover();
                editForm.elements.namedItem("title").focus();
            });
        }

        const image = card.querySelector(".education-photo");
        const imageUrl = getSafeImageUrl(education.thumbnail);

        if (imageUrl) {
            image.alt = `Logo ${education.title}`;
            image.addEventListener("error", () => image.remove(), {
                once: true,
            });
            image.src = imageUrl;
        } else {
            image.remove();
        }

        return card;
    }

    async function fetchEducation() {
        activeController?.abort();

        const controller = new AbortController();
        activeController = controller;

        const query = searchInput.value.trim();
        const url = new URL(section.dataset.endpoint, window.location.origin);

        if (query) {
            url.searchParams.set("title", query);
        }

        showState("loading");

        try {
            const response = await fetch(url, {
                headers: {
                    Accept: "application/json",
                },
                signal: controller.signal,
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();

            // Respons pencarian lama tidak boleh menimpa hasil terbaru.
            if (controller.signal.aborted) return;

            if (!Array.isArray(data)) {
                throw new Error("Format respons Education tidak valid.");
            }

            grid.replaceChildren();

            if (data.length === 0) {
                emptyMessage.textContent = query
                    ? `Tidak ada pendidikan yang cocok dengan "${query}".`
                    : "Belum ada pendidikan yang ditambahkan.";

                showState("empty");
                return;
            }

            const fragment = document.createDocumentFragment();

            data.forEach((item) => {
                fragment.appendChild(buildEducationCard(item));
            });

            grid.appendChild(fragment);
            showState("ready");
        } catch (error) {
            if (controller.signal.aborted) return;

            console.error("Gagal memuat Education:", error);
            showState("error");
        }
    }

    function getValidationMessage(result, status, form = educationForm) {
        if (typeof result.detail === "string") {
            return result.detail;
        }

        const messages = Object.entries(result).flatMap(
            ([fieldName, errors]) => {
                const field = form?.elements.namedItem(fieldName);
                const label = field?.labels?.[0]?.textContent.trim();

                const values = Array.isArray(errors) ? errors : [errors];

                return values
                    .filter((message) => typeof message === "string")
                    .map((message) => (
                        label ? `${label}: ${message}` : message
                    ));
            },
        );

        return messages.join(" ") || `Permintaan gagal (HTTP ${status}).`;
    }

    async function editEducation(event) {
        event.preventDefault();

        const button = editForm.querySelector("button[type='submit']");
        if (button.disabled) return;

        button.disabled = true;
        button.textContent = "Menyimpan...";
        editForm.setAttribute("aria-busy", "true");

        try {
            const csrfToken = editForm.querySelector(
                "[name='csrfmiddlewaretoken']",
            ).value;

            const response = await fetch(editForm.action, {
                method: "PATCH",
                headers: {
                    Accept: "application/json",
                    "X-CSRFToken": csrfToken,
                },
                body: new FormData(editForm),
            });

            const result = await response.json().catch(() => ({}));

            if (!response.ok) {
                showToast(
                    "Gagal mengubah pendidikan",
                    getValidationMessage(result, response.status, editForm),
                    "error",
                    6000,
                );
                return;
            }

            if (editModal.matches(":popover-open")) {
                editModal.hidePopover();
            }

            showToast(
                "Berhasil",
                "Pendidikan berhasil diperbarui.",
                "success",
            );

            window.clearTimeout(debounceTimer);
            await fetchEducation();
        } catch (error) {
            console.error("Gagal mengedit Education:", error);

            showToast(
                "Koneksi bermasalah",
                "Status penyimpanan belum dapat dipastikan. "
                    + "Periksa daftar sebelum mencoba kembali.",
                "error",
                6000,
            );
        } finally {
            button.disabled = false;
            button.textContent = "Simpan Perubahan";
            editForm.removeAttribute("aria-busy");
        }
    }

    async function addEducation(event) {
        event.preventDefault();

        const submitButton = educationForm.querySelector(
            "button[type='submit']",
        );

        if (submitButton.disabled) return;

        const originalLabel = submitButton.textContent;
        submitButton.disabled = true;
        submitButton.textContent = "Menyimpan...";
        educationForm.setAttribute("aria-busy", "true");

        try {
            const csrfToken = educationForm.querySelector(
                "[name='csrfmiddlewaretoken']",
            ).value;

            const response = await fetch(educationForm.action, {
                method: "POST",
                headers: {
                    Accept: "application/json",
                    "X-CSRFToken": csrfToken,
                },
                body: new FormData(educationForm),
            });

            const result = await response.json().catch(() => ({}));

            if (!response.ok) {
                showToast(
                    "Gagal menambahkan pendidikan",
                    getValidationMessage(result, response.status),
                    "error",
                    6000,
                );
                return;
            }

            educationForm.reset();

            if (educationModal.matches(":popover-open")) {
                educationModal.hidePopover();
            }

            showToast(
                "Berhasil",
                result.message || "Pendidikan berhasil ditambahkan.",
                "success",
            );

            // Tampilkan seluruh data agar hasil penambahan tidak
            // tersembunyi oleh pencarian sebelumnya.
            window.clearTimeout(debounceTimer);
            searchInput.value = "";

            await fetchEducation();
        } catch (error) {
            console.error("Gagal mengirim Education:", error);

            showToast(
                "Koneksi bermasalah",
                "Status penyimpanan belum dapat dipastikan. "
                    + "Periksa daftar pendidikan sebelum mencoba kembali.",
                "error",
                6000,
            );
        } finally {
            submitButton.disabled = false;
            submitButton.textContent = originalLabel;
            educationForm.removeAttribute("aria-busy");
        }
    }

    searchInput.addEventListener("input", () => {
        window.clearTimeout(debounceTimer);
        activeController?.abort();
        showState("loading");

        debounceTimer = window.setTimeout(fetchEducation, SEARCH_DELAY);
    });

    searchForm.addEventListener("submit", (event) => {
        event.preventDefault();
        window.clearTimeout(debounceTimer);
        fetchEducation();
    });

    retryButton.addEventListener("click", () => {
        window.clearTimeout(debounceTimer);
        fetchEducation();
    });

    if (educationForm && educationModal) {
        educationForm.addEventListener("submit", addEducation);
    }
    if (editForm && editModal) {
        editForm.addEventListener("submit", editEducation);
    }
    fetchEducation();
})();
