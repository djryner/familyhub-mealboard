# User Profile Image Upload Feature

## Overview
Admins can now upload profile pictures for users (children) when creating their accounts. Images are stored locally and displayed throughout the application, including the admin interface and the public leaderboard.

## Features

✅ **Image Upload**: Upload photos when creating or editing users  
✅ **Image Update**: Replace user photos at any time  
✅ **Image Removal**: Option to remove photos without uploading a new one  
✅ **Image Preview**: See a preview before submitting  
✅ **Multiple Formats**: Supports JPEG, PNG, GIF, and WebP  
✅ **File Size Limit**: Maximum 5MB per image  
✅ **Automatic Naming**: Files are named with user ID and timestamp  
✅ **Automatic Cleanup**: Old images are deleted when replaced or user is deleted  
✅ **Circular Display**: Images displayed in attractive circular frames  
✅ **Fallback**: Shows emoji placeholder if no image uploaded  

## User Experience

### Creating a User with Image

1. Navigate to Admin → Manage Users → Add User
2. Enter the user's name
3. Click "Choose File" under Profile Picture
4. Select an image (max 5MB)
5. See instant preview of the selected image
6. (Optional) Check "Parent" if user has admin privileges
7. Click "Create User"
8. User is created with their profile picture

### Editing a User

1. Navigate to Admin → Manage Users
2. Click "✏️ Edit" next to any user
3. Update the user's name if needed
4. To **update the photo**:
   - Click "Choose File" and select a new image
   - The old photo will be automatically deleted
5. To **remove the photo** without uploading a new one:
   - Check the "Remove current photo" checkbox
6. Update parent status if needed
7. Click "Save Changes"
8. Old images are automatically cleaned up

### Image Display

**Admin Users List:**
- Shows circular profile pictures (60x60px)
- Displays emoji placeholder if no image

**Leaderboard (Dashboard):**
- Shows smaller circular avatars (40x40px)
- Displays emoji placeholder if no image
- Blue border around images

**Chores & Other Pages:**
- Ready to display user images where needed

## Technical Implementation

### Backend

**New Dependencies:**
```json
{
  "multer": "^1.4.5-lts.1"  // File upload handling
}
```

**File Upload Configuration** (`src/utils/upload.js`):
- Stores files in `public/uploads/users/`
- File naming: `{userId}-{timestamp}.{ext}`
- Validates file types (images only)
- Limits file size to 5MB
- Provides cleanup functions for old images

**Database Schema** (`users` table):
```sql
ALTER TABLE users ADD COLUMN image_url TEXT;
```

**Route Updates** (`src/routes/admin.js`):
- `POST /admin/users/create`: Accepts `multipart/form-data` for image upload
- `GET /admin/users/:id/edit`: Display edit form with current user data
- `POST /admin/users/:id/edit`: Update user with optional new image
- `POST /admin/users/:id/delete`: Deletes user and their image file
- Uses `uploadUserImage.single('userImage')` middleware
- Saves image path to database
- Automatically deletes old images when replaced or user is deleted

### Frontend

**Form Updates** (`views/admin/create_user.ejs` & `views/admin/edit_user.ejs`):
- Added `enctype="multipart/form-data"` to forms
- Image upload input with preview
- Edit form shows current image if exists
- Edit form has "Remove current photo" option
- JavaScript for client-side preview

**Display Updates:**
- `views/admin/users.ejs`: Shows avatars in user list with Edit & Delete buttons
- `views/admin/edit_user.ejs`: NEW - Complete edit form with image update
- `views/index.ejs`: Shows avatars in leaderboard

**Styling** (`public/css/admin.css` & `public/css/style.css`):
- Circular image containers
- Preview area with dashed border
- Responsive sizing
- Fallback placeholder styling

## File Structure

```
public/
  uploads/
    users/
      alice-1703180123456.jpg
      bob-1703180234567.png
      charlie-1703180345678.jpg
```

## Image Specifications

### Upload Requirements
- **Formats**: JPEG, JPG, PNG, GIF, WebP
- **Max Size**: 5MB (5,242,880 bytes)
- **Validation**: Server-side type checking

### Display Sizes
- **Admin List**: 60x60px (circular)
- **Leaderboard**: 40x40px (circular)
- **Preview**: 150x150px (circular)

### Image Processing
- **object-fit**: `cover` (fills circle, crops if needed)
- **Border**: 2-3px solid border
- **Background**: Light gray fallback color

## Security Considerations

✅ **File Type Validation**: Only image MIME types allowed  
✅ **File Size Limit**: Prevents large uploads  
✅ **Server-side Validation**: Multer filters invalid files  
✅ **Unique Filenames**: Timestamp prevents overwrites  
✅ **Local Storage**: No external services, full control  

## Browser Compatibility

- ✅ Chrome/Edge (desktop & mobile)
- ✅ Safari (desktop & mobile)
- ✅ Firefox (desktop & mobile)
- ✅ File input works on all platforms
- ✅ Preview works with FileReader API

## API Reference

### Create User Endpoint
```
POST /admin/users/create
Content-Type: multipart/form-data

Fields:
  - name: string (required)
  - isParent: boolean (optional)
  - userImage: file (optional, max 5MB)
```

### Edit User Endpoint
```
POST /admin/users/:userId/edit
Content-Type: multipart/form-data

Fields:
  - name: string (required)
  - isParent: boolean (optional)
  - userImage: file (optional, max 5MB)
  - removeImage: boolean (optional, "1" to remove)
```

### Response
```
Redirect to /admin/users with success message
```

## Database Schema

```sql
CREATE TABLE users (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  color TEXT,
  avatar TEXT,
  is_parent INTEGER DEFAULT 0,
  image_url TEXT  -- New field
);
```

## Migration

**File**: `migrations/008_users_image_url.sql`
```sql
ALTER TABLE users ADD COLUMN image_url TEXT;
```

**Apply to existing database:**
```bash
sqlite3 familyhub.db < migrations/008_users_image_url.sql
```

## Usage Examples

### Creating User with Image (cURL)
```bash
curl -X POST http://localhost:8000/admin/users/create \
  -F "name=Sarah" \
  -F "isParent=1" \
  -F "userImage=@/path/to/photo.jpg"
```

### Updating User with New Image (cURL)
```bash
curl -X POST http://localhost:8000/admin/users/sarah/edit \
  -F "name=Sarah Smith" \
  -F "isParent=1" \
  -F "userImage=@/path/to/new-photo.jpg"
```

### Removing User Image (cURL)
```bash
curl -X POST http://localhost:8000/admin/users/sarah/edit \
  -F "name=Sarah Smith" \
  -F "isParent=1" \
  -F "removeImage=1"
```

### Image URLs Stored
```
/uploads/users/sarah-1703180123456.jpg
```

### Displaying Images (EJS)
```ejs
<% if (user.image_url) { %>
  <img src="<%= user.image_url %>" alt="<%= user.name %>">
<% } else { %>
  <%= user.avatar || '👤' %>
<% } %>
```

## Future Enhancements (Optional)

1. **Image Cropping**: Client-side crop tool
2. **Image Compression**: Reduce file sizes automatically
3. **Multiple Images**: Gallery of photos per user
4. **Thumbnails**: Generate multiple sizes
5. **CDN Integration**: Upload to cloud storage
6. **Face Detection**: Auto-crop to face
7. **Bulk Upload**: Add multiple users with photos at once

## Troubleshooting

**Image not uploading:**
- Check file size (must be < 5MB)
- Verify file type (JPEG, PNG, GIF, WebP only)
- Ensure `public/uploads/users/` directory exists
- Check server logs for errors

**Image not displaying:**
- Verify `image_url` is saved in database
- Check file exists in `public/uploads/users/`
- Ensure static files are served correctly
- Check browser console for 404 errors

**Preview not working:**
- Verify JavaScript is enabled
- Check browser supports FileReader API
- Look for console errors

## Testing Checklist

✅ Upload JPEG image (create)  
✅ Upload PNG image (create)  
✅ Upload GIF image (create)  
✅ Upload WebP image (create)  
✅ Preview shows before submit  
✅ File size validation (reject > 5MB)  
✅ File type validation (reject non-images)  
✅ Image appears in admin list  
✅ Image appears in leaderboard  
✅ Emoji fallback works  
✅ Circular display is correct  
✅ Edit user name  
✅ Update user photo (old photo deleted)  
✅ Remove user photo (checkbox)  
✅ Delete user (image file deleted)  

---

**Status**: ✅ Fully Implemented with Edit & Delete Cleanup
**Date**: December 21, 2025
