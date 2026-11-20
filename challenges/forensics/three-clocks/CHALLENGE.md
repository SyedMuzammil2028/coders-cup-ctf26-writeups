# Three Clocks

| Field | Details |
| --- | --- |
| Category | Forensics |
| Initial points | 350 |
| Author | Muz4mmil |

## Original challenge statement

Three systems. Three clocks. One incident.

A confidential document was exported from an organization's internal portal. The security team recovered browser activity, application audit logs, and filesystem records from the suspected workstation.

However, each source records time differently, making the incident timeline appear inconsistent.

Your task is to investigate the evidence, identify the account responsible for the unauthorized export, and determine the exact time the export was completed.

Important: All timestamps must be normalized to Coordinated Universal Time (UTC). Your final flag must contain the successful unauthorized export's timestamp in UTC, not the local time shown in an individual evidence source.

Flag format: `ACM{YYYYMMDD_HHMM_username}`

Download the evidence and reconstruct the timeline.
