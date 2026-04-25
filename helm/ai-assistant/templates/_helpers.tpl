{{/*
Expand the name of the chart.
*/}}
{{- define "ai-assistant.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "ai-assistant.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Chart label.
*/}}
{{- define "ai-assistant.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels.
*/}}
{{- define "ai-assistant.labels" -}}
helm.sh/chart: {{ include "ai-assistant.chart" . }}
{{ include "ai-assistant.selectorLabels" . }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels.
*/}}
{{- define "ai-assistant.selectorLabels" -}}
app.kubernetes.io/name: {{ include "ai-assistant.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Service hostname helpers — used in provider YAML generation.
*/}}
{{- define "ai-assistant.ollamaHost" -}}
{{- printf "%s-ollama" (include "ai-assistant.fullname" .) }}
{{- end }}

{{- define "ai-assistant.llamacppHost" -}}
{{- printf "%s-llamacpp" (include "ai-assistant.fullname" .) }}
{{- end }}

{{- define "ai-assistant.embeddingHost" -}}
{{- printf "%s-embedding" (include "ai-assistant.fullname" .) }}
{{- end }}

{{- define "ai-assistant.redisHost" -}}
{{- printf "%s-redis" (include "ai-assistant.fullname" .) }}
{{- end }}

{{- define "ai-assistant.qdrantHost" -}}
{{- printf "%s-qdrant" (include "ai-assistant.fullname" .) }}
{{- end }}

{{/*
Generated providers/default.yaml content based on enabled model server.
Ollama takes precedence when both are enabled.
*/}}
{{- define "ai-assistant.providerDefault" -}}
{{- if .Values.ollama.enabled }}
api_base: http://{{ include "ai-assistant.ollamaHost" . }}:11434
model: {{ .Values.ollama.model }}
timeout: {{ .Values.ollama.timeout }}
{{- else if .Values.llamacpp.enabled }}
api_base: http://{{ include "ai-assistant.llamacppHost" . }}:8080/v1
model: {{ .Values.llamacpp.model }}
api_key: dummy
timeout: {{ .Values.llamacpp.timeout }}
{{- end }}
{{- end }}
