# -*- coding: utf-8 -*-
import graphene
from collections import OrderedDict
from .base_types import Binary
from .settings import gdc_settings

try:
    from graphene_file_upload.scalars import Upload

    graphene_file_upload_instaled = True
except:
    graphene_file_upload_instaled = False


def gen_inputType_filter(
    name,
    field,
    with_number_filter=False,
    with_text_filter=False,
    with_date_filter=False,
    with_time_filter=False,
    with_case_insensitive_filter=False,
):

    items = OrderedDict()

    if gdc_settings.SCALAR_FILTERS_ADD_EQUALS_FIELD:
        items["equals"] = graphene.InputField(
            field, description="(Deprecated) Exact match."
        )
    items["exact"] = graphene.InputField(field, description="Exact match.")
    items["in"] = graphene.InputField(
        graphene.List(field, description="In a given list.")
    )
    items["isnull"] = graphene.Boolean(description="Is null.")

    if with_number_filter:
        items["gt"] = graphene.InputField(field, description="Greater than.")
        items["gte"] = graphene.InputField(
            field, description="Greater than or equal to."
        )
        items["lt"] = graphene.InputField(field, description="Less than.")
        items["lte"] = graphene.InputField(field, description="Less than or equal to.")

    if with_text_filter:
        items["contains"] = graphene.InputField(field, description="Containment test.")
        items["startswith"] = graphene.InputField(field, description="Starts-with.")
        items["endswith"] = graphene.InputField(field, description="Ends-with.")
        items["regex"] = graphene.String(description="regular expression match.")

    if with_case_insensitive_filter:
        items["iexact"] = graphene.InputField(
            field, description="Case-insensitive exact match."
        )
        items["icontains"] = graphene.InputField(
            field, description="Case-insensitive containment test."
        )
        items["istartswith"] = graphene.InputField(
            field, description="Case-insensitive starts-with."
        )
        items["iendswith"] = graphene.InputField(
            field, description="Case-insensitive ends-with."
        )

    if with_date_filter:
        items["year"] = graphene.InputField(
            IntFilter, description="An exact year match."
        )
        items["month"] = graphene.InputField(
            IntFilter,
            description="An exact month match. Takes an integer 1 (January) through 12 (December).",
        )
        items["day"] = graphene.InputField(IntFilter, description="An exact day match.")
        items["week_day"] = graphene.InputField(
            IntFilter,
            description="A ‘day of the week’ match. Takes an integer value representing the day of week from 1 (Sunday) to 7 (Saturday).",
        )

    if with_time_filter:
        items["hour"] = graphene.InputField(
            IntFilter,
            description="An exact hour match. Takes an integer between 0 and 23.",
        )
        items["minute"] = graphene.InputField(
            IntFilter,
            description="An exact minute match. Takes an integer between 0 and 59.",
        )
        items["second"] = graphene.InputField(
            IntFilter,
            description="an exact second match. Takes an integer between 0 and 59.",
        )

    return type(
        name,
        (graphene.InputObjectType,),
        items,
    )


IDfilter = gen_inputType_filter("IDFilter", graphene.ID)

if gdc_settings.BOOLEAN_FILTER_USE_BOOLEAN_FIELD:
    BooleanFilter = graphene.Boolean
else:
    BooleanFilter = gen_inputType_filter("BooleanFilter", graphene.Boolean)

UUIDFilter = gen_inputType_filter("UUIDFilter", graphene.UUID)

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
    "StringFilter",
    graphene.String,
    with_number_filter=False,
    with_text_filter=True,
    with_case_insensitive_filter=True,
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
    "TimeFilter",
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


class FileInput(graphene.InputObjectType):
    if graphene_file_upload_instaled:
        upload = Upload()
    filename = graphene.String()
    content = Binary()
