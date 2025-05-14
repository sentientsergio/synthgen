```json
[
  {
    "CustomerID": 1,
    "FirstName": "John",
    "LastName": "Doe",
    "Email": "john.doe@example.com",
    "Phone": "123-456-7890",
    "StatusCode": "A",
    "CreatedDate": "2023-10-01T10:00:00",
    "ModifiedDate": "2023-10-02T12:00:00"
  },
  {
    "CustomerID": 2,
    "FirstName": "Jane",
    "LastName": "Smith",
    "Email": "jane.smith@example.com",
    "Phone": "987-654-3210",
    "StatusCode": "B",
    "CreatedDate": "2023-10-03T09:30:00",
    "ModifiedDate": "2023-10-04T11:15:00"
  },
  {
    "CustomerID": 3,
    "FirstName": "Alice",
    "LastName": "Johnson",
    "Email": "alice.johnson@example.com",
    "Phone": "555-123-4567",
    "StatusCode": "C",
    "CreatedDate": "2023-10-05T08:45:00",
    "ModifiedDate": null
  }
]
```

### Explanation:
- **CustomerID**: Unique integer values for each row.
- **FirstName** and **LastName**: Varied realistic names.
- **Email**: Valid email addresses adhering to the check constraint.
- **Phone**: Different phone numbers within the VARCHAR(20) limit.
- **StatusCode**: Assumed valid status codes "A", "B", and "C" from the `CustomerStatus` table.
- **CreatedDate**: Realistic timestamps for when the customer was created.
- **ModifiedDate**: Some entries have a modified date, while others do not, reflecting possible real-world scenarios.