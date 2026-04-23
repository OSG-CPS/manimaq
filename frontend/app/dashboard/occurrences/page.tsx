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

function getDefaultDateTimeLocal() {
  const now = new Date();
  const adjusted = new Date(now.getTime() - now.getTimezoneOffset() * 60000);
  return adjusted.toISOString().slice(0, 16);
}

function toApiDateTime(value: string) {
  return value ? new Date(value).toISOString() : null;
}

function toInputDateTime(value: string) {
  const date = new Date(value);
  const adjusted = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
  return adjusted.toISOString().slice(0, 16);
}

const initialForm = {
  equipment_id: "",
  severity: "media",
  safety_risk: false,
  production_stop: false,
  description: "",
  occurred_at: getDefaultDateTimeLocal(),
};

export default function OccurrencesPage() {
  const [equipments, setEquipments] = useState<EquipmentOption[]>([]);
  const [occurrences, setOccurrences] = useState<OccurrenceRecord[]>([]);
  const [selectedOccurrence, setSelectedOccurrence] = useState<OccurrenceRecord | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [filterSeverity, setFilterSeverity] = useState("");
  const [form, setForm] = useState(initialForm);

  async function loadEquipments() {
    const data = await fetchApi<EquipmentOption[]>("/equipment-history/catalog");
    setEquipments(data);
    if (!form.equipment_id && data.length > 0) {
      setForm((current) => ({ ...current, equipment_id: String(data[0].id) }));
    }
  }

  async function loadOccurrences(severity = filterSeverity) {
    setLoading(true);
    setError("");
    try {
      const suffix = severity ? `?severity=${encodeURIComponent(severity)}` : "";
      const data = await fetchApi<OccurrenceRecord[]>(`/occurrences${suffix}`);
      setOccurrences(data);
      if (selectedOccurrence) {
        setSelectedOccurrence(data.find((item) => item.id === selectedOccurrence.id) ?? null);
      }
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Falha ao carregar ocorrencias.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    async function bootstrap() {
      try {
        await Promise.all([loadEquipments(), loadOccurrences("")]);
      } catch (requestError) {
        setError(requestError instanceof Error ? requestError.message : "Falha ao preparar pagina.");
        setLoading(false);
      }
    }

    void bootstrap();
  }, []);

  function resetForm() {
    setEditingId(null);
    setForm((current) => ({
      ...initialForm,
      equipment_id: current.equipment_id || (equipments[0] ? String(equipments[0].id) : ""),
      occurred_at: getDefaultDateTimeLocal(),
    }));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    setMessage("");

    try {
      const payload = {
        equipment_id: Number(form.equipment_id),
        severity: form.severity,
        safety_risk: form.safety_risk,
        production_stop: form.production_stop,
        description: form.description,
        occurred_at: toApiDateTime(form.occurred_at),
      };

      if (editingId) {
        await fetchApi<OccurrenceRecord>(`/occurrences/${editingId}`, {
          method: "PUT",
          body: JSON.stringify(payload),
        });
        setMessage("Ocorrencia atualizada com sucesso.");
      } else {
        await fetchApi<OccurrenceRecord>("/occurrences", {
          method: "POST",
          body: JSON.stringify(payload),
        });
        setMessage("Ocorrencia registrada com sucesso.");
      }

      resetForm();
      await loadOccurrences();
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Falha ao salvar ocorrencia.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="stack-lg">
      <header className="panel stack">
        <p className="helper-text">Fluxo operacional</p>
        <h2 className="section-title">Ocorrencias</h2>
        <p className="helper-text">
          Registre falhas por equipamento com severidade padronizada, risco a seguranca e parada de producao.
        </p>
      </header>

      <section className="module-grid">
        <article className="panel stack">
          <div className="toolbar-inline">
            <select
              className="input"
              onChange={(event) => setFilterSeverity(event.target.value)}
              value={filterSeverity}
            >
              <option value="">Todas as severidades</option>
              <option value="baixa">Baixa</option>
              <option value="media">Media</option>
              <option value="alta">Alta</option>
              <option value="critica">Critica</option>
            </select>
            <button className="secondary-button" onClick={() => void loadOccurrences()} type="button">
              Filtrar
            </button>
          </div>

          {loading ? <p className="helper-text">Carregando ocorrencias...</p> : null}
          {error ? <div className="error-box">{error}</div> : null}
          {message ? <div className="success-box">{message}</div> : null}

          <div className="table-list">
            {occurrences.map((occurrence) => (
              <div
                className={`table-row ${occurrence.production_stop ? "table-row-danger" : ""}`}
                key={occurrence.id}
              >
                <div className="stack-sm">
                  <div className="toolbar-inline">
                    <strong>{occurrence.equipment.tag}</strong>
                    <span className={`status-pill severity-${occurrence.severity}`}>{occurrence.severity}</span>
                    {occurrence.production_stop ? <span className="status-pill status-stop">Parada</span> : null}
                  </div>
                  <p className="helper-text">
                    {occurrence.equipment.name} | {occurrence.author.name} |{" "}
                    {new Date(occurrence.occurred_at).toLocaleString("pt-BR")}
                  </p>
                  <p>{occurrence.description}</p>
                </div>
                <div className="row-actions">
                  <button
                    className="secondary-button inline-button"
                    onClick={() => setSelectedOccurrence(occurrence)}
                    type="button"
                  >
                    Detalhar
                  </button>
                  <button
                    className="secondary-button inline-button"
                    onClick={() => {
                      setEditingId(occurrence.id);
                      setForm({
                        equipment_id: String(occurrence.equipment_id),
                        severity: occurrence.severity,
                        safety_risk: occurrence.safety_risk,
                        production_stop: occurrence.production_stop,
                        description: occurrence.description,
                        occurred_at: toInputDateTime(occurrence.occurred_at),
                      });
                    }}
                    type="button"
                  >
                    Editar
                  </button>
                </div>
              </div>
            ))}
          </div>
        </article>

        <article className="panel stack">
          <div className="stack-sm">
            <h3 className="section-title">{editingId ? "Editar ocorrencia" : "Nova ocorrencia"}</h3>
            <p className="helper-text">Se a data ficar como esta, o registro entra com o horario atual.</p>
          </div>

          <form className="stack" onSubmit={handleSubmit}>
            <label className="label" htmlFor="occurrence-equipment">
              Equipamento
              <select
                className="input"
                id="occurrence-equipment"
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

            <label className="label" htmlFor="occurrence-severity">
              Severidade
              <select
                className="input"
                id="occurrence-severity"
                onChange={(event) => setForm((current) => ({ ...current, severity: event.target.value }))}
                value={form.severity}
              >
                <option value="baixa">Baixa</option>
                <option value="media">Media</option>
                <option value="alta">Alta</option>
                <option value="critica">Critica</option>
              </select>
            </label>

            <label className="checkbox">
              <input
                checked={form.safety_risk}
                onChange={(event) => setForm((current) => ({ ...current, safety_risk: event.target.checked }))}
                type="checkbox"
              />
              Ha risco a seguranca
            </label>

            <label className="checkbox">
              <input
                checked={form.production_stop}
                onChange={(event) => setForm((current) => ({ ...current, production_stop: event.target.checked }))}
                type="checkbox"
              />
              Gerou parada de producao
            </label>

            <label className="label" htmlFor="occurrence-occurred-at">
              Data e hora da ocorrencia
              <input
                className="input"
                id="occurrence-occurred-at"
                onChange={(event) => setForm((current) => ({ ...current, occurred_at: event.target.value }))}
                type="datetime-local"
                value={form.occurred_at}
              />
            </label>

            <label className="label" htmlFor="occurrence-description">
              Descricao
              <textarea
                className="input textarea"
                id="occurrence-description"
                onChange={(event) => setForm((current) => ({ ...current, description: event.target.value }))}
                required
                value={form.description}
              />
            </label>

            <div className="toolbar-inline">
              <button className="primary-button" disabled={submitting} type="submit">
                {submitting ? "Salvando..." : editingId ? "Salvar alteracoes" : "Registrar ocorrencia"}
              </button>
              {editingId ? (
                <button className="secondary-button" onClick={resetForm} type="button">
                  Cancelar edicao
                </button>
              ) : null}
            </div>
          </form>

          {selectedOccurrence ? (
            <div className="detail-box stack">
              <h4 className="section-title">Detalhe rapido</h4>
              <p className="helper-text">Equipamento: {selectedOccurrence.equipment.tag}</p>
              <p className="helper-text">Autor: {selectedOccurrence.author.name}</p>
              <p className="helper-text">
                Data/hora: {new Date(selectedOccurrence.occurred_at).toLocaleString("pt-BR")}
              </p>
              <p className="helper-text">Risco: {selectedOccurrence.safety_risk ? "Sim" : "Nao"}</p>
              <p className="helper-text">Parada: {selectedOccurrence.production_stop ? "Sim" : "Nao"}</p>
              <p>{selectedOccurrence.description}</p>
            </div>
          ) : null}
        </article>
      </section>
    </section>
  );
}
