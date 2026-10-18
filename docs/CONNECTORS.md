# Connector Contracts: GitHub, GitLab, Telegram, and Discord

## General rules

- Connecting a source requires explicit administrator authorization and an explicit destination/repository registration.
- Credentials are read-only where the source platform supports it. Chat send permissions are separate, minimal permissions granted only for the intended bot behavior.
- Ingested content is untrusted data. Never execute scripts, links, code, commands or instructions from messages/issues/readmes.
- Normalize event IDs, provider timestamps, authors, source URL, thread/reply relationships, edit/delete state, and source ACL scope.
- Preserve raw provider IDs for debugging/deduplication, but redact payloads and secrets from logs.
- Every connector has a capability report: permissions granted, backfill support, earliest available event, last successful cursor, rate-limit status and missing capabilities.

## GitHub

Use a GitHub App or fine-grained read-only token with the minimum required repository permissions. Prefer installation credentials over a developer's personal token in production. Scope each installation to explicitly selected repositories.

Planned data: repository metadata, branch/ref SHA, commits and diffs, PRs/reviews/comments, issues/comments, releases/tags, check runs/workflows, webhook deliveries. The provider adapter must identify which events need different permission scopes and API calls.

Relevant official reference: https://docs.github.com/en/apps/creating-github-apps/setting-up-a-github-app/choosing-permissions-for-a-github-app

## GitLab

Use a project/group access token or OAuth/App installation with the narrowest read-only scopes available. Support GitLab.com and explicitly configured self-managed instances through the same adapter contract.

Planned data: project/repository metadata, commits/diffs, merge requests and notes, issues and notes, releases/tags, pipelines/jobs, webhook events, and provider cursors. Respect server configuration, visibility, API pagination, rate limits and token expiry.

Relevant references:
- https://docs.gitlab.com/user/project/integrations/webhook_events/
- https://docs.gitlab.com/api/

## Telegram (standard Bot API)

Telegram Business is **not required** for ordinary group/channel monitoring. A regular bot is the default connector.

- Create a bot with BotFather and add it to each intended group/channel.
- In groups, bots with privacy mode enabled receive a limited set of messages. To observe ordinary group messages, privacy mode must be disabled or the bot must have the appropriate admin status. Telegram still excludes messages sent by other bots.
- Bots receive messages from channels where they are members; channel administration may be required for the intended posting behavior.
- Configure the bot's allowed updates, webhook secret or long polling, destination allowlist, reply/mention policy and minimum required send permissions.
- Telegram Bot API updates are not a general historic group-message export. Start the live-ingestion cursor at installation/authorization time and report the actual earliest event. Do not pretend past messages were scanned.
- Business-connection updates may be added as an optional adapter for business private-chat use cases; they are not a prerequisite for team groups.

Official references:
- https://core.telegram.org/bots/faq
- https://core.telegram.org/bots/api

## Discord

- Add a bot through the Developer Portal and authorize only intended guilds/channels.
- Grant the minimum channel view/read-history permissions; grant Send Messages only where responses are enabled.
- Use the Gateway for new messages and the REST API for history backfill where permitted.
- Message Content is a privileged intent. It must be enabled in the Developer Portal, and apps subject to verification need approval. Without it, message content fields are empty in most cases, with documented exceptions such as DMs with the app and messages mentioning the app.
- The connector must display whether the intent is enabled, denied or insufficient. It must not silently use empty message bodies as valid conversation context.
- Start backfill only for authorized channels and rate-limit the history request. Track the oldest successfully indexed message ID/time.
- Handle threads, forum posts, message edits/deletes, attachments metadata, and permission changes.

Official references:
- https://discord.com/developers/docs/events/gateway
- https://discord.com/developers/docs/resources/channel#get-channel-messages
- https://discord.com/developers/docs/topics/permissions

## Destination behavior and consent

Each group/channel is registered independently and has explicit modes:
- `disabled`: no content processing.
- `observe`: persist allowed events but do not reply.
- `mention_only`: answer only on mention or platform command.
- `reply_only`: answer when directly replied to.
- `proactive_approved`: only approved event types can trigger suggestions.

Default is `mention_only` after administrator opt-in. Proactive mode must require an explicit admin change, rate limits, quiet hours, duplicate suppression and a confidence threshold. Provide a visible `/status` command and an easy disable/uninstall flow.

## Connector failure cases

Test and document missing permissions, expired credentials, rate limits, duplicate/out-of-order events, reconnect gaps, message edits/deletes, inaccessible thread parents, unsupported media, and provider outage. A bot must not answer using content from an unregistered or unauthorized destination.
