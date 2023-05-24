window.addEventListener("DOMContentLoaded", (event) => {
    const dropZone = document.getElementById("drop_zone");
    const box = document.getElementsByClassName("box")[0]; 
    const btn_choose = document.getElementById("btn_choose");

    const form_data_DOM = document.getElementById('my_form');
    // console.log(form_data_DOM);

    const file_input = form_data_DOM.querySelector("input");
    // console.log(file_input);

    const file_input_name = form_data_DOM.querySelector("h5");
    // console.log(file_input_name);
    
    btn_choose.onclick = (event) => {
        // console.log('btn_choose.onclick');
        file_input.click();
    };

    file_input.addEventListener("change", function (e) {
        displayUpload(e.target.files[0].name);    
    });

    dropZone.addEventListener("drop", (event) => {
        dropHandler(event);
    });

    dropZone.addEventListener("dragover", (e) => {
        dragOverHandler(e);
    });

    function displayUpload(fileName) {
        // console.log("debug displayUpload");
        file_input_name.innerHTML = fileName;
        box.innerHTML = form_data_DOM.outerHTML;
        // console.log(dropZone);
    }

    function dropHandler(event) {
        // console.log("File(s) dropped");
      
        // Prevent default behavior (Prevent file from being opened)
        event.preventDefault();
      
        if (event.dataTransfer.items) {
            // Use DataTransferItemList interface to access the file(s)
            [...event.dataTransfer.items].forEach((item, i) => {
                // If dropped items aren't files, reject them
                if (item.kind === "file") {
                    const file = item.getAsFile();
                    console.log(`… file[${i}].name = ${file.name}`);
                    displayUpload(file.name);
                }
            });
        } else {
            // Use DataTransfer interface to access the file(s)
            [...event.dataTransfer.files].forEach((file, i) => {
                console.log(`… file[${i}].name = ${file.name}`);
                displayUpload(file.name);
            });
        }
    }

    function dragOverHandler(event) {
        // console.log("File(s) in drop zone");
      
        // Prevent default behavior (Prevent file from being opened)
        event.preventDefault();
    }

});