import { useEffect, useState } from "react";
import { api } from "../api/client";
type R = { id: number; name: string; max_weight_kg: number; max_volume_l: number; max_bags: number | null };
export default function RoutesPage() {
  const [rows, setRows] = useState<R[]>([]);
  const [draft, setDraft] = useState<Record<number, string>>({});
  const [msg, setMsg] = useState(""); const [err, setErr] = useState("");
  useEffect(() => {
    api<R[]>("/routes").then(rs => {
      setRows(rs);
      setDraft(Object.fromEntries(rs.map(r => [r.id, r.max_bags == null ? "" : String(r.max_bags)])));
    });
  }, []);
  async function save(r: R) {
    setMsg(""); setErr("");
    const raw = (draft[r.id] ?? "").trim();
    const v = raw === "" ? null : Number(raw);
    if (v !== null && (!Number.isInteger(v) || v < 1)) { setErr("袋数上限需为正整数，或留空表示不限"); return; }
    try {
      const out = await api<R>(`/routes/${r.id}`, { method: "PATCH", body: JSON.stringify({ max_bags: v }) });
      setRows(rows.map(x => (x.id === r.id ? out : x)));
      setMsg(`已保存 ${r.name}：袋数上限 ${out.max_bags ?? "不限"}`);
    } catch (e) { setErr(e instanceof Error ? e.message : String(e)); }
  }
  return (<>
    <h2>路线</h2>
    {msg && <div className="ok">{msg}</div>}
    {err && <div className="err">{err}</div>}
    <table className="table"><thead><tr><th>名称</th><th>重量上限 kg</th><th>体积上限 L</th><th>袋数上限</th><th></th></tr></thead>
    <tbody>{rows.map(r => <tr key={r.id}><td>{r.name}</td><td className="mono">{r.max_weight_kg}</td><td className="mono">{r.max_volume_l}</td>
      <td><input className="mono" style={{ width: "6rem" }} type="number" min={1} step={1} placeholder="不限"
        value={draft[r.id] ?? ""} onChange={e => setDraft({ ...draft, [r.id]: e.target.value })} /></td>
      <td><button onClick={() => save(r)}>保存</button></td></tr>)}</tbody></table>
  </>);
}
