window.addEventListener("DOMContentLoaded", function() {
    const tab1 = document.querySelector(".tab-1");
    const tab2 = document.querySelector(".tab-2");

    let activeTabRender = document.querySelectorAll(".activeTabRender")[0];
    var activeTab = document.getElementById("activeTab");

    const tab1Title = document.querySelector(".tab-1-title");
    const tab2Title = document.querySelector(".tab-2-title");
    
    const dropZone = document.querySelector(".drop-zone");
    
    const fileInputImage = document.querySelector("#file-input-image");
    const studentListInput = document.querySelectorAll(".student-list")[0]
    
    const closeBtn = document.querySelector(".close-btn")
    
    const btnSubmit1 = document.getElementById("btn-submit-1");
    const btnSubmit2 = document.getElementById("btn-submit-2");

    const extractFileWrap = document.querySelector(".extract-file-wrap");

    const downLoadRegion = document.getElementById("download-region");

    const countResult = document.querySelector(".count-result");

    activeTab.value = "tab1";
    

    tab1.addEventListener("click", function() {
        activeTab.value = "tab1"

        tab1.classList.add("active");
        tab2.classList.remove("active");
    
        tab1Title.classList.add("show")
        tab2Title.classList.remove("show")

        studentListInput.classList.remove("hide")
    
        btnSubmit1.classList.add("show")
        btnSubmit2.classList.remove("show")
    
        extractFileWrap.classList.add("show")
        countResult.classList.remove("show")
    });
    
    tab2.addEventListener("click", function() {
        activeTab.value = "tab2"

        tab2.classList.add("active");
        tab1.classList.remove("active");

        tab2Title.classList.add("show")
        tab1Title.classList.remove("show")

        studentListInput.classList.add("hide")

        btnSubmit2.classList.add("show")
        btnSubmit1.classList.remove("show")

        countResult.classList.add("show")
        extractFileWrap.classList.remove("show")
    });

    document.querySelectorAll(".drop-zone__input").forEach((inputElement) => {
        const dropZoneElement = inputElement.closest(".drop-zone");
        dropZoneElement.addEventListener("click", (e) => {
            inputElement.click();
        });

        inputElement.addEventListener("change", (e) => {
            const file = e.target.files[0];
            if (file) {
                dropZone.classList.add("disable")
                updateThumbnail(dropZoneElement, file);
                closeBtn.classList.add("show")
            }
            else {
                dropZone.classList.remove("disable")
                closeBtn.classList.remove("show")
            }      
        });

        dropZoneElement.addEventListener("dragover", (e) => {
            e.preventDefault();
            dropZoneElement.classList.add("drop-zone--over");
        });
      
        ["dragleave", "dragend"].forEach((type) => {
            dropZoneElement.addEventListener(type, (e) => {
                dropZoneElement.classList.remove("drop-zone--over");
            });
        });
      
        dropZoneElement.addEventListener("drop", (e) => {
            e.preventDefault();
        
            if (e.dataTransfer.files.length) {
                inputElement.files = e.dataTransfer.files;

                var event = new Event('change', { bubbles: true });
                inputElement.dispatchEvent(event);
            }
        
            dropZoneElement.classList.remove("drop-zone--over");
        });
    });
      
    function updateThumbnail(dropZoneElement, file) {
        let thumbnailElement = dropZoneElement.querySelector(".drop-zone__thumb");
    
        // First time - remove the prompt
        if (dropZoneElement.querySelector(".drop-zone__prompt")) {
            // dropZoneElement.querySelector(".drop-zone__prompt").style.display = "none";
            dropZoneElement.querySelector(".drop-zone__prompt").classList.remove("show");
            dropZoneElement.querySelector(".drop-zone__prompt").classList.add("hide");
        }
    
        // First time - there is no thumbnail element, so lets create it
        if (!thumbnailElement) {
            thumbnailElement = document.createElement("div");
            thumbnailElement.classList.add("drop-zone__thumb");
            dropZoneElement.appendChild(thumbnailElement);
        }
    
        thumbnailElement.dataset.label = file.name;
        // Show thumbnail for image files
        if (file.type.startsWith("image/")) {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => {
                thumbnailElement.style.backgroundImage = `url('${reader.result}')`;
            };
        } else {
            thumbnailElement.style.backgroundImage = null;
        }
    }
    
    closeBtn.addEventListener("click", function() {
        const dropZoneThumb = document.querySelector(".drop-zone__thumb")
        dropZoneThumb.remove()
        
        const dropZonePrompt = document.querySelector(".drop-zone__prompt")
        // dropZonePrompt.style.display = "block";
        dropZonePrompt.classList.remove("hide");
        dropZonePrompt.classList.add("show");
        
        closeBtn.classList.remove("show")
        dropZone.classList.remove("disable")
        
        fileInputImage.value = null;
    });
        
    btnSubmit1.onclick = () => {
        console.log("Submit Successfully")
    }

    btnSubmit2.onclick = () => {
        console.log("Submit Successfully")
    }

    downLoadRegion.addEventListener("click", function() {
        console.log('downLoadFile.addEventListener click');
        window.location.href = '/download';
    });

    if (activeTabRender.innerHTML == "tab1") {
        tab1.click();
    }
    else {
        tab2.click();
    }

});



