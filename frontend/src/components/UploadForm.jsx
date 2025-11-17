// src/components/UploadForm.jsx
import { useState } from "react";

export default function UploadForm({ setParsed, setLoading, setErrorMsg }) {
  const [file, setFile] = useState(null);

  const onSubmit = async (e) => {
    e.preventDefault();
    setParsed(null);
    setErrorMsg("");

    if (!file) {
      setErrorMsg("Please choose a file first.");
      return;
    }

    setLoading(true);

    const form = new FormData();
    form.append("file", file);

    try {
      const res = await fetch("http://127.0.0.1:5000/upload", {
        method: "POST",
        body: form,
      });

      if (!res.ok) {
        const maybeJson = await res.json().catch(() => null);
        const msg =
          maybeJson?.error ||
          `Upload failed with status ${res.status}`;
        setErrorMsg(msg);
        setParsed(null);
      } else {
        const data = await res.json();
        setParsed(data);
      }
    } catch (err) {
      console.error(err);
      setErrorMsg("Could not reach the server. Is the backend running?");
      setParsed(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form
      onSubmit={onSubmit}
      className="flex flex-col gap-3 border border-gray-200 rounded-xl p-4 bg-gray-50"
    >
      <label className="text-sm font-medium text-gray-700">
        Upload syllabus file (PDF or .txt)
      </label>
      <input
        type="file"
        accept=".pdf,.txt"
        onChange={(e) => setFile(e.target.files[0] || null)}
        className="block w-full text-sm text-gray-700
                   file:mr-3 file:py-2 file:px-4
                   file:rounded-md file:border-0
                   file:text-sm file:font-medium
                   file:bg-pink-100 file:text-pink-700
                   hover:file:bg-pink-200"
      />
      <button
        type="submit"
        className="inline-flex items-center justify-center px-4 py-2 rounded-md
                   bg-pink-600 text-white text-sm font-medium
                   hover:bg-pink-700 disabled:bg-pink-300"
        disabled={!file}
      >
        Upload &amp; Parse
      </button>
      <p className="text-xs text-gray-500">
        We don’t store your file — it’s parsed once and discarded.
      </p>
    </form>
  );
}
