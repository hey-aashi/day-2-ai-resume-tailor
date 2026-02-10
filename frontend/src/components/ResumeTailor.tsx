import React, { useCallback, useRef, useState } from "react";
import {
  FileUp,
  FileText,
  Loader2,
  Sparkles,
  Tags,
  Wrench,
  Brain,
  AlertCircle,
  CheckCircle,
} from "lucide-react";

type UploadResponse = {
  resume_id: string;
  filename: string;
  size_bytes: number;
};

type TailoredResponse = {
  summary_enhancement: string;
  keyword_optimization: string[];
  skills_gap: string[];
  recommendations: string[];
};

const API_BASE = "http://127.0.0.1:8000";
const MAX_SIZE_BYTES = 10 * 1024 * 1024;

function isPdf(file: File) {
  const nameOk = file.name.toLowerCase().endsWith(".pdf");
  const typeOk =
    file.type === "application/pdf" ||
    file.type === "application/x-pdf" ||
    file.type === "application/acrobat";
  return nameOk || typeOk;
}

export default function ResumeTailor() {
  const [file, setFile] = useState<File | null>(null);
  const [jobDesc, setJobDesc] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<TailoredResponse | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const onFileSelect = useCallback((f: File | null) => {
    setError(null);
    setResult(null);
    if (!f) {
      setFile(null);
      return;
    }
    if (!isPdf(f)) {
      setError("Only PDF files are allowed.");
      setFile(null);
      return;
    }
    if (f.size > MAX_SIZE_BYTES) {
      setError("File size exceeds 10MB limit.");
      setFile(null);
      return;
    }
    setFile(f);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      const f = e.dataTransfer.files?.[0] || null;
      onFileSelect(f);
    },
    [onFileSelect],
  );

  const handleAnalyze = useCallback(async () => {
    setError(null);
    setResult(null);
    if (!file) {
      setError("Please upload a PDF resume.");
      return;
    }
    const cleanedJob = jobDesc.trim();
    if (cleanedJob.length < 200) {
      setError("Job description must be at least 200 characters.");
      return;
    }
    try {
      setLoading(true);
      const fd = new FormData();
      fd.append("file", file);
      const uploadRes = await fetch(`${API_BASE}/upload-resume`, {
        method: "POST",
        body: fd,
      });
      if (!uploadRes.ok) {
        const msg = await safeError(uploadRes);
        throw new Error(`Upload failed: ${msg}`);
      }
      const uploadJson = (await uploadRes.json()) as UploadResponse;
      const tailorRes = await fetch(`${API_BASE}/tailor`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          resume_id: uploadJson.resume_id,
          job_description: cleanedJob,
        }),
      });
      if (!tailorRes.ok) {
        const msg = await safeError(tailorRes);
        throw new Error(`Tailor failed: ${msg}`);
      }
      const tailorJson = (await tailorRes.json()) as TailoredResponse;
      setResult(tailorJson);
    } catch (e: any) {
      setError(e?.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }, [file, jobDesc]);

  const safeError = async (res: Response) => {
    try {
      const j = await res.json();
      return j?.detail || res.statusText;
    } catch {
      return res.statusText;
    }
  };

  const disabled =
    loading || !file || jobDesc.trim().length < 200 || !!error;

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-gray-100">
      <div className="max-w-7xl mx-auto px-6 py-10">
        <header className="mb-8 flex items-center gap-3">
          <Sparkles className="h-7 w-7 text-emerald-400" />
          <h1 className="text-2xl font-semibold">
            AI Resume Tailor
          </h1>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <section
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
            className="bg-[#1a1a1a] rounded-lg p-6 border border-gray-800"
          >
            <div
              className="border-2 border-dashed border-gray-700 rounded-lg p-8 flex flex-col items-center justify-center hover:border-blue-500 transition cursor-pointer"
              onClick={() => fileInputRef.current?.click()}
            >
              <FileUp className="h-12 w-12 text-blue-400 mb-3" />
              <p className="text-sm text-gray-300 text-center">
                Drag & drop your PDF resume here, or click to browse.
              </p>
              <p className="text-xs text-gray-500 mt-1">
                Max size: 10MB. Only .pdf files accepted.
              </p>
              <input
                ref={fileInputRef}
                type="file"
                accept="application/pdf,.pdf"
                className="hidden"
                onChange={(e) => onFileSelect(e.target.files?.[0] || null)}
              />
            </div>

            {file && (
              <div className="mt-4 flex items-center gap-2 bg-[#121212] rounded px-3 py-2 border border-gray-800">
                <FileText className="h-5 w-5 text-emerald-400" />
                <span className="text-sm">
                  {file.name} • {(file.size / (1024 * 1024)).toFixed(2)} MB
                </span>
                <CheckCircle className="h-5 w-5 text-emerald-500 ml-auto" />
              </div>
            )}

            <div className="mt-6">
              <label className="block text-sm mb-2 text-gray-300">
                Job Description (min 200 characters)
              </label>
              <textarea
                value={jobDesc}
                onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setJobDesc(e.target.value)}
                placeholder="Paste the job description here..."
                className="w-full h-48 resize-y rounded-lg bg-[#121212] border border-gray-800 focus:border-blue-500 focus:ring-0 p-3 text-sm"
              />
              <div className="mt-2 text-xs text-gray-400">
                  {jobDesc.trim().length} / 2000
                </div>
            </div>

            <div className="mt-6">
              <button
                onClick={handleAnalyze}
                disabled={disabled}
                className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition ${
                  disabled
                    ? "bg-gray-700 text-gray-400 cursor-not-allowed"
                    : "bg-blue-600 hover:bg-blue-500 text-white"
                }`}
              >
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Brain className="h-4 w-4" />
                    Analyze
                  </>
                )}
              </button>
              {error && (
                <div className="mt-3 flex items-center gap-2 text-red-400 text-sm">
                  <AlertCircle className="h-4 w-4" />
                  <span>{error}</span>
                </div>
              )}
            </div>
          </section>

          <section className="bg-[#1a1a1a] rounded-lg p-6 border border-gray-800">
            {!result ? (
              <div className="text-sm text-gray-400">
                Results will appear here after analysis.
              </div>
            ) : (
              <div className="space-y-6">
                <div className="bg-[#121212] rounded-lg p-4 border border-gray-800">
                  <div className="flex items-center gap-2 mb-2">
                    <Sparkles className="h-5 w-5 text-emerald-400" />
                    <h3 className="text-sm font-semibold">Summary</h3>
                  </div>
                  <p className="text-sm text-gray-200 leading-6">
                    {result.summary_enhancement}
                  </p>
                </div>

                <div className="bg-[#121212] rounded-lg p-4 border border-gray-800">
                  <div className="flex items-center gap-2 mb-2">
                    <Tags className="h-5 w-5 text-blue-400" />
                    <h3 className="text-sm font-semibold">Keywords</h3>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {result.keyword_optimization.length === 0 ? (
                      <span className="text-xs text-gray-400">
                        No keywords suggested.
                      </span>
                    ) : (
                      result.keyword_optimization.map((kw: string) => (
                        <span
                          key={kw}
                          className="px-2 py-1 rounded-full text-xs bg-blue-600/20 border border-blue-600/40 text-blue-300"
                        >
                          {kw}
                        </span>
                      ))
                    )}
                  </div>
                </div>

                <div className="bg-[#121212] rounded-lg p-4 border border-gray-800">
                  <div className="flex items-center gap-2 mb-2">
                    <Wrench className="h-5 w-5 text-emerald-400" />
                    <h3 className="text-sm font-semibold">Skills Gap</h3>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {result.skills_gap.length === 0 ? (
                      <span className="text-xs text-gray-400">
                        No missing skills identified.
                      </span>
                    ) : (
                      result.skills_gap.map((skill: string) => (
                        <span
                          key={skill}
                          className="px-2 py-1 rounded-full text-xs bg-emerald-600/20 border border-emerald-600/40 text-emerald-300"
                        >
                          {skill}
                        </span>
                      ))
                    )}
                  </div>
                </div>

                <div className="bg-[#121212] rounded-lg p-4 border border-gray-800">
                  <div className="flex items-center gap-2 mb-2">
                    <Brain className="h-5 w-5 text-purple-400" />
                    <h3 className="text-sm font-semibold">Recommendations</h3>
                  </div>
                  <ul className="list-disc list-inside space-y-1 text-sm text-gray-200">
                    {result.recommendations.length === 0 ? (
                      <li className="text-gray-400">
                        No recommendations available.
                      </li>
                    ) : (
                      result.recommendations.map((rec: string, idx: number) => (
                        <li key={idx}>{rec}</li>
                      ))
                    )}
                  </ul>
                </div>
              </div>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}
