import { makeAssetApi } from './api/assets'
import type { AssetTypeConfig, FieldConfig, FieldOption } from './types/asset'

const HIDDEN_PROFILE: FieldConfig = {
  key: 'profile_id',
  label: 'Profile',
  type: 'select',
  required: true,
  hidden: true,
}

function opts(pairs: Array<[string, string]>): FieldOption[] {
  return pairs.map(([value, label]) => ({ value, label }))
}

// ---------------------------------------------------------------------------
// 1. Mutual Fund Holdings
// ---------------------------------------------------------------------------
export const mutualFundsConfig: AssetTypeConfig = {
  resourcePath: 'mutual-funds',
  title: 'Mutual Fund Holdings',
  singularLabel: 'Mutual Fund',
  api: makeAssetApi('mutual-funds'),
  fields: [
    HIDDEN_PROFILE,
    { key: 'folio_number', label: 'Folio Number', type: 'text', required: true },
    { key: 'scheme_name', label: 'Scheme Name', type: 'text', required: true },
    { key: 'scheme_code', label: 'Scheme Code', type: 'text', showInTable: false },
    { key: 'amc_name', label: 'AMC Name', type: 'text' },
    { key: 'units_held', label: 'Units Held', type: 'number', required: true },
    { key: 'avg_nav', label: 'Avg NAV', type: 'number' },
    { key: 'current_nav', label: 'Current NAV', type: 'number' },
    { key: 'invested_amount', label: 'Invested Amount', type: 'number', format: 'currency' },
    { key: 'current_value', label: 'Current Value', type: 'number', format: 'currency' },
  ],
}

// ---------------------------------------------------------------------------
// 2. Mutual Fund Transactions
// ---------------------------------------------------------------------------
export const mutualFundTransactionsConfig: AssetTypeConfig = {
  resourcePath: 'mutual-fund-transactions',
  title: 'Mutual Fund Transactions',
  singularLabel: 'Transaction',
  api: makeAssetApi('mutual-fund-transactions'),
  fields: [
    HIDDEN_PROFILE,
    { key: 'folio_number', label: 'Folio Number', type: 'text', required: true },
    { key: 'transaction_date', label: 'Transaction Date', type: 'datetime', required: true },
    {
      key: 'transaction_type',
      label: 'Type',
      type: 'select',
      required: true,
      options: opts([
        ['purchase', 'Purchase'],
        ['redemption', 'Redemption'],
        ['switch_in', 'Switch In'],
        ['switch_out', 'Switch Out'],
        ['dividend', 'Dividend'],
        ['sip', 'SIP'],
      ]),
    },
    { key: 'units', label: 'Units', type: 'number' },
    { key: 'nav', label: 'NAV', type: 'number' },
    { key: 'amount', label: 'Amount', type: 'number', format: 'currency' },
    { key: 'cas_source_file', label: 'CAS Source File', type: 'text', showInTable: false },
  ],
}

// ---------------------------------------------------------------------------
// 3. Stock Holdings
// ---------------------------------------------------------------------------
export const stocksConfig: AssetTypeConfig = {
  resourcePath: 'stocks',
  title: 'Stock Holdings',
  singularLabel: 'Stock',
  api: makeAssetApi('stocks'),
  fields: [
    HIDDEN_PROFILE,
    {
      key: 'exchange',
      label: 'Exchange',
      type: 'select',
      defaultValue: 'NSE',
      options: opts([
        ['NSE', 'NSE'],
        ['BSE', 'BSE'],
      ]),
    },
    { key: 'ticker', label: 'Ticker', type: 'text', required: true },
    { key: 'company_name', label: 'Company Name', type: 'text' },
    { key: 'isin', label: 'ISIN', type: 'text', showInTable: false },
    { key: 'quantity', label: 'Quantity', type: 'number', required: true },
    { key: 'avg_buy_price', label: 'Avg Buy Price', type: 'number', format: 'currency' },
    { key: 'current_price', label: 'Current Price', type: 'number', format: 'currency' },
    { key: 'broker', label: 'Broker', type: 'text' },
  ],
}

// ---------------------------------------------------------------------------
// 4. Stock Transactions
// ---------------------------------------------------------------------------
export const stockTransactionsConfig: AssetTypeConfig = {
  resourcePath: 'stock-transactions',
  title: 'Stock Transactions',
  singularLabel: 'Transaction',
  api: makeAssetApi('stock-transactions'),
  fields: [
    HIDDEN_PROFILE,
    { key: 'ticker', label: 'Ticker', type: 'text', required: true },
    { key: 'transaction_date', label: 'Transaction Date', type: 'datetime', required: true },
    {
      key: 'action',
      label: 'Action',
      type: 'select',
      required: true,
      options: opts([
        ['buy', 'Buy'],
        ['sell', 'Sell'],
      ]),
    },
    { key: 'quantity', label: 'Quantity', type: 'number', required: true },
    { key: 'price', label: 'Price', type: 'number', required: true, format: 'currency' },
    { key: 'brokerage', label: 'Brokerage', type: 'number', defaultValue: 0, format: 'currency' },
    { key: 'notes', label: 'Notes', type: 'textarea', showInTable: false },
  ],
}

// ---------------------------------------------------------------------------
// 5. Deposits (FD/RD)
// ---------------------------------------------------------------------------
export const depositsConfig: AssetTypeConfig = {
  resourcePath: 'deposits',
  title: 'Fixed & Recurring Deposits',
  singularLabel: 'Deposit',
  api: makeAssetApi('deposits'),
  fields: [
    HIDDEN_PROFILE,
    {
      key: 'type',
      label: 'Type',
      type: 'select',
      defaultValue: 'FD',
      options: opts([
        ['FD', 'FD'],
        ['RD', 'RD'],
      ]),
    },
    { key: 'bank_name', label: 'Bank Name', type: 'text', required: true },
    { key: 'branch', label: 'Branch', type: 'text', showInTable: false },
    { key: 'principal_amount', label: 'Principal Amount', type: 'number', required: true, format: 'currency' },
    { key: 'interest_rate', label: 'Interest Rate', type: 'number', required: true, format: 'percent' },
    {
      key: 'compounding',
      label: 'Compounding',
      type: 'select',
      defaultValue: 'quarterly',
      options: opts([
        ['monthly', 'Monthly'],
        ['quarterly', 'Quarterly'],
        ['annual', 'Annual'],
      ]),
      showInTable: false,
    },
    { key: 'start_date', label: 'Start Date', type: 'date', required: true },
    { key: 'maturity_date', label: 'Maturity Date', type: 'date' },
    { key: 'maturity_amount', label: 'Maturity Amount', type: 'number', format: 'currency' },
    { key: 'is_joint', label: 'Joint Account', type: 'boolean', defaultValue: false },
    { key: 'joint_holder_name', label: 'Joint Holder Name', type: 'text', showInTable: false },
    { key: 'nomination', label: 'Nomination', type: 'text', showInTable: false },
    { key: 'notes', label: 'Notes', type: 'textarea', showInTable: false },
    { key: 'is_active', label: 'Active', type: 'boolean', defaultValue: true },
  ],
}

// ---------------------------------------------------------------------------
// 6. Provident Funds
// ---------------------------------------------------------------------------
export const providentFundsConfig: AssetTypeConfig = {
  resourcePath: 'provident-funds',
  title: 'Provident Funds',
  singularLabel: 'Provident Fund',
  api: makeAssetApi('provident-funds'),
  fields: [
    HIDDEN_PROFILE,
    {
      key: 'type',
      label: 'Type',
      type: 'select',
      defaultValue: 'PPF',
      options: opts([
        ['PPF', 'PPF'],
        ['EPF', 'EPF'],
        ['GPF', 'GPF'],
        ['VPF', 'VPF'],
      ]),
    },
    { key: 'account_number', label: 'Account Number', type: 'text' },
    { key: 'bank_or_employer', label: 'Bank / Employer', type: 'text' },
    { key: 'opening_balance', label: 'Opening Balance', type: 'number', defaultValue: 0, format: 'currency' },
    { key: 'current_balance', label: 'Current Balance', type: 'number', defaultValue: 0, format: 'currency' },
    { key: 'interest_rate', label: 'Interest Rate', type: 'number', format: 'percent' },
    { key: 'maturity_date', label: 'Maturity Date', type: 'date' },
    { key: 'annual_contributions', label: 'Annual Contributions', type: 'text', showInTable: false },
    { key: 'employer_contribution', label: 'Employer Contribution', type: 'number', format: 'currency', showInTable: false },
  ],
}

// ---------------------------------------------------------------------------
// 7. Sukanya Samriddhi
// ---------------------------------------------------------------------------
export const sukanyaSamriddhiConfig: AssetTypeConfig = {
  resourcePath: 'sukanya-samriddhi',
  title: 'Sukanya Samriddhi',
  singularLabel: 'Account',
  api: makeAssetApi('sukanya-samriddhi'),
  fields: [
    HIDDEN_PROFILE,
    { key: 'account_number', label: 'Account Number', type: 'text' },
    { key: 'post_office_bank', label: 'Post Office / Bank', type: 'text' },
    { key: 'date_of_birth_child', label: 'Child DOB', type: 'date', showInTable: false },
    { key: 'account_opening_date', label: 'Opening Date', type: 'date', required: true },
    { key: 'maturity_date', label: 'Maturity Date', type: 'date' },
    { key: 'current_balance', label: 'Current Balance', type: 'number', defaultValue: 0, format: 'currency' },
    { key: 'interest_rate', label: 'Interest Rate', type: 'number', format: 'percent' },
    { key: 'annual_contributions', label: 'Annual Contributions', type: 'text', showInTable: false },
  ],
}

// ---------------------------------------------------------------------------
// 8. NPS
// ---------------------------------------------------------------------------
export const npsConfig: AssetTypeConfig = {
  resourcePath: 'nps',
  title: 'National Pension System',
  singularLabel: 'NPS Account',
  api: makeAssetApi('nps'),
  fields: [
    HIDDEN_PROFILE,
    { key: 'pran_number', label: 'PRAN Number', type: 'text' },
    {
      key: 'tier',
      label: 'Tier',
      type: 'select',
      defaultValue: 'Tier1',
      options: opts([
        ['Tier1', 'Tier 1'],
        ['Tier2', 'Tier 2'],
      ]),
    },
    { key: 'fund_manager', label: 'Fund Manager', type: 'text', showInTable: false },
    { key: 'scheme_preference', label: 'Scheme Preference', type: 'text', showInTable: false },
    { key: 'equity_pct', label: 'Equity %', type: 'number', format: 'percent' },
    { key: 'corporate_bond_pct', label: 'Corp Bond %', type: 'number', format: 'percent', showInTable: false },
    { key: 'govt_bond_pct', label: 'Govt Bond %', type: 'number', format: 'percent', showInTable: false },
    { key: 'current_nav', label: 'Current NAV', type: 'number', showInTable: false },
    { key: 'units_held', label: 'Units Held', type: 'number', showInTable: false },
    { key: 'current_value', label: 'Current Value', type: 'number', format: 'currency' },
    { key: 'employer_contribution_annual', label: 'Employer Contribution (Annual)', type: 'number', format: 'currency', showInTable: false },
    { key: 'self_contribution_annual', label: 'Self Contribution (Annual)', type: 'number', format: 'currency', showInTable: false },
  ],
}

// ---------------------------------------------------------------------------
// 9. Gold
// ---------------------------------------------------------------------------
export const goldConfig: AssetTypeConfig = {
  resourcePath: 'gold',
  title: 'Gold',
  singularLabel: 'Gold Holding',
  api: makeAssetApi('gold'),
  fields: [
    HIDDEN_PROFILE,
    {
      key: 'type',
      label: 'Type',
      type: 'select',
      defaultValue: 'physical',
      options: opts([
        ['physical', 'Physical'],
        ['SGB', 'Sovereign Gold Bond'],
        ['digital_gold', 'Digital Gold'],
        ['gold_etf', 'Gold ETF'],
        ['gold_fund', 'Gold Fund'],
      ]),
    },
    { key: 'quantity_grams', label: 'Quantity (grams)', type: 'number' },
    { key: 'units', label: 'Units', type: 'number', showInTable: false },
    { key: 'buy_price_per_gram_or_unit', label: 'Buy Price / gram or unit', type: 'number', format: 'currency' },
    { key: 'current_price_per_gram_or_unit', label: 'Current Price / gram or unit', type: 'number', format: 'currency' },
    { key: 'purchase_date', label: 'Purchase Date', type: 'date' },
    { key: 'sgb_series', label: 'SGB Series', type: 'text', showInTable: false },
    { key: 'sgb_maturity_date', label: 'SGB Maturity Date', type: 'date', showInTable: false },
    { key: 'sgb_interest_rate', label: 'SGB Interest Rate', type: 'number', format: 'percent', showInTable: false },
    { key: 'custodian', label: 'Custodian', type: 'text', showInTable: false },
    { key: 'notes', label: 'Notes', type: 'textarea', showInTable: false },
  ],
}

// ---------------------------------------------------------------------------
// 10. Real Estate
// ---------------------------------------------------------------------------
export const realEstateConfig: AssetTypeConfig = {
  resourcePath: 'real-estate',
  title: 'Real Estate',
  singularLabel: 'Property',
  api: makeAssetApi('real-estate'),
  fields: [
    HIDDEN_PROFILE,
    { key: 'property_name', label: 'Property Name', type: 'text', required: true },
    {
      key: 'property_type',
      label: 'Property Type',
      type: 'select',
      defaultValue: 'residential',
      options: opts([
        ['residential', 'Residential'],
        ['commercial', 'Commercial'],
        ['land', 'Land'],
      ]),
    },
    { key: 'address', label: 'Address', type: 'text', showInTable: false },
    { key: 'city', label: 'City', type: 'text' },
    { key: 'state', label: 'State', type: 'text', showInTable: false },
    { key: 'purchase_date', label: 'Purchase Date', type: 'date' },
    { key: 'purchase_price', label: 'Purchase Price', type: 'number', format: 'currency' },
    { key: 'registration_cost', label: 'Registration Cost', type: 'number', format: 'currency', showInTable: false },
    { key: 'stamp_duty', label: 'Stamp Duty', type: 'number', format: 'currency', showInTable: false },
    { key: 'other_costs', label: 'Other Costs', type: 'number', format: 'currency', showInTable: false },
    { key: 'current_estimated_value', label: 'Current Estimated Value', type: 'number', format: 'currency' },
    { key: 'outstanding_loan_amount', label: 'Outstanding Loan', type: 'number', format: 'currency' },
    { key: 'rental_income_monthly', label: 'Monthly Rental Income', type: 'number', format: 'currency' },
    { key: 'is_joint', label: 'Joint Ownership', type: 'boolean', defaultValue: false },
  ],
}

// ---------------------------------------------------------------------------
// 11. International Holdings
// ---------------------------------------------------------------------------
export const internationalConfig: AssetTypeConfig = {
  resourcePath: 'international',
  title: 'International Holdings',
  singularLabel: 'Holding',
  api: makeAssetApi('international'),
  fields: [
    HIDDEN_PROFILE,
    { key: 'platform', label: 'Platform', type: 'text' },
    { key: 'ticker', label: 'Ticker', type: 'text', required: true },
    { key: 'exchange', label: 'Exchange', type: 'text' },
    { key: 'company_name', label: 'Company Name', type: 'text' },
    { key: 'quantity', label: 'Quantity', type: 'number', required: true },
    { key: 'avg_buy_price_usd', label: 'Avg Buy Price (USD)', type: 'number' },
    { key: 'current_price_usd', label: 'Current Price (USD)', type: 'number' },
    { key: 'current_price_inr', label: 'Current Price (INR)', type: 'number', format: 'currency' },
    { key: 'buy_date', label: 'Buy Date', type: 'date', showInTable: false },
    { key: 'lrs_amount_used', label: 'LRS Amount Used', type: 'number', format: 'currency', showInTable: false },
  ],
}

// ---------------------------------------------------------------------------
// 12. Crypto
// ---------------------------------------------------------------------------
export const cryptoConfig: AssetTypeConfig = {
  resourcePath: 'crypto',
  title: 'Crypto',
  singularLabel: 'Crypto Holding',
  api: makeAssetApi('crypto'),
  fields: [
    HIDDEN_PROFILE,
    { key: 'coin_symbol', label: 'Coin Symbol', type: 'text', required: true },
    { key: 'coin_name', label: 'Coin Name', type: 'text' },
    { key: 'exchange', label: 'Exchange', type: 'text' },
    { key: 'quantity', label: 'Quantity', type: 'number', required: true },
    { key: 'avg_buy_price_inr', label: 'Avg Buy Price (INR)', type: 'number', format: 'currency' },
    { key: 'current_price_inr', label: 'Current Price (INR)', type: 'number', format: 'currency' },
  ],
}

// ---------------------------------------------------------------------------
// 13. Post Office Schemes
// ---------------------------------------------------------------------------
export const postOfficeConfig: AssetTypeConfig = {
  resourcePath: 'post-office',
  title: 'Post Office Schemes',
  singularLabel: 'Scheme',
  api: makeAssetApi('post-office'),
  fields: [
    HIDDEN_PROFILE,
    { key: 'scheme_type', label: 'Scheme Type', type: 'text', required: true },
    { key: 'account_number', label: 'Account Number', type: 'text', showInTable: false },
    { key: 'post_office', label: 'Post Office', type: 'text' },
    { key: 'principal_amount', label: 'Principal Amount', type: 'number', required: true, format: 'currency' },
    { key: 'interest_rate', label: 'Interest Rate', type: 'number', required: true, format: 'percent' },
    { key: 'start_date', label: 'Start Date', type: 'date', required: true },
    { key: 'maturity_date', label: 'Maturity Date', type: 'date' },
    { key: 'maturity_amount', label: 'Maturity Amount', type: 'number', format: 'currency' },
    { key: 'payout_frequency', label: 'Payout Frequency', type: 'text', showInTable: false },
    { key: 'notes', label: 'Notes', type: 'textarea', showInTable: false },
  ],
}

// ---------------------------------------------------------------------------
// 14. Goals — profile_id is the ONE resource where it's a real, visible,
// optional select (null = family-level goal), handled specially by AssetForm.
// ---------------------------------------------------------------------------
export const goalsConfig: AssetTypeConfig = {
  resourcePath: 'goals',
  title: 'Goals',
  singularLabel: 'Goal',
  api: makeAssetApi('goals'),
  fields: [
    { key: 'profile_id', label: 'Profile', type: 'select', required: false },
    { key: 'name', label: 'Goal Name', type: 'text', required: true },
    { key: 'target_amount', label: 'Target Amount', type: 'number', required: true, format: 'currency' },
    { key: 'target_date', label: 'Target Date', type: 'date' },
    { key: 'current_value', label: 'Current Value', type: 'number', format: 'currency' },
    { key: 'notes', label: 'Notes', type: 'textarea', showInTable: false },
  ],
}

// ---------------------------------------------------------------------------
// 15. Savings Accounts
// ---------------------------------------------------------------------------
export const savingsAccountsConfig: AssetTypeConfig = {
  resourcePath: 'savings-accounts',
  title: 'Savings Accounts',
  singularLabel: 'Account',
  api: makeAssetApi('savings-accounts'),
  fields: [
    HIDDEN_PROFILE,
    { key: 'bank_name', label: 'Bank Name', type: 'text', required: true },
    {
      key: 'account_type',
      label: 'Account Type',
      type: 'select',
      defaultValue: 'savings',
      options: opts([
        ['savings', 'Savings'],
        ['current', 'Current'],
      ]),
    },
    { key: 'account_number_last4', label: 'Account Number (last 4)', type: 'text' },
    { key: 'current_balance', label: 'Current Balance', type: 'number', defaultValue: 0, format: 'currency' },
  ],
}
