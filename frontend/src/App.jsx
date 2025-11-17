// src/App.jsx
import { useState } from "react";
import UploadForm from "./components/UploadForm.jsx";
import SummaryView from "./components/SummaryView.jsx";

function App() {
  const [parsed, setParsed] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  return (
    <div className="min-h-screen bg-pink-50 p-6">
      <div className="max-w-3xl mx-auto bg-white shadow-lg rounded-2xl p-6 border border-pink-100">
        <h1 className="text-2xl font-semibold mb-2 text-pink-700">
          Syllabus Summaries
        </h1>
        <p className="text-sm text-gray-600 mb-4">
          Upload a syllabus (PDF or .txt) and get the important info instantly:
          due dates, grading breakdown, textbooks, and a quick{" "}
          <span className="font-medium">“how to get an A”</span> summary.
        </p>

        <UploadForm
          setParsed={setParsed}
          setLoading={setLoading}
          setErrorMsg={setErrorMsg}
        />

        {loading && <p className="mt-4 text-sm text-gray-700">Parsing…</p>}
        {errorMsg && (
          <p className="mt-4 text-sm text-red-600">Error: {errorMsg}</p>
        )}
        {parsed && !loading && !errorMsg && (
          <SummaryView parsed={parsed} />
        )}
      </div>
    </div>
  );
}

export default App;
