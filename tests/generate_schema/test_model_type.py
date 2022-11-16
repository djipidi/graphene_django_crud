# -*- coding: utf-8 -*-
from tests.utils import SchemaTestCase


class DjangoCRUDObjectTypeSchemaTest(SchemaTestCase):
    def test_model_type(self):

        fields_to_test = [
            {
                "name": "id",
                "type": {"kind": "SCALAR", "name": "ID", "ofType": None},
                "args": [],
            },
            {
                "name": "binaryField",
                "type": {"kind": "SCALAR", "name": "Binary", "ofType": None},
                "args": [],
            },
            {
                "name": "booleanField",
                "type": {"kind": "SCALAR", "name": "Boolean", "ofType": None},
                "args": [],
            },
            {
                "name": "booleanFieldNullable",
                "type": {"kind": "SCALAR", "name": "Boolean", "ofType": None},
                "args": [],
            },
            {
                "name": "nullBooleanField",
                "type": {"kind": "SCALAR", "name": "Boolean", "ofType": None},
                "args": [],
            },
            {
                "name": "charField",
                "type": {"kind": "SCALAR", "name": "String", "ofType": None},
                "args": [],
            },
            {
                "name": "charFieldUnique",
                "type": {"kind": "SCALAR", "name": "String", "ofType": None},
                "args": [],
            },
            {
                "name": "charFieldNullable",
                "type": {"kind": "SCALAR", "name": "String", "ofType": None},
                "args": [],
            },
            {
                "name": "dateField",
                "type": {"kind": "SCALAR", "name": "Date", "ofType": None},
                "args": [],
            },
            {
                "name": "datetimeField",
                "type": {"kind": "SCALAR", "name": "DateTime", "ofType": None},
                "args": [],
            },
            {
                "name": "timeField",
                "type": {"kind": "SCALAR", "name": "Time", "ofType": None},
                "args": [],
            },
            {
                "name": "decimalField",
                "type": {"kind": "SCALAR", "name": "Float", "ofType": None},
                "args": [],
            },
            {
                "name": "durationField",
                "type": {"kind": "SCALAR", "name": "Float", "ofType": None},
                "args": [],
            },
            {
                "name": "emailField",
                "type": {"kind": "SCALAR", "name": "String", "ofType": None},
                "args": [],
            },
            {
                "name": "floatField",
                "type": {"kind": "SCALAR", "name": "Float", "ofType": None},
                "args": [],
            },
            {
                "name": "integerField",
                "type": {"kind": "SCALAR", "name": "Int", "ofType": None},
                "args": [],
            },
            {
                "name": "integerFieldUnique",
                "type": {"kind": "SCALAR", "name": "Int", "ofType": None},
                "args": [],
            },
            {
                "name": "smallIntegerField",
                "type": {"kind": "SCALAR", "name": "Int", "ofType": None},
                "args": [],
            },
            {
                "name": "smallIntegerFieldUnique",
                "type": {"kind": "SCALAR", "name": "Int", "ofType": None},
                "args": [],
            },
            {
                "name": "positiveIntegerField",
                "type": {"kind": "SCALAR", "name": "Int", "ofType": None},
                "args": [],
            },
            {
                "name": "positiveIntegerFieldUnique",
                "type": {"kind": "SCALAR", "name": "Int", "ofType": None},
                "args": [],
            },
            {
                "name": "slugField",
                "type": {"kind": "SCALAR", "name": "String", "ofType": None},
                "args": [],
            },
            {
                "name": "slugFieldUnique",
                "type": {"kind": "SCALAR", "name": "String", "ofType": None},
                "args": [],
            },
            {
                "name": "textField",
                "type": {"kind": "SCALAR", "name": "String", "ofType": None},
                "args": [],
            },
            {
                "name": "textFieldNullable",
                "type": {"kind": "SCALAR", "name": "String", "ofType": None},
                "args": [],
            },
            {
                "name": "urlField",
                "type": {"kind": "SCALAR", "name": "String", "ofType": None},
                "args": [],
            },
            {
                "name": "urlFieldUnique",
                "type": {"kind": "SCALAR", "name": "String", "ofType": None},
                "args": [],
            },
            {
                "name": "uuidField",
                "type": {"kind": "SCALAR", "name": "UUID", "ofType": None},
                "args": [],
            },
            {
                "name": "uuidFieldUnique",
                "type": {"kind": "SCALAR", "name": "UUID", "ofType": None},
                "args": [],
            },
            {
                "name": "foreignKeyField",
                "type": {
                    "kind": "OBJECT",
                    "name": "ModelTestGenerateSchemaAType",
                    "ofType": None,
                },
                "args": [],
            },
            {
                "name": "manytomanyField",
                "type": {
                    "kind": "OBJECT",
                    "name": "ModelTestGenerateSchemaATypeConnection",
                    "ofType": None,
                },
                "args": [
                    {
                        "name": "where",
                        "type": {
                            "kind": "INPUT_OBJECT",
                            "name": "ModelTestGenerateSchemaAWhereInput",
                            "ofType": None,
                        },
                    },
                    {
                        "name": "orderBy",
                        "type": {
                            "kind": "LIST",
                            "name": None,
                            "ofType": {
                                "kind": "INPUT_OBJECT",
                                "name": "ModelTestGenerateSchemaAOrderByInput",
                            },
                        },
                    },
                    {
                        "name": "limit",
                        "type": {"kind": "SCALAR", "name": "Int", "ofType": None},
                    },
                    {
                        "name": "offset",
                        "type": {"kind": "SCALAR", "name": "Int", "ofType": None},
                    },
                ],
            },
            {
                "name": "foreignKeyRelated",
                "type": {
                    "kind": "OBJECT",
                    "name": "ModelTestGenerateSchemaATypeConnection",
                    "ofType": None,
                },
                "args": [
                    {
                        "name": "where",
                        "type": {
                            "kind": "INPUT_OBJECT",
                            "name": "ModelTestGenerateSchemaAWhereInput",
                            "ofType": None,
                        },
                    },
                    {
                        "name": "orderBy",
                        "type": {
                            "kind": "LIST",
                            "name": None,
                            "ofType": {
                                "kind": "INPUT_OBJECT",
                                "name": "ModelTestGenerateSchemaAOrderByInput",
                            },
                        },
                    },
                    {
                        "name": "limit",
                        "type": {"kind": "SCALAR", "name": "Int", "ofType": None},
                    },
                    {
                        "name": "offset",
                        "type": {"kind": "SCALAR", "name": "Int", "ofType": None},
                    },
                ],
            },
            {
                "name": "oneToOneRelated",
                "type": {
                    "kind": "OBJECT",
                    "name": "ModelTestGenerateSchemaAType",
                    "ofType": None,
                },
                "args": [],
            },
            {
                "name": "manyToManyRelated",
                "type": {
                    "kind": "OBJECT",
                    "name": "ModelTestGenerateSchemaATypeConnection",
                    "ofType": None,
                },
                "args": [
                    {
                        "name": "where",
                        "type": {
                            "kind": "INPUT_OBJECT",
                            "name": "ModelTestGenerateSchemaAWhereInput",
                            "ofType": None,
                        },
                    },
                    {
                        "name": "orderBy",
                        "type": {
                            "kind": "LIST",
                            "name": None,
                            "ofType": {
                                "kind": "INPUT_OBJECT",
                                "name": "ModelTestGenerateSchemaAOrderByInput",
                            },
                        },
                    },
                    {
                        "name": "limit",
                        "type": {"kind": "SCALAR", "name": "Int", "ofType": None},
                    },
                    {
                        "name": "offset",
                        "type": {"kind": "SCALAR", "name": "Int", "ofType": None},
                    },
                ],
            },
            {
                "name": "foreignKeyBRelated",
                "type": {
                    "kind": "OBJECT",
                    "name": "ModelTestGenerateSchemaBTypeConnection",
                    "ofType": None,
                },
                "args": [
                    {
                        "name": "where",
                        "type": {
                            "kind": "INPUT_OBJECT",
                            "name": "ModelTestGenerateSchemaBWhereInput",
                            "ofType": None,
                        },
                    },
                    {
                        "name": "orderBy",
                        "type": {
                            "kind": "LIST",
                            "name": None,
                            "ofType": {
                                "kind": "INPUT_OBJECT",
                                "name": "ModelTestGenerateSchemaBOrderByInput",
                            },
                        },
                    },
                    {
                        "name": "limit",
                        "type": {"kind": "SCALAR", "name": "Int", "ofType": None},
                    },
                    {
                        "name": "offset",
                        "type": {"kind": "SCALAR", "name": "Int", "ofType": None},
                    },
                ],
            },
            {
                "name": "oneToOneBRelated",
                "type": {
                    "kind": "OBJECT",
                    "name": "ModelTestGenerateSchemaBType",
                    "ofType": None,
                },
                "args": [],
            },
            {
                "name": "manyToManyBRelated",
                "type": {
                    "kind": "OBJECT",
                    "name": "ModelTestGenerateSchemaBTypeConnection",
                    "ofType": None,
                },
                "args": [
                    {
                        "name": "where",
                        "type": {
                            "kind": "INPUT_OBJECT",
                            "name": "ModelTestGenerateSchemaBWhereInput",
                            "ofType": None,
                        },
                    },
                    {
                        "name": "orderBy",
                        "type": {
                            "kind": "LIST",
                            "name": None,
                            "ofType": {
                                "kind": "INPUT_OBJECT",
                                "name": "ModelTestGenerateSchemaBOrderByInput",
                            },
                        },
                    },
                    {
                        "name": "limit",
                        "type": {"kind": "SCALAR", "name": "Int", "ofType": None},
                    },
                    {
                        "name": "offset",
                        "type": {"kind": "SCALAR", "name": "Int", "ofType": None},
                    },
                ],
            },
        ]
        self.runtest_fields_of_type("ModelTestGenerateSchemaAType", fields_to_test)

    def test_model_where_input_type(self):
        fields_to_test = [
            {
                "name": "id",
                "type": {"kind": "INPUT_OBJECT", "name": "IDFilter", "ofType": None},
            },
            {
                "name": "booleanField",
                "type": {
                    "kind": "INPUT_OBJECT",
                    "name": "BooleanFilter",
                    "ofType": None,
                },
            },
            {
                "name": "booleanFieldNullable",
                "type": {
                    "kind": "INPUT_OBJECT",
                    "name": "BooleanFilter",
                    "ofType": None,
                },
            },
            {
                "name": "nullBooleanField",
                "type": {
                    "kind": "INPUT_OBJECT",
                    "name": "BooleanFilter",
                    "ofType": None,
                },
            },
            {
                "name": "charField",
                "type": {
                    "kind": "INPUT_OBJECT",
                    "name": "StringFilter",
                    "ofType": None,
                },
            },
            {
                "name": "charFieldUnique",
                "type": {
                    "kind": "INPUT_OBJECT",
                    "name": "StringFilter",
                    "ofType": None,
                },
            },
            {
                "name": "charFieldNullable",
                "type": {
                    "kind": "INPUT_OBJECT",
                    "name": "StringFilter",
                    "ofType": None,
                },
            },
            {
                "name": "dateField",
                "type": {"kind": "INPUT_OBJECT", "name": "DateFilter", "ofType": None},
            },
            {
                "name": "datetimeField",
                "type": {
                    "kind": "INPUT_OBJECT",
                    "name": "DatetimeFilter",
                    "ofType": None,
                },
            },
            {
                "name": "timeField",
                "type": {"kind": "INPUT_OBJECT", "name": "TimeFilter", "ofType": None},
            },
            {
                "name": "decimalField",
                "type": {"kind": "INPUT_OBJECT", "name": "FloatFilter", "ofType": None},
            },
            {
                "name": "durationField",
                "type": {"kind": "INPUT_OBJECT", "name": "FloatFilter", "ofType": None},
            },
            {
                "name": "emailField",
                "type": {
                    "kind": "INPUT_OBJECT",
                    "name": "StringFilter",
                    "ofType": None,
                },
            },
            {
                "name": "floatField",
                "type": {"kind": "INPUT_OBJECT", "name": "FloatFilter", "ofType": None},
            },
            {
                "name": "integerField",
                "type": {"kind": "INPUT_OBJECT", "name": "IntFilter", "ofType": None},
            },
            {
                "name": "integerFieldUnique",
                "type": {"kind": "INPUT_OBJECT", "name": "IntFilter", "ofType": None},
            },
            {
                "name": "smallIntegerField",
                "type": {"kind": "INPUT_OBJECT", "name": "IntFilter", "ofType": None},
            },
            {
                "name": "smallIntegerFieldUnique",
                "type": {"kind": "INPUT_OBJECT", "name": "IntFilter", "ofType": None},
            },
            {
                "name": "positiveIntegerField",
                "type": {"kind": "INPUT_OBJECT", "name": "IntFilter", "ofType": None},
            },
            {
                "name": "positiveIntegerFieldUnique",
                "type": {"kind": "INPUT_OBJECT", "name": "IntFilter", "ofType": None},
            },
            {
                "name": "slugField",
                "type": {
                    "kind": "INPUT_OBJECT",
                    "name": "StringFilter",
                    "ofType": None,
                },
            },
            {
                "name": "slugFieldUnique",
                "type": {
                    "kind": "INPUT_OBJECT",
                    "name": "StringFilter",
                    "ofType": None,
                },
            },
            {
                "name": "textField",
                "type": {
                    "kind": "INPUT_OBJECT",
                    "name": "StringFilter",
                    "ofType": None,
                },
            },
            {
                "name": "textFieldNullable",
                "type": {
                    "kind": "INPUT_OBJECT",
                    "name": "StringFilter",
                    "ofType": None,
                },
            },
            {
                "name": "urlField",
                "type": {
                    "kind": "INPUT_OBJECT",
                    "name": "StringFilter",
                    "ofType": None,
                },
            },
            {
                "name": "urlFieldUnique",
                "type": {
                    "kind": "INPUT_OBJECT",
                    "name": "StringFilter",
                    "ofType": None,
                },
            },
            {
                "name": "uuidField",
                "type": {"kind": "INPUT_OBJECT", "name": "UUIDFilter", "ofType": None},
            },
            {
                "name": "uuidFieldUnique",
                "type": {"kind": "INPUT_OBJECT", "name": "UUIDFilter", "ofType": None},
            },
            {
                "name": "foreignKeyField",
                "type": {
                    "kind": "INPUT_OBJECT",
                    "name": "ModelTestGenerateSchemaAWhereInput",
                    "ofType": None,
                },
            },
            {
                "name": "manytomanyField",
                "type": {
                    "kind": "INPUT_OBJECT",
                    "name": "ModelTestGenerateSchemaAWhereInput",
                    "ofType": None,
                },
            },
            {
                "name": "foreignKeyRelated",
                "type": {
                    "kind": "INPUT_OBJECT",
                    "name": "ModelTestGenerateSchemaAWhereInput",
                    "ofType": None,
                },
            },
            {
                "name": "oneToOneRelated",
                "type": {
                    "kind": "INPUT_OBJECT",
                    "name": "ModelTestGenerateSchemaAWhereInput",
                    "ofType": None,
                },
            },
            {
                "name": "manyToManyRelated",
                "type": {
                    "kind": "INPUT_OBJECT",
                    "name": "ModelTestGenerateSchemaAWhereInput",
                    "ofType": None,
                },
            },
            {
                "name": "foreignKeyBRelated",
                "type": {
                    "kind": "INPUT_OBJECT",
                    "name": "ModelTestGenerateSchemaBWhereInput",
                    "ofType": None,
                },
            },
            {
                "name": "oneToOneBRelated",
                "type": {
                    "kind": "INPUT_OBJECT",
                    "name": "ModelTestGenerateSchemaBWhereInput",
                    "ofType": None,
                },
            },
            {
                "name": "manyToManyBRelated",
                "type": {
                    "kind": "INPUT_OBJECT",
                    "name": "ModelTestGenerateSchemaBWhereInput",
                    "ofType": None,
                },
            },
            {
                "name": "OR",
                "type": {
                    "kind": "LIST",
                    "name": None,
                    "ofType": {
                        "kind": "INPUT_OBJECT",
                        "name": "ModelTestGenerateSchemaAWhereInput",
                    },
                },
            },
            {
                "name": "AND",
                "type": {
                    "kind": "LIST",
                    "name": None,
                    "ofType": {
                        "kind": "INPUT_OBJECT",
                        "name": "ModelTestGenerateSchemaAWhereInput",
                    },
                },
            },
            {
                "name": "NOT",
                "type": {
                    "kind": "INPUT_OBJECT",
                    "name": "ModelTestGenerateSchemaAWhereInput",
                    "ofType": None,
                },
            },
        ]
        self.runtest_fields_of_type(
            "ModelTestGenerateSchemaAWhereInput", fields_to_test, input_type=True
        )

    def test_model_create_input_type(self):

        fields_to_test = [
            {
                "name": "binaryField",
                "type": {
                    "kind": "NON_NULL",
                    "name": None,
                    "ofType": {"kind": "SCALAR", "name": "Binary"},
                },
            },
            {
                "name": "booleanField",
                "type": {
                    "kind": "NON_NULL",
                    "name": None,
                    "ofType": {"kind": "SCALAR", "name": "Boolean"},
                },
            },
            {
                "name": "booleanFieldNullable",
                "type": {"kind": "SCALAR", "name": "Boolean", "ofType": None},
            },
            {
                "name": "nullBooleanField",
                "type": {"kind": "SCALAR", "name": "Boolean", "ofType": None},
            },
            {
                "name": "charField",
                "type": {
                    "kind": "NON_NULL",
                    "name": None,
                    "ofType": {"kind": "SCALAR", "name": "String"},
                },
            },
            {
                "name": "charFieldUnique",
                "type": {
                    "kind": "NON_NULL",
                    "name": None,
                    "ofType": {"kind": "SCALAR", "name": "String"},
                },
            },
            {
                "name": "charFieldNullable",
                "type": {"kind": "SCALAR", "name": "String", "ofType": None},
            },
            {
                "name": "dateField",
                "type": {
                    "kind": "NON_NULL",
                    "name": None,
                    "ofType": {"kind": "SCALAR", "name": "Date"},
                },
            },
            {
                "name": "datetimeField",
                "type": {
                    "kind": "NON_NULL",
                    "name": None,
                    "ofType": {"kind": "SCALAR", "name": "DateTime"},
                },
            },
            {
                "name": "timeField",
                "type": {
                    "kind": "NON_NULL",
                    "name": None,
                    "ofType": {"kind": "SCALAR", "name": "Time"},
                },
            },
            {
                "name": "decimalField",
                "type": {
                    "kind": "NON_NULL",
                    "name": None,
                    "ofType": {"kind": "SCALAR", "name": "Float"},
                },
            },
            {
                "name": "durationField",
                "type": {
                    "kind": "NON_NULL",
                    "name": None,
                    "ofType": {"kind": "SCALAR", "name": "Float"},
                },
            },
            {
                "name": "emailField",
                "type": {
                    "kind": "NON_NULL",
                    "name": None,
                    "ofType": {"kind": "SCALAR", "name": "String"},
                },
            },
            {
                "name": "floatField",
                "type": {
                    "kind": "NON_NULL",
                    "name": None,
                    "ofType": {"kind": "SCALAR", "name": "Float"},
                },
            },
            {
                "name": "integerField",
                "type": {
                    "kind": "NON_NULL",
                    "name": None,
                    "ofType": {"kind": "SCALAR", "name": "Int"},
                },
            },
            {
                "name": "integerFieldUnique",
                "type": {
                    "kind": "NON_NULL",
                    "name": None,
                    "ofType": {"kind": "SCALAR", "name": "Int"},
                },
            },
            {
                "name": "smallIntegerField",
                "type": {
                    "kind": "NON_NULL",
                    "name": None,
                    "ofType": {"kind": "SCALAR", "name": "Int"},
                },
            },
            {
                "name": "smallIntegerFieldUnique",
                "type": {
                    "kind": "NON_NULL",
                    "name": None,
                    "ofType": {"kind": "SCALAR", "name": "Int"},
                },
            },
            {
                "name": "positiveIntegerField",
                "type": {
                    "kind": "NON_NULL",
                    "name": None,
                    "ofType": {"kind": "SCALAR", "name": "Int"},
                },
            },
            {
                "name": "positiveIntegerFieldUnique",
                "type": {
                    "kind": "NON_NULL",
                    "name": None,
                    "ofType": {"kind": "SCALAR", "name": "Int"},
                },
            },
            {
                "name": "slugField",
                "type": {
                    "kind": "NON_NULL",
                    "name": None,
                    "ofType": {"kind": "SCALAR", "name": "String"},
                },
            },
            {
                "name": "slugFieldUnique",
                "type": {
                    "kind": "NON_NULL",
                    "name": None,
                    "ofType": {"kind": "SCALAR", "name": "String"},
                },
            },
            {
                "name": "textField",
                "type": {
                    "kind": "NON_NULL",
                    "name": None,
                    "ofType": {"kind": "SCALAR", "name": "String"},
                },
            },
            {
                "name": "textFieldNullable",
                "type": {"kind": "SCALAR", "name": "String", "ofType": None},
            },
            {
                "name": "urlField",
                "type": {
                    "kind": "NON_NULL",
                    "name": None,
                    "ofType": {"kind": "SCALAR", "name": "String"},
                },
            },
            {
                "name": "urlFieldUnique",
                "type": {
                    "kind": "NON_NULL",
                    "name": None,
                    "ofType": {"kind": "SCALAR", "name": "String"},
                },
            },
            {
                "name": "uuidField",
                "type": {
                    "kind": "NON_NULL",
                    "name": None,
                    "ofType": {"kind": "SCALAR", "name": "UUID"},
                },
            },
            {
                "name": "uuidFieldUnique",
                "type": {
                    "kind": "NON_NULL",
                    "name": None,
                    "ofType": {"kind": "SCALAR", "name": "UUID"},
                },
            },
            {
                "name": "foreignKeyField",
                "type": {
                    "kind": "INPUT_OBJECT",
                    "name": "ModelTestGenerateSchemaACreateNestedInput",
                    "ofType": None,
                },
            },
            {
                "name": "manytomanyField",
                "type": {
                    "kind": "INPUT_OBJECT",
                    "name": "ModelTestGenerateSchemaACreateNestedManyInput",
                    "ofType": None,
                },
            },
            {
                "name": "foreignKeyRelated",
                "type": {
                    "kind": "INPUT_OBJECT",
                    "name": "ModelTestGenerateSchemaACreateNestedManyInput",
                    "ofType": None,
                },
            },
            {
                "name": "oneToOneRelated",
                "type": {
                    "kind": "INPUT_OBJECT",
                    "name": "ModelTestGenerateSchemaACreateNestedInput",
                    "ofType": None,
                },
            },
            {
                "name": "manyToManyRelated",
                "type": {
                    "kind": "INPUT_OBJECT",
                    "name": "ModelTestGenerateSchemaACreateNestedManyInput",
                    "ofType": None,
                },
            },
            {
                "name": "foreignKeyBRelated",
                "type": {
                    "kind": "INPUT_OBJECT",
                    "name": "ModelTestGenerateSchemaBCreateNestedManyInput",
                    "ofType": None,
                },
            },
            {
                "name": "oneToOneBRelated",
                "type": {
                    "kind": "INPUT_OBJECT",
                    "name": "ModelTestGenerateSchemaBCreateNestedInput",
                    "ofType": None,
                },
            },
            {
                "name": "manyToManyBRelated",
                "type": {
                    "kind": "INPUT_OBJECT",
                    "name": "ModelTestGenerateSchemaBCreateNestedManyInput",
                    "ofType": None,
                },
            },
        ]
        self.runtest_fields_of_type(
            "ModelTestGenerateSchemaACreateInput", fields_to_test, input_type=True
        )

    def test_model_update_input_type(self):

        fields_to_test = [
            {
                "name": "binaryField",
                "type": {"kind": "SCALAR", "name": "Binary", "ofType": None},
            },
            {
                "name": "booleanField",
                "type": {"kind": "SCALAR", "name": "Boolean", "ofType": None},
            },
            {
                "name": "booleanFieldNullable",
                "type": {"kind": "SCALAR", "name": "Boolean", "ofType": None},
            },
            {
                "name": "nullBooleanField",
                "type": {"kind": "SCALAR", "name": "Boolean", "ofType": None},
            },
            {
                "name": "charField",
                "type": {"kind": "SCALAR", "name": "String", "ofType": None},
            },
            {
                "name": "charFieldUnique",
                "type": {"kind": "SCALAR", "name": "String", "ofType": None},
            },
            {
                "name": "charFieldNullable",
                "type": {"kind": "SCALAR", "name": "String", "ofType": None},
            },
            {
                "name": "dateField",
                "type": {"kind": "SCALAR", "name": "Date", "ofType": None},
            },
            {
                "name": "datetimeField",
                "type": {"kind": "SCALAR", "name": "DateTime", "ofType": None},
            },
            {
                "name": "timeField",
                "type": {"kind": "SCALAR", "name": "Time", "ofType": None},
            },
            {
                "name": "decimalField",
                "type": {"kind": "SCALAR", "name": "Float", "ofType": None},
            },
            {
                "name": "durationField",
                "type": {"kind": "SCALAR", "name": "Float", "ofType": None},
            },
            {
                "name": "emailField",
                "type": {"kind": "SCALAR", "name": "String", "ofType": None},
            },
            {
                "name": "floatField",
                "type": {"kind": "SCALAR", "name": "Float", "ofType": None},
            },
            {
                "name": "integerField",
                "type": {"kind": "SCALAR", "name": "Int", "ofType": None},
            },
            {
                "name": "integerFieldUnique",
                "type": {"kind": "SCALAR", "name": "Int", "ofType": None},
            },
            {
                "name": "smallIntegerField",
                "type": {"kind": "SCALAR", "name": "Int", "ofType": None},
            },
            {
                "name": "smallIntegerFieldUnique",
                "type": {"kind": "SCALAR", "name": "Int", "ofType": None},
            },
            {
                "name": "positiveIntegerField",
                "type": {"kind": "SCALAR", "name": "Int", "ofType": None},
            },
            {
                "name": "positiveIntegerFieldUnique",
                "type": {"kind": "SCALAR", "name": "Int", "ofType": None},
            },
            {
                "name": "slugField",
                "type": {"kind": "SCALAR", "name": "String", "ofType": None},
            },
            {
                "name": "slugFieldUnique",
                "type": {"kind": "SCALAR", "name": "String", "ofType": None},
            },
            {
                "name": "textField",
                "type": {"kind": "SCALAR", "name": "String", "ofType": None},
            },
            {
                "name": "textFieldNullable",
                "type": {"kind": "SCALAR", "name": "String", "ofType": None},
            },
            {
                "name": "urlField",
                "type": {"kind": "SCALAR", "name": "String", "ofType": None},
            },
            {
                "name": "urlFieldUnique",
                "type": {"kind": "SCALAR", "name": "String", "ofType": None},
            },
            {
                "name": "uuidField",
                "type": {"kind": "SCALAR", "name": "UUID", "ofType": None},
            },
            {
                "name": "uuidFieldUnique",
                "type": {"kind": "SCALAR", "name": "UUID", "ofType": None},
            },
            {
                "name": "foreignKeyField",
                "type": {
                    "kind": "INPUT_OBJECT",
                    "name": "ModelTestGenerateSchemaAUpdateNestedInput",
                    "ofType": None,
                },
            },
            {
                "name": "manytomanyField",
                "type": {
                    "kind": "INPUT_OBJECT",
                    "name": "ModelTestGenerateSchemaAUpdateNestedManyInput",
                    "ofType": None,
                },
            },
            {
                "name": "foreignKeyRelated",
                "type": {
                    "kind": "INPUT_OBJECT",
                    "name": "ModelTestGenerateSchemaAUpdateNestedManyInput",
                    "ofType": None,
                },
            },
            {
                "name": "oneToOneRelated",
                "type": {
                    "kind": "INPUT_OBJECT",
                    "name": "ModelTestGenerateSchemaAUpdateNestedInput",
                    "ofType": None,
                },
            },
            {
                "name": "manyToManyRelated",
                "type": {
                    "kind": "INPUT_OBJECT",
                    "name": "ModelTestGenerateSchemaAUpdateNestedManyInput",
                    "ofType": None,
                },
            },
            {
                "name": "foreignKeyBRelated",
                "type": {
                    "kind": "INPUT_OBJECT",
                    "name": "ModelTestGenerateSchemaBUpdateNestedManyInput",
                    "ofType": None,
                },
            },
            {
                "name": "oneToOneBRelated",
                "type": {
                    "kind": "INPUT_OBJECT",
                    "name": "ModelTestGenerateSchemaBUpdateNestedInput",
                    "ofType": None,
                },
            },
            {
                "name": "manyToManyBRelated",
                "type": {
                    "kind": "INPUT_OBJECT",
                    "name": "ModelTestGenerateSchemaBUpdateNestedManyInput",
                    "ofType": None,
                },
            },
        ]
        self.runtest_fields_of_type(
            "ModelTestGenerateSchemaAUpdateInput", fields_to_test, input_type=True
        )

    def test_nested_create(self):

        fields_to_test = [
            {
                "name": "create",
                "type": {
                    "kind": "INPUT_OBJECT",
                    "name": "ModelTestGenerateSchemaBCreateInput",
                    "ofType": None
                }
            },
            {
                "name": "connect",
                "type": {
                    "kind": "INPUT_OBJECT",
                    "name": "ModelTestGenerateSchemaBWhereInput",
                    "ofType": None
                }
            }
        ]
        self.runtest_fields_of_type(
            "ModelTestGenerateSchemaBCreateNestedInput", fields_to_test, input_type=True
        )

    def test_only_exclude_extend_fields_options(self):
        with self.subTest():
            self.assertTypeIsComposeOfFields(
                "ModelTestGenerateSchemaCCreateInput",
                ["createExtend", "createUpdateOnly", "createOnly", "allInput"],
                input_type=True,
            )
        with self.subTest():
            self.assertTypeIsComposeOfFields(
                "ModelTestGenerateSchemaCUpdateInput",
                ["updateExtend", "createUpdateOnly", "updateOnly", "allInput"],
                input_type=True,
            )
        with self.subTest():
            self.assertTypeIsComposeOfFields(
                "ModelTestGenerateSchemaCWhereInput",
                ["id", "OR", "AND", "NOT", "whereOnly", "allInput"],
                input_type=True,
            )
        with self.subTest():
            self.assertTypeIsComposeOfFields(
                "ModelTestGenerateSchemaCOrderByInput",
                ["orderByOnly", "allInput"],
                input_type=True,
            )
        with self.subTest():
            self.assertTypeIsComposeOfFields(
                "ModelTestGenerateSchemaDCreateInput",
                ["createExtend", "createUpdateOnly", "createOnly", "allInput"],
                input_type=True,
            )
        with self.subTest():
            self.assertTypeIsComposeOfFields(
                "ModelTestGenerateSchemaDUpdateInput",
                ["updateExtend", "createUpdateOnly", "updateOnly", "allInput"],
                input_type=True,
            )
        with self.subTest():
            self.assertTypeIsComposeOfFields(
                "ModelTestGenerateSchemaDWhereInput",
                ["id", "OR", "AND", "NOT", "whereOnly", "allInput"],
                input_type=True,
            )
        with self.subTest():
            self.assertTypeIsComposeOfFields(
                "ModelTestGenerateSchemaDOrderByInput",
                ["id", "orderByOnly", "allInput"],
                input_type=True,
            )

    def test_disable_nested_mutations(self):
        with self.subTest():
            self.assertTypeIsComposeOfFields(
                "ModelTestGenerateSchemaFCreateNestedInput",
                ["connect"],
                input_type=True,
            )
        with self.subTest():
            self.assertTypeIsComposeOfFields(
                "ModelTestGenerateSchemaFCreateNestedManyInput",
                ["connect"],
                input_type=True,
            )
        with self.subTest():
            self.assertTypeIsComposeOfFields(
                "ModelTestGenerateSchemaFCreateNestedInput",
                ["connect"],
                input_type=True,
            )
        with self.subTest():
            self.assertTypeIsComposeOfFields(
                "ModelTestGenerateSchemaFUpdateNestedInput",
                ["connect", "disconnect"],
                input_type=True,
            )
        with self.subTest():
            self.assertTypeIsComposeOfFields(
                "ModelTestGenerateSchemaFUpdateNestedManyInput",
                ["connect", "disconnect"],
                input_type=True,
            )
        with self.subTest():
            self.assertTypeIsComposeOfFields(
                "ModelTestGenerateSchemaFUpdateNestedInput",
                ["connect", "disconnect"],
                input_type=True,
            )