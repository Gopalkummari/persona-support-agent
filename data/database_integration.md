# Database Integration Troubleshooting

## Overview
This document provides troubleshooting guidance for customers integrating our platform with external databases. Covers connection issues, query errors, and performance optimization.

---

## 1. Supported Databases

| Database      | Minimum Version | Connector     |
|---------------|-----------------|---------------|
| PostgreSQL    | 12.0            | psycopg2      |
| MySQL         | 8.0             | mysql-connector |
| MongoDB       | 5.0             | pymongo       |
| SQLite        | 3.35            | Built-in      |
| Redis         | 6.0             | redis-py      |
| Elasticsearch | 7.10            | elasticsearch-py |

---

## 2. Connection Errors

### Error: "Connection Refused" (ECONNREFUSED)
**Cause**: The database server is not running, or the connection details are incorrect.

**Resolution**:
1. Verify the database host, port, and credentials in your configuration
2. Ensure the database service is running: `systemctl status postgresql`
3. Check firewall rules allow inbound connections on the database port
4. For cloud databases, verify the IP allowlist includes your server's IP
5. Test connectivity with: `telnet <host> <port>`

### Error: "Authentication Failed"
**Cause**: Incorrect username or password, or the user lacks database access.

**Resolution**:
1. Verify credentials in your `.env` or configuration file
2. Reset the database user password if uncertain
3. Ensure the user has CONNECT privileges on the target database
4. For PostgreSQL, check `pg_hba.conf` for authentication method settings

### Error: "SSL Required" / "SSL Connection Error"
**Cause**: The database requires SSL connections but the client is not configured for SSL.

**Resolution**:
1. Set `sslmode=require` in your connection string
2. Download the CA certificate from your database provider
3. Configure the certificate path: `sslrootcert=/path/to/ca-cert.pem`
4. For self-signed certificates, set `sslmode=verify-ca`

---

## 3. Query Performance Issues

### Slow Queries
If queries are taking longer than expected:

1. **Enable Query Logging**: Add `log_min_duration_statement = 1000` to log queries taking more than 1 second
2. **Analyze Query Plans**: Run `EXPLAIN ANALYZE` before your query to see the execution plan
3. **Add Indexes**: Create indexes on frequently queried columns:
   ```sql
   CREATE INDEX idx_users_email ON users(email);
   ```
4. **Connection Pooling**: Use a connection pool to avoid creating new connections for each request:
   ```python
   from sqlalchemy import create_engine
   engine = create_engine('postgresql://...', pool_size=20, max_overflow=10)
   ```

### Connection Pool Exhaustion
**Symptoms**: "Too many connections" error, application hangs

**Resolution**:
1. Increase `max_connections` in your database configuration
2. Implement connection pooling with appropriate pool size
3. Ensure connections are properly closed after use (use context managers)
4. Monitor active connections: `SELECT count(*) FROM pg_stat_activity;`

---

## 4. Data Sync Issues

### Stale Data
If your application shows outdated data:
1. Check the sync interval in Settings → Integrations → Database
2. Manually trigger a sync by clicking "Sync Now"
3. Verify the last successful sync timestamp
4. Check for sync errors in the integration logs

### Duplicate Records
If duplicate records appear after sync:
1. Ensure your primary key column is correctly mapped
2. Check for case sensitivity issues in string-based keys
3. Enable deduplication in sync settings
4. Review the conflict resolution strategy (newest wins vs. manual review)

---

## 5. Internal Server Errors (HTTP 500)

When database operations cause internal errors:
1. Check application logs for the full error stack trace
2. Common causes:
   - Malformed SQL queries
   - Missing required columns in INSERT operations
   - Foreign key constraint violations
   - Disk space exhaustion on the database server
3. For our API, internal errors return an `error_id` — provide this to support for faster resolution
