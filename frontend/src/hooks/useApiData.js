import { useCallback, useEffect, useState } from "react";

export default function useApiData(loader, dependencies = []) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true); setError("");
    try { setData(await loader()); }
    catch (err) { setError(err.message); }
    finally { setLoading(false); }
  }, dependencies); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => { load(); }, [load]);
  return { data, loading, error, reload: load, setData };
}
