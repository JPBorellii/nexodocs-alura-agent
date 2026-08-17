# NexoDocs — Evidências finais

Pacote final aprovado para publicação em `docs/evidencias/`.

## Regras aplicadas

- Foram escolhidas apenas evidências que comprovam requisitos distintos.
- Capturas redundantes, erros intermediários e telas de credenciais foram excluídas.
- A evidência OCI 01 teve apenas os valores de IP público/privado redigidos para a cópia pública.
- As demais imagens tiveram somente recorte de interface quando necessário; o conteúdo técnico central não foi alterado.

## Arquivos

### `01_oci_instances_always_free.png`

OCI: duas VMs em execução, ambas marcadas Always Free, shape VM.Standard.E2.1.Micro, 1 OCPU e 1 GB. IPs foram redigidos na cópia pública.

SHA-256: `de80d8c27ec96c870721b5aa8987885ce9aa99052e7db73b8cc6d2ad829df66a`

### `02_wf01_pdf_ingestion_21_points.png`

WF01: ingestão do PDF concluída, com 21 itens enviados ao Qdrant.

SHA-256: `4e01f1bc62cfb7a60b4e4700deb54a7642bf724eb91b046141946b0c8daac304`

### `03_wf01r_retrieval_smoke_test.png`

WF01R: smoke test de retrieval com três consultas e ramos concluídos.

SHA-256: `28ba9063549c58a4c0ef2c474679eef1b498f3dc0df38882e9bb6765bd32ba72`

### `04_wf02_grounded_answer.png`

WF02: resposta factual grounded com fonte CH-MAN-001 v1.0, página 3.

SHA-256: `e2625efeb7a14fe0856f9936a2b3bad13c527ea345a77e53f0b71c0923223545`

### `05_wf02_exact_fallback.png`

WF02: fallback exato para informação ausente, sem alucinação.

SHA-256: `3a050f5bdf183c0c6aa47af0897e061f8291eba3b53b33e074309464c445c925`

### `06_wf02_clinical_safety.png`

WF02: segurança clínica — recusa de orientar aumento/dose e encaminhamento apropriado.

SHA-256: `7a23c4ff3d0d7eea8678884ddb3257290913108bc0ffcefb20d8818c6365afca`

### `07_wf01c_csv_ingestion.png`

WF01C: CSV com 5 registros, parsing, chunking, embeddings e 2 itens no Qdrant.

SHA-256: `ab5525e94477010156d3df66593a4f896354c0274b02cfb0b6abce2df3f673c2`

### `08_wf03_golden_evaluation.png`

WF03: golden evaluation final com métricas de grounding, fontes, segurança e correctness.

SHA-256: `efacae30f8100ecad340f92520bed768a8d683e06de3fe10365afea464626dd9`

### `09_qdrant_collections_validation.png`

Qdrant: validação direta das duas collections — principal com 21 points e CSV com 2, ambas green, 3072 dimensões, Cosine e PASS.

SHA-256: `f9d1804abe8f832ab21d9158cac2e12e0ead434d1e4bddc2c2bbd22982113cc1`
