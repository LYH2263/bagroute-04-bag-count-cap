import { useEffect, useState } from "react";
import { api } from "../api/client";
type R = { id: number; name: string; max_weight_kg: number; max_volume_l: number; max_bags: number };
export default function RoutesPage() {
  const [rows, setRows] = useState<R[]>([]);
  const [drafts, setDrafts] = useState<Record<number, string>>({});
  const [savedId, setSavedId] = useState<number | null>(null);
  const [err, setErr] = useState("");
  useEffect(() => { api<R[]>("/routes").then(setRows); }, []);

  async function save(r: R) {
    setErr(""); setSavedId(null);
    const value = Number(drafts[r.id]);
    if (!Number.isInteger(value) || value < 0) { setErr("袋数上限需为不小于 0 的整数（0 = 不限）"); return; }
    try {
      const updated = await api<R>(`/routes/${r.id}`, { method: "PATCH", body: JSON.stringify({ max_bags: value }) });
      setRows(rs => rs.map(x => (x.id === updated.id ? updated : x)));
      setDrafts(d => { const n = { ...d }; delete n[r.id]; return n; });
      setSavedId(r.id);
    } catch (e) { setErr(e instanceof Error ? e.message : String(e)); }
  }

  return (<>
    <h2>路线</h2>
    {err && <div className="err">{err}</div>}
    <table className="table"><thead><tr><th>名称</th><th>重量上限 kg</th><th>体积上限 L</th><th>袋数上限</th><th></th></tr></thead>
    <tbody>{rows.map(r => {
      const editing = r.id in drafts;
      const value = editing ? drafts[r.id] : String(r.max_bags);
      return (<tr key={r.id}>
        <td>{r.name}</td>
        <td className="mono">{r.max_weight_kg}</td>
        <td className="mono">{r.max_volume_l}</td>
        <td className="mono">
          <input
            aria-label={`${r.name} 袋数上限`}
            value={value}
            style={{ width: 90 }}
            onChange={e => setDrafts(d => ({ ...d, [r.id]: e.target.value }))}
          />
          <span style={{ marginLeft: 6, color: "#888" }}>{r.max_bags === 0 ? "不限" : `最多 ${r.max_bags} 袋`}</span>
        </td>
        <td>
          <button disabled={!editing} onClick={() => save(r)}>保存</button>
          {savedId === r.id && <span className="ok" style={{ marginLeft: 8 }}>已保存</span>}
        </td>
      </tr>);
    })}</tbody></table>
  </>);
}
