import argparse
import datetime
import os
import uuid

import numpy as np
import pandas as pd
import sqlalchemy as sa


def setup_table(engine):
    with engine.begin() as connection:
        connection.execute(
            sa.text("""
        DROP TABLE IF EXISTS dummy_metrics;
        CREATE TABLE dummy_metrics (
            created_at TIMESTAMPTZ,
            value1 INTEGER,
            value2 VARCHAR,
            value3 FLOAT
        );
        """)
        )


def generate_data(n):
    return pd.DataFrame(
        {
            "created_at": pd.date_range(
                start=datetime.date.today(),
                periods=n,
                freq="10s",
                tz="America/Los_Angeles",
            ),
            "value1": np.random.randint(0, 1000, size=n),
            "value2": [str(uuid.uuid4()) for _ in range(n)],
            "value3": np.random.rand(n),
        }
    )


def insert_data(data, engine):
    with engine.begin() as connection:
        data.to_sql(
            name="dummy_metrics",
            con=connection,
            if_exists="append",
            index=False,
            method="multi",
            chunksize=10_000,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate dummy metrics and insert to the database."
    )
    parser.add_argument(
        "-n",
        type=int,
        default=100,
        help="Number of dummy metrics to generate",
    )
    args = parser.parse_args()

    engine = sa.create_engine(os.environ["MONITORING_DB_CONNECTION_URL"])

    setup_table(engine)
    data = generate_data(args.n)
    insert_data(data, engine)
