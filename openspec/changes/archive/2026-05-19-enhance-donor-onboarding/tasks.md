## 1. Forms & Views

- [x] 1.1 Create `DonorRegistrationForm` in `project_rokto/users/forms.py` with mandatory Blood Group, DOB, and Locations.
- [x] 1.2 Implement `BecomeDonorView` in `project_rokto/users/views.py` using the new form and `LoginRequiredMixin`.
- [x] 1.3 Update `UserUpdateForm` to organize basic fields and ensure health fields remain optional for non-donors.
- [x] 1.4 Add URL path for `become-donor/` in `project_rokto/users/urls.py`.

## 2. Templates & UI Components

- [x] 2.1 Create `project_rokto/templates/users/donor_registration.html` with a sectioned layout (Health, Location, Info).
- [x] 2.2 Refactor `project_rokto/templates/users/user_form.html` to use a sectioned Bootstrap layout for better readability.
- [x] 2.3 Implement Granular Verification Dashboard in `project_rokto/templates/users/user_detail.html` (Phone, NID, Email badges).
- [x] 2.4 Add \"Become a Blood Donor\" nudge card in `user_detail.html` for users with incomplete donor profiles.
- [x] 2.5 Ensure all unverified statuses in the dashboard have direct \"Verify Now\" links for the account owner.

## 3. Testing & Verification

- [x] 3.1 Add unit tests for `BecomeDonorView` to verify mandatory field enforcement.
- [x] 3.2 Add integration tests for the \"Become a Donor\" nudge visibility logic.
- [x] 3.3 Verify Granular Verification UI displays correct statuses for all combinations of verified/unverified (Phone, NID, Email).
- [x] 3.4 Run `just check` to ensure no regressions and verify coverage.
