"use client";

import { CircleMarker, MapContainer, TileLayer, Tooltip } from "react-leaflet";
import { DistrictSummary } from "@/lib/api";

// Explicit hex severity (Leaflet SVG fills are most reliable with hex).
function gapHex(score: number): string {
  if (score >= 60) return "#c0392b";
  if (score >= 40) return "#dd6b20";
  if (score >= 20) return "#c7981b";
  return "#2f9e6f";
}

const LEGEND: { label: string; color: string }[] = [
  { label: "Critical (60+)", color: "#c0392b" },
  { label: "High (40–60)", color: "#dd6b20" },
  { label: "Moderate (20–40)", color: "#c7981b" },
  { label: "Balanced (<20)", color: "#2f9e6f" },
];

export default function IndiaMap({
  districts,
  onSelect,
  selectedId,
}: {
  districts: DistrictSummary[];
  onSelect: (d: DistrictSummary) => void;
  selectedId?: number | null;
}) {
  return (
    <div className="relative h-full w-full">
      <MapContainer
        center={[22.8, 80.5]}
        zoom={5}
        minZoom={4}
        maxZoom={9}
        scrollWheelZoom
        style={{ height: "100%", width: "100%", borderRadius: 8 }}
        worldCopyJump={false}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
          maxZoom={19}
          className="map-tiles"
        />
        {districts.map((d) => {
          const selected = d.id === selectedId;
          const radius = 5 + Math.min(14, d.employment_demand / 6);
          return (
            <CircleMarker
              key={d.id}
              center={[d.latitude, d.longitude]}
              radius={selected ? radius + 3 : radius}
              pathOptions={{
                color: selected ? "#14202e" : gapHex(d.overall_gap),
                weight: selected ? 2 : 1,
                fillColor: gapHex(d.overall_gap),
                fillOpacity: 0.72,
              }}
              eventHandlers={{ click: () => onSelect(d) }}
            >
              <Tooltip direction="top" offset={[0, -4]}>
                <div className="text-xs">
                  <div className="font-semibold">{d.name}</div>
                  <div className="text-muted">{d.state}</div>
                  <div className="mt-1">
                    Gap <b>{d.overall_gap.toFixed(0)}</b> · Demand{" "}
                    {d.employment_demand.toFixed(0)} · {d.critical_gaps} critical
                  </div>
                </div>
              </Tooltip>
            </CircleMarker>
          );
        })}
      </MapContainer>

      <div className="absolute bottom-3 left-3 z-[500] card px-3 py-2 text-xs">
        <div className="label mb-1.5">Skill-gap index</div>
        <div className="flex flex-col gap-1">
          {LEGEND.map((l) => (
            <div key={l.label} className="flex items-center gap-2">
              <span
                className="h-2.5 w-2.5 rounded-full"
                style={{ background: l.color }}
              />
              <span className="text-muted">{l.label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
