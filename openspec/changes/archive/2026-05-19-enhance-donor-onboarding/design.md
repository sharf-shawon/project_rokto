## Context

Project Rokto's current profile update page is unorganized, mixing basic user info with detailed donor health data. There is no clear distinction in the UI between a registered blood donor and a regular user, and the verification status is limited to a single "verified" flag. This design aims to split these concerns into a dedicated donor onboarding flow and a granular verification status dashboard on the profile page.

## Goals / Non-Goals

**Goals:**

- Separate donor registration from basic profile updates to allow for targeted validation.
- Make Blood Group, Date of Birth, and Preferred Locations mandatory for donors.
- Provide a clear, sectioned UI for all user/donor forms.
- Display individual verification states (Phone, NID, Email) with actionable links.
- Nudge guest users to become donors using native-styled UI components.

**Non-Goals:**

- Modifying the underlying data models (User, Donor).
- Changing the NID verification backend logic.
- Implementing an age-check on Date of Birth (separate concern).

## Decisions

### 1. Dedicated `DonorRegistrationForm` & View

We will create a new `BecomeDonorView` that uses a `DonorRegistrationForm`.

- **Rationale**: This allows us to set `required=True` on fields like `blood_group` and `date_of_birth` without affecting the `UserUpdateForm` (which guest users use for basic name/email changes).
- **Implementation**: The view will check if a user already has a completed donor profile and redirect/inform accordingly.

### 2. Form Layout Componentization

We will use a section-based layout in `user_form.html` and the new `donor_registration.html`.

- **Rationale**: Reduces cognitive load for users by grouping related fields (Health, Location, Identity).
- **Implementation**: Manual rendering of crispy fields within Bootstrap card/row structures instead of a single `{{ form|crispy }}`.

### 3. Granular Verification Dashboard

Replace the single "Verification Status" line in `user_detail.html` with a grid of status badges.

- **Statuses**:
  - **Phone**: Green (Verified) or Warning (Verify Now).
  - **NID**: Green (Verified), Blue (Pending Review), Red (Rejected), or Gray (Verify Now).
  - **Email**: Green (Verified) or Gray (Add Email).
- **Rationale**: Clearly communicates what is missing to the user, reducing support requests and improving trust.

### 4. Native Profile Nudge

A new `card` component will be added to the top of `user_detail.html` (only visible to the owner).

- **Logic**: `if not object.donor_profile.blood_group`.
- **Styling**: Matches existing card shadow-sm and border-0 styling, but with a background highlight or border-start-danger to draw attention.

## Risks / Trade-offs

- **[Risk]** Form abandonment: Mandatory fields in the donor flow might discourage registration. → **Mitigation**: Clear messaging explaining _why_ these are needed (e.g., "To help match you with seekers") and keeping the initial signup very simple.
- **[Risk]** Redundancy: Users might be confused between "Update Profile" and "Register as Donor". → **Mitigation**: The "Update Profile" button will dynamically change text or we will clearly label the sections.
