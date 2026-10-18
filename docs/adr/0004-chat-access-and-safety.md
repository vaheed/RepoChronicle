# ADR 0004: Chat Access and Safety

- Status: Accepted
- Date: 2026-10-18

## Context

The bot may observe engineering groups where participants discuss multiple projects, access levels and private information. Platform-level bot access must not automatically imply organization-wide permission to use every stored message.

## Decision

- Every chat destination is individually registered and opt-in.
- User identity and project/source scope are checked on every retrieval.
- Default behavior is mention/reply-only, not proactive.
- Telegram Business is optional; a regular Telegram Bot API bot serves ordinary groups and channels.
- Telegram privacy mode and channel membership constraints are disclosed and checked.
- Discord message content requires the appropriate privileged intent; channel access and message-history permission are checked.
- No cross-destination or cross-tenant evidence is returned without authorization.

## Consequences

- Connector setup is explicit rather than auto-discovery of every server/channel.
- Permission loss makes data unavailable/stale; it does not silently retain unlimited searchable access.
- Chat backfill claims must match actual provider capabilities.
