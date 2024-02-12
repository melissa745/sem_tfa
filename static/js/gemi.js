const form = document.getElementById("dataForm");

const handleSubmit = (e) => {
  e.preventDefault();

  // Get the input text and PDF file from the form
  const inputText = document.getElementById("input_text").value;
  const pdfFile = document.getElementById("pdf").files[0];

  // Call the Gemini API to extract text from the PDF file
  const geminiApiEndpoint = "AIzaSyAa1jzaUezK-Z3eOL4EuHkoiCslkySb-lo";

  const formData = new FormData();
  formData.append("pdf", pdfFile);

  fetch(geminiApiEndpoint, {
    method: "POST",
    body: formData
  }).then((response) => {
    return response.json();
  }).then((data) => {
    console.log("Data Response:",data.text)
    // Get the extracted text from the Gemini API response
    const extractedText = data.text;

    // Combine the input text and extracted text
    const combinedText = inputText + extractedText;

    // Call the Generative AI API with the combined text
    const model = new GoogleGenerativeAI(API_KEY);
    model.generate(combinedText).then((response) => {
      // Display the generated text in the results div
      const resultsDiv = document.getElementById("result");
      resultsDiv.textContent = response.candidates[0].output;
    });
  });
};

form.addEventListener("submit", handleSubmit);