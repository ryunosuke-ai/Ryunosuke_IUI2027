### 共通の出力形式

```text
出力はJSON objectのみとし、Markdownや前後の説明文を付けない。

必須キー:
- name
- model_type
- states
- positive_states
- negative_states
- observations
- initial_state_prior
- transition_likelihoods
- emission_likelihoods
- state_descriptions
- observation_descriptions
- dataset_hypothesis

model_typeは"transition_bayes_network"とする。

statesとobservationsには重複を含めない。
positive_statesとnegative_statesはstatesの部分集合とし、互いに重複させない。

initial_state_priorは全stateを含み、合計を1.0とする。
transition_likelihoodsはP(next_state | current_state)を表し、各行に全stateを含め、行合計を1.0とする。
emission_likelihoodsはP(observation | state)を表し、各行に全observationを含め、行合計を1.0とする。

各確率は0より大きく1より小さい数値とする。
ラベルには英小文字、数字、アンダースコアのみを使用する。
state_descriptionsとobservation_descriptionsは、後段のLLMが分類に利用できる具体的な日本語で記述する。
dataset_hypothesisは、コーパスから推定した会話目的を日本語で記述する。
```

## ESConv Prompt

```text
あなたは、会話コーパス分析、支援的対話分析、動的ベイズモデル設計の専門家です。

以下のESConv形式の小規模会話コーパスを分析し、このコーパスがどのような目的・場面・会話スタイルを重視しているかを、会話本文とアノテーションから推定してください。その上で、このコーパスらしい複数ターン会話を大量のprompt/responseデータから抽出するための、状態遷移を持つベイズモデルJSONを作成してください。

この分析で使える情報:
- dialog: userとassistantの実際の会話本文
- annotated_strategy: assistant発話に付与された既存の支援戦略ラベル
- emotion_type: 会話全体に関係する感情カテゴリ
- problem_type: 会話全体に関係する問題カテゴリ
- situation: userが置かれている状況説明
- survey_score: seeker/supporterによる会話評価や感情強度
- seeker/supporter comments: 会話後の自由記述コメント

重要な方針:
- データセット名や外部知識で目的を決めつけず、与えられた本文とアノテーションから推定してください。
- ESConvのアノテーションは有用な補助情報として積極的に使ってください。
- annotated_strategyを機械的にそのまま観測ラベルとしてコピーしないでください。会話本文と整合するよう、似た戦略を統合し、後段評価しやすい安定したontologyにしてください。
- emotion_type、problem_type、situationは、userのニーズや会話状態を推定する手がかりとして使ってください。
- survey_scoreと会話後コメントは、高品質な会話に現れやすい進行・応答戦略を推定する補助情報として使ってください。
- 低頻度すぎるラベルや、prompt/response評価で区別しにくいラベルは統合してください。
- negative_statesは、攻撃的・文法破綻した応答だけではなく、一見自然でもこのコーパスの高品質会話目的から外れる状態を表してください。

Strategy利用方針:
- annotated_strategyは、assistant発話の意図を示す高価値なアノテーションとして強く参照してください。
- 観測ラベルは、annotated_strategyの分布と会話本文を照合して設計してください。
- Question、Reflection of feelings、Restatement or Paraphrasing、Affirmation and Reassurance、Providing Suggestions、Information、Self-disclosure、Othersなどは、必要に応じて統合・再命名し、後段LLMがprompt/responseから安定して分類できる粒度にしてください。
- positive側では、本文・survey・コメント上で支援的に働いているstrategy系列の尤度を高くしてください。
- negative側では、感情反映不足、早すぎる助言、一般論、文脈を拾わない質問など、ESConvの支援目的から外れる応答戦略の尤度を高くしてください。

作業手順:
1. コーパス全体を読み、本文とアノテーションからデータセットの目的、会話場面、望ましい会話スタイルを推定してください。
2. 会話がどのような状態を経て進むかを推定し、状態ラベルを4〜7個作ってください。
3. 状態は会話の進行局面・対話目的上の局面を表し、単なる表現技法や1文だけの特徴にはしないでください。
4. 望ましい会話状態をpositive_states、コーパスから外れる状態をnegative_statesに分類してください。
5. 状態間の遷移確率transition_likelihoodsをP(next_state | current_state)として設定してください。
6. prompt/responseから観測できるassistant応答戦略ラベルを4〜8個作ってください。
7. 観測ラベルは、そのターンのresponseが文脈に対して何をしているかを表し、状態ラベルと同じ意味にしないでください。
8. 各状態で各観測ラベルが出る確率emission_likelihoodsをP(observation | state)として設定してください。
9. initial_state_priorは、会話開始時に各状態がどの程度生じるかを設定してください。

出力には、name、model_type、states、positive_states、negative_states、observations、initial_state_prior、transition_likelihoods、emission_likelihoods、state_descriptions、observation_descriptions、dataset_hypothesisを含めてください。statesは4〜7個、observationsは4〜8個とし、本当に必要なラベルだけに絞ってください。

以下が分析対象コーパスです。

[ESConv CORPUS]
```

### ESConvのコーパス入力形式

```text
# conversation_id={conversation_id}

## conversation_annotations
source_dataset: ESConv
source_split: {split}
experience_type: {experience_type}
emotion_type: {emotion_type}
problem_type: {problem_type}
situation: {situation}
survey_score: {survey_score}
seeker_question1: {seeker_comment}
seeker_question2: {seeker_comment}
supporter_question1: {supporter_comment}
supporter_question2: {supporter_comment}

## dialog
{turn_index}. user: {utterance}
{turn_index}. assistant [annotated_strategy={strategy}]: {utterance}
...
```

## MathDial Prompt

```text
あなたは会話コーパス分析、個別指導対話、動的ベイズモデル設計の専門家です。

以下のMathDial形式の小規模会話コーパスを分析し、このコーパスが重視する個別指導の進め方を表す状態遷移ベイズモデルを作成してください。目的は数学問題そのものを抽出することではなく、学習者の誤りや混乱を診断し、質問や段階的ヒントで自己修正を促す会話スタイルを大量対話から選別することです。

利用できる情報:
- question / ground_truth: 問題と参照解答。数学的文脈の確認にだけ使う。
- dialog: assistant（Teacher）とuser（Student）の完全な複数ターン会話。
- annotated_teacher_moves: MathDial公式のTeacher move。probing、focus、telling、genericがある。連結発話では複数値の場合がある。

Teacher move利用方針:
- annotated_teacher_movesはassistant発話の機能を示す高価値なannotationとして強く参照する。
- ただし4ラベルを機械的に状態名へコピーしない。会話本文、直前の学習者状態、次の学習者反応と照合する。
- probingとfocusが、誤り診断、焦点化、段階的推論、自己修正へどう使い分けられるかを分析する。
- tellingは、診断後の必要な説明・訂正と、情報不足のまま答えを与える早すぎるtellingを区別する。
- genericは、励まし・会話管理として有効な場合と、学習状態に根拠づけられない場合を区別する。
- 診断後に学習者の誤りへ対応して行う説明・訂正は、正の指導戦略として明確に表現する。

モデル設計方針:
1. 状態は会話の進行局面を表す4〜7個とし、単なる数学トピックや表現技法にしない。
2. positive_statesは、診断、足場かけ、自己修正、適切な説明、理解確認などMathDialらしい進行を表す。
3. negative_statesは、早すぎる直接解答、学習者状態を無視した説明、文脈非依存応答などを表す。
4. observationsはprompt/responseから後段LLMが安定分類できるassistant応答戦略を4〜8個作る。
5. initial_state_prior、P(next_state | current_state)、P(observation | state)をコーパス本文とannotationに基づいて設定する。
6. 低頻度・曖昧で区別しにくいラベルは統合する。
7. premature direct answerとは別に、反復、文脈不一致、根拠のない称賛などを表すoff-style observationを必ず作る。
8. 各positive stateと各negative stateに、反対群よりemissionが0.10以上高く、その状態を識別できるobservationを最低1つ持たせる。
9. negative群が優勢なobservationを最低2種類作る。早すぎる直接解答と、文脈不一致・根拠なし応答を同じobservationへ統合しない。
10. stateは潜在的な会話局面、observationは応答から直接分類する機能である。state名とobservation名を同一または機能的に重複させない。

出力には、name、model_type、states、positive_states、negative_states、observations、initial_state_prior、transition_likelihoods、emission_likelihoods、state_descriptions、observation_descriptions、dataset_hypothesisを含めてください。statesは4〜7個、observationsは4〜8個としてください。

以下が分析対象コーパスです。

[MATHDIAL CORPUS]
```

### MathDialのコーパス入力形式

```text
# conversation_id={conversation_id}
question: {mathematics_problem}
ground_truth: {reference_answer}

## dialog
{turn_index}. user: {student_utterance}
{turn_index}. assistant [annotated_teacher_moves={teacher_moves}]: {teacher_utterance}
...
```

## MediTOD Prompt

```text
あなたは医療対話コーパス分析、病歴聴取、動的ベイズモデル設計の専門家です。

以下のMediTOD小規模コーパスを分析し、このコーパスが表現する体系的な病歴聴取の進め方を状態遷移ベイズモデルとして作成してください。目的は医学的診断知識そのものではなく、情報不足を認識し、症状属性を確認し、関連症状から既往歴・服薬・検査・生活背景へ順序立てて移る医療者側の会話スタイルをWildChatから選別することです。

入力には、train全体から決定論的に集計したintent/slot/attribute頻度、会話十分位別slot分布、doctor slot遷移、doctor actionから次patient informationへの遷移と、層化した完全診療が含まれます。official_annotationsは高価値な外部annotationとして強く参照してください。ただし、ラベル名をそのままstate名へコピーせず、会話本文、段階、次の患者情報と照合してください。

必ず区別する機能:
- 主訴を開放的に聴取する。
- 発症時期、期間、経過、重症度、特徴を確認する。
- 関連症状とred flagを確認する。
- 既往歴、家族歴、服薬、検査、習慣、曝露、旅行、生活背景を確認する。
- 既知情報を要約し、適切な次段階へ移る。
- 情報不足のまま診断や対応方針を断定する早すぎるassessment/adviceを識別する。
- すでに得た情報の不要な反復質問と、直前文脈に合わない質問・応答を識別する。

モデル設計方針:
1. statesは病歴聴取の進行局面を表す4〜7個とする。
2. positive_statesは不足情報の認識、適切な質問、情報統合、段階移行を表す。
3. negative_statesは早すぎる診断・助言、重複質問、文脈不一致を表す。
4. observationsはprompt/responseから後段LLMが直接分類できる医療者応答機能を6〜10個作る。
5. state名とobservation名を機能的に重複させない。
6. 各正負stateに反対群よりemissionが0.10以上高い識別observationを持たせる。
7. negative優勢observationは最低2種類とし、premature assessmentとredundancy/misalignmentを統合しない。
8. 病歴聴取の質問と、情報が揃った後の適切な要約・説明を両方正当に扱う。

出力には、name、model_type、states、positive_states、negative_states、observations、initial_state_prior、transition_likelihoods、emission_likelihoods、state_descriptions、observation_descriptions、dataset_hypothesisを含めてください。statesは4〜7個、observationsは6〜10個としてください。

以下が分析対象です。

[MEDITOD AGGREGATES AND CORPUS]
```

### MediTODのコーパス入力形式

```text
# deterministic_train_annotation_aggregates
{
  "train_conversations": ...,
  "train_turns": ...,
  "intent_frequency": {...},
  "slot_frequency": {...},
  "attribute_frequency": {...},
  "slot_by_conversation_decile": {...},
  "doctor_slot_transitions": {...},
  "doctor_action_to_next_patient_information": {...},
  "annotation_disagreement_turns": ...
}

# stratified_complete_consultations

## conversation_id={conversation_id}
{turn_index}. user [official_annotations={annotations}]: {patient_utterance}
{turn_index}. assistant [official_annotations={annotations}]: {doctor_utterance}
...
```
