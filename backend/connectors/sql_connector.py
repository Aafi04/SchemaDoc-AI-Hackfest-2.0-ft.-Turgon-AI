"""
SQL Connector — dialect-agnostic schema extraction + statistical profiling.
Ported from src/backend/connectors/sql_connector.py with updated imports.
"""
from typing import Dict, Any, List, Optional
import datetime
import logging
from sqlalchemy import create_engine, inspect, MetaData, Table, select, func, text, Column
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from backend.core.state import TableSchema, ColumnMetadata, ColumnStats

logger = logging.getLogger(__name__)


class SQLConnector:
    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string)
        self.inspector = inspect(self.engine)
        self.metadata = MetaData()

    def get_live_schema(self) -> Dict[str, TableSchema]:
        """
        Orchestrates the full extraction: Structure + Statistics.
        Returns the 'schema_raw' state object.
        """
        schema_out: Dict[str, TableSchema] = {}
        table_names = self.inspector.get_table_names()

        logger.info(f"Connected to DB. Found tables: {table_names}")

        for t_name in table_names:
            try:
                table_obj = Table(t_name, self.metadata, autoload_with=self.engine)
                columns_meta, fk_list = self._extract_structure(t_name, table_obj)
                row_count, health_score, col_stats = self._profile_data(table_obj, columns_meta)

                for col_name, stats in col_stats.items():
                    if col_name in columns_meta:
                        columns_meta[col_name]["stats"] = stats

                schema_out[t_name] = {
                    "table_name": t_name,
                    "row_count": row_count,
                    "columns": columns_meta,
                    "health_score": health_score,
                    "description": None,
                    "foreign_keys": fk_list,
                }

            except Exception as e:
                logger.error(f"Error processing table '{t_name}': {e}")
                continue

        return schema_out

    def _extract_structure(
        self, table_name: str, table_obj: Table
    ) -> tuple[Dict[str, ColumnMetadata], List[dict]]:
        """Extracts names, types, constraints, and Foreign Keys."""
        cols_out = {}

        columns = self.inspector.get_columns(table_name)
        pk_constraint = self.inspector.get_pk_constraint(table_name)
        pk_cols = pk_constraint.get("constrained_columns", [])
        fks = self.inspector.get_foreign_keys(table_name)

        fk_list = []
        fk_map = {}

        for fk in fks:
            if fk["constrained_columns"]:
                local_col = fk["constrained_columns"][0]
                ref_table = fk["referred_table"]
                ref_col = fk["referred_columns"][0]
                fk_map[local_col] = ref_table
                fk_list.append(
                    {
                        "column": local_col,
                        "referred_table": ref_table,
                        "referred_column": ref_col,
                    }
                )

        for col in columns:
            name = col["name"]
            tags = []
            if name in pk_cols:
                tags.append("PK")
            if name in fk_map:
                tags.append("FK")

            cols_out[name] = {
                "name": name,
                "original_type": str(col["type"]),
                "nullable": col["nullable"],
                "description": col.get("comment", None),
                "business_logic": None,
                "potential_pii": False,
                "tags": tags,
                "stats": None,
            }

        return cols_out, fk_list

    def _profile_data(self, table_obj: Table, cols_meta: Dict[str, ColumnMetadata]):
        stats_out: Dict[str, ColumnStats] = {}
        row_count = 0
        health_score = 100.0

        try:
            with self.engine.connect() as conn:
                count_query = select(func.count()).select_from(table_obj)
                row_count = conn.execute(count_query).scalar() or 0

                if row_count == 0:
                    return 0, 100.0, {}

                for col_name, meta in cols_meta.items():
                    col_obj = table_obj.c[col_name]

                    null_query = select(func.count()).where(col_obj == None)
                    null_count = conn.execute(null_query).scalar() or 0
                    null_percentage = round((null_count / row_count) * 100, 2)

                    unique_query = select(func.count(func.distinct(col_obj)))
                    unique_count = conn.execute(unique_query).scalar() or 0
                    unique_percentage = (
                        round((unique_count / row_count) * 100, 2) if row_count > 0 else 0.0
                    )

                    sample_query = select(col_obj).where(col_obj != None).limit(3)
                    samples = [str(r[0]) for r in conn.execute(sample_query).fetchall()]

                    col_stat: ColumnStats = {
                        "null_count": null_count,
                        "null_percentage": null_percentage,
                        "unique_count": unique_count,
                        "unique_percentage": unique_percentage,
                        "sample_values": samples,
                        "min_value": None,
                        "max_value": None,
                        "mean_value": None,
                    }

                    type_str = meta["original_type"].upper()
                    if any(
                        t in type_str
                        for t in ["INT", "FLOAT", "DECIMAL", "NUMERIC", "REAL"]
                    ):
                        try:
                            stats_q = select(
                                func.min(col_obj), func.max(col_obj), func.avg(col_obj)
                            )
                            min_v, max_v, avg_v = conn.execute(stats_q).fetchone()
                            col_stat["min_value"] = (
                                float(min_v) if min_v is not None else None
                            )
                            col_stat["max_value"] = (
                                float(max_v) if max_v is not None else None
                            )
                            col_stat["mean_value"] = (
                                round(float(avg_v), 4) if avg_v is not None else None
                            )
                            if (
                                min_v is not None
                                and min_v < 0
                                and "ID" in col_name.upper()
                            ):
                                health_score -= 5
                        except Exception:
                            pass

                    stats_out[col_name] = col_stat

                    if null_percentage > 10.0:
                        health_score -= 2.5
                    if null_percentage > 50.0:
                        health_score -= 5.0

        except SQLAlchemyError as e:
            return row_count, health_score, stats_out

        return row_count, max(0.0, health_score), stats_out
