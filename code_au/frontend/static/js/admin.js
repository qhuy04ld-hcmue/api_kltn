const API_BASE = "/api";

async function adminSearch() {

    const q = document.getElementById("admin_keyword").value.trim();
    if (!q) return alert("Nhập từ khóa");

    try {
        const res = await fetch(`${API_BASE}/search/keyword?q=${q}`);
        const data = await res.json();
        renderAdminTable(data.data || []);
    } catch (err) {
        alert("Search error");
        console.error(err);
    }
}

async function adminFilter() {

    const class_id = document.getElementById("admin_class_id").value.trim();
    const subject_id = document.getElementById("admin_subject_id").value.trim();
    const topic_id = document.getElementById("admin_topic_id").value.trim();

    try {
        const res = await fetch(
            `${API_BASE}/filter?class_id=${class_id}&subject_id=${subject_id}&topic_id=${topic_id}`
        );
        const data = await res.json();
        renderAdminTable(data.data || []);
    } catch (err) {
        alert("Filter error");
        console.error(err);
    }
}

function renderAdminTable(list) {

    const tbody = document.getElementById("admin_result");
    tbody.innerHTML = "";

    list.forEach(item => {

        let files = "";

        if (item.files) {
            item.files.forEach(f => {
                const objectName = f.file_url.split("/").pop();
                files += `
                    <button class="btn btn-sm btn-primary m-1"
                        onclick="viewFile('${f.bucket}','${objectName}')">
                        ${f.file_name}
                    </button>
                `;
            });
        }

        tbody.innerHTML += `
            <tr>
                <td>${item.lesson_id}</td>
                <td>${item.lesson_name || ""}</td>
                <td>${files}</td>
            </tr>
        `;
    });
}
