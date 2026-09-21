from datetime import datetime
from dateutil.relativedelta import relativedelta

from prefect import flow

import score


@flow
def run(start_date, end_date):
    d = start_date
    while d <= end_date:
        score.run(
            taxi_type="green",
            year=d.year,
            month=d.month,
            model_id="m-205aad2b19454838af2cfe5644624f7e",
        )
        d = d + relativedelta(months=1)


if __name__ == "__main__":
    run(
        start_date=datetime(year=2021, month=3, day=1),
        end_date=datetime(year=2022, month=4, day=1),
    )
