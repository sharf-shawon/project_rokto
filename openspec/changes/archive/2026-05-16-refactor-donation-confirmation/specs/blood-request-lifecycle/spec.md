## MODIFIED Requirements

### Requirement: Dual-Party Confirmation

A donation SHALL only be considered successful when both the seeker and the donor confirm the donation (YES/YES). This confirmation logic MUST be enforced at the model level to ensure consistency across all access methods (API, Web UI, etc.).

#### Scenario: Successful donation confirmation update

- **WHEN** both seeker and donor confirm "YES" for a request
- **THEN** the donor's `last_donation_date` is updated to the request's donation date, and the request is marked as fully confirmed.

#### Scenario: Out-of-order confirmation date protection

- **WHEN** a donation is confirmed for a date that is older than the donor's existing `last_donation_date`
- **THEN** the donation is marked as confirmed, but the donor's `last_donation_date` remains unchanged.
