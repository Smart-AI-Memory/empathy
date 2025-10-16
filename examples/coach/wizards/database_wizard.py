"""
Database Wizard

Schema design, migrations, query optimization, and database architecture.
Uses Empathy Framework Level 3 (Proactive) for query analysis and Level 4
(Anticipatory) for predicting data growth and scaling issues.

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

import re
from typing import List, Dict, Any

from .base_wizard import (
    BaseWizard,
    WizardTask,
    WizardOutput,
    WizardArtifact,
    WizardRisk,
    WizardHandoff,
    EmpathyChecks,
)


class DatabaseWizard(BaseWizard):
    """
    Wizard for database design, migrations, and optimization

    Uses:
    - Level 2: Guide user through schema design decisions
    - Level 3: Proactively detect query performance issues
    - Level 4: Anticipate data growth and scaling bottlenecks
    """

    def can_handle(self, task: WizardTask) -> float:
        """Determine if this is a database task"""
        # High-priority database phrases (worth 2 points each)
        database_phrases = [
            "database", "schema", "migration", "sql", "query", "index"
        ]

        # Secondary indicators (worth 1 point each)
        secondary_keywords = [
            "alembic", "postgres", "mysql", "mongodb", "table", "column",
            "constraint", "foreign key", "join", "transaction", "orm"
        ]

        task_lower = (task.task + " " + task.context).lower()

        # Count high-priority matches (2 points each)
        primary_matches = sum(2 for phrase in database_phrases if phrase in task_lower)

        # Count secondary matches (1 point each)
        secondary_matches = sum(1 for keyword in secondary_keywords if keyword in task_lower)

        total_score = primary_matches + secondary_matches

        return min(total_score / 6.0, 1.0)  # 6+ points = 100% confidence

    def execute(self, task: WizardTask) -> WizardOutput:
        """Execute database design workflow"""

        # Step 1: Assess emotional context
        emotional_state = self._assess_emotional_state(task)

        # Step 2: Extract constraints
        constraints = self._extract_constraints(task)

        # Step 3: Analyze database requirements
        diagnosis = self._analyze_database_requirements(task)

        # Step 4: Design schema (Level 3: Proactive)
        schema_design = self._design_schema(task)

        # Step 5: Analyze query patterns
        query_analysis = self._analyze_query_patterns(task)

        # Step 6: Create migration plan
        migration_plan = self._create_migration_plan(task, schema_design)

        # Step 7: Generate migration scripts
        migration_scripts = self._generate_migration_scripts(task, schema_design)

        # Step 8: Create index recommendations
        index_recommendations = self._recommend_indexes(task, query_analysis)

        # Step 9: Predict data growth issues (Level 4: Anticipatory)
        growth_forecast = self._predict_data_growth(task, schema_design)

        # Step 10: Identify risks
        risks = self._identify_risks(task, migration_plan)

        # Step 11: Create artifacts
        artifacts = [
            WizardArtifact(
                type="doc",
                title="Database Design Document",
                content=self._generate_design_document(diagnosis, schema_design)
            ),
            WizardArtifact(
                type="code",
                title="Migration Scripts",
                content=migration_scripts
            ),
            WizardArtifact(
                type="doc",
                title="Schema Diagram (Mermaid ERD)",
                content=self._generate_schema_diagram(schema_design)
            ),
            WizardArtifact(
                type="code",
                title="Index Recommendations",
                content=index_recommendations
            ),
            WizardArtifact(
                type="doc",
                title="Rollback Plan",
                content=self._create_rollback_plan(task, migration_plan)
            ),
            WizardArtifact(
                type="doc",
                title="Data Growth Forecast",
                content=growth_forecast
            )
        ]

        # Step 12: Generate next actions
        next_actions = migration_plan + self._generate_anticipatory_actions(task)

        # Step 13: Create empathy checks
        empathy_checks = EmpathyChecks(
            cognitive=f"Considered {task.role}'s constraints: data integrity, zero-downtime migrations, rollback safety",
            emotional=f"Acknowledged: Database changes are high-risk, {emotional_state['urgency']} urgency detected",
            anticipatory=growth_forecast[:200] + "..." if len(growth_forecast) > 200 else growth_forecast
        )

        return WizardOutput(
            wizard_name=self.name,
            diagnosis=diagnosis,
            plan=migration_plan,
            artifacts=artifacts,
            risks=risks,
            handoffs=self._create_handoffs(task),
            next_actions=next_actions,
            empathy_checks=empathy_checks,
            confidence=self.can_handle(task)
        )

    def _analyze_database_requirements(self, task: WizardTask) -> str:
        """Analyze database requirements from task description"""
        analysis = "# Database Requirements Analysis\n\n"
        analysis += f"**Objective**: {task.task}\n\n"

        # Categorize database task
        categories = []
        task_lower = (task.task + " " + task.context).lower()

        if any(kw in task_lower for kw in ["schema", "design", "table", "model"]):
            categories.append("Schema Design")
        if any(kw in task_lower for kw in ["migration", "alembic", "migrate", "alter"]):
            categories.append("Database Migration")
        if any(kw in task_lower for kw in ["slow", "query", "performance", "optimize"]):
            categories.append("Query Optimization")
        if any(kw in task_lower for kw in ["index", "indexing"]):
            categories.append("Index Strategy")
        if any(kw in task_lower for kw in ["backup", "restore", "recovery"]):
            categories.append("Data Recovery")

        if not categories:
            categories.append("General Database Task")

        analysis += f"**Category**: {', '.join(categories)}\n\n"
        analysis += f"**Context**: {task.context[:300]}...\n" if len(task.context) > 300 else f"**Context**: {task.context}\n"

        return analysis

    def _design_schema(self, task: WizardTask) -> Dict[str, Any]:
        """Design database schema"""
        task_lower = (task.task + " " + task.context).lower()

        # Example schema design based on common patterns
        schema = {
            "tables": [],
            "relationships": [],
            "constraints": []
        }

        # Infer table structure from context
        if "user" in task_lower:
            schema["tables"].append({
                "name": "users",
                "columns": [
                    {"name": "id", "type": "UUID", "constraints": ["PRIMARY KEY"]},
                    {"name": "email", "type": "VARCHAR(255)", "constraints": ["UNIQUE", "NOT NULL"]},
                    {"name": "name", "type": "VARCHAR(255)", "constraints": ["NOT NULL"]},
                    {"name": "created_at", "type": "TIMESTAMP", "constraints": ["DEFAULT NOW()"]},
                    {"name": "updated_at", "type": "TIMESTAMP", "constraints": ["DEFAULT NOW()"]}
                ],
                "indexes": [
                    {"name": "idx_users_email", "columns": ["email"], "type": "BTREE"}
                ]
            })

        if "order" in task_lower or "product" in task_lower:
            schema["tables"].append({
                "name": "orders",
                "columns": [
                    {"name": "id", "type": "UUID", "constraints": ["PRIMARY KEY"]},
                    {"name": "user_id", "type": "UUID", "constraints": ["NOT NULL"]},
                    {"name": "status", "type": "VARCHAR(50)", "constraints": ["NOT NULL"]},
                    {"name": "total", "type": "DECIMAL(10,2)", "constraints": ["NOT NULL"]},
                    {"name": "created_at", "type": "TIMESTAMP", "constraints": ["DEFAULT NOW()"]}
                ],
                "indexes": [
                    {"name": "idx_orders_user_id", "columns": ["user_id"], "type": "BTREE"},
                    {"name": "idx_orders_status", "columns": ["status"], "type": "BTREE"},
                    {"name": "idx_orders_created_at", "columns": ["created_at"], "type": "BTREE"}
                ]
            })

            schema["relationships"].append({
                "from_table": "orders",
                "to_table": "users",
                "type": "many-to-one",
                "foreign_key": "user_id"
            })

        # Default table if none detected
        if not schema["tables"]:
            schema["tables"].append({
                "name": "example_table",
                "columns": [
                    {"name": "id", "type": "SERIAL", "constraints": ["PRIMARY KEY"]},
                    {"name": "name", "type": "VARCHAR(255)", "constraints": ["NOT NULL"]},
                    {"name": "created_at", "type": "TIMESTAMP", "constraints": ["DEFAULT NOW()"]}
                ]
            })

        return schema

    def _analyze_query_patterns(self, task: WizardTask) -> List[Dict[str, Any]]:
        """Analyze common query patterns"""
        task_lower = (task.task + " " + task.context).lower()

        patterns = []

        # Detect query patterns
        if "search" in task_lower or "filter" in task_lower:
            patterns.append({
                "pattern": "Filtering/Search",
                "example": "SELECT * FROM users WHERE email LIKE '%@example.com'",
                "recommendation": "Add GIN index for text search or BTREE for exact matches"
            })

        if "join" in task_lower or "relationship" in task_lower:
            patterns.append({
                "pattern": "Join Queries",
                "example": "SELECT * FROM orders o JOIN users u ON o.user_id = u.id",
                "recommendation": "Ensure foreign key columns are indexed"
            })

        if "aggregate" in task_lower or "count" in task_lower or "sum" in task_lower:
            patterns.append({
                "pattern": "Aggregation",
                "example": "SELECT user_id, COUNT(*) FROM orders GROUP BY user_id",
                "recommendation": "Consider materialized views for frequently computed aggregates"
            })

        # Default pattern
        if not patterns:
            patterns.append({
                "pattern": "Standard CRUD",
                "example": "SELECT, INSERT, UPDATE, DELETE operations",
                "recommendation": "Ensure primary keys and commonly filtered columns are indexed"
            })

        return patterns

    def _create_migration_plan(self, task: WizardTask, schema: Dict) -> List[str]:
        """Create step-by-step migration plan"""
        plan = ["## Database Migration Plan\n"]

        plan.append("1. **Backup current database**")
        plan.append("   a. Create full database dump")
        plan.append("   b. Verify backup integrity")
        plan.append("   c. Store in secure location")

        plan.append("\n2. **Test migration in development**")
        plan.append("   a. Apply migration to dev database")
        plan.append("   b. Run application tests")
        plan.append("   c. Verify data integrity")

        plan.append("\n3. **Test migration in staging**")
        plan.append("   a. Apply migration to staging (copy of prod data)")
        plan.append("   b. Run smoke tests")
        plan.append("   c. Measure migration duration")

        plan.append("\n4. **Prepare production migration**")
        plan.append("   a. Schedule maintenance window (if needed)")
        plan.append("   b. Notify stakeholders")
        plan.append("   c. Prepare rollback plan")

        plan.append("\n5. **Execute production migration**")
        plan.append("   a. Enable maintenance mode (if downtime required)")
        plan.append("   b. Apply migration")
        plan.append("   c. Verify schema changes")
        plan.append("   d. Run post-migration tests")

        plan.append("\n6. **Post-migration validation**")
        plan.append("   a. Monitor error rates")
        plan.append("   b. Check query performance")
        plan.append("   c. Verify data integrity constraints")

        return plan

    def _generate_migration_scripts(self, task: WizardTask, schema: Dict) -> str:
        """Generate database migration scripts"""
        scripts = "# Database Migration Scripts\n\n"

        scripts += "## Alembic Migration (Python/SQLAlchemy)\n\n"
        scripts += "```python\n"
        scripts += '"""Add users and orders tables\n\n'
        scripts += 'Revision ID: 001\n'
        scripts += 'Revises: \n'
        scripts += 'Create Date: 2025-01-15 10:00:00\n'
        scripts += '"""\n\n'
        scripts += "from alembic import op\n"
        scripts += "import sqlalchemy as sa\n"
        scripts += "from sqlalchemy.dialects import postgresql\n\n"
        scripts += "revision = '001'\n"
        scripts += "down_revision = None\n\n"
        scripts += "def upgrade():\n"

        for table in schema.get("tables", []):
            scripts += f"    # Create {table['name']} table\n"
            scripts += f"    op.create_table(\n"
            scripts += f"        '{table['name']}',\n"
            for col in table.get("columns", []):
                col_type = col["type"]
                constraints = " ".join(col.get("constraints", []))
                scripts += f"        sa.Column('{col['name']}', sa.{col_type}(), {constraints}),\n"
            scripts += "    )\n\n"

            # Add indexes
            for idx in table.get("indexes", []):
                scripts += f"    # Create index on {table['name']}\n"
                columns = ", ".join([f"'{c}'" for c in idx["columns"]])
                scripts += f"    op.create_index('{idx['name']}', '{table['name']}', [{columns}])\n\n"

        scripts += "\ndef downgrade():\n"
        for table in reversed(schema.get("tables", [])):
            scripts += f"    op.drop_table('{table['name']}')\n"

        scripts += "```\n\n"

        scripts += "## Raw SQL Migration\n\n"
        scripts += "```sql\n"
        scripts += "-- Migration: Up\n"
        scripts += "BEGIN;\n\n"

        for table in schema.get("tables", []):
            scripts += f"-- Create {table['name']} table\n"
            scripts += f"CREATE TABLE {table['name']} (\n"
            col_defs = []
            for col in table.get("columns", []):
                col_def = f"    {col['name']} {col['type']}"
                if col.get("constraints"):
                    col_def += " " + " ".join(col["constraints"])
                col_defs.append(col_def)
            scripts += ",\n".join(col_defs)
            scripts += "\n);\n\n"

            # Add indexes
            for idx in table.get("indexes", []):
                columns = ", ".join(idx["columns"])
                scripts += f"CREATE INDEX {idx['name']} ON {table['name']} ({columns});\n"

            scripts += "\n"

        scripts += "COMMIT;\n\n"

        scripts += "-- Migration: Down (Rollback)\n"
        scripts += "BEGIN;\n\n"
        for table in reversed(schema.get("tables", [])):
            scripts += f"DROP TABLE IF EXISTS {table['name']} CASCADE;\n"
        scripts += "\nCOMMIT;\n"
        scripts += "```\n"

        return scripts

    def _recommend_indexes(self, task: WizardTask, query_patterns: List[Dict]) -> str:
        """Recommend database indexes"""
        recommendations = "# Index Recommendations\n\n"

        recommendations += "## General Indexing Strategy\n\n"
        recommendations += "### Primary Indexes (High Priority)\n"
        recommendations += "- **Primary Keys**: Automatically indexed\n"
        recommendations += "- **Foreign Keys**: MUST be indexed for join performance\n"
        recommendations += "- **Frequently Filtered Columns**: WHERE clause columns\n"
        recommendations += "- **Sort Columns**: ORDER BY columns\n\n"

        recommendations += "### Composite Indexes\n"
        recommendations += "- **Order matters**: Most selective column first\n"
        recommendations += "- **Covers multiple queries**: INDEX(user_id, created_at)\n"
        recommendations += "- **Leftmost prefix rule**: Can use INDEX(a,b) for queries on 'a' alone\n\n"

        recommendations += "## Query-Specific Recommendations\n\n"

        for i, pattern in enumerate(query_patterns, 1):
            recommendations += f"### {i}. {pattern['pattern']}\n"
            recommendations += f"**Example Query**:\n```sql\n{pattern['example']}\n```\n\n"
            recommendations += f"**Recommendation**: {pattern['recommendation']}\n\n"

        recommendations += "## Index Creation Scripts\n\n"
        recommendations += "```sql\n"
        recommendations += "-- Create indexes concurrently (PostgreSQL - no table lock)\n"
        recommendations += "CREATE INDEX CONCURRENTLY idx_users_email ON users(email);\n"
        recommendations += "CREATE INDEX CONCURRENTLY idx_orders_user_id ON orders(user_id);\n"
        recommendations += "CREATE INDEX CONCURRENTLY idx_orders_created_at ON orders(created_at);\n\n"
        recommendations += "-- Composite index for common query pattern\n"
        recommendations += "CREATE INDEX CONCURRENTLY idx_orders_user_created ON orders(user_id, created_at DESC);\n\n"
        recommendations += "-- Partial index for frequently filtered subset\n"
        recommendations += "CREATE INDEX CONCURRENTLY idx_orders_active ON orders(user_id) WHERE status = 'active';\n"
        recommendations += "```\n\n"

        recommendations += "## Index Monitoring\n\n"
        recommendations += "```sql\n"
        recommendations += "-- Check index usage (PostgreSQL)\n"
        recommendations += "SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch\n"
        recommendations += "FROM pg_stat_user_indexes\n"
        recommendations += "ORDER BY idx_scan ASC;\n\n"
        recommendations += "-- Find unused indexes (idx_scan = 0)\n"
        recommendations += "-- Consider dropping if consistently unused\n"
        recommendations += "```\n\n"

        recommendations += "## Expected Impact\n"
        recommendations += "- **Query Performance**: 10-100x faster for indexed columns\n"
        recommendations += "- **Write Performance**: 5-10% slower (index maintenance overhead)\n"
        recommendations += "- **Storage**: +10-20% disk space for indexes\n"

        return recommendations

    def _predict_data_growth(self, task: WizardTask, schema: Dict) -> str:
        """Level 4: Predict data growth and scaling issues"""
        forecast = "# Data Growth Forecast (Level 4: Anticipatory)\n\n"

        forecast += "## Current State\n"
        forecast += "- Tables: " + str(len(schema.get("tables", []))) + "\n"
        forecast += "- Estimated rows: ~100K (baseline)\n"
        forecast += "- Growth rate: ~10K rows/month (assumed)\n\n"

        forecast += "## Projected Issues (Next 30-90 Days)\n\n"

        forecast += "### ⚠️ Query Performance Degradation (60 days)\n"
        forecast += "**Prediction**: At 10K rows/month, tables will exceed 1M rows in ~90 days\n"
        forecast += "**Impact**: Full table scans become prohibitively slow (5+ seconds)\n"
        forecast += "**Preventive Action**:\n"
        forecast += "- Add indexes NOW on commonly filtered columns\n"
        forecast += "- Implement query pagination (LIMIT/OFFSET or cursor-based)\n"
        forecast += "- Monitor slow query log (queries > 1s)\n\n"

        forecast += "### ⚠️ Storage Capacity (90 days)\n"
        forecast += "**Prediction**: At current growth, database will reach 80% storage capacity\n"
        forecast += "**Impact**: Database may halt writes when full (critical outage)\n"
        forecast += "**Preventive Action**:\n"
        forecast += "- Set up storage monitoring alerts (warn at 70%, critical at 85%)\n"
        forecast += "- Plan storage expansion (vertical scaling or sharding)\n"
        forecast += "- Implement data archival strategy for old records\n\n"

        forecast += "### ⚠️ Backup Duration (45 days)\n"
        forecast += "**Prediction**: Database backups will exceed maintenance window\n"
        forecast += "**Impact**: Cannot complete backups during allowed downtime\n"
        forecast += "**Preventive Action**:\n"
        forecast += "- Switch to incremental/continuous backups (WAL archiving)\n"
        forecast += "- Consider hot standby replica for zero-downtime backups\n"
        forecast += "- Test restore procedures (backups are useless if you can't restore)\n\n"

        forecast += "### ⚠️ Index Bloat (60 days)\n"
        forecast += "**Prediction**: Frequent updates will cause index fragmentation\n"
        forecast += "**Impact**: Indexes become less effective, query performance degrades\n"
        forecast += "**Preventive Action**:\n"
        forecast += "- Schedule weekly VACUUM ANALYZE (PostgreSQL)\n"
        forecast += "- Monitor index bloat ratio (pg_stat_user_indexes)\n"
        forecast += "- Plan periodic REINDEX for heavily updated tables\n\n"

        forecast += "## Recommended Timeline\n"
        forecast += "- **Now (Week 1)**: Create indexes, set up monitoring\n"
        forecast += "- **Week 4**: Implement pagination for large result sets\n"
        forecast += "- **Week 8**: Set up automated backups with verification\n"
        forecast += "- **Week 10**: Plan sharding/partitioning strategy (before 10M+ rows)\n"

        return forecast

    def _generate_design_document(self, diagnosis: str, schema: Dict) -> str:
        """Generate comprehensive database design document"""
        doc = f"{diagnosis}\n\n"

        doc += "## Schema Design\n\n"

        for table in schema.get("tables", []):
            doc += f"### Table: {table['name']}\n\n"
            doc += "| Column | Type | Constraints |\n"
            doc += "|--------|------|-------------|\n"
            for col in table.get("columns", []):
                constraints = " ".join(col.get("constraints", []))
                doc += f"| {col['name']} | {col['type']} | {constraints} |\n"
            doc += "\n"

            if table.get("indexes"):
                doc += "**Indexes:**\n"
                for idx in table["indexes"]:
                    columns = ", ".join(idx["columns"])
                    doc += f"- `{idx['name']}`: {idx['type']} on ({columns})\n"
                doc += "\n"

        if schema.get("relationships"):
            doc += "## Relationships\n\n"
            for rel in schema["relationships"]:
                doc += f"- `{rel['from_table']}` → `{rel['to_table']}` ({rel['type']})\n"
                doc += f"  - Foreign Key: `{rel['foreign_key']}`\n"

        return doc

    def _generate_schema_diagram(self, schema: Dict) -> str:
        """Generate Mermaid ERD diagram"""
        diagram = "# Entity Relationship Diagram\n\n"
        diagram += "```mermaid\n"
        diagram += "erDiagram\n"

        # Define entities
        for table in schema.get("tables", []):
            table_name = table['name'].upper()
            diagram += f"    {table_name} {{\n"
            for col in table.get("columns", []):
                col_type = col['type'].split('(')[0]  # Remove size
                diagram += f"        {col_type} {col['name']}\n"
            diagram += "    }\n"

        # Define relationships
        for rel in schema.get("relationships", []):
            from_table = rel['from_table'].upper()
            to_table = rel['to_table'].upper()
            if rel['type'] == 'many-to-one':
                diagram += f"    {from_table} }}o--|| {to_table} : \"{rel['foreign_key']}\"\n"
            elif rel['type'] == 'one-to-many':
                diagram += f"    {from_table} ||--o{{ {to_table} : \"has\"\n"
            elif rel['type'] == 'many-to-many':
                diagram += f"    {from_table} }}o--o{{ {to_table} : \"relates\"\n"

        diagram += "```\n\n"
        diagram += "**Note**: View this diagram in a Mermaid-compatible viewer (GitHub, VSCode, etc.)\n"

        return diagram

    def _create_rollback_plan(self, task: WizardTask, migration_plan: List[str]) -> str:
        """Create rollback plan for migrations"""
        rollback = "# Database Rollback Plan\n\n"

        rollback += "## When to Rollback\n"
        rollback += "- Migration fails validation tests\n"
        rollback += "- Application errors spike after deployment\n"
        rollback += "- Data integrity issues detected\n"
        rollback += "- Performance degradation beyond acceptable threshold\n\n"

        rollback += "## Rollback Procedure\n\n"
        rollback += "### Option 1: Automatic Rollback (Preferred)\n"
        rollback += "```bash\n"
        rollback += "# Alembic downgrade\n"
        rollback += "alembic downgrade -1  # Rollback one migration\n"
        rollback += "alembic downgrade base  # Rollback all migrations\n"
        rollback += "```\n\n"

        rollback += "### Option 2: Manual Rollback\n"
        rollback += "```sql\n"
        rollback += "-- Run the 'down' migration SQL\n"
        rollback += "BEGIN;\n"
        rollback += "-- Execute rollback statements from migration script\n"
        rollback += "-- Verify data integrity\n"
        rollback += "COMMIT;  -- or ROLLBACK if issues detected\n"
        rollback += "```\n\n"

        rollback += "### Option 3: Restore from Backup (Last Resort)\n"
        rollback += "```bash\n"
        rollback += "# Stop application\n"
        rollback += "systemctl stop app-server\n\n"
        rollback += "# Restore database from backup\n"
        rollback += "pg_restore -d database_name backup_file.dump\n\n"
        rollback += "# Verify restore\n"
        rollback += "psql -d database_name -c 'SELECT COUNT(*) FROM users;'\n\n"
        rollback += "# Restart application\n"
        rollback += "systemctl start app-server\n"
        rollback += "```\n\n"

        rollback += "## Post-Rollback Actions\n"
        rollback += "1. **Verify Data Integrity**: Run data validation queries\n"
        rollback += "2. **Check Application Health**: Monitor error rates for 30 minutes\n"
        rollback += "3. **Root Cause Analysis**: Investigate what went wrong\n"
        rollback += "4. **Fix & Retry**: Update migration, test thoroughly, retry\n\n"

        rollback += "## Rollback Testing\n"
        rollback += "- Test rollback procedure in staging BEFORE production migration\n"
        rollback += "- Measure rollback duration (must fit in maintenance window)\n"
        rollback += "- Verify application works after rollback\n"

        return rollback

    def _identify_risks(self, task: WizardTask, migration_plan: List[str]) -> List[WizardRisk]:
        """Identify database migration risks"""
        risks = []

        # Data loss risk
        risks.append(WizardRisk(
            risk="Migration may cause data loss or corruption",
            mitigation="Create full database backup before migration. Test migration on copy of production data in staging.",
            severity="high"
        ))

        # Downtime risk
        risks.append(WizardRisk(
            risk="Migration may require downtime (table locks during ALTER)",
            mitigation="Use online DDL operations: CREATE INDEX CONCURRENTLY (PostgreSQL) or pt-online-schema-change (MySQL)",
            severity="medium"
        ))

        # Performance impact
        risks.append(WizardRisk(
            risk="New indexes may slow down write operations",
            mitigation="Monitor write throughput after migration. Consider adding indexes during low-traffic periods.",
            severity="low"
        ))

        # Rollback complexity
        risks.append(WizardRisk(
            risk="Some migrations are difficult or impossible to rollback (data type changes)",
            mitigation="Test rollback procedure in staging. Keep detailed rollback plan ready.",
            severity="high"
        ))

        return risks

    def _create_handoffs(self, task: WizardTask) -> List[WizardHandoff]:
        """Create handoffs for database work"""
        handoffs = []

        if task.role == "developer":
            handoffs.append(WizardHandoff(
                owner="DBA / Database Administrator",
                what="Review migration scripts, approve index strategy, verify backup procedures",
                when="Before production migration"
            ))
            handoffs.append(WizardHandoff(
                owner="DevOps / SRE",
                what="Set up database monitoring, configure backup automation, prepare rollback plan",
                when="Before production deployment"
            ))

        return handoffs
