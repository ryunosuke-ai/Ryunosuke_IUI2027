以下が、supplementaryに掲載する3ドメインの全state、全strategy、target states、initial distribution、transition matrix、observation matrixです。実装上、strategyはobservation labelに対応します。

## ESConv

### 全state

1. `opening_rapport`
2. `clarify_problem`
3. `empathic_support`
4. `collaborative_planning`
5. `closing_encouragement`
6. `misaligned_support`

### 全strategy

1. `greet_checkin`
2. `explore_question`
3. `reflect_validate`
4. `practical_guidance`
5. `self_disclosure`
6. `close_meta`
7. `misattuned_generic`

### Target states

- `opening_rapport`
- `clarify_problem`
- `empathic_support`
- `collaborative_planning`
- `closing_encouragement`

### Initial distribution

| State                    | Probability |
| ------------------------ | ----------: |
| `opening_rapport`        |        0.44 |
| `clarify_problem`        |        0.26 |
| `empathic_support`       |        0.14 |
| `collaborative_planning` |        0.07 |
| `closing_encouragement`  |        0.03 |
| `misaligned_support`     |        0.06 |

### Transition matrix \(P(s*t \mid s*{t-1})\)

| Current \ Next           | opening_rapport | clarify_problem | empathic_support | collaborative_planning | closing_encouragement | misaligned_support |
| ------------------------ | --------------: | --------------: | ---------------: | ---------------------: | --------------------: | -----------------: |
| `opening_rapport`        |            0.10 |            0.48 |             0.19 |                   0.07 |                  0.04 |               0.12 |
| `clarify_problem`        |            0.03 |            0.26 |             0.34 |                   0.25 |                  0.04 |               0.08 |
| `empathic_support`       |            0.02 |            0.20 |             0.32 |                   0.30 |                  0.10 |               0.06 |
| `collaborative_planning` |            0.01 |            0.12 |             0.21 |                   0.36 |                  0.23 |               0.07 |
| `closing_encouragement`  |            0.01 |            0.04 |             0.10 |                   0.12 |                  0.66 |               0.07 |
| `misaligned_support`     |            0.04 |            0.16 |             0.16 |                   0.16 |                  0.08 |               0.40 |

### Observation matrix \(P(o_t \mid s_t)\)

| State \ Strategy         | greet_checkin | explore_question | reflect_validate | practical_guidance | self_disclosure | close_meta | misattuned_generic |
| ------------------------ | ------------: | ---------------: | ---------------: | -----------------: | --------------: | ---------: | -----------------: |
| `opening_rapport`        |          0.42 |             0.29 |             0.15 |               0.03 |            0.04 |       0.03 |               0.04 |
| `clarify_problem`        |          0.05 |             0.43 |             0.26 |               0.09 |            0.05 |       0.03 |               0.09 |
| `empathic_support`       |          0.03 |             0.12 |             0.53 |               0.10 |            0.12 |       0.04 |               0.06 |
| `collaborative_planning` |          0.02 |             0.16 |             0.17 |               0.47 |            0.08 |       0.04 |               0.06 |
| `closing_encouragement`  |          0.03 |             0.04 |             0.23 |               0.07 |            0.05 |       0.52 |               0.06 |
| `misaligned_support`     |          0.04 |             0.14 |             0.07 |               0.16 |            0.11 |       0.08 |               0.40 |

## MathDial

### 全state

1. `orientation`
2. `fault_mapping`
3. `repair_cycle`
4. `stalled_recovery`
5. `resolution_window`
6. `ungrounded_resolution`
7. `interaction_breakdown`

### 全strategy

1. `solution_process_elicitation`
2. `diagnostic_probe`
3. `focused_step_prompt`
4. `analogy_transfer_prompt`
5. `diagnosis_grounded_explanation`
6. `verification_reflection`
7. `premature_direct_answer`
8. `off_style_response`

### Target states

- `orientation`
- `fault_mapping`
- `repair_cycle`
- `stalled_recovery`
- `resolution_window`

### Initial distribution

| State                   | Probability |
| ----------------------- | ----------: |
| `orientation`           |        0.54 |
| `fault_mapping`         |        0.20 |
| `repair_cycle`          |        0.09 |
| `stalled_recovery`      |        0.06 |
| `resolution_window`     |        0.04 |
| `ungrounded_resolution` |        0.03 |
| `interaction_breakdown` |        0.04 |

### Transition matrix \(P(s*t \mid s*{t-1})\)

| Current \ Next          | orientation | fault_mapping | repair_cycle | stalled_recovery | resolution_window | ungrounded_resolution | interaction_breakdown |
| ----------------------- | ----------: | ------------: | -----------: | ---------------: | ----------------: | --------------------: | --------------------: |
| `orientation`           |        0.11 |          0.49 |         0.17 |             0.06 |              0.10 |                  0.03 |                  0.04 |
| `fault_mapping`         |        0.03 |          0.24 |         0.41 |             0.15 |              0.08 |                  0.05 |                  0.04 |
| `repair_cycle`          |        0.02 |          0.12 |         0.32 |             0.20 |              0.25 |                  0.05 |                  0.04 |
| `stalled_recovery`      |        0.02 |          0.13 |         0.30 |             0.15 |              0.32 |                  0.05 |                  0.03 |
| `resolution_window`     |        0.05 |          0.08 |         0.12 |             0.07 |              0.54 |                  0.03 |                  0.11 |
| `ungrounded_resolution` |        0.03 |          0.08 |         0.18 |             0.22 |              0.19 |                  0.24 |                  0.06 |
| `interaction_breakdown` |        0.05 |          0.14 |         0.13 |             0.10 |              0.08 |                  0.16 |                  0.34 |

### Observation matrix \(P(o_t \mid s_t)\)

| State \ Strategy        | solution_process_elicitation | diagnostic_probe | focused_step_prompt | analogy_transfer_prompt | diagnosis_grounded_explanation | verification_reflection | premature_direct_answer | off_style_response |
| ----------------------- | ---------------------------: | ---------------: | ------------------: | ----------------------: | -----------------------------: | ----------------------: | ----------------------: | -----------------: |
| `orientation`           |                         0.45 |             0.20 |                0.08 |                    0.05 |                           0.05 |                    0.10 |                    0.03 |               0.04 |
| `fault_mapping`         |                         0.08 |             0.43 |                0.20 |                    0.10 |                           0.06 |                    0.07 |                    0.03 |               0.03 |
| `repair_cycle`          |                         0.03 |             0.19 |                0.36 |                    0.24 |                           0.08 |                    0.06 |                    0.02 |               0.02 |
| `stalled_recovery`      |                         0.03 |             0.09 |                0.15 |                    0.05 |                           0.48 |                    0.10 |                    0.07 |               0.03 |
| `resolution_window`     |                         0.04 |             0.08 |                0.16 |                    0.04 |                           0.10 |                    0.52 |                    0.02 |               0.04 |
| `ungrounded_resolution` |                         0.03 |             0.05 |                0.07 |                    0.03 |                           0.13 |                    0.08 |                    0.57 |               0.04 |
| `interaction_breakdown` |                         0.05 |             0.07 |                0.06 |                    0.05 |                           0.06 |                    0.08 |                    0.07 |               0.56 |

## MediTOD

### 全state

1. `agenda_entry`
2. `problem_representation`
3. `risk_boundary`
4. `whole_person_context`
5. `evidence_consolidation`
6. `insufficient_basis_path`
7. `broken_context_path`

### 全strategy

1. `open_complaint_invitation`
2. `missing_information_clarification`
3. `symptom_attribute_probe`
4. `associated_red_flag_probe`
5. `history_context_probe`
6. `summary_and_stage_signal`
7. `conditional_assessment_or_plan`
8. `unsupported_assessment_or_advice`
9. `redundant_requestioning`
10. `context_misaligned_response`

### Target states

- `agenda_entry`
- `problem_representation`
- `risk_boundary`
- `whole_person_context`
- `evidence_consolidation`

### Initial distribution

| State                     | Probability |
| ------------------------- | ----------: |
| `agenda_entry`            |        0.58 |
| `problem_representation`  |        0.18 |
| `risk_boundary`           |        0.07 |
| `whole_person_context`    |        0.05 |
| `evidence_consolidation`  |        0.03 |
| `insufficient_basis_path` |        0.05 |
| `broken_context_path`     |        0.04 |

### Transition matrix \(P(s*t \mid s*{t-1})\)

| Current \ Next            | agenda_entry | problem_representation | risk_boundary | whole_person_context | evidence_consolidation | insufficient_basis_path | broken_context_path |
| ------------------------- | -----------: | ---------------------: | ------------: | -------------------: | ---------------------: | ----------------------: | ------------------: |
| `agenda_entry`            |         0.16 |                   0.51 |          0.13 |                 0.08 |                   0.05 |                    0.04 |                0.03 |
| `problem_representation`  |         0.03 |                   0.37 |          0.31 |                 0.16 |                   0.07 |                   0.035 |               0.025 |
| `risk_boundary`           |         0.02 |                   0.14 |          0.35 |                 0.30 |                   0.12 |                    0.04 |                0.03 |
| `whole_person_context`    |        0.015 |                  0.065 |          0.09 |                 0.48 |                   0.27 |                   0.045 |               0.035 |
| `evidence_consolidation`  |         0.02 |                   0.04 |          0.04 |                 0.06 |                   0.67 |                    0.10 |                0.07 |
| `insufficient_basis_path` |         0.04 |                   0.09 |          0.06 |                 0.05 |                   0.13 |                    0.55 |                0.08 |
| `broken_context_path`     |         0.05 |                   0.11 |          0.08 |                 0.08 |                   0.08 |                    0.12 |                0.48 |

### Observation matrix \(P(o_t \mid s_t)\)

| State \ Strategy          | open_complaint_invitation | missing_information_clarification | symptom_attribute_probe | associated_red_flag_probe | history_context_probe | summary_and_stage_signal | conditional_assessment_or_plan | unsupported_assessment_or_advice | redundant_requestioning | context_misaligned_response |
| ------------------------- | ------------------------: | --------------------------------: | ----------------------: | ------------------------: | --------------------: | -----------------------: | -----------------------------: | -------------------------------: | ----------------------: | --------------------------: |
| `agenda_entry`            |                      0.50 |                              0.12 |                    0.10 |                      0.05 |                  0.04 |                     0.06 |                           0.04 |                             0.02 |                    0.03 |                        0.04 |
| `problem_representation`  |                      0.04 |                              0.12 |                    0.52 |                      0.14 |                  0.06 |                     0.05 |                           0.03 |                             0.01 |                   0.015 |                       0.015 |
| `risk_boundary`           |                     0.025 |                              0.09 |                    0.15 |                      0.54 |                  0.07 |                    0.055 |                           0.04 |                            0.015 |                  0.0075 |                      0.0075 |
| `whole_person_context`    |                     0.015 |                              0.07 |                   0.065 |                      0.10 |                  0.56 |                     0.07 |                           0.05 |                            0.015 |                   0.025 |                        0.03 |
| `evidence_consolidation`  |                     0.015 |                              0.07 |                    0.04 |                      0.05 |                  0.08 |                     0.39 |                           0.31 |                            0.015 |                   0.015 |                       0.015 |
| `insufficient_basis_path` |                     0.025 |                             0.035 |                    0.05 |                      0.04 |                  0.04 |                     0.07 |                           0.15 |                             0.53 |                   0.025 |                       0.035 |
| `broken_context_path`     |                     0.025 |                             0.045 |                    0.06 |                      0.05 |                  0.06 |                     0.04 |                           0.04 |                             0.05 |                    0.32 |                        0.31 |
