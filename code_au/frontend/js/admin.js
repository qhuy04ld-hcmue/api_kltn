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
                //const objectName = f.file_url.split("/").pop();
                let objectName = f.file_url;

                // Nếu là full URL thì cắt bỏ domain + bucket
                if (objectName.startsWith("http")) {
                    const url = new URL(objectName);
                    const parts = url.pathname.split("/");
                    parts.shift(); // remove empty
                    parts.shift(); // remove bucket name
                    objectName = parts.join("/");
                }


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
async function viewFile(bucket, objectName) {

    const res = await fetch(
        `/api/file/presigned?bucket=${bucket}&object_name=${objectName}`
    );

    const data = await res.json();

    if (!data.url) {
        alert("Không mở được file");
        return;
    }

    const ext = objectName.split('.').pop().toLowerCase();

    // Nếu là PDF → mở tab mới
    if (ext === "pdf") {
        window.open(data.url, "_blank");
        return;
    }

    // Video / image → mở modal
    let content = "";

    if (["mp4","webm","mov"].includes(ext)) {
        content = `
            <video controls width="100%">
                <source src="${data.url}">
            </video>
        `;
    } else {
        content = `
            <img src="${data.url}" class="img-fluid"/>
        `;
    }

    document.getElementById("fileViewer").innerHTML = content;
    new bootstrap.Modal(document.getElementById("fileModal")).show();
}



/*
async function viewFile(bucket, objectName) {

    const res = await fetch(
        `/api/file/presigned?bucket=${bucket}&object_name=${objectName}`
    );

    const data = await res.json();

    if (!data.url) {
        alert("Không mở được file");
        return;
    }

    const ext = objectName.split('.').pop().toLowerCase();

    let content = "";

    if (["mp4","webm"].includes(ext)) {
        content = `<video controls width="100%">
                     <source src="${data.url}">
                   </video>`;
    } else if (ext === "pdf") {
        content = `<iframe src="${data.url}" width="100%" height="600px"></iframe>`;
    } else {
        content = `<img src="${data.url}" class="img-fluid"/>`;
    }

    document.getElementById("fileViewer").innerHTML = content;
    new bootstrap.Modal(document.getElementById("fileModal")).show();
}
*/
