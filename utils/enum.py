import enum

import sqlalchemy.types


def gtfs_enum_type(vanilla_enum: enum.Enum):
    return sqlalchemy.types.Enum(
        vanilla_enum,
        values_callable=lambda x: [str(member.value) for member in vanilla_enum],
    )
