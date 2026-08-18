# Manifesto de Evidências — NexoDocs V2

Conjunto público/sanitizado de evidências do Challenge Alura Agentes.

> **Importante:** a pasta `privadas_originais/` contém os cinco novos prints brutos e NÃO deve ser publicada no GitHub. A pasta `docs/evidencias/` é a versão preparada para o repositório público.

## Evidências públicas

### 01_oci_instances_always_free.png
OCI: duas VMs Always Free / E2 Micro usadas no projeto.
- SHA-256: `DE80D8C27EC96C870721B5AA8987885CE9AA99052E7DB73B8CC6D2AD829DF66A`

### 02_wf01_pdf_ingestion_21_points.png
WF01: ingestão do PDF corporativo concluída com 21 pontos no Qdrant.
- SHA-256: `4E01F1BC62CFB7A60B4E4700DEB54A7642BF724EB91B046141946B0C8DAAC304`

### 03_wf01r_retrieval_smoke_test.png
WF01R: smoke test de recuperação semântica em três consultas.
- SHA-256: `28BA9063549C58A4C0EF2C474679EEF1B498F3DC0DF38882E9BB6765BD32BA72`

### 04_wf02_grounded_answer.png
WF02: resposta factual fundamentada em documento e fonte.
- SHA-256: `E2625EFEB7A14FE0856F9936A2B3BAD13C527EA345A77E53F0B71C0923223545`

### 05_wf02_exact_fallback.png
WF02: fallback exato quando a informação não existe na base.
- SHA-256: `3A050F5BDF183C0C6AA47AF0897E061F8291EBA3B53B33E074309464C445C925`

### 06_wf02_clinical_safety.png
WF02: comportamento seguro em pergunta clínica.
- SHA-256: `7A23C4FF3D0D7EEA8678884DDB3257290913108BC0FFCEFB20D8818C6365AFCA`

### 07_wf01c_csv_ingestion.png
WF01C: ingestão do CSV corporativo em coleção separada.
- SHA-256: `AB5525E94477010156D3DF66593A4F896354C0274B02CFB0B6ABCE2DF3F673C2`

### 08_wf03_golden_evaluation.png
WF03: avaliação Golden Dataset validando qualidade do RAG.
- SHA-256: `EFACAE30F8100ECAD340F92520BED768A8D683E06DE3FE10365AFEA464626DD9`

### 09_qdrant_collections_validation.png
Validação Qdrant das coleções principal e CSV (green, 3072, Cosine).
- SHA-256: `F9D1804ABE8F832AB21D9158CAC2E12E0EAD434D1E4BDDC2C2BBD22982113CC1`

### 10_private_demo_mobile_frontend.png
Demo privada: frontend NexoDocs aberto em celular por acesso HTTPS externo; URL temporária removida da versão pública.
- SHA-256: `480252F85D0B0B14A2CBA356C4FD25CD3C34F2F98D4661DE0FAEC170C5E2AC94`

### 11_private_demo_grounded_answer.png
Demo privada: resposta factual sobre tolerância de atraso, selo RAG validado e fonte CH-MAN-001 v1.0, página 3.
- SHA-256: `01C6C491AC2EEE6E30FD2F96D4D77DA7980CCDF9CEF8674BA48CF735D653ECE6`

### 12_private_demo_exact_fallback.png
Demo privada: pergunta ausente retornando o fallback exato, com RAG validado.
- SHA-256: `5ED573CE55477DE5504AE2DB49F03544F5E9A67277CE212516AC6AA13AE04353`

### 13_private_demo_cloudflare_webhook.png
Execução externa: Webhook do n8n recebendo requisição via Cloudflare/HTTPS; IP e URL temporária redigidos.
- SHA-256: `BFFC4F0E610AC43A8241F840E6847DDF1CC7DC6B583B5D402C7783DFCEABF021`

### 14_private_demo_rag_tool_execution.png
Execução externa: Agent confirma chamada da ferramenta buscar_base_corporativa no fluxo da demo.
- SHA-256: `B443CFDD923AB61C8ACC45B218F11688E6150C17DD87DBC7A48223F602B782C9`
