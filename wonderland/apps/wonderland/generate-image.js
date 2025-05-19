const fs = require('fs');
const path = require('path');

// Create a simple colored square PNG for the app icon
const width = 256;
const height = 256;

// Create the assets directory if it doesn't exist
const assetsDir = path.join(__dirname, 'assets');
if (!fs.existsSync(assetsDir)) {
  fs.mkdirSync(assetsDir, { recursive: true });
}

// Create a simple HTML file that will generate our image
const htmlContent = `
<!DOCTYPE html>
<html>
<head>
  <title>Generate Wonderland Icon</title>
</head>
<body>
  <canvas id="canvas" width="${width}" height="${height}" style="display:none;"></canvas>
  <script>
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    
    // Fill background with a light blue color (like sky)
    ctx.fillStyle = '#87CEFA';
    ctx.fillRect(0, 0, ${width}, ${height});
    
    // Draw ground (green)
    ctx.fillStyle = '#7cbb78';
    ctx.fillRect(0, ${height/2}, ${width}, ${height/2});
    
    // Draw a mushroom
    // Stem
    ctx.fillStyle = '#f5d7b2';
    ctx.fillRect(${width/2-20}, ${height/2-40}, 40, 80);
    
    // Cap
    ctx.fillStyle = '#e05e5e';
    ctx.beginPath();
    ctx.ellipse(${width/2}, ${height/2-40}, 80, 30, 0, 0, 2 * Math.PI);
    ctx.fill();
    
    // Draw white spots on the mushroom cap
    ctx.fillStyle = '#FFFFFF';
    [
      [${width/2-40}, ${height/2-50}],
      [${width/2+30}, ${height/2-45}],
      [${width/2}, ${height/2-60}],
      [${width/2-20}, ${height/2-30}],
      [${width/2+40}, ${height/2-30}]
    ].forEach(([x, y]) => {
      ctx.beginPath();
      ctx.arc(x, y, 8, 0, 2 * Math.PI);
      ctx.fill();
    });
    
    // Create a download link
    const dataUrl = canvas.toDataURL('image/png');
    const link = document.createElement('a');
    link.download = 'image.png';
    link.href = dataUrl;
    link.textContent = 'Download PNG';
    document.body.appendChild(link);
    link.click();
  </script>
</body>
</html>
`;

// Write the HTML file
fs.writeFileSync(path.join(__dirname, 'generate-image.html'), htmlContent);

console.log('HTML file created at:', path.join(__dirname, 'generate-image.html'));
console.log('Please open this file in a browser to generate and download the image.png file');
console.log('After downloading, move the image.png file to the assets directory');
