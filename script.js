function updatePreview() {
    // ดึงค่าจาก Input
    const name = document.getElementById('inName').value;
    const role = document.getElementById('inRole').value;
    const email = document.getElementById('inEmail').value;
    const phone = document.getElementById('inPhone').value;
    const exp = document.getElementById('inExp').value;
    const skills = document.getElementById('inSkills').value;

    // ส่งค่าไปที่ Preview
    document.getElementById('outName').innerText = name || "ชื่อ-นามสกุล";
    document.getElementById('outRole').innerText = role || "ตำแหน่งงาน";
    document.getElementById('outEmail').innerText = email || "example@mail.com";
    document.getElementById('outPhone').innerText = phone || "08x-xxx-xxxx";
    document.getElementById('outExp').innerText = exp || "รายละเอียดจะแสดงตรงนี้...";

    // จัดการส่วน Skills
    const skillsContainer = document.getElementById('outSkills');
    skillsContainer.innerHTML = "";
    if (skills) {
        skills.split(',').forEach(s => {
            if(s.trim() !== "") {
                const span = document.createElement('span');
                span.className = "skill-item";
                span.innerText = s.trim();
                skillsContainer.appendChild(span);
            }
        });
    }
}

function exportPDF() {
    const element = document.getElementById('resume-to-print');
    const opt = {
        margin: 0.5,
        filename: 'resume.pdf',
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2 },
        jsPDF: { unit: 'in', format: 'a4', orientation: 'portrait' }
    };
    html2pdf().set(opt).from(element).save();
}
