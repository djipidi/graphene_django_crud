# -*- coding: utf-8 -*-
import graphene
from collections import OrderedDict


def gen_inputType_filter(
    name,
    field,
    with_number_filter=False,
    with_text_filter=False,
    with_date_filter=False,
    with_time_filter=False,
):

    items = OrderedDict()

    items["equals"] = graphene.Field(field)
    items["in"] = graphene.List(field)
    items["isnull"] = graphene.Boolean()

    if with_number_filter:
        items["gt"] = graphene.Field(field)
        items["gte"] = graphene.Field(field)
        items["lt"] = graphene.Field(field)
        items["lte"] = graphene.Field(field)

    if with_text_filter:
        items["contains"] = graphene.Field(field)
        items["startswith"] = graphene.Field(field)
        items["endswith"] = graphene.Field(field)
        items["regex"] = graphene.String()

    if with_date_filter:
        items["year"] = graphene.Field(IntFilter)
        items["month"] = graphene.Field(IntFilter)
        items["day"] = graphene.Field(IntFilter)
        items["week_day"] = graphene.Field(IntFilter)

    if with_time_filter:
        items["hour"] = graphene.Field(IntFilter)
        items["minute"] = graphene.Field(IntFilter)
        items["second"] = graphene.Field(IntFilter)

    return type(
        name,
        (graphene.InputObjectType,),
        items,
    )


IntFilter = gen_inputType_filter(
    "IntFilter", graphene.Int, with_number_filter=True, with_text_filter=True
)
DecimalFilter = gen_inputType_filter(
    "DecimalFilter", graphene.Decimal, with_number_filter=True, with_text_filter=True
)
FloatFilter = gen_inputType_filter(
    "FloatFilter", graphene.Float, with_number_filter=True, with_text_filter=True
)

StringFilter = gen_inputType_filter(
    "StringFilter", graphene.String, with_number_filter=False, with_text_filter=True
)

DateTimeFilter = gen_inputType_filter(
    "DatetimeFilter",
    graphene.DateTime,
    with_number_filter=True,
    with_text_filter=False,
    with_date_filter=True,
    with_time_filter=True,
)
TimeFilter = gen_inputType_filter(
    "timeFilter",
    graphene.Time,
    with_number_filter=True,
    with_text_filter=False,
    with_time_filter=True,
)
DateFilter = gen_inputType_filter(
    "DateFilter",
    graphene.Date,
    with_number_filter=True,
    with_text_filter=False,
    with_date_filter=True,
)
