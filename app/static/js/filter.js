async function filterData(){
    const class_id = document.getElementById("class_id").value;
    const subject_id = document.getElementById("subject_id").value;
    const topic_id = document.getElementById("topic_id").value;
    const lesson_id = document.getElementById("lesson_id").value;
    const from_date = document.getElementById("from_date").value;
    const to_date = document.getElementById("to_date").value;

    const res = await fetch(
        `/filter/?class_id=${class_id}&subject_id=${subject_id}&topic_id=${topic_id}&lesson_id=${lesson_id}&from_date=${from_date}&to_date=${to_date}`
    );

    const data = await res.json();
    renderResult(data);
}
