/*
 * Loading overlay for every backend action.
 *
 * Any <form> or <a> with a data-loading-title attribute shows the overlay
 * when it is submitted / clicked. Optional data-loading-steps is a "|"-separated
 * list of backend steps; the page is a plain form POST, so real progress is not
 * available - steps advance on a timer (data-loading-step-ms) and the last one
 * stays active until the server responds and the new page loads.
 */
(function () {
    var overlay, titleEl, elapsedEl, stepsEl, noteEl;
    var timers = [];

    function build() {
        overlay = document.createElement("div");
        overlay.className = "loading-overlay";
        overlay.setAttribute("role", "status");
        overlay.setAttribute("aria-live", "polite");
        overlay.innerHTML =
            '<div class="loading-box">' +
            '<div class="loading-spinner"></div>' +
            '<p class="loading-title"></p>' +
            '<p class="loading-elapsed"></p>' +
            '<ul class="loading-steps"></ul>' +
            '<p class="loading-note"></p>' +
            "</div>";
        document.body.appendChild(overlay);
        titleEl = overlay.querySelector(".loading-title");
        elapsedEl = overlay.querySelector(".loading-elapsed");
        stepsEl = overlay.querySelector(".loading-steps");
        noteEl = overlay.querySelector(".loading-note");
    }

    function clearTimers() {
        timers.forEach(clearInterval);
        timers = [];
    }

    function show(el) {
        var steps = (el.dataset.loadingSteps || "").split("|").filter(Boolean);
        var stepMs = parseInt(el.dataset.loadingStepMs, 10) || 4000;

        titleEl.textContent = el.dataset.loadingTitle;
        noteEl.textContent = el.dataset.loadingNote || "";
        stepsEl.innerHTML = "";
        steps.forEach(function (text) {
            var li = document.createElement("li");
            li.textContent = text;
            stepsEl.appendChild(li);
        });

        var items = stepsEl.children;
        var current = 0;
        if (items.length) items[0].className = "active";

        // Advance to the next step; never finish the last one (server does that)
        if (items.length > 1) {
            timers.push(setInterval(function () {
                if (current >= items.length - 1) return;
                items[current].className = "done";
                current += 1;
                items[current].className = "active";
            }, stepMs));
        }

        var start = Date.now();
        elapsedEl.textContent = "0s elapsed";
        timers.push(setInterval(function () {
            elapsedEl.textContent = Math.floor((Date.now() - start) / 1000) + "s elapsed";
        }, 1000));

        overlay.classList.add("active");
    }

    function hide() {
        clearTimers();
        if (overlay) overlay.classList.remove("active");
        document.querySelectorAll("button.is-loading").forEach(function (btn) {
            btn.classList.remove("is-loading");
            btn.disabled = false;
            if (btn.dataset.originalText) btn.textContent = btn.dataset.originalText;
        });
    }

    document.addEventListener("DOMContentLoaded", function () {
        build();

        document.querySelectorAll("form[data-loading-title]").forEach(function (form) {
            form.addEventListener("submit", function (event) {
                var btn = form.querySelector("button[type=submit]");
                // Block double submits while the request is running
                if (btn && btn.disabled) {
                    event.preventDefault();
                    return;
                }
                if (btn) {
                    btn.dataset.originalText = btn.textContent;
                    btn.textContent = form.dataset.loadingButton || "Please wait...";
                    btn.classList.add("is-loading");
                    btn.disabled = true;
                }
                show(form);
            });
        });

        document.querySelectorAll("a[data-loading-title]").forEach(function (link) {
            link.addEventListener("click", function (event) {
                // Let ctrl/cmd-click open a new tab without the overlay
                if (event.ctrlKey || event.metaKey || event.shiftKey) return;
                show(link);
            });
        });
    });

    // Back/forward cache restores the page with the overlay still visible
    window.addEventListener("pageshow", function (event) {
        if (event.persisted) hide();
    });
})();
