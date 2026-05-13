// File version: 2.1; date: 2026-05-12

const FIELD_GROUPS = [
  ["Research path", ["workflow_path", "study_name", "language", "study_design", "analysis_unit", "observation_unit", "outcome_type", "alternative"]],
  ["Statistical target", ["alpha", "power", "primary_comparisons", "allocation_ratio", "effect_size_d", "mean_control", "mean_intervention", "sd_pooled", "pre_post_correlation", "proportion_control", "proportion_intervention"]],
  ["Corrections", ["apply_fpc", "finite_population", "cluster_average_size", "intraclass_correlation", "response_rate", "completion_rate", "usable_data_rate", "extra_buffer_rate"]],
  ["Achieved result", ["planned_control_n", "planned_intervention_n", "planned_total_n", "planned_effect_size", "planned_alpha", "planned_power", "observed_control_n", "observed_intervention_n", "observed_total_n", "observed_control_events", "observed_intervention_events", "observed_pre_success_post_failure", "observed_pre_failure_post_success", "observed_effect_size"]],
  ["Labels and notes", ["intervention_label", "control_label", "notes"]]
];

const FIELD_TYPES = {
  workflow_path: "workflow",
  language: "language",
  study_design: "design",
  outcome_type: "outcome",
  alternative: "alternative",
  notes: "textarea",
  apply_fpc: "checkbox",
  primary_comparisons: "int",
  finite_population: "optional_int",
  planned_control_n: "optional_int",
  planned_intervention_n: "optional_int",
  planned_total_n: "optional_int",
  observed_control_n: "optional_int",
  observed_intervention_n: "optional_int",
  observed_total_n: "optional_int",
  observed_control_events: "optional_int",
  observed_intervention_events: "optional_int",
  observed_pre_success_post_failure: "optional_int",
  observed_pre_failure_post_success: "optional_int"
};

const NUMERIC_FIELDS = new Set([
  "alpha", "power", "primary_comparisons", "allocation_ratio", "effect_size_d", "mean_control",
  "mean_intervention", "sd_pooled", "pre_post_correlation", "proportion_control",
  "proportion_intervention", "finite_population", "cluster_average_size", "intraclass_correlation",
  "response_rate", "completion_rate", "usable_data_rate", "extra_buffer_rate",
  "planned_control_n", "planned_intervention_n", "planned_total_n", "planned_effect_size",
  "planned_alpha", "planned_power", "observed_control_n", "observed_intervention_n",
  "observed_total_n", "observed_control_events", "observed_intervention_events",
  "observed_pre_success_post_failure", "observed_pre_failure_post_success", "observed_effect_size"
]);

const WEB_TEXT = {
  en: {
    language: "Language",
    run: "Run",
    wizard: "Wizard",
    configuration: "Configuration",
    results: "Results",
    loadPlan: "Load plan",
    reset: "Reset",
    back: "Back",
    next: "Next",
    configHelp: "All inputs used by the API.",
    loadJson: "Load JSON",
    saveJson: "Save JSON",
    noCalculation: "No calculation yet.",
    summary: "Summary",
    sensitivity: "Sensitivity",
    benchmarks: "Plan / Benchmarks",
    suggestions: "Suggestions",
    apiHelp: "Same calculation engine, HTTP interface.",
    rangeIssue: "Review recommended ranges or allow override",
    calculationComplete: "Calculation complete.",
    resetComplete: "Reset complete.",
    jsonLoaded: "JSON loaded.",
    noSensitivity: "No sensitivity table for this run.",
    noBenchmarks: "Run an achieved-result workflow to see plan and benchmark rows.",
    noPlanRows: "No plan or benchmark rows for this result.",
    noSuggestions: "No suggestions.",
    noWarnings: "No warnings.",
    warnings: "Warnings"
  },
  pt: {
    language: "Idioma",
    run: "Executar",
    wizard: "Wizard",
    configuration: "Configuracao",
    results: "Resultados",
    loadPlan: "Carregar plano",
    reset: "Reiniciar",
    back: "Anterior",
    next: "Proximo",
    configHelp: "Todas as entradas usadas pela API.",
    loadJson: "Carregar JSON",
    saveJson: "Salvar JSON",
    noCalculation: "Ainda nao ha calculo.",
    summary: "Resumo",
    sensitivity: "Sensibilidade",
    benchmarks: "Plano / Benchmarks",
    suggestions: "Sugestoes",
    apiHelp: "Mesmo motor de calculo, interface HTTP.",
    rangeIssue: "Revise as faixas recomendadas ou permita a liberacao",
    calculationComplete: "Calculo concluido.",
    resetComplete: "Reinicializacao concluida.",
    jsonLoaded: "JSON carregado.",
    noSensitivity: "Nao ha tabela de sensibilidade para esta execucao.",
    noBenchmarks: "Execute um fluxo de resultado alcancado para ver plano e benchmarks.",
    noPlanRows: "Nao ha linhas de plano ou benchmark para este resultado.",
    noSuggestions: "Sem sugestoes.",
    noWarnings: "Sem alertas.",
    warnings: "Alertas"
  }
};

let config = {};
let explanations = {};
let uiText = {};
let currentPlan = null;
let wizardIndex = 0;
let pendingLoadMode = null;

const $ = (id) => document.getElementById(id);

document.addEventListener("DOMContentLoaded", async () => {
  await loadLanguage("en");
  bindEvents();
  renderAll();
  updateApiExample();
});

function bindEvents() {
  document.querySelectorAll(".tab").forEach((button) => {
    button.addEventListener("click", () => selectMainTab(button.dataset.tab));
  });
  document.querySelectorAll(".result-tab").forEach((button) => {
    button.addEventListener("click", () => selectResultTab(button.dataset.result));
  });
  $("languageSelect").addEventListener("change", async (event) => {
    config.language = event.target.value;
    await loadLanguage(event.target.value, false);
    renderAll();
  });
  $("runTop").addEventListener("click", runCalculation);
  $("runConfig").addEventListener("click", runCalculation);
  $("nextWizard").addEventListener("click", nextWizard);
  $("prevWizard").addEventListener("click", previousWizard);
  $("resetWizard").addEventListener("click", resetWizard);
  $("saveJson").addEventListener("click", saveJson);
  $("loadJson").addEventListener("click", () => openFile("config"));
  $("loadPlanWizard").addEventListener("click", () => openFile("plan"));
  $("fileInput").addEventListener("change", loadJsonFile);
  $("downloadText").addEventListener("click", () => downloadReport("text"));
  $("downloadHtml").addEventListener("click", () => downloadReport("html"));
  $("downloadPdf").addEventListener("click", () => downloadReport("pdf"));
}

async function loadLanguage(language, resetConfig = true) {
  const configPromise = resetConfig
    ? fetch(`/api/default-config?language=${language}`).then((response) => response.json())
    : Promise.resolve(config);
  const [defaultConfig, explanationData, textData] = await Promise.all([
    configPromise,
    fetch(`/api/explanations?language=${language}`).then((response) => response.json()),
    fetch(`/api/ui-text?language=${language}`).then((response) => response.json())
  ]);
  config = defaultConfig;
  explanations = explanationData;
  uiText = textData;
  document.documentElement.lang = language;
  applyStaticText();
}

function renderAll() {
  normalizeWorkflow();
  renderWizard();
  renderConfig();
  updateApiExample();
}

function webText(key) {
  const language = config.language || $("languageSelect")?.value || "en";
  return WEB_TEXT[language]?.[key] || WEB_TEXT.en[key] || key;
}

function applyStaticText() {
  document.querySelectorAll("[data-i18n]").forEach((element) => {
    element.textContent = webText(element.dataset.i18n);
  });
}

function normalizeWorkflow() {
  if (config.workflow_path === "plan_study") {
    config.analysis_mode = "plan";
    config.had_planned_sample = false;
  } else if (config.workflow_path === "evaluate_done") {
    config.analysis_mode = "evaluate";
    config.had_planned_sample = false;
  } else if (config.workflow_path === "evaluate_against_plan") {
    config.analysis_mode = "evaluate";
    config.had_planned_sample = true;
  }
  const outcomes = validOutcomeValues();
  if (!outcomes.includes(config.outcome_type)) config.outcome_type = outcomes[0];
}

function validOutcomeValues() {
  if (config.study_design === "pretest_posttest_control") return ["continuous"];
  if (config.study_design === "one_group_pre_post" && config.analysis_mode === "plan") return ["continuous"];
  return ["continuous", "binary"];
}

function renderWizard() {
  const fields = wizardFields();
  wizardIndex = Math.min(wizardIndex, fields.length - 1);
  const field = fields[wizardIndex];
  $("wizardProgress").textContent = `${wizardIndex + 1} / ${fields.length}`;
  $("wizardQuestion").textContent = questionFor(field);
  $("wizardWhy").textContent = helpFor(field) || "This value changes the calculation and how the result should be interpreted.";
  $("wizardInput").innerHTML = "";
  const label = document.createElement("label");
  label.textContent = labelFor(field);
  const input = inputFor(field);
  input.addEventListener("change", () => {
    writeFieldFromInput(field, input);
    normalizeWorkflow();
    renderAll();
  });
  $("wizardInput").append(label, input);
  const rangeControl = rangeControlFor(field);
  if (rangeControl) $("wizardInput").append(document.createElement("span"), rangeControl);
  $("prevWizard").disabled = wizardIndex === 0;
  $("nextWizard").textContent = wizardIndex === fields.length - 1 ? webText("run") : webText("next");
}

function renderConfig() {
  const grid = $("configGrid");
  grid.innerHTML = "";
  FIELD_GROUPS.forEach(([group, fields]) => {
    const title = document.createElement("h3");
    title.className = "group-title";
    title.textContent = group;
    grid.append(title);
    fields.forEach((field) => {
      if (!showField(field)) return;
      const card = document.createElement("div");
      card.className = "field-card";
      const label = document.createElement("label");
      label.innerHTML = `<span>${labelFor(field)}</span><button type="button" title="Help">?</button>`;
      label.querySelector("button").addEventListener("click", () => toast(helpFor(field) || field, 5000));
      const input = inputFor(field);
      input.addEventListener("change", async () => {
        writeFieldFromInput(field, input);
        if (field === "language") {
          $("languageSelect").value = config.language;
          await loadLanguage(config.language, false);
        }
        normalizeWorkflow();
        renderAll();
      });
      const help = document.createElement("p");
      help.className = "help";
      help.textContent = shortHelp(field);
      if (isOutOfRange(field) && !hasRangeOverride(field)) card.classList.add("range-warning");
      card.append(label, input);
      if (help.textContent) card.append(help);
      const range = rangeFor(field);
      if (range) {
        const rangeEl = document.createElement("div");
        rangeEl.className = "range";
        rangeEl.textContent = range;
        card.append(rangeEl);
        card.append(rangeControlFor(field));
      }
      grid.append(card);
    });
  });
}

function inputFor(field) {
  const type = FIELD_TYPES[field] || "text";
  let input;
  if (type === "workflow" || type === "language" || type === "design" || type === "outcome" || type === "alternative") {
    input = document.createElement("select");
    optionsFor(type).forEach(([value, label]) => {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = label;
      input.append(option);
    });
    input.value = config[field] ?? "";
  } else if (type === "textarea") {
    input = document.createElement("textarea");
    input.value = config[field] ?? "";
  } else if (type === "checkbox") {
    input = document.createElement("input");
    input.type = "checkbox";
    input.checked = Boolean(config[field]);
  } else {
    input = document.createElement("input");
    input.type = NUMERIC_FIELDS.has(field) ? "number" : "text";
    input.step = integerField(field) ? "1" : "any";
    input.value = config[field] ?? "";
  }
  input.id = `field-${field}`;
  return input;
}

function writeFieldFromInput(field, input) {
  if (input.type === "checkbox") {
    config[field] = input.checked;
  } else if (NUMERIC_FIELDS.has(field)) {
    config[field] = input.value === "" ? null : Number(input.value);
  } else {
    config[field] = input.value;
  }
}

function optionsFor(type) {
  if (type === "language") {
    return [
      ["en", "English"],
      ["pt", "Portuguese (pt)"]
    ];
  }
  if (type === "workflow") {
    return [
      ["plan_study", uiText.workflow_plan_study || "Plan a study"],
      ["evaluate_done", uiText.workflow_evaluate_done || "Analyze a completed study"],
      ["evaluate_against_plan", uiText.workflow_evaluate_against_plan || "Compare completed study with plan"]
    ];
  }
  if (type === "design") {
    return [
      ["parallel_two_group", uiText.design_parallel_two_group || "Two independent groups"],
      ["pretest_posttest_control", uiText.design_pretest_posttest_control || "Pre-test/post-test with control"],
      ["one_group_pre_post", uiText.design_one_group_pre_post || "One-group pre-test/post-test"]
    ];
  }
  if (type === "outcome") {
    const labels = {
      continuous: uiText.outcome_continuous || "Continuous",
      binary: uiText.outcome_binary || "Binary"
    };
    return validOutcomeValues().map((value) => [value, labels[value]]);
  }
  return [
    ["two_sided", uiText.alternative_two_sided || "Two-sided"],
    ["greater", uiText.alternative_greater || "Intervention greater"],
    ["less", uiText.alternative_less || "Intervention smaller"]
  ];
}

function wizardFields() {
  const fields = ["workflow_path", "study_name", "study_design", "outcome_type", "alpha", "power"];
  const design = config.study_design;
  const mode = config.analysis_mode;
  const outcome = config.outcome_type;
  const hasPlan = config.workflow_path === "evaluate_against_plan";
  if (mode === "plan") {
    if (design !== "one_group_pre_post") fields.push("allocation_ratio");
    if (design === "parallel_two_group" && outcome === "binary") {
      fields.push("proportion_control", "proportion_intervention");
    } else {
      fields.push("effect_size_d");
    }
    if (design === "pretest_posttest_control") fields.push("pre_post_correlation");
    fields.push("response_rate", "completion_rate", "usable_data_rate", "extra_buffer_rate", "primary_comparisons", "cluster_average_size", "intraclass_correlation");
  } else {
    if (hasPlan) {
      if (design === "one_group_pre_post") fields.push("planned_total_n");
      else fields.push("planned_control_n", "planned_intervention_n");
      fields.push("planned_effect_size", "planned_alpha", "planned_power");
    }
    if (design === "one_group_pre_post") {
      fields.push("observed_total_n");
      if (outcome === "binary") fields.push("observed_pre_success_post_failure", "observed_pre_failure_post_success");
      else fields.push("observed_effect_size");
    } else {
      if (design === "parallel_two_group") fields.push("allocation_ratio");
      if (design === "pretest_posttest_control") fields.push("pre_post_correlation");
      fields.push("observed_control_n", "observed_intervention_n");
      if (design === "parallel_two_group" && outcome === "binary") fields.push("observed_control_events", "observed_intervention_events");
      else fields.push("observed_effect_size");
    }
  }
  return fields;
}

function showField(field) {
  const design = config.study_design;
  const mode = config.analysis_mode;
  const outcome = config.outcome_type;
  const hasPlan = config.workflow_path === "evaluate_against_plan";
  if (field === "allocation_ratio") return design !== "one_group_pre_post";
  if (field === "pre_post_correlation") return design === "pretest_posttest_control";
  if (["mean_control", "mean_intervention", "sd_pooled"].includes(field)) return mode === "plan" && outcome === "continuous" && design !== "one_group_pre_post";
  if (field === "effect_size_d") return mode === "plan" && outcome === "continuous";
  if (["proportion_control", "proportion_intervention"].includes(field)) return mode === "plan" && outcome === "binary" && design === "parallel_two_group";
  if (["observed_control_n", "observed_intervention_n"].includes(field)) return mode === "evaluate" && design !== "one_group_pre_post";
  if (field === "observed_total_n") return mode === "evaluate" && design === "one_group_pre_post";
  if (["observed_control_events", "observed_intervention_events"].includes(field)) return mode === "evaluate" && design === "parallel_two_group" && outcome === "binary";
  if (["observed_pre_success_post_failure", "observed_pre_failure_post_success"].includes(field)) return mode === "evaluate" && design === "one_group_pre_post" && outcome === "binary";
  if (field === "observed_effect_size") return mode === "evaluate" && outcome === "continuous";
  if (["planned_control_n", "planned_intervention_n"].includes(field)) return hasPlan && design !== "one_group_pre_post";
  if (field === "planned_total_n") return hasPlan && design === "one_group_pre_post";
  if (["planned_effect_size", "planned_alpha", "planned_power"].includes(field)) return hasPlan;
  if (field === "control_label") return design !== "one_group_pre_post";
  return true;
}

function labelFor(field) {
  return uiText[`field_${field}`] || field.replaceAll("_", " ");
}

function questionFor(field) {
  return uiText[`wizard_question_${field}`] || labelFor(field);
}

function helpFor(field) {
  return explanations.fields?.[field]?.help || "";
}

function shortHelp(field) {
  const help = helpFor(field);
  return help.length > 180 ? `${help.slice(0, 180)}...` : help;
}

function rangeFor(field) {
  const rec = explanations.fields?.[field]?.recommended;
  if (!rec) return "";
  const typical = Array.isArray(rec.typical) ? ` Typical: ${rec.typical.join(", ")}.` : "";
  return `Recommended: ${rec.min} to ${rec.max}.${typical}`;
}

function rangeControlFor(field) {
  const rec = explanations.fields?.[field]?.recommended;
  if (!rec) return null;
  const wrapper = document.createElement("label");
  wrapper.className = "override-row";
  const checkbox = document.createElement("input");
  checkbox.type = "checkbox";
  checkbox.checked = hasRangeOverride(field);
  checkbox.addEventListener("change", () => {
    setRangeOverride(field, checkbox.checked);
    renderAll();
  });
  const span = document.createElement("span");
  span.textContent = uiText.range_override || "Allow outside range";
  wrapper.append(checkbox, span);
  return wrapper;
}

function hasRangeOverride(field) {
  return Array.isArray(config.range_override_fields) && config.range_override_fields.includes(field);
}

function setRangeOverride(field, allow) {
  const fields = new Set(config.range_override_fields || []);
  if (allow) fields.add(field);
  else fields.delete(field);
  config.range_override_fields = Array.from(fields).sort();
}

function isOutOfRange(field) {
  const rec = explanations.fields?.[field]?.recommended;
  const value = Number(config[field]);
  if (!rec || Number.isNaN(value) || config[field] === null || config[field] === "") return false;
  return value < Number(rec.min) || value > Number(rec.max);
}

function rangeIssues() {
  return Object.keys(explanations.fields || {})
    .filter((field) => showField(field) && isOutOfRange(field) && !hasRangeOverride(field))
    .map((field) => `${labelFor(field)} = ${config[field]} is outside ${rangeFor(field).toLowerCase()}`);
}

function integerField(field) {
  return (FIELD_TYPES[field] || "").includes("int") || field === "primary_comparisons";
}

async function nextWizard() {
  const fields = wizardFields();
  if (wizardIndex === fields.length - 1) {
    if (await runCalculation()) selectMainTab("results");
    return;
  }
  wizardIndex += 1;
  renderWizard();
}

function previousWizard() {
  wizardIndex = Math.max(0, wizardIndex - 1);
  renderWizard();
}

function resetWizard() {
  loadLanguage(config.language || "en").then(() => {
    wizardIndex = 0;
    currentPlan = null;
    renderAll();
    toast(webText("resetComplete"));
  });
}

async function runCalculation() {
  normalizeWorkflow();
  const issues = rangeIssues();
  if (issues.length > 0) {
    toast(`${webText("rangeIssue")}: ${issues[0]}`, 8000);
    selectMainTab("config");
    renderConfig();
    return false;
  }
  const response = await fetch("/api/calculate", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(config)
  });
  const payload = await response.json();
  if (!response.ok) {
    toast(payload.error || "Calculation failed.", 6000);
    return false;
  }
  currentPlan = payload;
  renderResults(payload);
  toast(webText("calculationComplete"));
  return true;
}

function renderResults(plan) {
  $("resultState").textContent = `${plan.config.study_name} - ${plan.summary.method}`;
  $("summaryResult").innerHTML = summaryHtml(plan);
  $("sensitivityResult").innerHTML = sensitivityHtml(plan.sensitivity);
  $("benchmarksResult").innerHTML = benchmarkHtml(plan.observed_analysis);
  $("suggestionsResult").innerHTML = notesHtml(plan);
  $("jsonResult").textContent = JSON.stringify(plan, null, 2);
}

function summaryHtml(plan) {
  const summary = plan.summary;
  if (plan.config.analysis_mode === "evaluate" && plan.observed_analysis) {
    const obs = plan.observed_analysis;
    return `<div class="summary-grid">
      ${metric("Observed total", obs.observed_total)}
      ${metric("Observed effect", fmt(obs.observed_effect_size, 4))}
      ${metric("p-value", fmt(obs.p_value, 6))}
      ${metric("Achieved power", pct(obs.achieved_power))}
    </div>
    <pre class="code-panel">${escapeHtml(plan.report)}</pre>`;
  }
  return `<div class="summary-grid">
    ${metric("Initial valid", summary.initial_valid.total)}
    ${metric("Design adjusted", summary.design_adjusted_valid.total)}
    ${metric("Assigned", summary.assigned_needed.total)}
    ${metric("Invited", summary.invited_needed.total)}
  </div>
  <pre class="code-panel">${escapeHtml(plan.report)}</pre>`;
}

function metric(label, value) {
  return `<div class="metric"><span>${escapeHtml(label)}</span><b>${escapeHtml(String(value))}</b></div>`;
}

function sensitivityHtml(rows) {
  if (!rows || rows.length === 0) return `<p class="muted">${escapeHtml(webText("noSensitivity"))}</p>`;
  return table(["Scenario", "Control", "Intervention", "Total", "Invited"], rows.map((row) => [row.label, row.control, row.intervention, row.total, row.invited_total]));
}

function benchmarkHtml(observed) {
  if (!observed) return `<p class="muted">${escapeHtml(webText("noBenchmarks"))}</p>`;
  const rows = [];
  (observed.planned_targets || []).forEach((target) => rows.push(["Previous plan", target]));
  (observed.benchmark_targets || []).forEach((target) => rows.push(["Benchmark", target]));
  if (rows.length === 0) return `<p class="muted">${escapeHtml(webText("noPlanRows"))}</p>`;
  return table(
    ["Category", "Target", "Required control", "Required intervention", "Required total", "Additional", "Status"],
    rows.map(([category, target]) => [
      category,
      target.label,
      target.required_control,
      target.required_intervention,
      target.required_total,
      target.additional_total,
      target.achieved ? `<span class="pill ok">Reached</span>` : `<span class="pill missing">Needs more</span>`
    ]),
    true
  );
}

function notesHtml(plan) {
  const warnings = (plan.warnings || []).map((item) => `<div class="note warning">${escapeHtml(item)}</div>`).join("");
  const suggestions = (plan.suggestions || []).map((item) => `<div class="note">${escapeHtml(item)}</div>`).join("");
  return `<div class="suggestion-list">${suggestions || `<p class="muted">${escapeHtml(webText("noSuggestions"))}</p>`}</div>
  <h3>${escapeHtml(webText("warnings"))}</h3>
  <div class="warning-list">${warnings || `<p class="muted">${escapeHtml(webText("noWarnings"))}</p>`}</div>`;
}

function table(headers, rows, raw = false) {
  return `<table class="result-table"><thead><tr>${headers.map((h) => `<th>${escapeHtml(h)}</th>`).join("")}</tr></thead><tbody>
    ${rows.map((row) => `<tr>${row.map((cell) => `<td>${raw ? cell : escapeHtml(String(cell))}</td>`).join("")}</tr>`).join("")}
  </tbody></table>`;
}

function saveJson() {
  downloadBlob(JSON.stringify(config, null, 2), "application/json", filename("json"));
}

function openFile(mode) {
  pendingLoadMode = mode;
  $("fileInput").value = "";
  $("fileInput").click();
}

async function loadJsonFile(event) {
  const file = event.target.files[0];
  if (!file) return;
  const data = JSON.parse(await file.text());
  if (pendingLoadMode === "plan") {
    await applyLoadedPlan(data);
  } else {
    config = {...config, ...data};
  }
  normalizeWorkflow();
  renderAll();
  toast(webText("jsonLoaded"));
}

async function applyLoadedPlan(data) {
  let planned = data;
  if (!data.summary && (data.workflow_path || data.study_design || data.effect_size_d)) {
    const response = await fetch("/api/calculate", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({...data, workflow_path: "plan_study", analysis_mode: "plan"})
    });
    if (response.ok) planned = await response.json();
  }
  const summary = planned.summary || planned;
  const planConfig = planned.config || data;
  const valid = summary.design_adjusted_valid || planned.design_adjusted_valid || {};
  const assigned = summary.assigned_needed || planned.assigned_needed || {};
  config.planned_control_n = valid.control ?? assigned.control ?? config.planned_control_n;
  config.planned_intervention_n = valid.intervention ?? assigned.intervention ?? config.planned_intervention_n;
  config.planned_total_n = valid.total ?? assigned.total ?? config.planned_total_n;
  config.planned_effect_size = summary.effect_size_used ?? planConfig.effect_size_d ?? config.planned_effect_size;
  config.planned_alpha = planConfig.alpha ?? config.planned_alpha;
  config.planned_power = planConfig.power ?? config.planned_power;
  config.workflow_path = "evaluate_against_plan";
  config.study_design = planConfig.study_design ?? config.study_design;
  config.outcome_type = planConfig.outcome_type ?? config.outcome_type;
}

async function downloadReport(kind) {
  if (!currentPlan && !(await runCalculation())) return;
  const response = await fetch(`/api/report/${kind}`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(config)
  });
  if (!response.ok) {
    const payload = await response.json();
    toast(payload.error || "Export failed.", 6000);
    return;
  }
  const blob = await response.blob();
  downloadBlob(blob, blob.type, filename(kind === "text" ? "txt" : kind));
}

function downloadBlob(payload, type, name) {
  const blob = payload instanceof Blob ? payload : new Blob([payload], {type});
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = name;
  link.click();
  URL.revokeObjectURL(link.href);
}

function filename(extension) {
  const base = (config.study_name || "isp-report").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
  return `${base || "isp-report"}.${extension}`;
}

function selectMainTab(name) {
  document.querySelectorAll(".tab").forEach((button) => button.classList.toggle("active", button.dataset.tab === name));
  document.querySelectorAll(".panel").forEach((panel) => panel.classList.toggle("active", panel.id === name));
}

function selectResultTab(name) {
  document.querySelectorAll(".result-tab").forEach((button) => button.classList.toggle("active", button.dataset.result === name));
  document.querySelectorAll(".result-panel").forEach((panel) => panel.classList.toggle("active", panel.id === `${name}Result`));
}

function updateApiExample() {
  $("apiExample").textContent = `fetch("/api/calculate", {
  method: "POST",
  headers: {"Content-Type": "application/json"},
  body: JSON.stringify(${JSON.stringify(config, null, 2)})
}).then(response => response.json())`;
}

function fmt(value, digits) {
  return Number(value || 0).toFixed(digits);
}

function pct(value) {
  return `${(Number(value || 0) * 100).toFixed(1)}%`;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function toast(message, ms = 2600) {
  const toastEl = $("toast");
  toastEl.textContent = message;
  toastEl.classList.add("show");
  window.clearTimeout(toastEl.timer);
  toastEl.timer = window.setTimeout(() => toastEl.classList.remove("show"), ms);
}
