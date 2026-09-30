"""
Table Schemas configuration for AdventureWorksDW Medallion Pipeline.
Defines BigQuery TableSchemas and column layouts for all 28+ tables.
"""
from typing import Dict, List
from google.cloud import bigquery

# Schema definition for all 28 DW source tables
TABLE_SCHEMAS: Dict[str, Dict] = {
    "DimAccount": {
        "csv_file": "DimAccount.csv",
        "columns": [
            ("AccountKey", "INTEGER"),
            ("ParentAccountKey", "INTEGER"),
            ("AccountCodeAlternateKey", "INTEGER"),
            ("ParentAccountCodeAlternateKey", "INTEGER"),
            ("AccountDescription", "STRING"),
            ("AccountType", "STRING"),
            ("Operator", "STRING"),
            ("CustomMembers", "STRING"),
            ("ValueType", "STRING"),
            ("CustomMemberOptions", "STRING"),
        ]
    },
    "DimCurrency": {
        "csv_file": "DimCurrency.csv",
        "columns": [
            ("CurrencyKey", "INTEGER"),
            ("CurrencyAlternateKey", "STRING"),
            ("CurrencyName", "STRING"),
        ]
    },
    "DimCustomer": {
        "csv_file": "DimCustomer.csv",
        "columns": [
            ("CustomerKey", "INTEGER"),
            ("GeographyKey", "INTEGER"),
            ("CustomerAlternateKey", "STRING"),
            ("Title", "STRING"),
            ("FirstName", "STRING"),
            ("MiddleName", "STRING"),
            ("LastName", "STRING"),
            ("NameStyle", "BOOLEAN"),
            ("BirthDate", "DATE"),
            ("MaritalStatus", "STRING"),
            ("Suffix", "STRING"),
            ("Gender", "STRING"),
            ("EmailAddress", "STRING"),
            ("YearlyIncome", "NUMERIC"),
            ("TotalChildren", "INTEGER"),
            ("NumberChildrenAtHome", "INTEGER"),
            ("EnglishEducation", "STRING"),
            ("SpanishEducation", "STRING"),
            ("FrenchEducation", "STRING"),
            ("EnglishOccupation", "STRING"),
            ("SpanishOccupation", "STRING"),
            ("FrenchOccupation", "STRING"),
            ("HouseOwnerFlag", "STRING"),
            ("NumberCarsOwned", "INTEGER"),
            ("AddressLine1", "STRING"),
            ("AddressLine2", "STRING"),
            ("Phone", "STRING"),
            ("DateFirstPurchase", "DATE"),
            ("CommuteDistance", "STRING"),
        ]
    },
    "DimDate": {
        "csv_file": "DimDate.csv",
        "columns": [
            ("DateKey", "INTEGER"),
            ("FullDateAlternateKey", "DATE"),
            ("DayNumberOfWeek", "INTEGER"),
            ("EnglishDayNameOfWeek", "STRING"),
            ("SpanishDayNameOfWeek", "STRING"),
            ("FrenchDayNameOfWeek", "STRING"),
            ("DayNumberOfMonth", "INTEGER"),
            ("DayNumberOfYear", "INTEGER"),
            ("WeekNumberOfYear", "INTEGER"),
            ("EnglishMonthName", "STRING"),
            ("SpanishMonthName", "STRING"),
            ("FrenchMonthName", "STRING"),
            ("MonthNumberOfYear", "INTEGER"),
            ("CalendarQuarter", "INTEGER"),
            ("CalendarYear", "INTEGER"),
            ("CalendarSemester", "INTEGER"),
            ("FiscalQuarter", "INTEGER"),
            ("FiscalYear", "INTEGER"),
            ("FiscalSemester", "INTEGER"),
        ]
    },
    "DimDepartmentGroup": {
        "csv_file": "DimDepartmentGroup.csv",
        "columns": [
            ("DepartmentGroupKey", "INTEGER"),
            ("ParentDepartmentGroupKey", "INTEGER"),
            ("DepartmentGroupName", "STRING"),
        ]
    },
    "DimEmployee": {
        "csv_file": "DimEmployee.csv",
        "columns": [
            ("EmployeeKey", "INTEGER"),
            ("ParentEmployeeKey", "INTEGER"),
            ("EmployeeNationalIDAlternateKey", "STRING"),
            ("ParentEmployeeNationalIDAlternateKey", "STRING"),
            ("SalesTerritoryKey", "INTEGER"),
            ("FirstName", "STRING"),
            ("LastName", "STRING"),
            ("MiddleName", "STRING"),
            ("NameStyle", "BOOLEAN"),
            ("Title", "STRING"),
            ("HireDate", "DATE"),
            ("BirthDate", "DATE"),
            ("LoginID", "STRING"),
            ("EmailAddress", "STRING"),
            ("Phone", "STRING"),
            ("MaritalStatus", "STRING"),
            ("EmergencyContactName", "STRING"),
            ("EmergencyContactPhone", "STRING"),
            ("SalariedFlag", "BOOLEAN"),
            ("Gender", "STRING"),
            ("PayFrequency", "INTEGER"),
            ("BaseRate", "NUMERIC"),
            ("VacationHours", "INTEGER"),
            ("SickLeaveHours", "INTEGER"),
            ("CurrentFlag", "BOOLEAN"),
            ("SalesPersonFlag", "BOOLEAN"),
            ("DepartmentName", "STRING"),
            ("StartDate", "DATE"),
            ("EndDate", "DATE"),
            ("Status", "STRING"),
            ("EmployeePhoto", "BYTES"),
        ]
    },
    "DimGeography": {
        "csv_file": "DimGeography.csv",
        "columns": [
            ("GeographyKey", "INTEGER"),
            ("City", "STRING"),
            ("StateProvinceCode", "STRING"),
            ("StateProvinceName", "STRING"),
            ("CountryRegionCode", "STRING"),
            ("EnglishCountryRegionName", "STRING"),
            ("SpanishCountryRegionName", "STRING"),
            ("FrenchCountryRegionName", "STRING"),
            ("PostalCode", "STRING"),
            ("SalesTerritoryKey", "INTEGER"),
            ("IpAddressLocator", "STRING"),
        ]
    },
    "DimOrganization": {
        "csv_file": "DimOrganization.csv",
        "columns": [
            ("OrganizationKey", "INTEGER"),
            ("ParentOrganizationKey", "INTEGER"),
            ("PercentageOfOwnership", "STRING"),
            ("OrganizationName", "STRING"),
            ("CurrencyKey", "INTEGER"),
        ]
    },
    "DimProduct": {
        "csv_file": "DimProduct.csv",
        "columns": [
            ("ProductKey", "INTEGER"),
            ("ProductAlternateKey", "STRING"),
            ("ProductSubcategoryKey", "INTEGER"),
            ("WeightUnitMeasureCode", "STRING"),
            ("SizeUnitMeasureCode", "STRING"),
            ("EnglishProductName", "STRING"),
            ("SpanishProductName", "STRING"),
            ("FrenchProductName", "STRING"),
            ("StandardCost", "NUMERIC"),
            ("FinishedGoodsFlag", "BOOLEAN"),
            ("Color", "STRING"),
            ("SafetyStockLevel", "INTEGER"),
            ("ReorderPoint", "INTEGER"),
            ("ListPrice", "NUMERIC"),
            ("Size", "STRING"),
            ("SizeRange", "STRING"),
            ("Weight", "FLOAT"),
            ("DaysToManufacture", "INTEGER"),
            ("ProductLine", "STRING"),
            ("DealerPrice", "NUMERIC"),
            ("Class", "STRING"),
            ("Style", "STRING"),
            ("ModelName", "STRING"),
            ("LargePhoto", "BYTES"),
            ("EnglishDescription", "STRING"),
            ("FrenchDescription", "STRING"),
            ("ChineseDescription", "STRING"),
            ("ArabicDescription", "STRING"),
            ("HebrewDescription", "STRING"),
            ("ThaiDescription", "STRING"),
            ("GermanDescription", "STRING"),
            ("JapaneseDescription", "STRING"),
            ("TurkishDescription", "STRING"),
            ("StartDate", "TIMESTAMP"),
            ("EndDate", "TIMESTAMP"),
            ("Status", "STRING"),
        ]
    },
    "DimProductCategory": {
        "csv_file": "DimProductCategory.csv",
        "columns": [
            ("ProductCategoryKey", "INTEGER"),
            ("ProductCategoryAlternateKey", "INTEGER"),
            ("EnglishProductCategoryName", "STRING"),
            ("SpanishProductCategoryName", "STRING"),
            ("FrenchProductCategoryName", "STRING"),
        ]
    },
    "DimProductSubcategory": {
        "csv_file": "DimProductSubcategory.csv",
        "columns": [
            ("ProductSubcategoryKey", "INTEGER"),
            ("ProductSubcategoryAlternateKey", "INTEGER"),
            ("EnglishProductSubcategoryName", "STRING"),
            ("SpanishProductSubcategoryName", "STRING"),
            ("FrenchProductSubcategoryName", "STRING"),
            ("ProductCategoryKey", "INTEGER"),
        ]
    },
    "DimPromotion": {
        "csv_file": "DimPromotion.csv",
        "columns": [
            ("PromotionKey", "INTEGER"),
            ("PromotionAlternateKey", "INTEGER"),
            ("EnglishPromotionName", "STRING"),
            ("SpanishPromotionName", "STRING"),
            ("FrenchPromotionName", "STRING"),
            ("DiscountPct", "FLOAT"),
            ("EnglishPromotionType", "STRING"),
            ("SpanishPromotionType", "STRING"),
            ("FrenchPromotionType", "STRING"),
            ("EnglishPromotionCategory", "STRING"),
            ("SpanishPromotionCategory", "STRING"),
            ("FrenchPromotionCategory", "STRING"),
            ("StartDate", "TIMESTAMP"),
            ("EndDate", "TIMESTAMP"),
            ("MinQty", "INTEGER"),
            ("MaxQty", "INTEGER"),
        ]
    },
    "DimReseller": {
        "csv_file": "DimReseller.csv",
        "columns": [
            ("ResellerKey", "INTEGER"),
            ("GeographyKey", "INTEGER"),
            ("ResellerAlternateKey", "STRING"),
            ("Phone", "STRING"),
            ("BusinessType", "STRING"),
            ("ResellerName", "STRING"),
            ("NumberEmployees", "INTEGER"),
            ("OrderFrequency", "STRING"),
            ("OrderMonth", "INTEGER"),
            ("FirstOrderYear", "INTEGER"),
            ("LastOrderYear", "INTEGER"),
            ("ProductLine", "STRING"),
            ("AddressLine1", "STRING"),
            ("AddressLine2", "STRING"),
            ("AnnualSales", "NUMERIC"),
            ("BankName", "STRING"),
            ("MinPaymentType", "INTEGER"),
            ("MinPaymentAmount", "NUMERIC"),
            ("AnnualRevenue", "NUMERIC"),
            ("YearOpened", "INTEGER"),
        ]
    },
    "DimSalesReason": {
        "csv_file": "DimSalesReason.csv",
        "columns": [
            ("SalesReasonKey", "INTEGER"),
            ("SalesReasonAlternateKey", "INTEGER"),
            ("SalesReasonName", "STRING"),
            ("SalesReasonReasonType", "STRING"),
        ]
    },
    "DimSalesTerritory": {
        "csv_file": "DimSalesTerritory.csv",
        "columns": [
            ("SalesTerritoryKey", "INTEGER"),
            ("SalesTerritoryAlternateKey", "INTEGER"),
            ("SalesTerritoryRegion", "STRING"),
            ("SalesTerritoryCountry", "STRING"),
            ("SalesTerritoryGroup", "STRING"),
            ("SalesTerritoryImage", "BYTES"),
        ]
    },
    "DimScenario": {
        "csv_file": "DimScenario.csv",
        "columns": [
            ("ScenarioKey", "INTEGER"),
            ("ScenarioName", "STRING"),
        ]
    },
    "FactCallCenter": {
        "csv_file": "FactCallCenter.csv",
        "columns": [
            ("FactCallCenterID", "INTEGER"),
            ("DateKey", "INTEGER"),
            ("WageType", "STRING"),
            ("Shift", "STRING"),
            ("LevelOneOperators", "INTEGER"),
            ("LevelTwoOperators", "INTEGER"),
            ("TotalOperators", "INTEGER"),
            ("Calls", "INTEGER"),
            ("AutomaticResponses", "INTEGER"),
            ("Orders", "INTEGER"),
            ("IssuesRaised", "INTEGER"),
            ("AverageTimePerIssue", "INTEGER"),
            ("ServiceGrade", "FLOAT"),
            ("Date", "TIMESTAMP"),
        ]
    },
    "FactCurrencyRate": {
        "csv_file": "FactCurrencyRate.csv",
        "columns": [
            ("CurrencyKey", "INTEGER"),
            ("DateKey", "INTEGER"),
            ("AverageRate", "FLOAT"),
            ("EndOfDayRate", "FLOAT"),
            ("Date", "TIMESTAMP"),
        ]
    },
    "FactFinance": {
        "csv_file": "FactFinance.csv",
        "columns": [
            ("FinanceKey", "INTEGER"),
            ("DateKey", "INTEGER"),
            ("OrganizationKey", "INTEGER"),
            ("DepartmentGroupKey", "INTEGER"),
            ("ScenarioKey", "INTEGER"),
            ("AccountKey", "INTEGER"),
            ("Amount", "FLOAT"),
            ("Date", "TIMESTAMP"),
        ]
    },
    "FactInternetSales": {
        "csv_file": "FactInternetSales.csv",
        "columns": [
            ("ProductKey", "INTEGER"),
            ("OrderDateKey", "INTEGER"),
            ("DueDateKey", "INTEGER"),
            ("ShipDateKey", "INTEGER"),
            ("CustomerKey", "INTEGER"),
            ("PromotionKey", "INTEGER"),
            ("CurrencyKey", "INTEGER"),
            ("SalesTerritoryKey", "INTEGER"),
            ("SalesOrderNumber", "STRING"),
            ("SalesOrderLineNumber", "INTEGER"),
            ("RevisionNumber", "INTEGER"),
            ("OrderQuantity", "INTEGER"),
            ("UnitPrice", "NUMERIC"),
            ("ExtendedAmount", "NUMERIC"),
            ("UnitPriceDiscountPct", "FLOAT"),
            ("DiscountAmount", "FLOAT"),
            ("ProductStandardCost", "NUMERIC"),
            ("TotalProductCost", "NUMERIC"),
            ("SalesAmount", "NUMERIC"),
            ("TaxAmt", "NUMERIC"),
            ("Freight", "NUMERIC"),
            ("CarrierTrackingNumber", "STRING"),
            ("CustomerPONumber", "STRING"),
            ("OrderDate", "TIMESTAMP"),
            ("DueDate", "TIMESTAMP"),
            ("ShipDate", "TIMESTAMP"),
        ]
    },
    "FactInternetSalesReason": {
        "csv_file": "FactInternetSalesReason.csv",
        "columns": [
            ("SalesOrderNumber", "STRING"),
            ("SalesOrderLineNumber", "INTEGER"),
            ("SalesReasonKey", "INTEGER"),
        ]
    },
    "FactProductInventory": {
        "csv_file": "FactProductInventory.csv",
        "columns": [
            ("ProductKey", "INTEGER"),
            ("DateKey", "INTEGER"),
            ("MovementDate", "DATE"),
            ("UnitCost", "NUMERIC"),
            ("UnitsIn", "INTEGER"),
            ("UnitsOut", "INTEGER"),
            ("UnitsBalance", "INTEGER"),
        ]
    },
    "FactResellerSales": {
        "csv_file": "FactResellerSales.csv",
        "columns": [
            ("ProductKey", "INTEGER"),
            ("OrderDateKey", "INTEGER"),
            ("DueDateKey", "INTEGER"),
            ("ShipDateKey", "INTEGER"),
            ("ResellerKey", "INTEGER"),
            ("EmployeeKey", "INTEGER"),
            ("PromotionKey", "INTEGER"),
            ("CurrencyKey", "INTEGER"),
            ("SalesTerritoryKey", "INTEGER"),
            ("SalesOrderNumber", "STRING"),
            ("SalesOrderLineNumber", "INTEGER"),
            ("RevisionNumber", "INTEGER"),
            ("OrderQuantity", "INTEGER"),
            ("UnitPrice", "NUMERIC"),
            ("ExtendedAmount", "NUMERIC"),
            ("UnitPriceDiscountPct", "FLOAT"),
            ("DiscountAmount", "FLOAT"),
            ("ProductStandardCost", "NUMERIC"),
            ("TotalProductCost", "NUMERIC"),
            ("SalesAmount", "NUMERIC"),
            ("TaxAmt", "NUMERIC"),
            ("Freight", "NUMERIC"),
            ("CarrierTrackingNumber", "STRING"),
            ("CustomerPONumber", "STRING"),
            ("OrderDate", "TIMESTAMP"),
            ("DueDate", "TIMESTAMP"),
            ("ShipDate", "TIMESTAMP"),
        ]
    },
    "FactSalesQuota": {
        "csv_file": "FactSalesQuota.csv",
        "columns": [
            ("SalesQuotaKey", "INTEGER"),
            ("EmployeeKey", "INTEGER"),
            ("DateKey", "INTEGER"),
            ("CalendarYear", "INTEGER"),
            ("CalendarQuarter", "INTEGER"),
            ("SalesAmountQuota", "NUMERIC"),
            ("Date", "TIMESTAMP"),
        ]
    },
    "FactSurveyResponse": {
        "csv_file": "FactSurveyResponse.csv",
        "columns": [
            ("SurveyResponseKey", "INTEGER"),
            ("DateKey", "INTEGER"),
            ("CustomerKey", "INTEGER"),
            ("ProductCategoryKey", "INTEGER"),
            ("EnglishProductCategoryName", "STRING"),
            ("ProductSubcategoryKey", "INTEGER"),
            ("EnglishProductSubcategoryName", "STRING"),
            ("Date", "TIMESTAMP"),
        ]
    },
    "ProspectiveBuyer": {
        "csv_file": "ProspectiveBuyer.csv",
        "columns": [
            ("ProspectiveBuyerKey", "INTEGER"),
            ("ProspectAlternateKey", "STRING"),
            ("FirstName", "STRING"),
            ("MiddleName", "STRING"),
            ("LastName", "STRING"),
            ("BirthDate", "TIMESTAMP"),
            ("MaritalStatus", "STRING"),
            ("Gender", "STRING"),
            ("EmailAddress", "STRING"),
            ("YearlyIncome", "NUMERIC"),
            ("TotalChildren", "INTEGER"),
            ("NumberChildrenAtHome", "INTEGER"),
            ("Education", "STRING"),
            ("Occupation", "STRING"),
            ("HouseOwnerFlag", "STRING"),
            ("NumberCarsOwned", "INTEGER"),
            ("AddressLine1", "STRING"),
            ("AddressLine2", "STRING"),
            ("City", "STRING"),
            ("StateProvinceCode", "STRING"),
            ("PostalCode", "STRING"),
            ("Phone", "STRING"),
            ("Salutation", "STRING"),
            ("Unknown", "INTEGER"),
        ]
    }
}

def get_bq_schema(table_name: str, add_metadata_fields: bool = True) -> List[bigquery.SchemaField]:
    """Generates BigQuery SchemaField list for a table."""
    table_def = TABLE_SCHEMAS.get(table_name)
    if not table_def:
        raise ValueError(f"Table '{table_name}' not defined in TABLE_SCHEMAS.")
    
    fields = []
    for col_name, col_type in table_def["columns"]:
        fields.append(bigquery.SchemaField(col_name, col_type, mode="NULLABLE"))
        
    if add_metadata_fields:
        fields.append(bigquery.SchemaField("_ingested_at", "TIMESTAMP", mode="NULLABLE", description="Dataflow ingestion timestamp"))
        fields.append(bigquery.SchemaField("_source_file", "STRING", mode="NULLABLE", description="Source GCS file path"))
        fields.append(bigquery.SchemaField("_raw_row_id", "STRING", mode="NULLABLE", description="Unique ingestion row identifier"))
        
    return fields
