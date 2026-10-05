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

    function buildEducationCard(item) {
        const education = item.fields;
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
                encodeURIComponent(item.pk),
            );

            if (element.tagName === "FORM") {
                element.action = url;
            } else {
                element.href = url;
            }
        });

        const deleteForm = card.querySelector("[data-action='delete']");

        if (deleteForm) {
            deleteForm.addEventListener("submit", (event) => {
                if (!window.confirm("Yakin ingin menghapus pendidikan ini?")) {
                    event.preventDefault();
                }
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

    function getValidationMessage(result, status) {
        if (result.errors) {
            return Object.entries(result.errors)
                .flatMap(([fieldName, errors]) => {
                    const field = educationForm.elements.namedItem(fieldName);
                    const label = field?.labels?.[0]?.textContent.trim();

                    return errors.map((error) => (
                        label ? `${label}: ${error.message}` : error.message
                    ));
                })
                .join(" ");
        }

        return result.message || `Permintaan gagal (HTTP ${status}).`;
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
            const response = await fetch(educationForm.action, {
                method: "POST",
                headers: {
                    Accept: "application/json",
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

    fetchEducation();
})();