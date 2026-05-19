## Why

The current user onboarding process in Project Rokto doesn't effectively differentiate between a guest user and a blood donor. Profile updates are unorganized, and verification status is opaque (a single "verified" flag). To improve donor conversion and trust across Bangladesh, we need a dedicated registration flow for donors and a clearer, granular verification UI on the profile page.

## What Changes

- **Dedicated Donor Registration Flow** — Introduction of `BecomeDonorView` and `DonorRegistrationForm` to handle donor-specific onboarding separately from basic account updates.
- **Mandatory Donor Fields** — Marking Blood Group, Date of Birth, and Preferred Locations as mandatory _only_ within the donor registration flow.
- **Granular Verification UI** — Replacing the single verification badge with individual statuses for Phone, NID, and Email, including direct action links for unverified items.
- **"Become a Donor" Nudge** — A prominent, native-styled call-to-action on the profile page for guest users.
- **Organized Form Layout** — Section-based layout for both profile updates and donor registration to reduce cognitive load.

## Capabilities

### New Capabilities

- `donor-onboarding-flow`: A dedicated, multi-step process to register as a blood donor with mandatory health and location data.
- `granular-verification-status`: UI component and logic to display and action specific verification requirements (Phone, NID, Email).

### Modified Capabilities

- _(None - existing specs don't cover specific onboarding UI layouts)_

## Impact

- **Views**: New `BecomeDonorView`, updated `UserUpdateView` in `project_rokto/users/views.py`.
- **Forms**: New `DonorRegistrationForm`, updated `UserUpdateForm` in `project_rokto/users/forms.py`.
- **Templates**: `user_detail.html` (for granular badges and nudge), `user_form.html` (restructured layout), and a new `donor_registration.html`.
- **URLs**: New path for `users:become_donor`.
