const API_BASE = "/api";

document.addEventListener("DOMContentLoaded", () => {

    const insertForm = document.getElementById("insertForm");
    if (!insertForm) return;

    insertForm.addEventListener("submit", async function (e) {
        e.preventDefault();

        const formData = new FormData(this);

        try {
            const res = await fetch(`${API_BASE}/crud/insert`, {
                method: "POST",
                body: formData
            });

            const data = await res.json();
            alert(JSON.stringify(data));
            insertForm.reset();

        } catch (err) {
            alert("Insert error");
            console.error(err);
        }
    });
});

async function softDelete() {

    const id = document.getElementById("delete_id").value.trim();
    if (!id) return alert("Nhập lesson_id");

    try {
        const res = await fetch(`${API_BASE}/crud/soft-delete/${id}`, {
            method: "DELETE"
        });

        const data = await res.json();
        alert(JSON.stringify(data));

    } catch (err) {
        alert("Delete error");
        console.error(err);
    }
}
document.addEventListener("DOMContentLoaded", () => {

    const updateForm = document.getElementById("updateForm");

    if (updateForm) {
        updateForm.addEventListener("submit", async function(e){
            e.preventDefault();

            const lessonId = document.getElementById("update_id").value.trim();
            if(!lessonId) return alert("Nhập lesson_id");

            const formData = new FormData(this);

            try {
                const res = await fetch(`/api/crud/update/${lessonId}`, {
                    method: "PUT",
                    body: formData
                });

                const data = await res.json();
                alert(JSON.stringify(data));

            } catch(err){
                alert("Update error");
                console.error(err);
            }
        });
    }
});
