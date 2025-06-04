// DOM Elements
const fileInput = document.getElementById("fileInput");
const submitBtn = document.getElementById("submitBtn");
const errorMessage = document.getElementById("errorMessage");
const successMessage = document.getElementById("successMessage");
const progressContainer = document.getElementById("progressContainer");
const progressBar = document.getElementById("progressBar");
const progressText = document.getElementById("progressText");
const processingMessage = document.getElementById("processingMessage");

// Constants
const POLL_INTERVAL = 2000; // 2 seconds
const MAX_POLL_TIME = 300000; // 5 minutes timeout

// Event Listeners
fileInput.addEventListener("change", handleFileSelection);
submitBtn.addEventListener("click", handleUpload);

function handleFileSelection() {
  const file = fileInput.files[0];
  if (!file) return;

  if (!file.name.endsWith(".csv")) {
    showError("Only CSV files are allowed");
    return;
  }

  showSuccess(`File selected: ${file.name}`);
}

function handleUpload(e) {
  e.preventDefault();
  console.log("Upload button clicked");

  if (!fileInput.files.length) {
    console.log("No file selected");
    showError("Please select a file first");
    return;
  }

  resetUI();
  progressContainer.style.display = "block";
  updateProgress(0, "Preparing upload...");
  console.log("Starting upload process");

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  // Add timeout to fetch request
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 10000);

  fetch("/upload", {
    method: "POST",
    body: formData,
    signal: controller.signal,
  })
    .then((response) => {
      clearTimeout(timeoutId);
      console.log("Received response from server");
      if (!response.ok) {
        console.error("Server response not OK:", response.status);
        throw new Error(`Server error: ${response.status}`);
      }
      return response.json();
    })
    .then((data) => {
      console.log("Upload successful, data:", data);
      if (data.success) {
        updateProgress(30, "Processing started...");
        pollTaskStatus(data.task_id, data.dataset_id);
      } else {
        throw new Error(data.message);
      }
    })
    .catch((error) => {
      console.error("Upload error:", error);
      clearTimeout(timeoutId);
      if (error.name === "AbortError") {
        showError("Request timed out. Please try again.");
      } else {
        handleUploadError(error);
      }
    });
}

function pollTaskStatus(taskId, datasetId) {
  let pollStartTime = Date.now();
  let attempts = 0;
  const maxAttempts = 30; // 30 attempts max
  const pollInterval = 2000; // 2 seconds

  const poll = () => {
    attempts++;

    // Timeout check
    if (attempts > maxAttempts) {
      showError("Processing took too long, please check back later");
      return;
    }

    fetch(`/api/task-status/${taskId}`)
      .then((response) => {
        if (!response.ok) throw new Error("Network error");
        return response.json();
      })
      .then((data) => {
        console.log("Poll response:", data); // Debug log

        if (data.state === "Success") {
          handleSuccess(data, datasetId);
        } else if (data.state === "Failed") {
          handleFailure(data);
        } else if (data.state === "In Progress") {
          const progress =
            data.progress ||
            (data.current && data.total
              ? Math.round((data.current / data.total) * 100)
              : 0);
          updateProgress(
            progress,
            data.status || `Processing (${data.current}/${data.total})`
          );
          setTimeout(poll, pollInterval);
        } else {
          // PENDING state or unknown
          updateProgress(5, "Waiting for processing to start...");
          setTimeout(poll, pollInterval);
        }
      })
      .catch((error) => {
        console.error("Poll error:", error);
        if (attempts > 3) {
          showError("Failed to check processing status");
        } else {
          setTimeout(poll, pollInterval);
        }
      });
  };

  // Start polling
  poll();
}

// Helper functions
function handleSuccess(data, datasetId) {
  updateProgress(100, "Processing complete!");
  showSuccess("Dataset processed successfully!");
  setTimeout(() => {
    window.location.href = `/dashboard?dataset_id=${datasetId}`;
  }, 1500);
}

function handleFailure(data) {
  let errorMsg = "Processing failed";

  if (data.error) {
    if (typeof data.error === "object" && data.error.error_message) {
      errorMsg = data.error.error_message;
    } else if (typeof data.error === "string") {
      errorMsg = data.error;
    }
  } else if (data.result?.error) {
    errorMsg = data.result.error;
  }

  showError(errorMsg);
}

function handleUploadError(error) {
  let errorMsg = "An error occurred during upload";

  if (
    error.response &&
    error.response.error &&
    error.response.error.error_message
  ) {
    errorMsg = error.response.error.error_message;
  } else if (error.message) {
    errorMsg = error.message;
  }

  showError(errorMsg);
  resetUI();
}

function updateProgress(percent, message = "") {
  progressBar.style.width = `${percent}%`;
  progressText.textContent = `${percent}%`;
  if (message) {
    processingMessage.textContent = message;
    processingMessage.style.display = "block";
  }
}

function showError(message) {
  errorMessage.textContent = message;
  errorMessage.style.display = "block";
  successMessage.style.display = "none";
}

function showSuccess(message) {
  successMessage.textContent = message;
  successMessage.style.display = "block";
  errorMessage.style.display = "none";
}

function resetUI() {
  submitBtn.disabled = false;
  progressContainer.style.display = "none";
  processingMessage.style.display = "none";
  progressBar.style.width = "0%";
  progressText.textContent = "0%";
}
