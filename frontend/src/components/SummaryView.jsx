// src/components/SummaryView.jsx
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";

export default function SummaryView({ parsed }) {
  const grading = parsed?.grading_breakdown || [];
  const textbooks = parsed?.textbooks || [];
  const howToGetA = parsed?.how_to_get_A || "";
  const workload = parsed?.weekly_workload || [];

  return (
    <div className="mt-6 space-y-6">
      <h2 className="text-lg font-semibold text-gray-800">
        Key Findings
      </h2>

      {/* Grading breakdown */}
      <section className="border border-gray-200 rounded-xl p-4 bg-white">
        <h3 className="font-semibold text-gray-800 mb-2">
          Grading breakdown
        </h3>
        {grading.length > 0 ? (
          <ul className="list-disc ml-6 space-y-1">
            {grading.map((g, i) => (
              <li key={i}>
                <span className="font-medium">
                  {g.name || "Component"}
                </span>{" "}
                —{" "}
                {g.percent != null ? `${g.percent}%` : "weight unknown"}
                {g.line && (
                  <div className="text-xs text-gray-500">
                    {g.line}
                  </div>
                )}
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-gray-500">
            No clear grading breakdown detected.
          </p>
        )}
      </section>

      {/* Textbooks */}
      <section className="border border-gray-200 rounded-xl p-4 bg-white">
        <h3 className="font-semibold text-gray-800 mb-2">
          Textbooks / readings
        </h3>
        {textbooks.length > 0 ? (
          <ul className="list-disc ml-6 space-y-1">
            {textbooks.map((t, i) => (
              <li key={i} className="text-sm text-gray-700">
                {t}
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-gray-500">
            No explicit textbooks found.
          </p>
        )}
      </section>

      {/* How to get an A */}
      <section className="border border-gray-200 rounded-xl p-4 bg-white">
        <h3 className="font-semibold text-gray-800 mb-2">
          How to get an A
        </h3>
        <p className="text-sm text-gray-700 leading-relaxed">
          {howToGetA}
        </p>
      </section>

      {/* Weekly workload */}
      <section className="border border-gray-200 rounded-xl p-4 bg-white">
        <h3 className="font-semibold text-gray-800 mb-2">
          Predicted weekly workload
        </h3>
        {workload.length > 0 ? (
          <div style={{ width: "100%", height: 260 }}>
            <ResponsiveContainer>
              <BarChart data={workload}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="week" tick={{ fontSize: 10 }} />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <p className="text-sm text-gray-500">
            Not enough date information to estimate weekly workload.
          </p>
        )}
      </section>
    </div>
  );
}
