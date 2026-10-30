"use client";

import { useEffect, useRef, useState } from "react";

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

export function MapLibreMap({
  points,
  center = [78.9629, 20.5937], // India center default
  zoom = 4,
  className = "w-full h-[500px]",
}: MapProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const mapInstance = useRef<any>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    let isMounted = true;

    async function initMap() {
      if (!mapContainer.current || mapInstance.current) return;

      try {
        const maplibregl = (await import("maplibre-gl")).default;
        // Inject MapLibre CSS dynamically if not present
        if (!document.getElementById("maplibre-css")) {
          const link = document.createElement("link");
          link.id = "maplibre-css";
          link.rel = "stylesheet";
          link.href = "https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.css";
          document.head.appendChild(link);
        }

        const map = new maplibregl.Map({
          container: mapContainer.current,
          style: {
            version: 8,
            sources: {
              osm: {
                type: "raster",
                tiles: [
                  "https://a.basemaps.cartocdn.com/light_all/{z}/{x}/{y}@2x.png",
                  "https://b.basemaps.cartocdn.com/light_all/{z}/{x}/{y}@2x.png",
                  "https://c.basemaps.cartocdn.com/light_all/{z}/{x}/{y}@2x.png",
                ],
                tileSize: 256,
                attribution: "© OpenStreetMap contributors, © CARTO",
              },
            },
            layers: [
              {
                id: "osm-layer",
                type: "raster",
                source: "osm",
                minzoom: 0,
                maxzoom: 19,
              },
            ],
          },
          center: center,
          zoom: zoom,
        });

        map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");

        map.on("load", () => {
          if (!isMounted) return;
          map.resize();
          mapInstance.current = map;
          setLoaded(true);
        });

        // Trigger resize after a short delay to account for layout shifts
        setTimeout(() => {
          if (isMounted && map) {
            map.resize();
          }
        }, 500);
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

  // Update Markers when points change
  useEffect(() => {
    if (!mapInstance.current || !loaded) return;

    const map = mapInstance.current;
    import("maplibre-gl").then(({ default: maplibregl }) => {
      // Clear existing markers
      const existingMarkers = document.querySelectorAll(".traffic-marker");
      existingMarkers.forEach((m) => m.remove());

      // Add markers
      const samplePoints = points.slice(0, 400); // Prevent DOM overload

      samplePoints.forEach((p) => {
        if (!p.latitude || !p.longitude) return;

        const isFatal = p.severity.toLowerCase().includes("fatal") || p.fatalities > 0;
        const color = isFatal ? "#dc2626" : p.injured > 0 ? "#d97706" : "#0a545c";

        const el = document.createElement("div");
        el.className = "traffic-marker cursor-pointer transition-transform hover:scale-125";
        el.style.width = isFatal ? "12px" : "8px";
        el.style.height = isFatal ? "12px" : "8px";
        el.style.backgroundColor = color;
        el.style.borderRadius = "50%";
        el.style.border = "1.5px solid #ffffff";
        el.style.boxShadow = `0 1px 4px rgba(0,0,0,0.25)`;

        const popup = new maplibregl.Popup({ offset: 12 }).setHTML(`
          <div style="font-family: inherit; font-size: 12px; color: #0f172a;">
            <div style="font-weight: 700; margin-bottom: 4px; color: ${color};">
              ${p.severity}
            </div>
            <div><strong>Location:</strong> ${p.district || "Unknown"}, ${p.state || ""}</div>
            <div><strong>Road Type:</strong> ${p.road_type || "N/A"}</div>
            <div><strong>Fatalities:</strong> ${p.fatalities} | <strong>Injured:</strong> ${p.injured}</div>
            <div><strong>Collision:</strong> ${p.collision_type || "N/A"}</div>
          </div>
        `);

        new maplibregl.Marker({ element: el })
          .setLngLat([p.longitude, p.latitude])
          .setPopup(popup)
          .addTo(map);
      });
    });
  }, [points, loaded]);

  return (
    <div className={`relative rounded-xl overflow-hidden border border-slate-200 bg-white shadow-sm ${className}`}>
      <div ref={mapContainer} className="w-full h-full" />
      
      {/* Map Legend Overlay */}
      <div className="absolute bottom-4 left-4 bg-white/95 backdrop-blur border border-slate-200 rounded-lg p-3 text-xs z-10 shadow-md">
        <div className="font-bold text-slate-800 mb-2 tracking-wider uppercase text-[10px]">
          Incident Severity
        </div>
        <div className="space-y-1.5">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-red-600 shadow-sm"></span>
            <span className="text-slate-700 font-medium">Fatal Collision</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-600 shadow-sm"></span>
            <span className="text-slate-700 font-medium">Casualty / Injury</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-brand-teal shadow-sm"></span>
            <span className="text-slate-700 font-medium">Minor / Damage Only</span>
          </div>
        </div>
      </div>
    </div>
  );
}
