document.addEventListener("DOMContentLoaded", () => {
    fetch("http://127.0.0.1:5000/sentiment-data")
        .then(response => response.json())
        .then(data => {
            document.getElementById("sentiment-score").textContent = data.overallSentimentScore;
            document.getElementById("positive-score").textContent = `${data.positiveScore}%`;
            document.getElementById("neutral-score").textContent = `${data.neutralScore}%`;
            document.getElementById("negative-score").textContent = `${data.negativeScore}%`;
            renderSentimentTrendChart(data.trend);
        })
        .catch(error => console.error("Error fetching sentiment data:", error));
});

function renderSentimentTrendChart(trendData) {
    // Implement chart logic if needed, for example with Chart.js
}
