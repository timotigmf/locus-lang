const escape = (s) =>
  String(s).replace(
    /[&<>"']/g,
    (c) =>
      ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&apos;",
      })[c],
  );
export function drawMap(data) {
  const positions = new Map();
  let component = 0;
  for (const room of data.rooms) {
    if (positions.has(room.id)) continue;
    positions.set(room.id, { x: component * 300, y: 0 });
    const queue = [room.id];
    for (let i = 0; i < queue.length; i++) {
      const id = queue[i],
        p = positions.get(id);
      for (const link of data.links) {
        const next =
          link.from === id ? link.to : link.to === id ? link.from : null;
        if (next && !positions.has(next)) {
          const sign = link.from === id ? 1 : -1,
            offsets = {
              nord: [0, -155],
              sud: [0, 155],
              est: [245, 0],
              ovest: [-245, 0],
              nordest: [245, -155],
              sudest: [245, 155],
              sudovest: [-245, 155],
              nordovest: [-245, -155],
              su: [0, -155],
              giù: [0, 155],
              dentro: [245, 155],
              fuori: [-245, -155],
            },
            [dx, dy] = offsets[link.direction] ?? [0, -155];
          let x = p.x + dx * sign,
            y = p.y + dy * sign;
          while ([...positions.values()].some((p) => p.x === x && p.y === y)) {
            if (dx) y += 155;
            else x += 245;
          }
          positions.set(next, { x, y });
          queue.push(next);
        }
      }
    }
    component++;
  }
  const values = [...positions.values()];
  const minX = Math.min(0, ...values.map((p) => p.x)),
    minY = Math.min(0, ...values.map((p) => p.y));
  for (const p of values) {
    p.x += 45 - minX;
    p.y += 60 - minY;
  }
  const width = Math.max(440, ...values.map((p) => p.x + 250)),
    height = Math.max(300, ...values.map((p) => p.y + 120));
  let body = "";
  for (const link of data.links) {
    const a = positions.get(link.from),
      b = positions.get(link.to);
    if (!a || !b) continue;
    const door = data.doors.find(
      (d) =>
        (d.from === link.from && d.to === link.to) ||
        (d.to === link.from && d.from === link.to),
    );
    const directions = link.oneWay
      ? link.direction + " (solo andata)"
      : ({
          nord: "nord / sud",
          est: "est / ovest",
          nordest: "nordest / sudovest",
          sudest: "sudest / nordovest",
          su: "su / giù",
          dentro: "dentro / fuori",
        }[link.direction] ?? link.direction);
    const topologyStyle = ["su", "giù"].includes(link.direction)
      ? ' stroke-dasharray="6 4"'
      : ["dentro", "fuori"].includes(link.direction)
        ? ' stroke-dasharray="2 3"'
        : "";
    const arrow = link.oneWay ? ' marker-end="url(#freccia-senso-unico)"' : "";
    body += `<path d="M${a.x + 95},${a.y + 35} L${b.x + 95},${b.y + 35}" stroke="#9eb8ad" stroke-width="2"${topologyStyle}${arrow} fill="none"/><text x="${(a.x + b.x) / 2 + 105}" y="${(a.y + b.y) / 2 + 35}" fill="#687f72" font-size="10">${escape(door?.label ?? directions)}</text>`;
  }
  for (const r of data.rooms) {
    const p = positions.get(r.id);
    const initial = r.id === data.entry;
    const vehicles = (data.vehicles ?? [])
      .filter((vehicle) => vehicle.room === r.id)
      .map((vehicle) => vehicle.label)
      .join(", ");
    const vehicleLine = vehicles
      ? `<text x="${p.x + 16}" y="${p.y + 62}" font-size="9" fill="#72583d">MEZZO · ${escape(vehicles.length > 24 ? vehicles.slice(0, 23) + "…" : vehicles)}</text>`
      : "";
    body += `<g><title>${escape(r.label)}</title><rect x="${p.x}" y="${p.y}" width="190" height="70" rx="8" fill="${initial ? "#e5eee2" : "#fffefa"}" stroke="${initial ? "#698c68" : "#b8cbbf"}"/><text x="${p.x + 16}" y="${p.y + 22}" font-size="8" letter-spacing="1" fill="#6e8677">${initial ? "PUNTO INIZIALE" : "LUOGO"}</text><text x="${p.x + 16}" y="${p.y + 46}" font-size="13" fill="#294a3e">${escape(r.label.length > 23 ? r.label.slice(0, 22) + "…" : r.label)}</text>${vehicleLine}</g>`;
  }
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" role="img" aria-label="Mappa dei luoghi" font-family="system-ui,sans-serif"><title>Mappa LOCUS</title><defs><marker id="freccia-senso-unico" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#9eb8ad"/></marker></defs><rect width="100%" height="100%" fill="#f8fbf7"/>${body}<text x="20" y="25" font-size="10" fill="#758b7c">N ↑ · LOCUS / ATLANTE</text></svg>`;
}
