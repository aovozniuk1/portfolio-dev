"""Aggregation transformations for summary reporting."""

import logging

import pandas as pd

logger = logging.getLogger(__name__)


class Aggregator:
    """Computes summary statistics and aggregations from cleaned sales data."""

    def aggregate(self, df: pd.DataFrame) -> dict:
        """Produce a summary report dictionary.

        Sections:
            - overview: total revenue, orders, average order value
            - by_region: revenue and order count per region
            - by_product: revenue and quantity per product
            - monthly_trends: revenue per month
            - top_customers: top 10 customers by total spend

        Args:
            df: Cleaned dataframe with 'total', 'month', etc.

        Returns:
            Nested dictionary suitable for JSON serialization.
        """
        summary = {
            "overview": self._overview(df),
            "by_region": self._by_region(df),
            "by_product": self._by_product(df),
            "monthly_trends": self._monthly_trends(df),
            "top_customers": self._top_customers(df),
        }
        logger.info("Generated summary report with %d sections", len(summary))
        return summary

    @staticmethod
    def _overview(df: pd.DataFrame) -> dict:
        total_revenue = round(float(df["total"].sum()), 2)
        total_orders = len(df)
        avg_order = round(total_revenue / total_orders, 2) if total_orders else 0
        return {
            "total_revenue": total_revenue,
            "total_orders": total_orders,
            "average_order_value": avg_order,
            "unique_products": int(df["product"].nunique()),
            "unique_customers": int(df["customer_email"].nunique()),
            "date_range": {
                "start": str(df["date"].min().date()),
                "end": str(df["date"].max().date()),
            },
        }

    @staticmethod
    def _by_region(df: pd.DataFrame) -> list:
        grouped = (
            df.groupby("region")
            .agg(revenue=("total", "sum"), orders=("total", "count"))
            .round(2)
            .sort_values("revenue", ascending=False)
        )
        return [
            {"region": region, "revenue": float(row["revenue"]), "orders": int(row["orders"])}
            for region, row in grouped.iterrows()
        ]

    @staticmethod
    def _by_product(df: pd.DataFrame) -> list:
        grouped = (
            df.groupby("product")
            .agg(
                revenue=("total", "sum"),
                quantity_sold=("quantity", "sum"),
                avg_price=("price", "mean"),
            )
            .round(2)
            .sort_values("revenue", ascending=False)
        )
        return [
            {
                "product": product,
                "revenue": float(row["revenue"]),
                "quantity_sold": int(row["quantity_sold"]),
                "avg_price": float(row["avg_price"]),
            }
            for product, row in grouped.iterrows()
        ]

    @staticmethod
    def _monthly_trends(df: pd.DataFrame) -> list:
        grouped = (
            df.groupby("month")
            .agg(revenue=("total", "sum"), orders=("total", "count"))
            .round(2)
            .sort_index()
        )
        return [
            {"month": month, "revenue": float(row["revenue"]), "orders": int(row["orders"])}
            for month, row in grouped.iterrows()
        ]

    @staticmethod
    def _top_customers(df: pd.DataFrame, top_n: int = 10) -> list:
        grouped = (
            df.groupby("customer_email")
            .agg(total_spent=("total", "sum"), order_count=("total", "count"))
            .round(2)
            .sort_values("total_spent", ascending=False)
            .head(top_n)
        )
        return [
            {
                "email": email,
                "total_spent": float(row["total_spent"]),
                "order_count": int(row["order_count"]),
            }
            for email, row in grouped.iterrows()
        ]
