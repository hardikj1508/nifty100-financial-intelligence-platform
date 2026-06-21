# Data Quality Report

## Overview

This report summarizes the quality assessment of all datasets used in the Nifty 100 Financial Intelligence Platform project.

Validation checks performed:

- Dataset shape
- Missing values
- Duplicate records
- Column standardization

## Companies

Shape: (92, 12)
Missing Values:
- company_logo: 1
- website: 1
- nse_profile: 1
- bse_profile: 1
- face_value: 1
- book_value: 1
- roce_percentage: 1
- roe_percentage: 2

Duplicate Rows: 0
Remarks:Dataset is mostly complete. A small number of financial fields are missing.

## Balance Sheet

Shape: (1312, 13)
Missing Values: 0
Duplicate Rows: 0
Remarks:Dataset is complete with no missing values.

## Cash Flow

Shape: (1187, 7)
Missing Values: 8
Duplicate Rows: 0
Remarks:A few cash flow values are unavailable in the source dataset.

## Documents

Shape: (1585, 4)
Missing Values: 52
Duplicate Rows: 0
Remarks:Several annual report links are unavailable.

## Financial Ratios

Shape: (1184, 16)
Missing Values: 170
Duplicate Rows: 0
Remarks:Missing values occur in ratio-related metrics and are expected from source data.

## Market Cap

Shape: (552, 9)
Missing Values: 0
Duplicate Rows: 0
Remarks:Dataset is complete.

## Peer Groups

Shape: (56, 4)
Missing Values: 0
Duplicate Rows: 0
Remarks:Dataset is complete.

## Profit & Loss

Shape: (1276, 15)
Missing Values: 231
Duplicate Rows: 0
Remarks:Some profitability metrics are missing from the source dataset.

## Pros and Cons

Shape: (16, 4)
Missing Values: 6
Duplicate Rows: 0
Remarks:Some companies do not have pros or cons information available.

## Sectors

Shape: (92, 6)
Missing Values: 0
Duplicate Rows: 0
Remarks:Dataset is complete.

## Stock Prices

Shape: (5520, 9)
Missing Values: 0
Duplicate Rows: 0
Remarks:Dataset is complete.

## Analysis

Shape: (20, 6)
Missing Values: 0
Duplicate Rows: 0
Remarks:Dataset is complete.

# Summary

Total datasets analyzed: 10

Findings:
- No duplicate records detected.
- Column names successfully standardized.
- Most datasets are complete.
- Missing values exist in a few datasets due to unavailable source information.
- Processed datasets have been saved successfully for downstream analytics and dashboard development.

# Manual Data Quality Review

## Random Company Review
ATGL, GAIL, APOLLOHOSP, EICHERMOT, BEL

## Sample Verification
ATGL records reviewed manually and values appeared valid.

## Year Coverage
Min Year: Dec 2012
Max Year: TTM

## Companies with <5 Years Data
JIOFIN (3 years)

## Foreign Key Check
0 violations

## Result
Manual review completed successfully.