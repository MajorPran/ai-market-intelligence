        """
        Database configuration and models for AI Market Intelligence Tool
        Uses SQLAlchemy ORM with SQLite for simplicity (easily upgradeable to PostgreSQL)
        """

        import sqlite3
        from datetime import datetime, timezone
        from pathlib import Path
        from typing import Optional, List, Dict, Any
        from dataclasses import dataclass
        from enum import Enum
        import json
        import logging

        from config.settings import settings

        logger = logging.getLogger('intelligence.database')

        class ContentStatus(Enum):
            """Status of scraped content"""
            PENDING = "pending"
            PROCESSED = "processed" 
            ANALYZED = "analyzed"
            ARCHIVED = "archived"
            ERROR = "error"

        class AlertSeverity(Enum):
            """Alert severity levels"""
            LOW = "low"
            MEDIUM = "medium"
            HIGH = "high"
            CRITICAL = "critical"

        @dataclass
        class ScrapedContent:
            """Data model for scraped content"""
            id: Optional[int] = None
            url: str = ""
            title: str = ""
            content: str = ""
            summary: str = ""
            author: str = ""
            published_date: Optional[datetime] = None
            scraped_date: datetime = None
            source_domain: str = ""
            content_type: str = "article"
            word_count: int = 0
            status: ContentStatus = ContentStatus.PENDING
            metadata: Dict[str, Any] = None

            def __post_init__(self):
                if self.scraped_date is None:
                    self.scraped_date = datetime.now(timezone.utc)
                if self.metadata is None:
                    self.metadata = {}

        @dataclass 
        class ContentAnalysis:
            """Data model for LLM analysis results"""
            id: Optional[int] = None
            content_id: int = 0
            sentiment_score: float = 0.0
            sentiment_label: str = "neutral"
            key_topics: List[str] = None
            entities: List[str] = None
            trends: List[str] = None
            competitive_mentions: List[str] = None
            innovation_score: float = 0.0
            market_impact_score: float = 0.0
            analysis_date: datetime = None
            llm_model: str = ""
            confidence_score: float = 0.0

            def __post_init__(self):
                if self.analysis_date is None:
                    self.analysis_date = datetime.now(timezone.utc)
                if self.key_topics is None:
                    self.key_topics = []
                if self.entities is None:
                    self.entities = []
                if self.trends is None:
                    self.trends = []
                if self.competitive_mentions is None:
                    self.competitive_mentions = []

        @dataclass
        class TrendData:
            """Data model for identified trends"""
            id: Optional[int] = None
            trend_name: str = ""
            description: str = ""
            category: str = ""
            confidence_score: float = 0.0
            first_detected: datetime = None
            last_updated: datetime = None
            mention_count: int = 0
            growth_rate: float = 0.0
            related_keywords: List[str] = None

            def __post_init__(self):
                if self.first_detected is None:
                    self.first_detected = datetime.now(timezone.utc)
                if self.last_updated is None:
                    self.last_updated = datetime.now(timezone.utc)
                if self.related_keywords is None:
                    self.related_keywords = []

        @dataclass
        class Alert:
            """Data model for alerts"""
            id: Optional[int] = None
            title: str = ""
            message: str = ""
            severity: AlertSeverity = AlertSeverity.LOW
            category: str = ""
            triggered_date: datetime = None
            resolved_date: Optional[datetime] = None
            is_resolved: bool = False
            source_content_id: Optional[int] = None
            metadata: Dict[str, Any] = None

            def __post_init__(self):
                if self.triggered_date is None:
                    self.triggered_date = datetime.now(timezone.utc)
                if self.metadata is None:
                    self.metadata = {}

        class DatabaseManager:
            """Manages database operations with SQLite"""

            def __init__(self, db_path: Optional[Path] = None):
                self.db_path = db_path or settings.DATA_DIR / "intelligence.db"
                self.init_database()

            def init_database(self):
                """Initialize database with required tables"""
                try:
                    with sqlite3.connect(self.db_path) as conn:
                        conn.execute("PRAGMA foreign_keys = ON")

                        # Create tables
                        self._create_content_table(conn)
                        self._create_analysis_table(conn)
                        self._create_trends_table(conn)
                        self._create_alerts_table(conn)
                        self._create_embeddings_table(conn)
                        self._create_reports_table(conn)

                        conn.commit()
                        logger.info(f"✅ Database initialized at {self.db_path}")

                except Exception as e:
                    logger.error(f"Failed to initialize database: {e}")
                    raise

            def _create_content_table(self, conn):
                """Create scraped_content table"""
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS scraped_content (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        url TEXT UNIQUE NOT NULL,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        summary TEXT,
                        author TEXT,
                        published_date TIMESTAMP,
                        scraped_date TIMESTAMP NOT NULL,
                        source_domain TEXT NOT NULL,
                        content_type TEXT DEFAULT 'article',
                        word_count INTEGER DEFAULT 0,
                        status TEXT DEFAULT 'pending',
                        metadata TEXT DEFAULT '{}',
                        UNIQUE(url)
                    )
                """)

            def _create_analysis_table(self, conn):
                """Create content_analysis table"""
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS content_analysis (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        content_id INTEGER NOT NULL,
                        sentiment_score REAL DEFAULT 0.0,
                        sentiment_label TEXT DEFAULT 'neutral',
                        key_topics TEXT DEFAULT '[]',
                        entities TEXT DEFAULT '[]',
                        trends TEXT DEFAULT '[]',
                        competitive_mentions TEXT DEFAULT '[]',
                        innovation_score REAL DEFAULT 0.0,
                        market_impact_score REAL DEFAULT 0.0,
                        analysis_date TIMESTAMP NOT NULL,
                        llm_model TEXT NOT NULL,
                        confidence_score REAL DEFAULT 0.0,
                        FOREIGN KEY (content_id) REFERENCES scraped_content (id)
                    )
                """)

            def _create_trends_table(self, conn):
                """Create trends table"""
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS trends (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        trend_name TEXT UNIQUE NOT NULL,
                        description TEXT,
                        category TEXT,
                        confidence_score REAL DEFAULT 0.0,
                        first_detected TIMESTAMP NOT NULL,
                        last_updated TIMESTAMP NOT NULL,
                        mention_count INTEGER DEFAULT 0,
                        growth_rate REAL DEFAULT 0.0,
                        related_keywords TEXT DEFAULT '[]'
                    )
                """)

            def _create_alerts_table(self, conn):
                """Create alerts table"""
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS alerts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        message TEXT NOT NULL,
                        severity TEXT NOT NULL,
                        category TEXT,
                        triggered_date TIMESTAMP NOT NULL,
                        resolved_date TIMESTAMP,
                        is_resolved BOOLEAN DEFAULT FALSE,
                        source_content_id INTEGER,
                        metadata TEXT DEFAULT '{}',
                        FOREIGN KEY (source_content_id) REFERENCES scraped_content (id)
                    )
                """)

            def _create_embeddings_table(self, conn):
                """Create vector embeddings table"""
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS content_embeddings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        content_id INTEGER NOT NULL,
                        embedding_model TEXT NOT NULL,
                        embedding_vector BLOB NOT NULL,
                        created_date TIMESTAMP NOT NULL,
                        FOREIGN KEY (content_id) REFERENCES scraped_content (id),
                        UNIQUE(content_id, embedding_model)
                    )
                """)

            def _create_reports_table(self, conn):
                """Create reports table"""
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS reports (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        report_type TEXT NOT NULL,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        format TEXT NOT NULL,
                        generated_date TIMESTAMP NOT NULL,
                        date_range_start TIMESTAMP,
                        date_range_end TIMESTAMP,
                        metadata TEXT DEFAULT '{}'
                    )
                """)

            def save_content(self, content: ScrapedContent) -> int:
                """Save scraped content to database"""
                try:
                    with sqlite3.connect(self.db_path) as conn:
                        cursor = conn.execute("""
                            INSERT OR REPLACE INTO scraped_content 
                            (url, title, content, summary, author, published_date, 
                             scraped_date, source_domain, content_type, word_count, 
                             status, metadata)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            content.url, content.title, content.content, content.summary,
                            content.author, content.published_date, content.scraped_date,
                            content.source_domain, content.content_type, content.word_count,
                            content.status.value, json.dumps(content.metadata)
                        ))

                        content_id = cursor.lastrowid
                        logger.debug(f"Saved content: {content.title[:50]}...")
                        return content_id

                except Exception as e:
                    logger.error(f"Failed to save content: {e}")
                    raise

            def save_analysis(self, analysis: ContentAnalysis) -> int:
                """Save content analysis to database"""
                try:
                    with sqlite3.connect(self.db_path) as conn:
                        cursor = conn.execute("""
                            INSERT INTO content_analysis 
                            (content_id, sentiment_score, sentiment_label, key_topics,
                             entities, trends, competitive_mentions, innovation_score,
                             market_impact_score, analysis_date, llm_model, confidence_score)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            analysis.content_id, analysis.sentiment_score, analysis.sentiment_label,
                            json.dumps(analysis.key_topics), json.dumps(analysis.entities),
                            json.dumps(analysis.trends), json.dumps(analysis.competitive_mentions),
                            analysis.innovation_score, analysis.market_impact_score,
                            analysis.analysis_date, analysis.llm_model, analysis.confidence_score
                        ))

                        analysis_id = cursor.lastrowid
                        logger.debug(f"Saved analysis for content_id: {analysis.content_id}")
                        return analysis_id

                except Exception as e:
                    logger.error(f"Failed to save analysis: {e}")
                    raise

            def save_trend(self, trend: TrendData) -> int:
                """Save or update trend data"""
                try:
                    with sqlite3.connect(self.db_path) as conn:
                        # Try to update existing trend
                        cursor = conn.execute("""
                            UPDATE trends SET
                                description = ?, category = ?, confidence_score = ?,
                                last_updated = ?, mention_count = ?, growth_rate = ?,
                                related_keywords = ?
                            WHERE trend_name = ?
                        """, (
                            trend.description, trend.category, trend.confidence_score,
                            trend.last_updated, trend.mention_count, trend.growth_rate,
                            json.dumps(trend.related_keywords), trend.trend_name
                        ))

                        if cursor.rowcount == 0:
                            # Insert new trend
                            cursor = conn.execute("""
                                INSERT INTO trends 
                                (trend_name, description, category, confidence_score,
                                 first_detected, last_updated, mention_count, growth_rate,
                                 related_keywords)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                trend.trend_name, trend.description, trend.category,
                                trend.confidence_score, trend.first_detected, trend.last_updated,
                                trend.mention_count, trend.growth_rate,
                                json.dumps(trend.related_keywords)
                            ))

                        trend_id = cursor.lastrowid
                        logger.debug(f"Saved trend: {trend.trend_name}")
                        return trend_id

                except Exception as e:
                    logger.error(f"Failed to save trend: {e}")
                    raise

            def save_alert(self, alert: Alert) -> int:
                """Save alert to database"""
                try:
                    with sqlite3.connect(self.db_path) as conn:
                        cursor = conn.execute("""
                            INSERT INTO alerts 
                            (title, message, severity, category, triggered_date,
                             resolved_date, is_resolved, source_content_id, metadata)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            alert.title, alert.message, alert.severity.value, alert.category,
                            alert.triggered_date, alert.resolved_date, alert.is_resolved,
                            alert.source_content_id, json.dumps(alert.metadata)
                        ))

                        alert_id = cursor.lastrowid
                        logger.info(f"Created {alert.severity.value} alert: {alert.title}")
                        return alert_id

                except Exception as e:
                    logger.error(f"Failed to save alert: {e}")
                    raise

            def get_unprocessed_content(self, limit: int = 100) -> List[ScrapedContent]:
                """Get content that needs processing"""
                try:
                    with sqlite3.connect(self.db_path) as conn:
                        conn.row_factory = sqlite3.Row
                        cursor = conn.execute("""
                            SELECT * FROM scraped_content 
                            WHERE status = 'pending'
                            ORDER BY scraped_date ASC
                            LIMIT ?
                        """, (limit,))

                        content_list = []
                        for row in cursor.fetchall():
                            content = ScrapedContent(
                                id=row['id'],
                                url=row['url'],
                                title=row['title'],
                                content=row['content'],
                                summary=row['summary'],
                                author=row['author'],
                                published_date=row['published_date'],
                                scraped_date=row['scraped_date'],
                                source_domain=row['source_domain'],
                                content_type=row['content_type'],
                                word_count=row['word_count'],
                                status=ContentStatus(row['status']),
                                metadata=json.loads(row['metadata'] or '{}')
                            )
                            content_list.append(content)

                        return content_list

                except Exception as e:
                    logger.error(f"Failed to get unprocessed content: {e}")
                    return []

            def get_recent_trends(self, days: int = 7, limit: int = 20) -> List[TrendData]:
                """Get recent trending topics"""
                try:
                    with sqlite3.connect(self.db_path) as conn:
                        conn.row_factory = sqlite3.Row
                        cursor = conn.execute("""
                            SELECT * FROM trends 
                            WHERE last_updated >= datetime('now', '-{} days')
                            ORDER BY confidence_score DESC, mention_count DESC
                            LIMIT ?
                        """.format(days), (limit,))

                        trends_list = []
                        for row in cursor.fetchall():
                            trend = TrendData(
                                id=row['id'],
                                trend_name=row['trend_name'],
                                description=row['description'],
                                category=row['category'],
                                confidence_score=row['confidence_score'],
                                first_detected=row['first_detected'],
                                last_updated=row['last_updated'],
                                mention_count=row['mention_count'],
                                growth_rate=row['growth_rate'],
                                related_keywords=json.loads(row['related_keywords'] or '[]')
                            )
                            trends_list.append(trend)

                        return trends_list

                except Exception as e:
                    logger.error(f"Failed to get recent trends: {e}")
                    return []

            def get_active_alerts(self) -> List[Alert]:
                """Get unresolved alerts"""
                try:
                    with sqlite3.connect(self.db_path) as conn:
                        conn.row_factory = sqlite3.Row
                        cursor = conn.execute("""
                            SELECT * FROM alerts 
                            WHERE is_resolved = FALSE
                            ORDER BY triggered_date DESC
                        """)

                        alerts_list = []
                        for row in cursor.fetchall():
                            alert = Alert(
                                id=row['id'],
                                title=row['title'],
                                message=row['message'],
                                severity=AlertSeverity(row['severity']),
                                category=row['category'],
                                triggered_date=row['triggered_date'],
                                resolved_date=row['resolved_date'],
                                is_resolved=bool(row['is_resolved']),
                                source_content_id=row['source_content_id'],
                                metadata=json.loads(row['metadata'] or '{}')
                            )
                            alerts_list.append(alert)

                        return alerts_list

                except Exception as e:
                    logger.error(f"Failed to get active alerts: {e}")
                    return []

            def update_content_status(self, content_id: int, status: ContentStatus):
                """Update content processing status"""
                try:
                    with sqlite3.connect(self.db_path) as conn:
                        conn.execute("""
                            UPDATE scraped_content 
                            SET status = ? 
                            WHERE id = ?
                        """, (status.value, content_id))

                        logger.debug(f"Updated content {content_id} status to {status.value}")

                except Exception as e:
                    logger.error(f"Failed to update content status: {e}")

            def get_database_stats(self) -> Dict[str, int]:
                """Get database statistics"""
                try:
                    with sqlite3.connect(self.db_path) as conn:
                        stats = {}

                        # Count records in each table
                        tables = ['scraped_content', 'content_analysis', 'trends', 'alerts']
                        for table in tables:
                            cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                            stats[table] = cursor.fetchone()[0]

                        # Additional stats
                        cursor = conn.execute("""
                            SELECT COUNT(*) FROM scraped_content 
                            WHERE scraped_date >= datetime('now', '-24 hours')
                        """)
                        stats['content_last_24h'] = cursor.fetchone()[0]

                        cursor = conn.execute("""
                            SELECT COUNT(*) FROM alerts 
                            WHERE is_resolved = FALSE
                        """)
                        stats['active_alerts'] = cursor.fetchone()[0]

                        return stats

                except Exception as e:
                    logger.error(f"Failed to get database stats: {e}")
                    return {}

        # Global database instance
        db = DatabaseManager()