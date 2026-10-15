# Claude Code / Codex compatibility

確認日: 2026-10-16。Claude Code用の `plugins/` と `.claude-plugin/` は
変更せず、既存の11 Skills、参照資料、テンプレート、7つのエージェント指示を
再利用して `codex/plugins/` に自己完結したCodexパッケージを生成します。
インストール先から元のClaudeパッケージを参照する依存やシンボリックリンクはありません。

## 仕様と構成

OpenAI公式の [Package your plugin](https://developers.openai.com/plugins/build/plugins)
に従い、各パッケージのルートにAgent Plugins 1.0.0の `plugin.json` を配置します。
Skillsはルートの `skills/` で検出され、OpenAI固有設定は
`extensions.com.openai` に置きます。`.codex-plugin/plugin.json` は互換用の
フォールバックなので、この構成では重複して作成しません。
カタログは [.agents/plugins/marketplace.json](../.agents/plugins/marketplace.json) です。

```text
plugins/<name>/                 Claude Code用の原本
codex/plugins/<name>/
  plugin.json                  Codex用ポータブルマニフェスト
  skills/*/SKILL.md             name / descriptionを持つSkills
  skills/*/agents/openai.yaml   明示呼び出し用ポリシー
  agents/*.md                  新規Subagentへ渡す役割指示（自動登録用ではない）
  docs/                        共通ルールとCodex実行アダプター
.agents/plugins/marketplace.json
```

## インストールと使用

対応する最新Codexクライアントと、認証済みの `gh`、Gitが必要です。
このリポジトリのルートでカタログを追加します。

```sh
codex plugin marketplace add .
codex plugin list --marketplace k1nak0 --available --json
```

デスクトップアプリでは再起動後、Plugins Directoryで `k1nak0 workflows` を
選び、必要なプラグインをインストールします。CLI 0.162.1では次の操作も
提供されています（CLIの `codex plugin add --help` で確認）。

```sh
codex plugin add task-splitter@k1nak0
codex plugin add implementation-workflow@k1nak0
codex plugin add light-workflow@k1nak0
```

新規会話で `$task-splitter:task-splitter`、
`$implementation-workflow:implementation-workflow`、
`$light-workflow:light-workflow` を明示して要求を渡します。
導入確認には `$implementation-workflow:onboarding` を使用します。
これらは実際のCodexローダーが返した名前です。
Claude Codeでは従来のインストール・スラッシュコマンドをそのまま使えます。

## 変換と制約

| 対象 | 調査結果・Codexでの実装 | 直接移植できない点・代替案 |
|---|---|---|
| commands | 原本に独立したcommandsはなく、入口を含め全11件が既存Skills | Claudeの `/plugin:skill` をCodexの明示的な `$skill` 呼び出しに変更 |
| Skills | 本文・テンプレートを再利用し、必須のnameを追加。Claude用フロントマターを除去 | `user-invocable: false` と同一の非表示制御は保証しない。全Skillsを明示呼び出し用にして、内部フェーズはオーケストレーターが読む |
| Subagents | 7つの役割指示を維持し、役割本文と絶対パスを新規の標準Codex Subagentに渡す | Claudeのagents配列は登録されない。Codexのカスタムagent種別を偽装せず、通常エージェントへの指示として渡す |
| 新規コンテキスト | 各フェーズ・修正ラウンドで新規作成し、完了待ち・結果収集後に終了。継続情報はファイル | 親会話を引き継がない生成を使えるクライアントが必要。利用不可なら独立レビューを含む処理を停止し、対応クライアントを案内 |
| エージェントの役割 | repository-explorer、library-researcher、test-writer、test-reviewer、implementer、code-reviewer、persistence-engineer | 名前は自動登録されない。実行アダプターが対応するagents文書を読み込む |
| モデル・権限 | `model: sonnet`、`permissionMode: acceptEdits`、`maxTurns: 50` を除去 | Claudeモデルや権限の自動付与は不可。Codexセッションのモデル・権限を継承。フェーズの再試行上限は維持するが50ターン制限は保証しない |
| Skill / Agentツール | 本文の操作例をrun_skill / delegateという明示的なワークフロー疑似コードに変更 | 同名ツールは作らない。Skillsはファイルを読んで同一会話で実行、委譲はネイティブSubagentツールに対応付け |
| 進捗・質問 | TaskCreate/Update/Listを計画・チェックリストに、AskUserQuestionを会話上の質問に対応付け | 専用Task APIの同じUIは再現しない。必要な回答・承認は待つ。既存のユーザー承認は再要求しない |
| MCP | 原本にMCPサーバー設定なし。GitHubはgh、任意ツールは利用先のdocs/toolsやdocs/tool.mdで指定 | 変換すべき接続・認証情報はなく、空の設定は追加しない。将来同梱する場合はroot mcp.jsonとMCPスキーマ、明示的transport typeを使う |
| Hooks | 原本にHooksもスクリプトもなく、実行イベントへの依存なし | 修正対象なし。将来追加時はイベント・入力/出力・実行権限を個別検証。現仕様では手動デスクトップインストールと信頼操作が必要で、Hooks付きは公開ディレクトリ対象外 |
| 環境変数 | CLAUDE_PLUGIN_ROOTを廃止し、実際のインストール先からルートを解決 | WORKFLOW_PLUGIN_ROOTはシェル例のために明示設定する作業変数。Codexが自動設定するという前提を置かない |
| ツール・設定 | ファイル操作・検索・Web検索をセッションの実ツールに対応付け、CLAUDE.mdをAGENTS.mdに変更 | ToolSearch等の固定名や特定ホストのネットワーク前提は使わない。利用不能な機能は報告し、制限を迂回しない |
| 作業ファイル・再開 | `.codex/workflow-runs/<workflow>/<task-id>/` を使用 | Claudeの `.claude/` の既存実行履歴は自動変換しない。必要なら利用者が対象を明示して移行。Codex設定を守るため `.codex/` 全体をgitignoreしない |

Subagentの権限・MCP継承は公式の
[Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)、
Skillsの形式と明示呼び出しは
[Build skills](https://learn.chatgpt.com/docs/build-skills) を参照。
詳細な実行手順は各パッケージの `docs/codex-runtime.md` に同梱しています。

## 再生成・検証

原本を変更したら次を実行して、生成物も一緒にコミットします。

```sh
python3 scripts/build_codex.py
python3 scripts/build_codex.py --check
python3 scripts/check_codex.py
```

生成後の差分、必須メタデータ、残存するClaude専用記法、役割と内部Skillsの
参照先、別ディレクトリへコピーした全パッケージの相対リンクを検証します。
CIでも同期検査・静的検証を実行します。将来commands/MCP/Hooksが原本に
追加された場合は、未対応のまま生成せず、明示的な移植を求めて失敗します。

実機確認: Codex CLI 0.162.1で設定ファイルを書き換えない一時的な `-c` 指定を
使い、3パッケージの名前・バージョン・ソースの検出を確認しました。
さらにapp-serverの `plugin/read` で3つのマニフェストとSkillsを読み込み、
表示情報・名前空間付きスキル名・MCP/Hooksが空であることを確認しました。
11 Skills、7役割、全内部リンクの検証も成功しています。
これはパッケージとカタログの検証であり、モデルを使う全フェーズのE2E実行や
GUIでのインストール完了を意味しません。

実際の導入先では、新規会話で次の受入確認を行ってください。

1. `$implementation-workflow:onboarding` でGit/gh、AGENTS.md、プロジェクトのツール文書を確認する。
2. `$task-splitter:task-splitter` で小さな要求を渡し、確認前にIssue/PRが作られないことを確認する。
3. `$implementation-workflow:implementation-workflow` で調査・テスト作者・テストレビューが別の新規
   Subagentで実行され、テスト凍結後にimplementerが凍結対象を編集しないことを確認する。
4. `$light-workflow:light-workflow` で小さな修正を行い、差分・検証結果が提示され、未承認の
   コミット・push・PR作成が行われないことを確認する。

Issue作成、push、PR作成を伴うE2E確認はこの移植作業では実行していません。
