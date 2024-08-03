function createLoader() {
    var loader = document.createElement('div');
    loader.className = 'loader-wrapper';
    loader.innerHTML = '<span class="loader"><span class="loader-inner"></span></span>';
    document.body.appendChild(loader);
return loader;
}

function removeLoader(loader) {
    document.body.removeChild(loader);
}

function handleFileUpload(event) {
    var file = event.target.files[0];
    var uploadMessageElement = document.getElementById('upload-message');
    var predictButtonElement = document.getElementById('predict-button');  // Get the predict button element
    var framesElement = document.getElementById('frame-input'); 
    if (file) {
        if (file.type.startsWith('video/')) {
            var formData = new FormData();
            formData.append('file', file);
            formData.append('frames', framesElement.value);  // Append the number of frames to the form data
            fetch('http://localhost:5000/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.text())
            .then(success => {
                uploadMessageElement.style.display = 'block';
                uploadMessageElement.innerText = success;
                uploadMessageElement.className = 'success-message';
                var checkboxContainer = document.querySelector('.checkbox-container');
                checkboxContainer.style.display = ''; // Display the checkbox container
                checkboxContainer.classList.add('checkbox-container-display');
                predictButtonElement.style.display = 'block';  // Display the predict button
                var parts = success.split(' ');  // Split the string at spaces
                var label = parts[1].split(',')[0];  // Split the second part at commas and get the first part
                // If the label of the video is correct formated. Check the boxes
                if (label === 'ulnua_krank') {
                    document.querySelector('.krank-box').checked = true;
                    document.querySelector('input[name="group"][value="ulnua"]').checked = true;
                } else if (label === 'ulnoa_krank') {
                    document.querySelector('.krank-box').checked = true;
                    document.querySelector('input[name="group"][value="ulnoa"]').checked = true;
                } else if (label === 'medua_krank') {
                    document.querySelector('.krank-box').checked = true;
                    document.querySelector('input[name="group"][value="medua"]').checked = true;
                } else if (label === 'medoa_krank') {
                    document.querySelector('.krank-box').checked = true;
                    document.querySelector('input[name="group"][value="medoa"]').checked = true;
                } else if (label === 'ulnua') {
                    document.querySelector('input[name="group"][value="ulnua"]').checked = true;
                } else if (label === 'ulnoa') {
                    document.querySelector('input[name="group"][value="ulnoa"]').checked = true;
                } else if (label === 'medua') {
                    document.querySelector('input[name="group"][value="medua"]').checked = true;
                } else if (label === 'medoa') {
                    document.querySelector('input[name="group"][value="medoa"]').checked = true;
                }

                console.log(value);  // Log the value
            })
            .catch(error => console.log(error));
        } else {
            uploadMessageElement.style.display = 'block';
            uploadMessageElement.innerText = 'Invalid file type. Please upload a video file.';
            uploadMessageElement.className = 'error-message';
        }
    }
}
    function predict() {
        $('#upload-message').hide();
        // Create the loader
        var loader = createLoader();
        fetch('http://localhost:5000/predict')
            .then(response => response.json())
            .then(data => {
                // Handle the response data here
                console.log(data);
                displayImages(data);
                document.getElementById('save-button').style.color = 'white';
                // Remove the loader
                removeLoader(loader);
            })
            .catch(error => console.log(error));

}
function displayImages(data) {
const imageGrid = document.getElementById('image-grid');
imageGrid.innerHTML = '';  // Clear all existing images

data.forEach(imageFileName => {
    const imgElement = document.createElement('img');
    imgElement.src = '/static/detected_nerves/' + imageFileName; // Path to your images
    imgElement.style.width = '40%';
    imgElement.style.margin = '10px 0';  // 10px margin top and bottom
    imgElement.style.border = '4px solid green';  // Default border color
    imgElement.dataset.filename = imageFileName;  // Set the filename as a data attribute
    let clickCount = 0;
    // Add click event listener
    imgElement.addEventListener('click', function() {
        clickCount++;
        switch (clickCount % 3) {
            case 1:
                this.style.border = '4px solid red';
                break;
            case 2:
                this.style.border = '4px solid orange';
                break;
            default:
                this.style.border = '4px solid green';
                clickCount = 0;
        }
    });

    imageGrid.appendChild(imgElement);
});

// Show the save button
document.getElementById('save-button').style.display = 'block';

}

document.getElementById('save-button').addEventListener('click', function() {
    const imageElements = document.querySelectorAll('#image-grid img');
    const krankBoxChecked = document.querySelector('.krank-box').checked;
    const selectedRadio = document.querySelector('input[name="group"]:checked');
    const selectedRadioValue = selectedRadio ? selectedRadio.value : null;

    const data = Array.from(imageElements).map(img => ({
        filename: img.dataset.filename,
        borderStyle: img.style.border,
        krankBoxChecked: krankBoxChecked,
        selectedRadioValue: selectedRadioValue
    }));

    const json = JSON.stringify(data);

    fetch('http://localhost:5000/save_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: json
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.result === true) {
            document.getElementById('save-button').style.color = 'green';
            window.location.href = '/classification_home';
        }
    });
});