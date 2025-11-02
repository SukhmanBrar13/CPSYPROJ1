import { Fragment } from "react";

type AvgItem = {
  diet_type: string;
  avg_protein_g: number;
  avg_carbs_g: number;
  avg_fat_g: number;
};

function colorScale(v: number, min: number, max: number) {
  if (max <= min) return "rgb(229 231 235)";
  const t = (v - min) / (max - min);
  const r = Math.round(14 + t * (245 - 14));
  const g = Math.round(165 + t * (158 - 165));
  const b = Math.round(233 + t * (11 - 233));
  return `rgb(${r} ${g} ${b})`;
}

export default function AvgHeatmap({ data }: { data: AvgItem[] }) {
  const rows = data.map(d => ({
    diet: d.diet_type,
    Protein: d.avg_protein_g,
    Carbs: d.avg_carbs_g,
    Fat: d.avg_fat_g,
  }));

  const vals = rows.flatMap(r => [r.Protein, r.Carbs, r.Fat]);
  const min = Math.min(...vals);
  const max = Math.max(...vals);

  return (
    <div className="h-full w-full flex flex-col">
      <div className="text-xs text-gray-600 mb-2">
        Higher value = darker cell
      </div>

      <div className="min-h-0 flex-1 overflow-auto pr-1">
        <div
          className="grid gap-2"
          style={{ gridTemplateColumns: "110px repeat(3, 1fr)" }}
        >
          <div />
          {["Protein", "Carbs", "Fat"].map(h => (
            <div key={h} className="text-xs font-medium text-gray-700 text-center">
              {h}
            </div>
          ))}

          {rows.map(r => (
            <Fragment key={r.diet}>
              <div className="text-xs text-gray-700 truncate">{r.diet}</div>
              {(["Protein","Carbs","Fat"] as const).map(k => (
                <div
                  key={k}
                  className="h-7 rounded"
                  title={`${k}: ${Number(r[k]).toFixed(2)}`}
                  style={{ background: colorScale(Number(r[k]), min, max) }}
                />
              ))}
            </Fragment>
          ))}
        </div>
      </div>
    </div>
  );
}