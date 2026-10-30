"use client";

import { useEffect, useRef, useState } from "react";
import { Layers, Maximize2 } from "lucide-react";

interface MapPoint {
  id: string;
  latitude: number;
  longitude: number;
  severity: string;
  fatalities: number;
  injured: number;
  state?: string;
  district?: string;
  road_type?: string;
  collision_type?: string;
}

interface MapProps {
  points: MapPoint[];
  center?: [number, number]; // [lon, lat]
  zoom?: number;
  className?: string;
}

const MAP_STYLES = [
  { id: "dark", name: "Midnight Dark", url: "https://tiles.openfreemap.org/styles/dark" },
  { id: "fiord", name: "Fiord Blue", url: "https://tiles.openfreemap.org/styles/fiord" },
  { id: "liberty", name: "Street Vector", url: "https://tiles.openfreemap.org/styles/liberty" },
  {
    id: "osm",
    name: "OSM Standard",
    url: {
      version: 8,
      sources: {
        osm: {
          type: "raster",
          tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
          tileSize: 256,
          attribution: "© OpenStreetMap contributors",
        },
      },
      layers: [
        {
          id: "osm-tiles",
          type: "raster",
          source: "osm",
          minzoom: 0,
          maxzoom: 19,
        },
      ],
    },
  },
];

export function MapLibreMap({
  points,
  center = [78.9629, 20.5937], // India geographic centroid default
  zoom = 4.5,
  className = "w-full h-[520px]",
}: MapProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const mapInstance = useRef<any>(null);
  const markersRef = useRef<any[]>([]);
  const [loaded, setLoaded] = useState(false);
  const [activeStyle, setActiveStyle] = useState<string>("dark");

  // Initialize Map
  useEffect(() => {
    let isMounted = true;

    async function initMap() {
      if (!mapContainer.current || mapInstance.current) return;

      try {
        const maplibregl = (await import("maplibre-gl")).default;

        // Ensure MapLibre stylesheet is dynamically attached
        if (!document.getElementById("maplibre-css")) {
          const link = document.createElement("link");
          link.id = "maplibre-css";
          link.rel = "stylesheet";
          link.href = "https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.css";
          document.head.appendChild(link);
        }

        // Default to OpenFreeMap Dark style (zero API key, zero watermark, high performance vector tiles)
        const initialStyle = MAP_STYLES.find((s) => s.id === activeStyle)?.url || "https://tiles.openfreemap.org/styles/dark";

        const map = new maplibregl.Map({
          container: mapContainer.current,
          style: initialStyle as any,
          center: center,
          zoom: zoom,
          attributionControl: {
            compact: true,
            customAttribution: "OpenFreeMap | OpenStreetMap contributors",
          },
        });

        map.addControl(new maplibregl.NavigationControl({ showCompass: true }), "top-right");

        map.on("load", () => {
          if (!isMounted) return;
          map.resize();
          mapInstance.current = map;
          setLoaded(true);

          // Fit bounds if points already present
          if (points && points.length > 0) {
            fitBoundsToPoints(map, points);
          }
        });

        // Safe resize after layout settlement
        setTimeout(() => {
          if (isMounted && map) {
            map.resize();
          }
        }, 300);
      } catch (err: any) {
        console.error("MapLibre GL failed to initialize:", err);
      }
    }

    initMap();

    return () => {
      isMounted = false;
      if (mapInstance.current) {
        mapInstance.current.remove();
        mapInstance.current = null;
      }
    };
  }, []);

  // Helper to fit bounding box to all points
  const fitBoundsToPoints = async (map: any, pts: MapPoint[]) => {
    if (!map || !pts || pts.length === 0) return;
    try {
      const maplibregl = (await import("maplibre-gl")).default;
      const bounds = new maplibregl.LngLatBounds();
      let validCount = 0;

      pts.forEach((p) => {
        if (p.longitude && p.latitude && !isNaN(p.longitude) && !isNaN(p.latitude)) {
          // Verify reasonable coordinate bounds
          if (p.latitude >= -90 && p.latitude <= 90 && p.longitude >= -180 && p.longitude <= 180) {
            bounds.extend([p.longitude, p.latitude]);
            validCount++;
          }
        }
      });

      if (validCount > 0 && !bounds.isEmpty()) {
        map.fitBounds(bounds, {
          padding: 60,
          maxZoom: 11,
          duration: 900,
        });
      }
    } catch (e) {
      console.warn("Failed to auto-fit bounds:", e);
    }
  };

  // Change Basemap Style
  const handleStyleChange = (styleId: string) => {
    setActiveStyle(styleId);
    if (!mapInstance.current) return;
    const target = MAP_STYLES.find((s) => s.id === styleId);
    if (target) {
      mapInstance.current.setStyle(target.url as any);
    }
  };

  // Re-render Markers when points change or map loads
  useEffect(() => {
    if (!mapInstance.current || !loaded) return;

    const map = mapInstance.current;
    import("maplibre-gl").then(({ default: maplibregl }) => {
      // Clear existing markers
      markersRef.current.forEach((m) => m.remove());
      markersRef.current = [];

      // Render top 400 points to keep DOM smooth and responsive
      const samplePoints = points.slice(0, 450);

      samplePoints.forEach((p) => {
        if (!p.latitude || !p.longitude) return;

        const isFatal = (p.severity && p.severity.toLowerCase().includes("fatal")) || p.fatalities > 0;
        const hasInjury = p.injured > 0;
        const color = isFatal ? "#ef4444" : hasInjury ? "#f59e0b" : "#06b6d4";

        const el = document.createElement("div");
        el.className = "traffic-marker cursor-pointer transition-transform hover:scale-150 duration-150";
        el.style.width = isFatal ? "12px" : "9px";
        el.style.height = isFatal ? "12px" : "9px";
        el.style.backgroundColor = color;
        el.style.borderRadius = "50%";
        el.style.border = isFatal ? "2px solid #ffffff" : "1.5px solid #ffffff";
        el.style.boxShadow = isFatal
          ? "0 0 10px rgba(239, 68, 68, 0.8), 0 2px 4px rgba(0,0,0,0.5)"
          : hasInjury
          ? "0 0 8px rgba(245, 158, 11, 0.6), 0 2px 4px rgba(0,0,0,0.4)"
          : "0 0 6px rgba(6, 182, 212, 0.5), 0 2px 4px rgba(0,0,0,0.4)";

        const popupContent = `
          <div style="font-family: inherit; font-size: 12px; line-height: 1.4; color: #0f172a; padding: 2px;">
            <div style="font-weight: 700; font-size: 13px; margin-bottom: 4px; color: ${color}; display: flex; align-items: center; justify-content: space-between;">
              <span>${p.severity || "Incident"}</span>
              <span style="font-size: 10px; background: #f1f5f9; padding: 1px 5px; border-radius: 4px; color: #475569;">#${p.id || "REC"}</span>
            </div>
            <div style="margin-bottom: 2px;"><strong>Jurisdiction:</strong> ${p.district || "District"}, ${p.state || ""}</div>
            <div style="margin-bottom: 2px;"><strong>Corridor / Road:</strong> ${p.road_type || "Standard Highway"}</div>
            <div style="margin-bottom: 2px;">
              <strong>Casualties:</strong> 
              <span style="color: #dc2626; font-weight: 700;">${p.fatalities || 0} Fatal</span> | 
              <span style="color: #d97706; font-weight: 600;">${p.injured || 0} Injured</span>
            </div>
            <div><strong>Collision Type:</strong> ${p.collision_type || "Vehicular"}</div>
          </div>
        `;

        const popup = new maplibregl.Popup({ offset: 14, closeButton: true, maxWidth: "260px" }).setHTML(popupContent);

        const marker = new maplibregl.Marker({ element: el })
          .setLngLat([p.longitude, p.latitude])
          .setPopup(popup)
          .addTo(map);

        markersRef.current.push(marker);
      });

      // Automatically frame points on map
      fitBoundsToPoints(map, points);
    });
  }, [points, loaded]);

  return (
    <div className={`relative rounded-xl overflow-hidden border border-slate-700/60 bg-[#090d16] shadow-xl ${className}`}>
      {/* Map Container */}
      <div ref={mapContainer} className="w-full h-full" />

      {/* Top Left: Basemap Style Switcher & Recenter */}
      <div className="absolute top-3 left-3 flex items-center gap-2 z-10">
        <div className="flex items-center gap-1 bg-slate-900/90 backdrop-blur-md border border-slate-700/80 rounded-lg p-1 shadow-lg">
          <Layers className="w-3.5 h-3.5 text-cyan-400 ml-1.5 mr-0.5" />
          {MAP_STYLES.map((st) => (
            <button
              key={st.id}
              onClick={() => handleStyleChange(st.id)}
              className={`px-2 py-1 text-[11px] font-semibold rounded-md transition-all ${
                activeStyle === st.id
                  ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-xs"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
              }`}
            >
              {st.name}
            </button>
          ))}
        </div>

        <button
          onClick={() => fitBoundsToPoints(mapInstance.current, points)}
          title="Recenter and Fit All Incidents"
          className="flex items-center gap-1.5 px-2.5 py-1.5 bg-slate-900/90 hover:bg-slate-800 backdrop-blur-md border border-slate-700/80 rounded-lg text-slate-200 text-[11px] font-medium shadow-lg transition"
        >
          <Maximize2 className="w-3 h-3 text-cyan-400" />
          <span>Fit Extent</span>
        </button>
      </div>

      {/* Bottom Left: Map Legend Overlay */}
      <div className="absolute bottom-4 left-4 bg-slate-900/95 backdrop-blur-md border border-slate-700/80 rounded-xl p-3 text-xs z-10 shadow-xl min-w-[190px]">
        <div className="flex items-center justify-between font-bold text-slate-300 mb-2.5 tracking-wider uppercase text-[10px] border-b border-slate-800 pb-1.5">
          <span>Incident Severity</span>
          <span className="text-cyan-400 font-mono text-[9px] font-normal lowercase">no-key vector</span>
        </div>
        <div className="space-y-2">
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-red-500 shadow-[0_0_6px_rgba(239,68,68,0.8)]"></span>
              <span className="text-slate-200 font-medium">Fatal Collision</span>
            </div>
            <span className="text-[10px] font-mono text-red-400 font-semibold">
              {points.filter((p) => (p.severity && p.severity.toLowerCase().includes("fatal")) || p.fatalities > 0).length}
            </span>
          </div>
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-400 shadow-[0_0_6px_rgba(245,158,11,0.8)]"></span>
              <span className="text-slate-200 font-medium">Casualty / Injury</span>
            </div>
            <span className="text-[10px] font-mono text-amber-300 font-semibold">
              {points.filter((p) => !(p.severity && p.severity.toLowerCase().includes("fatal")) && p.injured > 0).length}
            </span>
          </div>
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 shadow-[0_0_6px_rgba(6,182,212,0.8)]"></span>
              <span className="text-slate-200 font-medium">Minor / Damage</span>
            </div>
            <span className="text-[10px] font-mono text-cyan-300 font-semibold">
              {points.filter((p) => !(p.severity && p.severity.toLowerCase().includes("fatal")) && (!p.injured || p.injured === 0)).length}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
