// sparkline.js - Canvas sparkline renderer

function drawSparkline(canvas, data, options = {}) {
    if (!canvas || !data || data.length < 2) return;

    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    const {
        color = '#e8a020',
        alertColor = '#e03030',
        alertHigh = null,
        alertLow = null,
        lineWidth = 1.5,
        fill = true
    } = options;

    // Determine if last value triggers alert
    const lastVal = data[data.length - 1];
    let lineColor = color;
    if (alertHigh !== null && lastVal >= alertHigh) lineColor = alertColor;
    if (alertLow !== null && lastVal <= alertLow) lineColor = alertColor;

    // Scale data to fit canvas
    const minVal = Math.min(...data);
    const maxVal = Math.max(...data);
    const range = maxVal - minVal || 1; // avoid division by zero

    const points = data.map((val, i) => {
        const x = (i / (data.length - 1)) * width;
        const y = height - ((val - minVal) / range) * (height * 0.8) - 4; // leave margin
        return { x, y };
    });

    // Draw fill
    if (fill) {
        ctx.beginPath();
        ctx.moveTo(points[0].x, height);
        points.forEach(p => ctx.lineTo(p.x, p.y));
        ctx.lineTo(points[points.length-1].x, height);
        ctx.closePath();
        ctx.fillStyle = lineColor + '20'; // 20 = 12% opacity
        ctx.fill();
    }

    // Draw line
    ctx.beginPath();
    ctx.moveTo(points[0].x, points[0].y);
    for (let i = 1; i < points.length; i++) {
        ctx.lineTo(points[i].x, points[i].y);
    }
    ctx.strokeStyle = lineColor;
    ctx.lineWidth = lineWidth;
    ctx.stroke();

    // Draw dot at latest value
    ctx.beginPath();
    ctx.arc(points[points.length-1].x, points[points.length-1].y, 3, 0, 2 * Math.PI);
    ctx.fillStyle = lineColor;
    ctx.fill();
    ctx.strokeStyle = '#000';
    ctx.lineWidth = 1;
    ctx.stroke();
}