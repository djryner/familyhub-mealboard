# Chores Feature Rework - Implementation Summary

## Overview
The chores management feature has been completely reworked to provide a user-centric workflow where admins first select a user, then manage chores specific to that user.

## Changes Made

### 1. Database Schema
No changes were needed to the existing database schema. The current tables support the new workflow:
- `chore_metadata` - Stores chore definitions (title, assigned_to, recurrence/frequency, points)
- `chores` - Stores individual chore occurrences (task_id, due_date, status)

### 2. Service Layer (`src/services/chores.js`)

#### New Methods Added:

**`getChoresByUser(userId)`**
- Fetches all chore definitions for a specific user
- Returns chore metadata ordered by title

**`createChore({ title, assignedTo, frequency, points })`**
- Creates a new chore definition with metadata
- Generates a unique task_id
- Calls `generateChoreOccurrences()` to create initial instances
- Supported frequencies: `daily`, `weekends`, `weekdays`, `school-week`

**`generateChoreOccurrences(taskId, frequency)`**
- Generates chore occurrences for the next 30 days based on frequency
- Frequency definitions:
  - `daily`: Every day
  - `weekends`: Saturday and Sunday only
  - `weekdays`: Monday through Friday
  - `school-week`: Sunday, Monday, Tuesday, Wednesday, Thursday

**`updateChore(taskId, { title, frequency, points })`**
- Updates chore definition
- Removes future pending occurrences
- Regenerates occurrences with new frequency

**`deleteChore(taskId)`**
- Deletes chore definition and all occurrences
- Past completions remain in history

### 3. Admin Routes (`src/routes/admin.js`)

#### New Routes:

**User Selection**
- `GET /admin/chores` - Display list of users to select from
- View: `views/admin/chores_select_user.ejs`

**User-Specific Chore Management**
- `GET /admin/chores/user/:userId` - Display all chores for selected user
- View: `views/admin/manage_user_chores.ejs`

**Create Chore**
- `GET /admin/chores/user/:userId/create` - Display create form
- `POST /admin/chores/user/:userId/create` - Handle form submission
- View: `views/admin/create_user_chore.ejs`

**Edit Chore**
- `GET /admin/chores/:taskId/edit` - Display edit form
- `POST /admin/chores/:taskId/edit` - Handle form submission
- View: `views/admin/edit_user_chore.ejs`

**Delete Chore**
- `GET /admin/chores/:taskId/delete-confirm` - Display confirmation page
- `POST /admin/chores/:taskId/delete` - Handle deletion
- View: `views/admin/delete_user_chore_confirm.ejs`

### 4. View Templates

#### Created 5 New EJS Templates:

1. **`chores_select_user.ejs`**
   - Lists all users with avatar/image
   - Shows count of assigned chores per user
   - Click to manage chores for that user

2. **`manage_user_chores.ejs`**
   - Shows all chores assigned to selected user
   - Displays: title, points, frequency
   - Actions: Edit, Delete
   - Button to add new chore

3. **`create_user_chore.ejs`**
   - Form with fields:
     - Chore Name (text input)
     - Frequency (dropdown: Every Day, Weekends, Weekdays, School Week)
     - Points per Completion (number input, default: 1)

4. **`edit_user_chore.ejs`**
   - Same form as create, pre-populated with existing values
   - Note explaining that changing frequency regenerates occurrences

5. **`delete_user_chore_confirm.ejs`**
   - Shows chore details
   - Warning about deletion
   - Confirm/Cancel buttons

## User Flow

### Admin Flow:
1. Navigate to `/admin/chores`
2. Select a user from the list
3. View all chores assigned to that user
4. Add new chore with:
   - Name
   - Frequency (daily, weekends, weekdays, school week)
   - Points value
5. Edit existing chores (updates frequency and regenerates occurrences)
6. Delete chores (removes definition and future occurrences)

### Frequency Definitions:
- **Every Day**: Chore appears every single day
- **Weekends**: Saturday and Sunday only
- **Weekdays**: Monday through Friday (Mon-Fri)
- **School Week**: Sunday through Thursday (Sun-Thu)

## Technical Notes

### Chore Generation
- When a chore is created, occurrences are generated for the next 30 days
- Occurrences are created in the `chores` table with status='pending'
- Each occurrence is linked to the chore definition via `task_id`

### Editing Behavior
- Editing a chore's frequency removes all future pending occurrences
- New occurrences are generated based on the updated frequency
- Past completed/ignored occurrences remain unchanged

### Points System
- Points are stored in the chore definition (`chore_metadata`)
- When a chore occurrence is completed, points are awarded based on the definition
- Points value can be any positive integer

## Testing the Feature

1. Start the server: `npm start`
2. Navigate to: `http://localhost:8000/admin`
3. Click "Manage Chores"
4. Select a user
5. Add a new chore with desired frequency and points
6. Verify occurrences are created correctly on the main dashboard

## Legacy Features Preserved

The old template-based chore system routes are still available:
- `GET /admin/chores/template/create`
- `POST /admin/chores/template/create`

These can be removed in a future update if no longer needed.

## Files Modified

### Modified:
- `src/services/chores.js` - Added user-centric chore management methods
- `src/routes/admin.js` - Added new routes for user-based chore workflow

### Created:
- `views/admin/chores_select_user.ejs`
- `views/admin/manage_user_chores.ejs`
- `views/admin/create_user_chore.ejs`
- `views/admin/edit_user_chore.ejs`
- `views/admin/delete_user_chore_confirm.ejs`

## Next Steps / Future Enhancements

1. Add ability to customize which days for "school week" (make it configurable)
2. Add bulk actions (delete multiple chores at once)
3. Add chore templates that can be quickly assigned to users
4. Add ability to pause/resume recurring chores
5. Add notifications/reminders for upcoming chores
6. Add ability to view completed chores history per user
7. Add analytics (completion rate, points earned over time)

---

**Date Implemented:** December 21, 2025
**Status:** ✅ Complete and Ready for Testing
