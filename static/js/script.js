document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const loadingState = document.getElementById('loading-state');
    const resultsContainer = document.getElementById('results-container');
    const previewImg = document.getElementById('preview-img');
    const statType = document.getElementById('stat-type');
    const statMeanSat = document.getElementById('stat-mean-sat');
    const statColoredRatio = document.getElementById('stat-colored-ratio');
    const statReason = document.getElementById('stat-reason');
    const statResolution = document.getElementById('stat-resolution');
    const errorToast = document.getElementById('error-toast');
    const errorMessage = document.getElementById('error-message');
    

    const channelR = document.getElementById('channel-r');
    const channelG = document.getElementById('channel-g');
    const channelB = document.getElementById('channel-b');
    

    const matrixTabs = document.querySelectorAll('.matrix-tab');
    const matrixTable = document.getElementById('matrix-table');
    
    let rgbChart = null;
    let currentMatrixData = null;

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
        loadingState.style.display = 'none';
        dropZone.style.display = 'block';
        resultsContainer.style.display = 'block';


        previewImg.src = data.image_url;
        statType.textContent = data.type;
        statReason.textContent = data.reason;
        
        if (data.type === 'Grayscale Image') {
            statType.style.color = '#a0a0b0';
            statType.style.textShadow = '0 0 10px rgba(160, 160, 176, 0.3)';
        } else {
            statType.style.color = 'var(--accent-blue)';
            statType.style.textShadow = '0 0 10px rgba(0, 240, 255, 0.3)';
        }

        statMeanSat.textContent = data.hsv_metrics.mean_saturation;
        statColoredRatio.textContent = `${data.hsv_metrics.colored_ratio}%`;
        statResolution.textContent = `${data.resolution} (${data.total_pixels.toLocaleString()} px)`;


        channelR.src = data.channels.r;
        channelG.src = data.channels.g;
        channelB.src = data.channels.b;
        
        const statsBody = document.getElementById('channel-stats-body');
        statsBody.innerHTML = `
            <tr>
                <td style="color: #ff4d4d; font-weight: bold;">Red</td>
                <td>${data.stats.r.min}</td><td>${data.stats.r.max}</td><td>${data.stats.r.mean}</td><td>${data.stats.r.std}</td>
            </tr>
            <tr>
                <td style="color: #4dff4d; font-weight: bold;">Green</td>
                <td>${data.stats.g.min}</td><td>${data.stats.g.max}</td><td>${data.stats.g.mean}</td><td>${data.stats.g.std}</td>
            </tr>
            <tr>
                <td style="color: #4d4dff; font-weight: bold;">Blue</td>
                <td>${data.stats.b.min}</td><td>${data.stats.b.max}</td><td>${data.stats.b.mean}</td><td>${data.stats.b.std}</td>
            </tr>
        `;


        currentMatrixData = data.matrix;
        renderMatrix('r');
        

        renderChart(data.histogram);
    }
    

    matrixTabs.forEach(tab => {
        tab.addEventListener('click', (e) => {
            matrixTabs.forEach(t => t.classList.remove('active'));
            e.target.classList.add('active');
            renderMatrix(e.target.dataset.channel);
        });
    });
    
    function renderMatrix(channel) {
        if (!currentMatrixData) return;
        
        const matrix = currentMatrixData[channel];
        matrixTable.innerHTML = '';
        

        let rgbBase = '';
        if (channel === 'r') rgbBase = '255, 0, 0';
        else if (channel === 'g') rgbBase = '0, 255, 0';
        else if (channel === 'b') rgbBase = '0, 0, 255';
        
        matrix.forEach(row => {
            const tr = document.createElement('tr');
            row.forEach(val => {
                const td = document.createElement('td');
                td.textContent = val;
                

                const opacity = Math.max(0.1, val / 255);
                td.style.backgroundColor = `rgba(${rgbBase}, ${opacity})`;
                
                tr.appendChild(td);
            });
            matrixTable.appendChild(tr);
        });
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
                        enabled: false
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


    const canvas = document.getElementById('math-bg');
    if (canvas) {
        const ctx = canvas.getContext('2d');
        let width, height;
        let particles = [];
        const symbols = ['[R, G, B]', 'Y = 0.299R + 0.587G + 0.114B', '∑', 'λ', 'det(A)', 'σ', 'R ≈ G ≈ B', 'T(v) = Av', 'v ∈ ℝ³', 'A^T', '||v||'];
        
        function resize() {
            width = canvas.width = window.innerWidth;
            height = canvas.height = window.innerHeight;
        }
        
        window.addEventListener('resize', resize);
        resize();
        
        class MathParticle {
            constructor() {
                this.reset();
                this.y = Math.random() * height;
            }
            
            reset() {
                this.x = Math.random() * width;
                this.y = height + Math.random() * 100;
                this.speed = 0.3 + Math.random() * 0.7;
                this.text = symbols[Math.floor(Math.random() * symbols.length)];
                this.fontSize = 14 + Math.random() * 20;
                this.opacity = 0.05 + Math.random() * 0.15;
                this.drift = (Math.random() - 0.5) * 0.2;
            }
            
            update() {
                this.y -= this.speed;
                this.x += this.drift;
                if (this.y < -50) {
                    this.reset();
                }
            }
            
            draw() {
                ctx.fillStyle = `rgba(74, 144, 226, ${this.opacity})`;
                ctx.font = `${this.fontSize}px 'JetBrains Mono', monospace`;
                ctx.fillText(this.text, this.x, this.y);
            }
        }
        
        for (let i = 0; i < 40; i++) {
            particles.push(new MathParticle());
        }
        
        function animate() {
            ctx.clearRect(0, 0, width, height);
            particles.forEach(p => {
                p.update();
                p.draw();
            });
            requestAnimationFrame(animate);
        }
        
        animate();
    }
});
