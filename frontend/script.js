// ================= CONFIG =================
const UPLOAD_API =
  "https://u37z50eof1.execute-api.us-east-1.amazonaws.com/prod/upload-url";

const DOWNLOAD_API =
  "https://u37z50eof1.execute-api.us-east-1.amazonaws.com/prod/download-url";

// Store uploaded S3 key
let uploadedKey = "";

// ================= UPLOAD IMAGE =================
async function uploadImage() {
  try {
    const fileInput = document.getElementById("imageFile");
    const resultsDiv = document.getElementById("results");

    if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
      alert("Please select an image");
      return;
    }

    const file = fileInput.files[0];
    const filename = Date.now() + "-" + file.name;

    resultsDiv.innerHTML = "Uploading image... ⏳";

    // 1️⃣ Call upload Lambda
    const res = await fetch(
      `${UPLOAD_API}?filename=${encodeURIComponent(filename)}`
    );

    if (!res.ok) {
      throw new Error("Upload Lambda API failed");
    }

    const lambdaResponse = await res.json();
    console.log("Upload Lambda response:", lambdaResponse);

    // 2️⃣ Validate response
    if (!lambdaResponse.upload_url || !lambdaResponse.key) {
      console.error("Unexpected Lambda response:", lambdaResponse);
      throw new Error("upload_url or key missing from Lambda response");
    }

    uploadedKey = lambdaResponse.key;

    // 3️⃣ Upload to S3
    const s3Res = await fetch(lambdaResponse.upload_url, {
      method: "PUT",
      headers: {
        "Content-Type": file.type
      },
      body: file
    });

    if (!s3Res.ok) {
      throw new Error("S3 upload failed");
    }

    resultsDiv.innerHTML = "Image uploaded ✅<br/>Processing... 🔄";

    // 4️⃣ Wait for optimization Lambda
    setTimeout(fetchOptimizedImages, 7000);

  } catch (err) {
    console.error("Upload error:", err);
    alert("❌ Upload failed. Check console.");
  }
}

// ================= DOWNLOAD OPTIMIZED IMAGES =================
async function fetchOptimizedImages() {
  const resultsDiv = document.getElementById("results");
  resultsDiv.innerHTML = "<h3>Optimized Images</h3>";

  if (!uploadedKey) {
    resultsDiv.innerHTML += "<p>No uploaded image key found.</p>";
    return;
  }

  const sizes = ["1080p", "720p", "480p"];

  for (const size of sizes) {
    try {
      const res = await fetch(
        `${DOWNLOAD_API}?key=${encodeURIComponent(uploadedKey)}&size=${size}`
      );

      if (!res.ok) {
        throw new Error(`Download API failed for ${size}`);
      }

      const data = await res.json();
      console.log(`Download response (${size}):`, data);

      if (!data.download_url) {
        throw new Error("download_url missing");
      }

      const link = document.createElement("a");
      link.href = data.download_url;
      link.target = "_blank";
      link.innerText = `Download ${size}`;

      resultsDiv.appendChild(link);
      resultsDiv.appendChild(document.createElement("br"));

    } catch (err) {
      console.error(`Error fetching ${size}:`, err);
      resultsDiv.innerHTML += `<p>❌ ${size} not ready</p>`;
    }
  }
}
