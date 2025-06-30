# Sample Project API Documentation

## Project: TaskManager

A comprehensive task management system with REST API, web interface, and mobile app support.

**Version:** 2.1.0  
**Last Updated:** 2024-01-15  
**Repository:** https://github.com/example/taskmanager  

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Authentication](#authentication)
4. [API Endpoints](#api-endpoints)
5. [Frontend Components](#frontend-components)
6. [Utility Functions](#utility-functions)
7. [Error Handling](#error-handling)
8. [SDK Usage](#sdk-usage)

---

## Overview

TaskManager is a full-stack application that provides:
- RESTful API for task management
- React-based web interface
- Mobile app (React Native)
- Real-time notifications
- Team collaboration features

### Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web App       │    │   Mobile App    │    │   Third-party   │
│   (React)       │    │ (React Native)  │    │   Integrations  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   REST API      │
                    │   (Node.js)     │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Database      │
                    │   (PostgreSQL)  │
                    └─────────────────┘
```

---

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/example/taskmanager.git
cd taskmanager

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
npm run migrate

# Start the development server
npm run dev
```

### Basic Usage

```javascript
import { TaskManagerAPI } from '@taskmanager/sdk';

const api = new TaskManagerAPI({
  apiKey: 'your-api-key',
  baseURL: 'https://api.taskmanager.com'
});

// Create a new task
const task = await api.tasks.create({
  title: 'Complete documentation',
  description: 'Write comprehensive API docs',
  dueDate: '2024-02-01',
  priority: 'high'
});

console.log('Task created:', task.id);
```

---

## Authentication

TaskManager uses API key authentication for server-to-server communication and JWT tokens for user sessions.

### API Key Authentication

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://api.taskmanager.com/v1/tasks
```

### JWT Authentication

```javascript
// Login to get JWT token
const response = await fetch('/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'secure_password'
  })
});

const { token } = await response.json();

// Use token for subsequent requests
const tasks = await fetch('/api/tasks', {
  headers: { 'Authorization': `Bearer ${token}` }
});
```

---

## API Endpoints

### Tasks

#### GET /api/v1/tasks

Retrieves a list of tasks with optional filtering and pagination.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| limit | integer | No | 20 | Number of tasks to return (max 100) |
| offset | integer | No | 0 | Number of tasks to skip |
| status | string | No | all | Filter by status: `pending`, `completed`, `all` |
| assignee | string | No | - | Filter by assignee user ID |
| due_date | string | No | - | Filter by due date (YYYY-MM-DD) |
| priority | string | No | - | Filter by priority: `low`, `medium`, `high` |

**Response:**

```json
{
  "status": "success",
  "data": {
    "tasks": [
      {
        "id": "task_123456",
        "title": "Complete API documentation",
        "description": "Write comprehensive docs for all endpoints",
        "status": "pending",
        "priority": "high",
        "assignee": {
          "id": "user_789",
          "name": "John Doe",
          "email": "john@example.com"
        },
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T14:20:00Z",
        "due_date": "2024-01-20T23:59:59Z"
      }
    ],
    "pagination": {
      "total": 150,
      "limit": 20,
      "offset": 0,
      "has_more": true
    }
  }
}
```

**Example Usage:**

```bash
# Get all tasks
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "https://api.taskmanager.com/v1/tasks"

# Get high priority tasks
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "https://api.taskmanager.com/v1/tasks?priority=high&limit=10"

# Get tasks due today
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "https://api.taskmanager.com/v1/tasks?due_date=2024-01-15"
```

#### POST /api/v1/tasks

Creates a new task.

**Request Body:**

```json
{
  "title": "string",
  "description": "string",
  "assignee_id": "string",
  "due_date": "string (ISO 8601)",
  "priority": "string",
  "tags": ["string"],
  "project_id": "string"
}
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "id": "task_123456",
    "title": "New task",
    "description": "Task description",
    "status": "pending",
    "priority": "medium",
    "assignee": {
      "id": "user_789",
      "name": "John Doe",
      "email": "john@example.com"
    },
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "due_date": "2024-01-20T23:59:59Z"
  }
}
```

**Example:**

```javascript
const newTask = await fetch('/api/v1/tasks', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer YOUR_TOKEN'
  },
  body: JSON.stringify({
    title: 'Review pull request',
    description: 'Review PR #123 for security updates',
    assignee_id: 'user_456',
    due_date: '2024-01-18T17:00:00Z',
    priority: 'high',
    tags: ['code-review', 'security'],
    project_id: 'proj_789'
  })
});

const task = await newTask.json();
```

#### PUT /api/v1/tasks/{task_id}

Updates an existing task.

**Path Parameters:**
- `task_id` (string, required): The unique task identifier

**Request Body:** Same as POST request, all fields optional

**Response:** Updated task object

**Example:**

```bash
curl -X PUT \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"status": "completed", "priority": "low"}' \
     "https://api.taskmanager.com/v1/tasks/task_123456"
```

#### DELETE /api/v1/tasks/{task_id}

Deletes a task.

**Path Parameters:**
- `task_id` (string, required): The unique task identifier

**Response:**

```json
{
  "status": "success",
  "message": "Task deleted successfully"
}
```

---

## Frontend Components

### TaskCard Component

A reusable React component for displaying task information.

```jsx
import React from 'react';
import PropTypes from 'prop-types';
import { formatDate, getPriorityColor } from '../utils/helpers';

/**
 * TaskCard component for displaying task information in a card layout.
 * 
 * @component
 * @param {Object} props - Component props
 * @param {Object} props.task - Task data object
 * @param {string} props.task.id - Task unique identifier
 * @param {string} props.task.title - Task title
 * @param {string} props.task.description - Task description
 * @param {string} props.task.status - Task status ('pending', 'completed', 'in_progress')
 * @param {string} props.task.priority - Task priority ('low', 'medium', 'high')
 * @param {string} props.task.due_date - Task due date (ISO string)
 * @param {Object} props.task.assignee - Assignee information
 * @param {boolean} [props.showActions=true] - Whether to show action buttons
 * @param {Function} [props.onEdit] - Callback when edit button is clicked
 * @param {Function} [props.onDelete] - Callback when delete button is clicked
 * @param {Function} [props.onStatusChange] - Callback when status changes
 * @param {string} [props.className] - Additional CSS classes
 * @returns {JSX.Element} TaskCard component
 * 
 * @example
 * // Basic usage
 * <TaskCard
 *   task={{
 *     id: 'task_123',
 *     title: 'Complete documentation',
 *     description: 'Write API docs',
 *     status: 'pending',
 *     priority: 'high',
 *     due_date: '2024-01-20T23:59:59Z',
 *     assignee: { name: 'John Doe', email: 'john@example.com' }
 *   }}
 * />
 * 
 * @example
 * // With custom actions
 * <TaskCard
 *   task={taskData}
 *   showActions={true}
 *   onEdit={(task) => setEditingTask(task)}
 *   onDelete={(taskId) => deleteTask(taskId)}
 *   onStatusChange={(taskId, newStatus) => updateTaskStatus(taskId, newStatus)}
 *   className="custom-card"
 * />
 * 
 * @since 1.0.0
 * @author Frontend Team
 */
const TaskCard = ({
  task,
  showActions = true,
  onEdit,
  onDelete,
  onStatusChange,
  className = ''
}) => {
  const handleStatusToggle = () => {
    if (onStatusChange) {
      const newStatus = task.status === 'pending' ? 'completed' : 'pending';
      onStatusChange(task.id, newStatus);
    }
  };

  const priorityColor = getPriorityColor(task.priority);
  const isOverdue = new Date(task.due_date) < new Date();

  return (
    <div className={`task-card ${className} ${task.status}`}>
      <div className="task-header">
        <h3 className="task-title">{task.title}</h3>
        <span 
          className={`priority-badge priority-${task.priority}`}
          style={{ backgroundColor: priorityColor }}
        >
          {task.priority}
        </span>
      </div>
      
      <p className="task-description">{task.description}</p>
      
      <div className="task-meta">
        <div className="assignee">
          <img 
            src={task.assignee?.avatar || '/default-avatar.png'} 
            alt={task.assignee?.name}
            className="avatar"
          />
          <span>{task.assignee?.name}</span>
        </div>
        
        <div className={`due-date ${isOverdue ? 'overdue' : ''}`}>
          <span>Due: {formatDate(task.due_date)}</span>
        </div>
      </div>
      
      {showActions && (
        <div className="task-actions">
          <button
            onClick={handleStatusToggle}
            className={`status-btn ${task.status}`}
          >
            {task.status === 'pending' ? 'Mark Complete' : 'Mark Pending'}
          </button>
          
          {onEdit && (
            <button onClick={() => onEdit(task)} className="edit-btn">
              Edit
            </button>
          )}
          
          {onDelete && (
            <button 
              onClick={() => onDelete(task.id)} 
              className="delete-btn"
            >
              Delete
            </button>
          )}
        </div>
      )}
    </div>
  );
};

TaskCard.propTypes = {
  /** Task data object */
  task: PropTypes.shape({
    id: PropTypes.string.isRequired,
    title: PropTypes.string.isRequired,
    description: PropTypes.string.isRequired,
    status: PropTypes.oneOf(['pending', 'completed', 'in_progress']).isRequired,
    priority: PropTypes.oneOf(['low', 'medium', 'high']).isRequired,
    due_date: PropTypes.string.isRequired,
    assignee: PropTypes.shape({
      name: PropTypes.string,
      email: PropTypes.string,
      avatar: PropTypes.string
    })
  }).isRequired,
  /** Whether to show action buttons */
  showActions: PropTypes.bool,
  /** Callback when edit button is clicked */
  onEdit: PropTypes.func,
  /** Callback when delete button is clicked */
  onDelete: PropTypes.func,
  /** Callback when status changes */
  onStatusChange: PropTypes.func,
  /** Additional CSS classes */
  className: PropTypes.string
};

export default TaskCard;
```

### TaskList Component

A container component for displaying multiple tasks.

```jsx
/**
 * TaskList component for displaying a collection of tasks with filtering and sorting.
 * 
 * @component
 * @param {Object} props - Component props
 * @param {Array} props.tasks - Array of task objects
 * @param {boolean} [props.loading=false] - Whether data is loading
 * @param {string} [props.emptyMessage='No tasks found'] - Message when no tasks
 * @param {Object} [props.filters] - Current filter settings
 * @param {Function} [props.onFilterChange] - Filter change callback
 * @param {string} [props.sortBy='due_date'] - Sort field
 * @param {string} [props.sortOrder='asc'] - Sort order ('asc' or 'desc')
 * @param {Function} [props.onSortChange] - Sort change callback
 * @returns {JSX.Element} TaskList component
 * 
 * @example
 * <TaskList
 *   tasks={tasks}
 *   loading={isLoading}
 *   filters={{ status: 'pending', priority: 'high' }}
 *   onFilterChange={handleFilterChange}
 *   sortBy="due_date"
 *   sortOrder="asc"
 *   onSortChange={handleSortChange}
 * />
 */
const TaskList = ({
  tasks,
  loading = false,
  emptyMessage = 'No tasks found',
  filters,
  onFilterChange,
  sortBy = 'due_date',
  sortOrder = 'asc',
  onSortChange
}) => {
  // Component implementation...
};
```

---

## Utility Functions

### Date and Time Utilities

```javascript
/**
 * Formats a date string for display in the UI.
 * 
 * @function formatDate
 * @param {string} dateString - ISO date string
 * @param {Object} [options={}] - Formatting options
 * @param {string} [options.format='short'] - Format type: 'short', 'long', 'relative'
 * @param {string} [options.timezone='UTC'] - Timezone for formatting
 * @returns {string} Formatted date string
 * @throws {Error} Throws error if dateString is invalid
 * 
 * @example
 * formatDate('2024-01-15T10:30:00Z')
 * // Returns: "Jan 15, 2024"
 * 
 * @example
 * formatDate('2024-01-15T10:30:00Z', { format: 'long' })
 * // Returns: "January 15, 2024 at 10:30 AM"
 * 
 * @example
 * formatDate('2024-01-15T10:30:00Z', { format: 'relative' })
 * // Returns: "2 days ago" or "in 3 hours"
 * 
 * @since 1.0.0
 * @author Utils Team
 */
export function formatDate(dateString, options = {}) {
  const { format = 'short', timezone = 'UTC' } = options;
  
  try {
    const date = new Date(dateString);
    
    if (isNaN(date.getTime())) {
      throw new Error(`Invalid date string: ${dateString}`);
    }
    
    switch (format) {
      case 'short':
        return date.toLocaleDateString('en-US', {
          month: 'short',
          day: 'numeric',
          year: 'numeric',
          timeZone: timezone
        });
        
      case 'long':
        return date.toLocaleDateString('en-US', {
          month: 'long',
          day: 'numeric',
          year: 'numeric',
          hour: 'numeric',
          minute: '2-digit',
          timeZone: timezone
        });
        
      case 'relative':
        return getRelativeTime(date);
        
      default:
        throw new Error(`Unsupported format: ${format}`);
    }
  } catch (error) {
    console.error('Error formatting date:', error);
    return 'Invalid date';
  }
}

/**
 * Gets relative time string (e.g., "2 hours ago", "in 3 days").
 * 
 * @function getRelativeTime
 * @param {Date} date - Date object to compare with current time
 * @returns {string} Relative time string
 * 
 * @example
 * getRelativeTime(new Date(Date.now() - 3600000))
 * // Returns: "1 hour ago"
 * 
 * @since 1.2.0
 */
export function getRelativeTime(date) {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSeconds = Math.floor(diffMs / 1000);
  const diffMinutes = Math.floor(diffSeconds / 60);
  const diffHours = Math.floor(diffMinutes / 60);
  const diffDays = Math.floor(diffHours / 24);
  
  if (diffSeconds < 60) {
    return 'just now';
  } else if (diffMinutes < 60) {
    return `${diffMinutes} minute${diffMinutes !== 1 ? 's' : ''} ago`;
  } else if (diffHours < 24) {
    return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
  } else if (diffDays < 7) {
    return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
  } else {
    return date.toLocaleDateString();
  }
}
```

### Task Utilities

```javascript
/**
 * Gets the appropriate color for a task priority level.
 * 
 * @function getPriorityColor
 * @param {string} priority - Priority level ('low', 'medium', 'high')
 * @returns {string} Hex color code
 * @throws {Error} Throws error if priority is not supported
 * 
 * @example
 * getPriorityColor('high')
 * // Returns: "#ff4757"
 * 
 * @example
 * getPriorityColor('medium')
 * // Returns: "#ffa502"
 * 
 * @since 1.0.0
 */
export function getPriorityColor(priority) {
  const colors = {
    low: '#2ed573',
    medium: '#ffa502',
    high: '#ff4757'
  };
  
  if (!colors[priority]) {
    throw new Error(`Unsupported priority level: ${priority}`);
  }
  
  return colors[priority];
}

/**
 * Validates task data before creation or update.
 * 
 * @function validateTask
 * @param {Object} taskData - Task data object
 * @param {boolean} [isUpdate=false] - Whether this is an update operation
 * @returns {Object} Validation result with isValid boolean and errors array
 * 
 * @example
 * const result = validateTask({
 *   title: 'New task',
 *   description: 'Task description',
 *   priority: 'high'
 * });
 * 
 * if (!result.isValid) {
 *   console.error('Validation errors:', result.errors);
 * }
 * 
 * @since 1.1.0
 */
export function validateTask(taskData, isUpdate = false) {
  const errors = [];
  const required = isUpdate ? [] : ['title'];
  
  // Check required fields
  required.forEach(field => {
    if (!taskData[field] || taskData[field].trim() === '') {
      errors.push(`${field} is required`);
    }
  });
  
  // Validate title length
  if (taskData.title && taskData.title.length > 200) {
    errors.push('Title must be less than 200 characters');
  }
  
  // Validate priority
  if (taskData.priority && !['low', 'medium', 'high'].includes(taskData.priority)) {
    errors.push('Priority must be one of: low, medium, high');
  }
  
  // Validate due date
  if (taskData.due_date) {
    const dueDate = new Date(taskData.due_date);
    if (isNaN(dueDate.getTime())) {
      errors.push('Due date must be a valid date');
    }
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
}
```

---

## Error Handling

### Error Response Format

All API errors follow a consistent format:

```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": [
      {
        "field": "title",
        "message": "Title is required"
      }
    ],
    "request_id": "req_123456789"
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `AUTHENTICATION_ERROR` | 401 | Invalid or missing authentication |
| `AUTHORIZATION_ERROR` | 403 | Insufficient permissions |
| `VALIDATION_ERROR` | 400 | Request validation failed |
| `NOT_FOUND` | 404 | Resource not found |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Internal server error |

### Error Handling in JavaScript

```javascript
/**
 * Custom error class for API errors.
 * 
 * @class APIError
 * @extends Error
 * @param {string} message - Error message
 * @param {number} status - HTTP status code
 * @param {string} code - Error code
 * @param {Object} [details] - Additional error details
 * 
 * @example
 * throw new APIError('Task not found', 404, 'NOT_FOUND');
 * 
 * @since 1.0.0
 */
class APIError extends Error {
  constructor(message, status, code, details = null) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

/**
 * Generic API request handler with error handling.
 * 
 * @async
 * @function apiRequest
 * @param {string} url - Request URL
 * @param {Object} [options={}] - Fetch options
 * @returns {Promise<Object>} API response data
 * @throws {APIError} Throws APIError on request failure
 * 
 * @example
 * try {
 *   const data = await apiRequest('/api/tasks', { method: 'GET' });
 *   console.log(data);
 * } catch (error) {
 *   if (error instanceof APIError) {
 *     console.error(`API Error: ${error.message} (${error.code})`);
 *   }
 * }
 * 
 * @since 1.0.0
 */
export async function apiRequest(url, options = {}) {
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      throw new APIError(
        data.error?.message || 'Request failed',
        response.status,
        data.error?.code || 'UNKNOWN_ERROR',
        data.error?.details
      );
    }
    
    return data;
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    
    // Handle network errors
    throw new APIError(
      'Network request failed',
      0,
      'NETWORK_ERROR'
    );
  }
}
```

---

## SDK Usage

### Installation

```bash
npm install @taskmanager/sdk
```

### Configuration

```javascript
import { TaskManagerSDK } from '@taskmanager/sdk';

const sdk = new TaskManagerSDK({
  apiKey: process.env.TASKMANAGER_API_KEY,
  baseURL: 'https://api.taskmanager.com',
  version: 'v1',
  timeout: 10000,
  retryAttempts: 3
});
```

### Task Operations

```javascript
// Create a task
const newTask = await sdk.tasks.create({
  title: 'Review code',
  description: 'Review the new authentication module',
  assignee_id: 'user_123',
  priority: 'high',
  due_date: '2024-01-20T17:00:00Z'
});

// Get tasks with filtering
const tasks = await sdk.tasks.list({
  status: 'pending',
  assignee: 'user_123',
  limit: 50
});

// Update a task
const updatedTask = await sdk.tasks.update('task_456', {
  status: 'completed',
  priority: 'medium'
});

// Delete a task
await sdk.tasks.delete('task_789');
```

### User Operations

```javascript
// Get current user
const user = await sdk.users.getCurrentUser();

// Update user profile
const updatedUser = await sdk.users.update(user.id, {
  name: 'John Smith',
  email: 'john.smith@example.com'
});

// Get team members
const team = await sdk.users.getTeamMembers();
```

### Real-time Events

```javascript
// Subscribe to task updates
sdk.events.subscribe('task.updated', (event) => {
  console.log('Task updated:', event.data);
});

// Subscribe to new task assignments
sdk.events.subscribe('task.assigned', (event) => {
  console.log('New task assigned:', event.data);
});

// Unsubscribe from events
sdk.events.unsubscribe('task.updated');
```

---

## Version History

### v2.1.0 (2024-01-15)
- Added real-time notifications
- Improved task filtering performance
- Added bulk operations support
- Updated React components with accessibility improvements

### v2.0.0 (2023-12-01)
- **Breaking Change:** Updated API authentication to use Bearer tokens
- Added GraphQL endpoint support
- Introduced team collaboration features
- Redesigned frontend components

### v1.5.0 (2023-10-15)
- Added task comments and attachments
- Improved mobile responsiveness
- Added export functionality
- Performance optimizations

### v1.0.0 (2023-08-01)
- Initial release
- Basic CRUD operations for tasks
- User authentication and authorization
- React web interface

---

## Support

- **Documentation:** https://docs.taskmanager.com
- **API Status:** https://status.taskmanager.com
- **GitHub Issues:** https://github.com/example/taskmanager/issues
- **Email Support:** support@taskmanager.com
- **Discord:** https://discord.gg/taskmanager

---

## License

MIT License - see [LICENSE](LICENSE) file for details.