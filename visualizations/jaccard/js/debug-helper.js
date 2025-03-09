
console.log("Debug helper loaded");

// Log all errors
window.onerror = function(msg, url, line) {
    console.error("Error:", msg, "at", url, "line", line);
    alert("Error loading visualization: " + msg);
    return false;
};

// Debug JSON loading
if (window.d3) {
    var originalD3Json = d3.json;
    d3.json = function(url, callback) {
        console.log("Loading JSON from:", url);
        
        originalD3Json(url, function(error, data) {
            if (error) {
                console.error("Error loading JSON:", error);
                alert("Failed to load data from " + url + ": " + error);
            } else {
                console.log("Successfully loaded data:", data);
            }
            callback(error, data);
        });
    };
}
