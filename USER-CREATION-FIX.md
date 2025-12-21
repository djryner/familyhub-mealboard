# User Creation Fix - Auto-generate User IDs

## Problem
When trying to add a user in the admin interface:
1. User types a name in the form
2. Clicks "Create User"
3. Form clears but no user is created
4. User is not redirected to the users list

**Root Cause**: The backend route expected both `id` and `name` fields, but the form only provided `name`. The route was silently failing the validation check and redirecting back to the form without showing an error.

## Solution
Updated the user creation route to **automatically generate unique IDs** from the user's name:

### ID Generation Logic
1. Take the user's name (e.g., "John Doe")
2. Convert to lowercase and remove special characters → "johndoe"
3. Check if ID already exists in database
4. If exists, append a number → "johndoe1", "johndoe2", etc.
5. Use the unique ID to create the user

### Example ID Generation
- "Alice" → `alice`
- "Bob Smith" → `bobsmith`
- "Bob Smith" (second user) → `bobsmith1`
- "Test User #1" → `testuser1`

## Changes Made

### Backend Route (`src/routes/admin.js`)
**Before**:
```javascript
router.post('/users/create', (req, res) => {
  const { id, name, color, avatar } = req.body;
  
  if (!id || !name) {  // Failed because no ID provided
    req.flash('error', 'ID and name are required.');
    return res.redirect('/admin/users/create');
  }
  
  db.prepare('INSERT INTO users (id, name, color, avatar) VALUES (?, ?, ?, ?)');
  stmt.run(id, name, color || '#3498db', avatar || '👤');
  ...
});
```

**After**:
```javascript
router.post('/users/create', (req, res) => {
  const { name, isParent } = req.body;
  
  if (!name) {  // Only name is required
    req.flash('error', 'Name is required.');
    return res.redirect('/admin/users/create');
  }
  
  // Auto-generate unique ID from name
  const baseId = name.toLowerCase().replace(/[^a-z0-9]/g, '');
  let id = baseId;
  let counter = 1;
  
  // Ensure ID is unique
  while (db.prepare('SELECT id FROM users WHERE id = ?').get(id)) {
    id = `${baseId}${counter}`;
    counter++;
  }
  
  // Insert the user with generated ID
  db.prepare('INSERT INTO users (id, name, color, avatar) VALUES (?, ?, ?, ?)');
  stmt.run(id, name, '#3498db', '👤');
  
  // Handle parent flag
  if (isParent) {
    db.prepare('UPDATE users SET is_parent = 1 WHERE id = ?').run(id);
  }
  ...
});
```

### Database Schema Update
**Added `is_parent` column to users table**:
- Type: INTEGER
- Default: 0 (false)
- Purpose: Mark users as parents with admin privileges

**Files Updated**:
- `src/db/init.js` - Added column to CREATE TABLE statement
- `migrations/007_users_is_parent.sql` - Migration file
- Applied to existing database with ALTER TABLE

### Form (`views/admin/create_user.ejs`)
No changes needed! The form already:
- Only asks for `name` (required field)
- Includes `isParent` checkbox (optional)

## Testing Results

✅ **Basic user creation**:
```bash
# Create user "TestUser"
# Result: ID = "testuser", Name = "TestUser"
```

✅ **Duplicate name handling**:
```bash
# Create another "TestUser"
# Result: ID = "testuser1", Name = "TestUser"
```

✅ **Parent flag**:
```bash
# Create "TestUser" with isParent checked
# Result: is_parent = 1
```

✅ **Redirect after creation**:
- Successfully redirects to `/admin/users`
- Shows success message: "User [Name] created successfully!"

## Benefits

1. **Simpler UX**: Users only need to enter a name
2. **No conflicts**: Automatic handling of duplicate names
3. **No manual IDs**: System generates clean, predictable IDs
4. **Backwards compatible**: Works with existing users
5. **Proper feedback**: Success/error messages display correctly

## User Flow

### Before (Broken):
1. Click "Add User"
2. Type name: "Sarah"
3. Click "Create User"
4. ❌ Form clears, nothing happens, no feedback

### After (Working):
1. Click "Add User"
2. Type name: "Sarah"
3. (Optional) Check "Parent" checkbox
4. Click "Create User"
5. ✅ Redirected to users list
6. ✅ See success message: "User Sarah created successfully!"
7. ✅ "Sarah" appears in the users list with ID "sarah"

## Database Impact

**Existing users** (not affected):
- alice → Alice
- bob → Bob
- charlie → Charlie

**New users** (auto-generated IDs):
- sarah → Sarah
- johndoe → John Doe
- johndoe1 → John Doe (duplicate)

## Edge Cases Handled

1. **Special characters**: "John O'Brien" → `johnobrien`
2. **Spaces**: "Mary Jane" → `maryjane`
3. **Numbers**: "User 123" → `user123`
4. **Duplicates**: Appends counter automatically
5. **Empty name**: Shows error message
6. **Very long names**: Uses full normalized string

---

**Status**: ✅ Fixed and tested
**Date**: December 21, 2025
