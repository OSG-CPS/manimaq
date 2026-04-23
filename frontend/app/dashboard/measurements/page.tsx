"use client";

import { FormEvent, useEffect, useState } from "react";

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

const defaultUnits: Record<MeasurementRecord["measurement_type"], string> = {
  vibracao: "mm/s",
  temperatura: "C",
  tensao: "V",
  corrente: "A",
};

function getDefaultDateTimeLocal() {
  const now = new Date();
  const adjusted = new Date(now.getTime() - now.getTimezoneOffset() * 60000);
  return adjusted.toISOString().slice(0, 16);
}

function toApiDateTime(value: string) {
  return value ? new Date(value).toISOString() : null;
}

export default function MeasurementsPage() {
  const [equipments, setEquipments] = useState<EquipmentOption[]>([]);
  const [measurements, setMeasurements] = useState<MeasurementRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [filterType, setFilterType] = useState("");
  const [form, setForm] = useState({
    equipment_id: "",
    measurement_type: "vibracao" as MeasurementRecord["measurement_type"],
    value: "",
    unit: defaultUnits.vibracao,
    measured_at: getDefaultDateTimeLocal(),
  });

  async function loadEquipments() {
    const data = await fetchApi<EquipmentOption[]>("/equipment-history/catalog");
    setEquipments(data);
    if (!form.equipment_id && data.length > 0) {
      setForm((current) => ({ ...current, equipment_id: String(data[0].id) }));
    }
  }

  async function loadMeasurements(type = filterType) {
    setLoading(true);
    setError("");
    try {
      const suffix = type ? `?measurement_type=${encodeURIComponent(type)}` : "";
      const data = await fetchApi<MeasurementRecord[]>(`/measurements${suffix}`);
      setMeasurements(data);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Falha ao carregar medicoes.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    async function bootstrap() {
      try {
        await Promise.all([loadEquipments(), loadMeasurements("")]);
      } catch (requestError) {
        setError(requestError instanceof Error ? requestError.message : "Falha ao preparar pagina.");
        setLoading(false);
      }
    }

    void bootstrap();
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    setMessage("");

    try {
      await fetchApi<MeasurementRecord>("/measurements", {
        method: "POST",
        body: JSON.stringify({
          equipment_id: Number(form.equipment_id),
          measurement_type: form.measurement_type,
          value: Number(form.value),
          unit: form.unit,
          measured_at: toApiDateTime(form.measured_at),
        }),
      });
      setMessage("Medicao registrada com sucesso.");
      setForm((current) => ({
        ...current,
        value: "",
        measured_at: getDefaultDateTimeLocal(),
      }));
      await loadMeasurements();
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Falha ao salvar medicao.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="stack-lg">
      <header className="panel stack">
        <p className="helper-text">Fluxo operacional</p>
        <h2 className="section-title">Medicoes</h2>
        <p className="helper-text">Lance vibracao, temperatura, tensao e corrente com unidade padrao ou customizada.</p>
      </header>

      <section className="module-grid">
        <article className="panel stack">
          <div className="toolbar-inline">
            <select className="input" onChange={(event) => setFilterType(event.target.value)} value={filterType}>
              <option value="">Todos os tipos</option>
              <option value="vibracao">Vibracao</option>
              <option value="temperatura">Temperatura</option>
              <option value="tensao">Tensao</option>
              <option value="corrente">Corrente</option>
            </select>
            <button className="secondary-button" onClick={() => void loadMeasurements()} type="button">
              Filtrar
            </button>
          </div>

          {loading ? <p className="helper-text">Carregando medicoes...</p> : null}
          {error ? <div className="error-box">{error}</div> : null}
          {message ? <div className="success-box">{message}</div> : null}

          <div className="table-list">
            {measurements.map((measurement) => (
              <div className="table-row" key={measurement.id}>
                <div className="stack-sm">
                  <div className="toolbar-inline">
                    <strong>{measurement.equipment.tag}</strong>
                    <span className="status-pill">{measurement.measurement_type}</span>
                  </div>
                  <p className="helper-text">
                    {measurement.equipment.name} | {measurement.author.name} |{" "}
                    {new Date(measurement.measured_at).toLocaleString("pt-BR")}
                  </p>
                </div>
                <div className="metric-inline">
                  {measurement.value} {measurement.unit}
                </div>
              </div>
            ))}
          </div>
        </article>

        <article className="panel stack measurements-form-panel">
          <div className="stack-sm">
            <h3 className="section-title">Nova medicao</h3>
            <p className="helper-text">Se a data ficar como esta, o registro entra com o horario atual.</p>
          </div>

          <form className="stack" onSubmit={handleSubmit}>
            <label className="label" htmlFor="measurement-equipment">
              Equipamento
              <select
                className="input"
                id="measurement-equipment"
                onChange={(event) => setForm((current) => ({ ...current, equipment_id: event.target.value }))}
                required
                value={form.equipment_id}
              >
                <option value="">Selecione</option>
                {equipments.map((equipment) => (
                  <option key={equipment.id} value={equipment.id}>
                    {equipment.tag} - {equipment.name}
                  </option>
                ))}
              </select>
            </label>

            <label className="label" htmlFor="measurement-type">
              Tipo
              <select
                className="input"
                id="measurement-type"
                onChange={(event) => {
                  const nextType = event.target.value as MeasurementRecord["measurement_type"];
                  setForm((current) => ({
                    ...current,
                    measurement_type: nextType,
                    unit: defaultUnits[nextType],
                  }));
                }}
                value={form.measurement_type}
              >
                <option value="vibracao">Vibracao</option>
                <option value="temperatura">Temperatura</option>
                <option value="tensao">Tensao</option>
                <option value="corrente">Corrente</option>
              </select>
            </label>

            <label className="label" htmlFor="measurement-value">
              Valor
              <input
                className="input"
                id="measurement-value"
                min="0.01"
                onChange={(event) => setForm((current) => ({ ...current, value: event.target.value }))}
                required
                step="0.01"
                type="number"
                value={form.value}
              />
            </label>

            <label className="label" htmlFor="measurement-unit">
              Unidade
              <input
                className="input"
                id="measurement-unit"
                onChange={(event) => setForm((current) => ({ ...current, unit: event.target.value }))}
                required
                value={form.unit}
              />
            </label>

            <label className="label" htmlFor="measurement-measured-at">
              Data e hora da medicao
              <input
                className="input"
                id="measurement-measured-at"
                onChange={(event) => setForm((current) => ({ ...current, measured_at: event.target.value }))}
                type="datetime-local"
                value={form.measured_at}
              />
            </label>

            <button className="primary-button" disabled={submitting} type="submit">
              {submitting ? "Salvando..." : "Registrar medicao"}
            </button>
          </form>
        </article>
      </section>
    </section>
  );
}
