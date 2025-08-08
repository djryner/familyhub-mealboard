# Family Hub - Meal Board

## Overview

Family Hub is a comprehensive family management dashboard designed to help families stay organized with chores, meal planning, and notifications. The application provides both public viewing access for family members and admin functionality for content management. Originally designed as a Raspberry Pi dashboard for displaying dinner plans from Google Calendar, it has evolved into a full-featured web application with database-backed content management.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Application Structure
- **Framework**: Flask-based web application with traditional server-side rendering
- **Database**: SQLAlchemy ORM with PostgreSQL (configurable via DATABASE_URL)
- **Authentication**: Replit Auth integration with OAuth support for admin access
- **Templates**: Jinja2 templating with Bootstrap 5 dark theme for responsive UI
- **Static Assets**: Font Awesome icons and Bootstrap CSS/JS from CDN

### Authentication & Authorization
- **Public Access**: All users can view chores, meal plans, and notifications without authentication
- **Admin Access**: Replit Auth OAuth flow for admin users with elevated permissions
- **User Management**: User and OAuth models support multiple authentication providers
- **Session Management**: Persistent sessions with browser-specific OAuth tokens

### Data Models
- **Users**: Profile information with admin role flags and OAuth provider support
- **Chores**: Task management with assignments, due dates, priorities, and completion tracking
- **Meal Plans**: Planned meals with dates, types (breakfast/lunch/dinner), and ingredient lists
- **Notifications**: Family announcements with types, expiration dates, and active status

### Frontend Architecture
- **Responsive Design**: Bootstrap 5 grid system optimized for mobile and tablet viewing
- **Dark Theme**: Consistent dark color scheme throughout the application
- **Interactive Elements**: Tab-based filtering, modal dialogs for admin actions, and real-time status updates
- **Progressive Enhancement**: JavaScript enhancements for better UX while maintaining core functionality without JS

### Backend Architecture
- **Route Organization**: Separated public routes (viewing) and admin routes (management) with decorator-based access control
- **Database Management**: Automatic table creation on startup with proper relationship handling
- **Error Handling**: Custom 403 pages and flash messaging for user feedback
- **WSGI Configuration**: ProxyFix middleware for proper HTTPS URL generation in production

## External Dependencies

### Authentication Services
- **Replit Auth**: Primary authentication provider for admin access
- **Flask-Dance**: OAuth2 consumer for handling authentication flows
- **Flask-Login**: Session management and user authentication state

### Database & ORM
- **SQLAlchemy**: Database ORM with declarative base models
- **Flask-SQLAlchemy**: Flask integration for database operations
- **PostgreSQL**: Production database (configurable via DATABASE_URL environment variable)

### Google Calendar Integration
- **Google Calendar API**: Read-only access to family calendar for meal planning
- **Service Account Authentication**: Credentials-based access to Google services
- **Python libraries**: google-api-python-client, google-auth packages for API interaction

### Frontend Dependencies
- **Bootstrap 5**: UI framework with dark theme variant from Replit CDN
- **Font Awesome 6**: Icon library for consistent visual elements
- **Native Browser APIs**: Local storage, DOM manipulation without additional frameworks

### Environment Configuration
- **DATABASE_URL**: PostgreSQL connection string
- **SESSION_SECRET**: Flask session encryption key
- **GOOGLE_APPLICATION_CREDENTIALS**: Path to Google service account JSON
- **FAMILYHUB_CALENDAR_ID**: Google Calendar ID for meal plan integration
- **FAMILYHUB_TZ**: Timezone for calendar event processing