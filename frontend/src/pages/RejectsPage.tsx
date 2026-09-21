import { useEffect, useState } from "react";
import { api } from "../api/client";
type Route = { id: number; name: string };
type Rj = { id: number; route_id: number; stop_id: number; stop_name: string; reason: string; created_at: string };
export default function RejectsPage() {
  const [rows, setRows] = useState<Rj[]>([]);
  const [routes, setRoutes] = useState<Route[]>([]);
  useEffect(() => {
    api<Rj[]>("/rejects").then(setRows);
    api<Route[]>("/routes").then(setRoutes).catch(() => {});
  }, []);
  const routeName = (id: number) => routes.find(r => r.id === id)?.name ?? `路线 ${id}`;
  return (<>
    <h2>拒收</h2>
    <table className="table"><thead><tr><th>时间</th><th>路线</th><th>订户</th><th>原因</th></tr></thead>
    <tbody>{rows.map(r => <tr key={r.id}>
      <td className="mono">{new Date(r.created_at).toLocaleString()}</td>
      <td>{routeName(r.route_id)}</td>
      <td>{r.stop_name}</td>
      <td className={r.reason.includes("袋数用尽") ? "err" : ""}>{r.reason}</td></tr>)}
      {!rows.length && <tr><td colSpan={4}>暂无拒收</td></tr>}
    </tbody></table>
  </>);
}
