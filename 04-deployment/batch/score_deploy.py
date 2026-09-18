import pathlib

from prefect import flow


if __name__ == "__main__":
    (
        flow.from_source(
            source=pathlib.Path(__file__).parent,
            entrypoint="score.py:run",
        ).deploy(
            name="scoring-batch-deploy",
            work_pool_name="local-pool",
            parameters={
                "taxi_type": "green",
                "year": 2021,
                "month": 2,
                "model_id": "m-205aad2b19454838af2cfe5644624f7e",
            },
        )
    )
