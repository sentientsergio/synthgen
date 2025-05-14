{
  "name": "EcommerceDB",
  "tables": [
    {
      "name": "EmailSubscription",
      "description": "Table for managing email subscriptions of users.",
      "columns": [
        {
          "name": "SubscriptionID",
          "data_type": {
            "name": "INT"
          },
          "nullable": false,
          "default_value": null,
          "is_identity": true,
          "description": "Unique identifier for each subscription."
        },
        {
          "name": "UserID",
          "data_type": {
            "name": "INT"
          },
          "nullable": true,
          "default_value": null,
          "is_identity": false,
          "description": "Identifier for the user associated with the subscription."
        },
        {
          "name": "Email",
          "data_type": {
            "name": "NVARCHAR",
            "length": 100
          },
          "nullable": false,
          "default_value": null,
          "is_identity": false,
          "description": "Email address of the subscriber."
        },
        {
          "name": "IsSubscribed",
          "data_type": {
            "name": "BIT"
          },
          "nullable": false,
          "default_value": "1",
          "is_identity": false,
          "description": "Indicates if the user is currently subscribed."
        },
        {
          "name": "SubscriptionDate",
          "data_type": {
            "name": "DATETIME"
          },
          "nullable": false,
          "default_value": "GETDATE()",
          "is_identity": false,
          "description": "Date when the subscription was created."
        },
        {
          "name": "UnsubscriptionDate",
          "data_type": {
            "name": "DATETIME"
          },
          "nullable": true,
          "default_value": null,
          "is_identity": false,
          "description": "Date when the subscription was cancelled."
        }
      ],
      "primary_key": {
        "name": "PK_EmailSubscription",
        "columns": [
          "SubscriptionID"
        ]
      },
      "foreign_keys": [
        {
          "name": "FK_EmailSubscription_User",
          "columns": [
            "UserID"
          ],
          "ref_table": "User",
          "ref_columns": [
            "UserID"
          ],
          "on_delete": "SET NULL",
          "on_update": null
        }
      ],
      "check_constraints": [],
      "is_reference_table": false
    }
  ],
  "description": "Schema for managing ecommerce email subscriptions.",
  "generation_rules": []
}