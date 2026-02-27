const API_BASE = "/api";

async function searchKeyword() {
    const q = document.getElementById("keyword").value.trim();
    if (!q) return alert("Nhập từ khóa");

    try {
        const res = await fetch(`${API_BASE}/search/keyword?q=${q}`);
        const data = await res.json();
        renderTable(data.data || []);
    } catch (err) {
        alert("Search error");
        console.error(err);
    }
}

async function filterLessons() {

    const class_id = document.getElementById("class_id").value.trim();
    const subject_id = document.getElementById("subject_id").value.trim();
    const topic_id = document.getElementById("topic_id").value.trim();

    try {
        const res = await fetch(
            `${API_BASE}/filter?class_id=${class_id}&subject_id=${subject_id}&topic_id=${topic_id}`
        );
        const data = await res.json();
        renderTable(data.data || []);
    } catch (err) {
        alert("Filter error");
        console.error(err);
    }
}

function renderTable(list) {
    const tbody = document.getElementById("result");
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

function viewFile(bucket, objectName) {

    const url = `${API_BASE}/file/${bucket}/${objectName}`;
    const ext = objectName.split('.').pop().toLowerCase();

    let content = "";

    if (["mp4", "webm"].includes(ext)) {
        content = `<video controls width="100%">
                     <source src="${url}">
                   </video>`;
    } else if (ext === "pdf") {
        content = `<iframe src="${url}" width="100%" height="600px"></iframe>`;
    } else {
        content = `<img src="${url}" class="img-fluid"/>`;
    }

    document.getElementById("fileViewer").innerHTML = content;
    new bootstrap.Modal(document.getElementById("fileModal")).show();
}
