# GET /v1/transcriptions Endpoint Implementation

## Overview

This implementation provides a paginated, filterable, and sortable GET endpoint for listing transcriptions.

## Endpoint Details

**URL:** `GET /v1/transcriptions`

**Base Path:** `/v1/transcriptions`

## Query Parameters

| Parameter | Type | Default | Description | Validation |
|-----------|------|---------|-------------|------------|
| `offset` | int | 0 | Number of records to skip | >= 0 |
| `limit` | int | 20 | Maximum records to return | 1-100 (enforced) |
| `date_from` | datetime | None | Filter created_at >= date_from | ISO 8601 format |
| `date_to` | datetime | None | Filter created_at <= date_to | ISO 8601 format, must be after date_from |
| `status` | string | None | Filter by status value | Any string |
| `sort_by` | string | created_at | Sort field | "created_at" or "updated_at" |
| `order` | string | desc | Sort order | "asc" or "desc" |

## Response Schema

```json
{
  "transcriptions": [
    {
      "id": 1,
      "audio_file_path": "/path/to/audio.mp3",
      "transcription_text": "Transcribed content",
      "language_detected": "en",
      "duration": 120.5,
      "status": "completed",
      "created_at": "2024-01-01T12:00:00",
      "updated_at": "2024-01-01T12:05:00"
    }
  ],
  "total": 1,
  "offset": 0,
  "limit": 20
}
```

## Example Requests

### Basic Request (Default Pagination)
```bash
GET /v1/transcriptions
```

### With Pagination
```bash
GET /v1/transcriptions?offset=20&limit=50
```

### Filter by Status
```bash
GET /v1/transcriptions?status=completed
```

### Filter by Date Range
```bash
GET /v1/transcriptions?date_from=2024-01-01T00:00:00&date_to=2024-01-31T23:59:59
```

### Sort by Updated Time (Ascending)
```bash
GET /v1/transcriptions?sort_by=updated_at&order=asc
```

### Combined Filters
```bash
GET /v1/transcriptions?status=completed&date_from=2024-01-01T00:00:00&limit=50&sort_by=created_at&order=desc
```

## Error Responses

### 400 Bad Request - Invalid Limit
```json
{
  "detail": "limit: Limit cannot exceed 100"
}
```

### 400 Bad Request - Invalid Date Range
```json
{
  "detail": "date_to: date_to must be after date_from"
}
```

### 400 Bad Request - Invalid Sort Field
```json
{
  "detail": "sort_by: Invalid sort field"
}
```

## Implementation Details

### File Structure

```
src/
├── routers/
│   └── transcription.py         # FastAPI router with GET endpoint
├── services/
│   └── transcription_service.py # Business logic and database queries
├── schemas/
│   └── transcription.py         # Pydantic models for validation and response
├── models/
│   └── transcription.py         # SQLAlchemy model for database
└── database.py                   # Database session management
```

### Key Features

1. **Pagination**
   - Default offset: 0, default limit: 20
   - Maximum limit enforced at 100 to prevent database overload
   - Returns pagination metadata in response

2. **Filtering**
   - Date range filtering on `created_at` field
   - Status filtering (exact match)
   - Filters are applied using SQLAlchemy AND conditions

3. **Sorting**
   - Sort by `created_at` or `updated_at`
   - Ascending or descending order
   - Default: `created_at` descending (newest first)

4. **Error Handling**
   - Query parameter validation using Pydantic
   - Returns 400 Bad Request with descriptive error messages
   - Handles invalid date formats, out-of-range values, etc.

5. **Empty Results**
   - Returns `{transcriptions: [], total: 0, offset: X, limit: Y}` for no matches
   - Does not throw errors on empty results

6. **Database Optimization**
   - Separate COUNT query for total records
   - Indexed fields for efficient filtering and sorting
   - Pagination applied at database level

## Database Model

The `Transcription` model includes:

- `id` (Primary Key, Integer)
- `audio_file_path` (String)
- `transcription_text` (Text, nullable)
- `language_detected` (String, nullable)
- `duration` (Float, nullable)
- `status` (String, indexed)
- `created_at` (DateTime, indexed, auto-generated)
- `updated_at` (DateTime, indexed, auto-updated)

## OpenAPI Documentation

The endpoint includes comprehensive OpenAPI documentation with:
- Detailed parameter descriptions
- Example responses for 200 and 400 status codes
- Request/response schemas
- Usage examples

Access the interactive API docs at `/docs` when the FastAPI server is running.

## Success Criteria Checklist

- ✅ Returns paginated list of transcriptions with correct offset/limit behavior
- ✅ Date range filtering works correctly with ISO 8601 timestamps
- ✅ Status filtering returns only matching records
- ✅ Total count reflects filtered results (not just current page)
- ✅ Sorting works in both ascending and descending order
- ✅ Empty results return `{transcriptions: [], total: 0}` not errors
- ✅ Invalid parameters return 400 with helpful validation messages
- ✅ Max limit of 100 enforced
- ✅ Comprehensive OpenAPI documentation with examples

## Testing

To test the endpoint:

1. Start the FastAPI server
2. Navigate to `/docs` for interactive testing
3. Try various combinations of query parameters
4. Verify pagination, filtering, and sorting behavior
5. Test edge cases (empty results, invalid parameters, max limit)

## Notes

- The database URL should be configured via environment variables in production
- Consider adding rate limiting for production use
- The service layer can be extended for additional filtering options
- Caching can be added for frequently accessed queries
