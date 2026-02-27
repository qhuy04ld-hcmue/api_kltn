const API_BASE = "/api";

document.addEventListener("DOMContentLoaded", () => {

    const form = document.getElementById("uploadForm");
    if (!form) return;

    form.addEventListener("submit", async function (e) {
        e.preventDefault();

        const formData = new FormData(this);

        try {
            const res = await fetch(`${API_BASE}/upload`, {
                method: "POST",
                body: formData
            });

            const data = await res.json();
            alert(JSON.stringify(data));
            form.reset();

        } catch (err) {
            alert("Upload error");
            console.error(err);
        }
    });
});
