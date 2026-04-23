"use client";

import { useEffect, useState } from "react";

import { fetchApi } from "@/lib/api";

type EquipmentOption = {
  id: number;
  tag: string;
  name: string;
  sector: string;
  active: boolean;
};

type UserSummary = {
  id: number;
  name: string;
  username: string;
  role: string;
  active: boolean;
};

type OccurrenceRecord = {
  id: number;
  equipment_id: number;
  severity: "baixa" | "media" | "alta" | "critica";
  safety_risk: boolean;
  production_stop: boolean;
  description: string;
  occurred_at: string;
  equipment: EquipmentOption;
  author: UserSummary;
  created_at: string;
  updated_at: string;
};

type MeasurementRecord = {
  id: number;
  equipment_id: number;
  measurement_type: "vibracao" | "temperatura" | "tensao" | "corrente";
  value: number;
  unit: string;
  measured_at: string;
  equipment: EquipmentOption;
  author: UserSummary;
  created_at: string;
  updated_at: string;
};

type HistoryResponse = {
  equipment: EquipmentOption;
  occurrences: OccurrenceRecord[];
  measurements: MeasurementRecord[];
};

export default function HistoryPage() {
  const [equipments, setEquipments] = useState<EquipmentOption[]>([]);
  const [selectedEquipmentId, setSelectedEquipmentId] = useState("");
  const [history, setHistory] = useState<HistoryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadCatalog() {
    const data = await fetchApi<EquipmentOption[]>("/equipment-history/catalog");
    setEquipments(data);
    if (!selectedEquipmentId && data.length > 0) {
      setSelectedEquipmentId(String(data[0].id));
      return data[0].id;
    }
    return selectedEquipmentId ? Number(selectedEquipmentId) : null;
  }

  async function loadHistory(equipmentId?: number) {
    const targetId = equipmentId ?? (selectedEquipmentId ? Number(selectedEquipmentId) : null);
    if (!targetId) {
      setLoading(false);
      return;
    }

    setLoading(true);
    setError("");
    try {
      const data = await fetchApi<HistoryResponse>(`/equipment-history/${targetId}`);
      setHistory(data);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Falha ao carregar historico.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    async function bootstrap() {
      try {
        const initialEquipmentId = await loadCatalog();
        if (initialEquipmentId) {
          await loadHistory(initialEquipmentId);
        }
      } catch (requestError) {
        setError(requestError instanceof Error ? requestError.message : "Falha ao preparar pagina.");
        setLoading(false);
      }
    }

    void bootstrap();
  }, []);

  return (
    <section className="stack-lg">
      <header className="panel stack">
        <p className="helper-text">Consulta operacional</p>
        <h2 className="section-title">Historico por equipamento</h2>
        <p className="helper-text">Consolida ocorrencias e medicoes para leitura rapida antes de agir no equipamento.</p>
      </header>

      <section className="panel stack">
        <div className="toolbar-inline">
          <select
            className="input"
            onChange={(event) => setSelectedEquipmentId(event.target.value)}
            value={selectedEquipmentId}
          >
            <option value="">Selecione um equipamento</option>
            {equipments.map((equipment) => (
              <option key={equipment.id} value={equipment.id}>
                {equipment.tag} - {equipment.name}
              </option>
            ))}
          </select>
          <button className="secondary-button" onClick={() => void loadHistory()} type="button">
            Consultar
          </button>
        </div>

        {loading ? <p className="helper-text">Carregando historico...</p> : null}
        {error ? <div className="error-box">{error}</div> : null}

        {history ? (
          <div className="stack-lg">
            <div className="detail-box stack">
              <h3 className="section-title">
                {history.equipment.tag} - {history.equipment.name}
              </h3>
              <p className="helper-text">
                Setor {history.equipment.sector} | {history.equipment.active ? "Ativo" : "Inativo"}
              </p>
            </div>

            <div className="history-grid">
              <article className="panel stack">
                <div className="toolbar-inline">
                  <h3 className="section-title">Ocorrencias</h3>
                  <span className="status-pill">{history.occurrences.length}</span>
                </div>
                <div className="table-list">
                  {history.occurrences.length === 0 ? (
                    <p className="helper-text">Nenhuma ocorrencia registrada para este equipamento.</p>
                  ) : (
                    history.occurrences.map((occurrence) => (
                      <div
                        className={`table-row ${occurrence.production_stop ? "table-row-danger" : ""}`}
                        key={occurrence.id}
                      >
                        <div className="stack-sm">
                          <div className="toolbar-inline">
                            <span className={`status-pill severity-${occurrence.severity}`}>
                              {occurrence.severity}
                            </span>
                            {occurrence.production_stop ? (
                              <span className="status-pill status-stop">Parada</span>
                            ) : null}
                          </div>
                          <p>{occurrence.description}</p>
                          <p className="helper-text">
                            {occurrence.author.name} | {new Date(occurrence.occurred_at).toLocaleString("pt-BR")}
                          </p>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </article>

              <article className="panel stack">
                <div className="toolbar-inline">
                  <h3 className="section-title">Medicoes</h3>
                  <span className="status-pill">{history.measurements.length}</span>
                </div>
                <div className="table-list">
                  {history.measurements.length === 0 ? (
                    <p className="helper-text">Nenhuma medicao registrada para este equipamento.</p>
                  ) : (
                    history.measurements.map((measurement) => (
                      <div className="table-row" key={measurement.id}>
                        <div className="stack-sm">
                          <div className="toolbar-inline">
                            <span className="status-pill">{measurement.measurement_type}</span>
                            <strong>
                              {measurement.value} {measurement.unit}
                            </strong>
                          </div>
                          <p className="helper-text">
                            {measurement.author.name} | {new Date(measurement.measured_at).toLocaleString("pt-BR")}
                          </p>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </article>
            </div>
          </div>
        ) : null}
      </section>
    </section>
  );
}
