document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const loadingState = document.getElementById('loading-state');
    const resultsContainer = document.getElementById('results-container');
    const previewImg = document.getElementById('preview-img');
    const statType = document.getElementById('stat-type');
    const statSimilarity = document.getElementById('stat-similarity');
    const statResolution = document.getElementById('stat-resolution');
    const statPixels = document.getElementById('stat-pixels');
    const errorToast = document.getElementById('error-toast');
    const errorMessage = document.getElementById('error-message');
    
    let rgbChart = null;

    // Drag & Drop Handlers
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
    });

    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });

    dropZone.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            handleFile(this.files[0]);
        }
    });

    function handleFile(file) {
        if (!file.type.match('image.*')) {
            showError('Please upload an image file (JPG, PNG).');
            return;
        }

        if (file.size > 10 * 1024 * 1024) {
            showError('File size exceeds 10MB limit.');
            return;
        }

        uploadImage(file);
    }

    function uploadImage(file) {
        // UI Updates
        dropZone.style.display = 'none';
        loadingState.style.display = 'block';
        resultsContainer.style.display = 'none';

        const formData = new FormData();
        formData.append('image', file);

        fetch('/api/analyze', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            displayResults(data);
        })
        .catch(error => {
            showError(error.message);
            resetUI();
        });
    }

    function displayResults(data) {
        // Hide loading, show results
        loadingState.style.display = 'none';
        dropZone.style.display = 'block'; // Allow another upload
        resultsContainer.style.display = 'block';

        // Update Stats
        previewImg.src = data.image_url;
        statType.textContent = data.type;
        
        // Dynamic coloring for type
        if (data.type === 'Grayscale Image') {
            statType.style.color = '#a0a0b0'; // gray
            statType.style.textShadow = '0 0 10px rgba(160, 160, 176, 0.3)';
        } else {
            statType.style.color = 'var(--accent-blue)';
            statType.style.textShadow = '0 0 10px rgba(0, 240, 255, 0.3)';
        }

        statSimilarity.textContent = `${data.similarity}%`;
        statResolution.textContent = data.resolution;
        statPixels.textContent = data.total_pixels.toLocaleString();

        // Render Chart
        renderChart(data.histogram);
    }

    function renderChart(histData) {
        const ctx = document.getElementById('rgbChart').getContext('2d');
        
        if (rgbChart) {
            rgbChart.destroy();
        }

        const labels = Array.from({length: 256}, (_, i) => i);

        rgbChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Red',
                        data: histData.r,
                        borderColor: 'rgba(255, 99, 132, 1)',
                        backgroundColor: 'rgba(255, 99, 132, 0.1)',
                        borderWidth: 2,
                        pointRadius: 0,
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: 'Green',
                        data: histData.g,
                        borderColor: 'rgba(75, 192, 192, 1)',
                        backgroundColor: 'rgba(75, 192, 192, 0.1)',
                        borderWidth: 2,
                        pointRadius: 0,
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: 'Blue',
                        data: histData.b,
                        borderColor: 'rgba(54, 162, 235, 1)',
                        backgroundColor: 'rgba(54, 162, 235, 0.1)',
                        borderWidth: 2,
                        pointRadius: 0,
                        fill: true,
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                plugins: {
                    legend: {
                        labels: {
                            color: '#a0a0b0',
                            font: {
                                family: "'Outfit', sans-serif"
                            }
                        }
                    },
                    tooltip: {
                        enabled: false // disable tooltips for performance on 256 points
                    }
                },
                scales: {
                    x: {
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        ticks: { color: '#a0a0b0' },
                        title: {
                            display: true,
                            text: 'Pixel Intensity (0-255)',
                            color: '#a0a0b0'
                        }
                    },
                    y: {
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        ticks: { color: '#a0a0b0' },
                        title: {
                            display: true,
                            text: 'Pixel Count',
                            color: '#a0a0b0'
                        }
                    }
                }
            }
        });
    }

    function showError(msg) {
        errorMessage.textContent = msg;
        errorToast.classList.add('show');
        setTimeout(() => {
            errorToast.classList.remove('show');
        }, 3000);
    }

    function resetUI() {
        loadingState.style.display = 'none';
        dropZone.style.display = 'block';
        fileInput.value = '';
    }
});
