# User Edit Feature - Quick Start Guide

## How to Edit a User

### Step 1: Navigate to Manage Users
1. Open the admin panel: `http://your-pi:8000/admin`
2. Click **"👥 Manage Users"**
3. You'll see a list of all users with their photos and points

### Step 2: Click Edit
1. Find the user you want to edit
2. Click the **"✏️ Edit"** button next to their name
3. The edit form will open showing their current information

### Step 3: Make Your Changes

#### To Update the Name:
- Simply type a new name in the "Name" field
- The user ID will remain the same

#### To Update the Photo:
- Click **"Choose File"** under Profile Picture
- Select a new image from your device
- You'll see an instant preview of the new photo
- The old photo will be automatically deleted when you save

#### To Remove the Photo:
- Check the box that says **"Remove current photo"**
- The preview will change to show the emoji placeholder
- The photo file will be deleted when you save

#### To Change Parent Status:
- Check or uncheck the **"Parent (has admin privileges)"** box
- Parents can access the admin panel

### Step 4: Save Changes
1. Click **"Save Changes"**
2. You'll be redirected to the users list
3. You'll see a success message
4. The changes will be visible immediately

### Step 5: Cancel (Optional)
- Click **"Cancel"** to go back without saving
- No changes will be made

---

## Visual Examples

### Edit Form Layout
```
┌─────────────────────────────────┐
│  ✏️ Edit User: Alex             │
├─────────────────────────────────┤
│                                 │
│  Name *                         │
│  [Alex________________]         │
│                                 │
│  Profile Picture                │
│     ┌─────────┐                │
│     │  👤 or  │  ← Current photo│
│     │  Photo  │                │
│     └─────────┘                │
│  [Choose File] no file chosen  │
│                                 │
│  ☐ Remove current photo         │
│                                 │
│  ☑ Parent (admin privileges)   │
│                                 │
│  [Save Changes] [Cancel]        │
└─────────────────────────────────┘
```

### Users List with Buttons
```
┌────────────────────────────────────────┐
│  👥 Manage Users         [➕ Add User] │
├────────────────────────────────────────┤
│                                        │
│  ┌─────────────────────────────────┐  │
│  │ 👤  Alex              [Edit] [X]│  │
│  │    ⭐ 150 points                │  │
│  └─────────────────────────────────┘  │
│                                        │
│  ┌─────────────────────────────────┐  │
│  │ 🙂  Sarah • 👑       [Edit] [X]│  │
│  │    ⭐ 250 points • Parent       │  │
│  └─────────────────────────────────┘  │
│                                        │
│  [← Back to Admin]                     │
└────────────────────────────────────────┘
```

---

## Common Scenarios

### Scenario 1: Add a Photo to Existing User
**Starting point**: User has no photo (shows 👤)

1. Click Edit on the user
2. Click "Choose File"
3. Select a photo
4. See preview
5. Click "Save Changes"
6. Photo now appears everywhere (list, leaderboard, etc.)

### Scenario 2: Change User's Photo
**Starting point**: User has a photo

1. Click Edit on the user
2. See current photo in preview
3. Click "Choose File"
4. Select new photo
5. Preview updates to new photo
6. Click "Save Changes"
7. Old photo deleted, new photo saved

### Scenario 3: Remove a Photo
**Starting point**: User has a photo

1. Click Edit on the user
2. See current photo in preview
3. Check "Remove current photo"
4. Preview changes to 👤 emoji
5. Click "Save Changes"
6. Photo deleted, emoji shown

### Scenario 4: Just Change the Name
**Starting point**: User exists

1. Click Edit on the user
2. Update the name field
3. Don't touch the photo
4. Click "Save Changes"
5. Name updated, photo unchanged

### Scenario 5: Make User a Parent
**Starting point**: Regular user

1. Click Edit on the user
2. Check "Parent (has admin privileges)"
3. Click "Save Changes"
4. User can now access admin panel

---

## Tips & Tricks

### ✨ Pro Tips
- **Preview before saving**: Always check the preview before clicking Save
- **High-quality photos**: Use clear, well-lit photos for best results
- **Square photos**: Work best for circular avatars
- **File size**: Keep under 1MB for fast uploads (max 5MB)
- **Mobile camera**: You can take photos directly if on mobile

### 🎯 Best Practices
- Use photos showing faces clearly
- Consistent photo style for all users
- Update photos occasionally to keep current
- Test on mobile and desktop

### ⚠️ Important Notes
- **Old photos are deleted**: When you upload a new photo or remove one
- **No undo**: After saving, changes are permanent (create backup first)
- **Emoji fallback**: If no photo, shows 👤 or custom emoji
- **Parent access**: Only parents can access admin panel

---

## Troubleshooting

### Problem: Photo won't upload
**Solutions**:
- Check file size (must be under 5MB)
- Check file type (must be JPEG, PNG, GIF, or WebP)
- Try a different photo
- Check internet connection
- Refresh the page and try again

### Problem: Preview doesn't show
**Solutions**:
- Make sure file is selected
- Check browser console for errors
- Try a different browser
- Clear cache and reload

### Problem: Changes don't save
**Solutions**:
- Check for error messages
- Ensure name field is filled
- Check server logs
- Verify uploads directory is writable

### Problem: Old photo still showing
**Solutions**:
- Hard refresh browser (Cmd+Shift+R or Ctrl+Shift+R)
- Clear browser cache
- Check if new photo was uploaded
- Verify in database

---

## Keyboard Shortcuts

- **Tab**: Move between fields
- **Enter**: Submit form (same as clicking Save)
- **Escape**: Close preview (if implemented)
- **Space**: Toggle checkbox

---

## Mobile Considerations

### On Mobile Devices
- Tap "Edit" button
- Tap "Choose File"
- Select "Camera" or "Photo Library"
- Take photo or select existing
- See preview
- Tap "Save Changes"

### Mobile Features
- Camera integration
- Touch-friendly buttons
- Large input fields
- Easy file selection
- Responsive design

---

## Security Notes

- Only admins can edit users
- Changes are logged
- Old photos securely deleted
- File types validated
- Size limits enforced

---

## Quick Reference

| Action | Button/Field | Result |
|--------|-------------|--------|
| Edit user | ✏️ Edit button | Opens edit form |
| Update name | Name field | Changes display name |
| Upload photo | Choose File | Replaces old photo |
| Remove photo | Remove checkbox | Deletes current photo |
| Grant admin | Parent checkbox | Gives admin access |
| Save | Save Changes button | Applies all changes |
| Cancel | Cancel button | Discards changes |

---

## Need Help?

- Check server logs: `/tmp/server.log`
- Review documentation: `USER-MANAGEMENT-COMPLETE.md`
- Check feature docs: `IMAGE-UPLOAD-FEATURE.md`
- Verify setup: `USER-EDIT-IMPLEMENTATION.md`

---

**Last Updated**: December 21, 2025  
**Version**: 1.0  
**Status**: Production Ready ✅
