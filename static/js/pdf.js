window.onload = function () {
    document.getElementById("download")
        .addEventListener("click", () => {
            const question = this.document.getElementById("main");
            console.log(question);
            console.log(window);
            var opt = {
                margin: 1,
                filename: 'test.pdf',
                image: { type: 'jpeg', quality: 0.98 },
                html2canvas: { scale: 2 },
                jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
            };
            html2pdf().from(question).set(opt).save();
        })
}
